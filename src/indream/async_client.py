from __future__ import annotations

import asyncio
import random
from typing import Any

import httpx

from indream.errors import APIError, Problem, create_api_error
from indream.resources.editor import AsyncEditorResource

TERMINAL_STATUSES = {"COMPLETED", "FAILED", "CANCELED"}


class AsyncExportsResource:
    def __init__(self, request: Any, poll_interval: float) -> None:
        self._request = request
        self._poll_interval = poll_interval

    async def create(
        self,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        data = await self._request(
            "POST",
            "/v1/exports",
            json=payload,
            idempotency_key=idempotency_key,
        )
        if not isinstance(data, dict):
            raise TypeError("Unexpected response payload")
        return data

    async def get(self, task_id: str) -> dict[str, Any]:
        data = await self._request("GET", f"/v1/exports/{task_id}")
        if not isinstance(data, dict):
            raise TypeError("Unexpected response payload")
        return data

    async def list(
        self,
        page_size: int | None = None,
        page_cursor: str | None = None,
        created_by_api_key_id: str | None = None,
    ) -> dict[str, Any]:
        query: list[str] = []
        if page_size is not None:
            query.append(f"pageSize={page_size}")
        if page_cursor is not None:
            query.append(f"pageCursor={page_cursor}")
        if created_by_api_key_id is not None:
            query.append(f"createdByApiKeyId={created_by_api_key_id}")

        suffix = f"?{'&'.join(query)}" if query else ""
        envelope = await self._request("GET", f"/v1/exports{suffix}", unwrap_data=False)

        # Keep the response envelope so pagination cursor metadata stays available.
        if not isinstance(envelope, dict):
            raise TypeError("Unexpected response payload")

        raw_items = envelope.get("data")
        if not isinstance(raw_items, list):
            raise TypeError("Unexpected response payload")

        meta = envelope.get("meta")
        if not isinstance(meta, dict):
            raise TypeError("Unexpected response payload")

        next_page_cursor = meta.get("nextPageCursor")
        if next_page_cursor is not None and not isinstance(next_page_cursor, str):
            raise TypeError("Unexpected response payload")

        items = [item for item in raw_items if isinstance(item, dict)]
        return {"items": items, "nextPageCursor": next_page_cursor}

    async def wait(
        self,
        task_id: str,
        timeout: float = 600,
        poll_interval: float | None = None,
    ) -> dict[str, Any]:
        interval = poll_interval if poll_interval is not None else self._poll_interval
        loop = asyncio.get_running_loop()
        started = loop.time()

        while True:
            if loop.time() - started > timeout:
                raise TimeoutError(f"wait timeout after {timeout} seconds")

            task = await self.get(task_id)
            status = task.get("status")
            if status in TERMINAL_STATUSES:
                if status in {"FAILED", "CANCELED"}:
                    raise APIError(
                        Problem(
                            type="TASK_TERMINAL_FAILURE",
                            title="Task failed",
                            status=422,
                            detail=task.get("error") or f"Task ended with status {status}",
                            error_code="TASK_TERMINAL_FAILURE",
                        )
                    )
                return task

            await asyncio.sleep(interval)


class AsyncIndreamClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.indream.ai",
        timeout: float = 60,
        max_retries: int = 2,
        poll_interval: float = 2,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._poll_interval = poll_interval
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            transport=transport,
        )

        self.exports = AsyncExportsResource(self._request, self._poll_interval)
        self.editor = AsyncEditorResource(self._request)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        skip_retry: bool = False,
        unwrap_data: bool = True,
    ) -> Any:
        attempt = 0

        while True:
            try:
                headers = {
                    "x-api-key": self._api_key,
                    "Accept": "application/json",
                }
                if idempotency_key:
                    headers["Idempotency-Key"] = idempotency_key

                response = await self._client.request(method, path, json=json, headers=headers)
                payload = response.json() if response.content else {}

                if response.status_code >= 400:
                    raise create_api_error(response.status_code, payload)

                if not isinstance(payload, dict) or "data" not in payload:
                    raise create_api_error(response.status_code, payload)

                if "meta" not in payload:
                    raise create_api_error(response.status_code, payload)

                if not unwrap_data:
                    return payload

                data = payload["data"]
                if not isinstance(data, dict):
                    raise create_api_error(response.status_code, payload)

                return data
            except APIError as error:
                if skip_retry:
                    raise

                if not self._should_retry(error.status) or attempt >= self._max_retries:
                    raise

                await self._sleep_with_backoff(attempt)
                attempt += 1
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout):
                if skip_retry or attempt >= self._max_retries:
                    raise
                await self._sleep_with_backoff(attempt)
                attempt += 1

    @staticmethod
    def _should_retry(status: int) -> bool:
        return status == 429 or status >= 500

    @staticmethod
    async def _sleep_with_backoff(attempt: int) -> None:
        base = min(3.0, 0.3 * (2**attempt))
        jitter = random.random() * 0.1
        await asyncio.sleep(base + jitter)
