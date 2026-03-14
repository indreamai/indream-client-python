from __future__ import annotations

import random
import time
from typing import Any

import httpx

from indream.errors import APIError, create_api_error
from indream.resources.editor import EditorResource
from indream.resources.exports import ExportsResource


class IndreamClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.indream.ai",
        timeout: float = 60,
        max_retries: int = 2,
        poll_interval: float = 2,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._poll_interval = poll_interval
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=self._timeout,
            transport=transport,
        )

        self.exports = ExportsResource(self._request, self._poll_interval)
        self.editor = EditorResource(self._request)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> IndreamClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _request(
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

                response = self._client.request(method, path, json=json, headers=headers)
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

                self._sleep_with_backoff(attempt)
                attempt += 1
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout):
                if skip_retry or attempt >= self._max_retries:
                    raise
                self._sleep_with_backoff(attempt)
                attempt += 1

    @staticmethod
    def _should_retry(status: int) -> bool:
        return status == 429 or status >= 500

    @staticmethod
    def _sleep_with_backoff(attempt: int) -> None:
        # Use exponential backoff with jitter to reduce retry bursts
        # under shared throttling windows.
        base = min(3.0, 0.3 * (2**attempt))
        jitter = random.random() * 0.1
        time.sleep(base + jitter)
