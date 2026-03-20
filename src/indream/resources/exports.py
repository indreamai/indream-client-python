from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from indream.editor_state_validator import validate_editor_state_or_raise
from indream.errors import APIError, Problem
from indream.types import ExportCreateResponse, ExportTask, ExportTaskListResponse

TERMINAL_STATUSES = {"COMPLETED", "FAILED", "CANCELED"}


class ExportsResource:
    def __init__(self, request: Callable[..., Any], poll_interval: float) -> None:
        self._request = request
        self._poll_interval = poll_interval

    def create(
        self,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> ExportCreateResponse:
        validate_editor_state_or_raise(payload.get("editorState"))
        data = self._request(
            "POST",
            "/v1/exports",
            json=payload,
            idempotency_key=idempotency_key,
        )
        return ExportCreateResponse.model_validate(data)

    def get(self, task_id: str) -> ExportTask:
        data = self._request("GET", f"/v1/exports/{task_id}")
        return ExportTask.model_validate(data)

    def list(
        self,
        page_size: int | None = None,
        page_cursor: str | None = None,
        created_by_api_key_id: str | None = None,
    ) -> ExportTaskListResponse:
        query: list[str] = []
        if page_size is not None:
            query.append(f"pageSize={page_size}")
        if page_cursor is not None:
            query.append(f"pageCursor={page_cursor}")
        if created_by_api_key_id is not None:
            query.append(f"createdByApiKeyId={created_by_api_key_id}")

        suffix = f"?{'&'.join(query)}" if query else ""
        envelope = self._request("GET", f"/v1/exports{suffix}", unwrap_data=False)

        # Keep envelope meta for pagination cursor handling.
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

        items = [ExportTask.model_validate(item) for item in raw_items]
        return ExportTaskListResponse(items=items, nextPageCursor=next_page_cursor)

    def wait(
        self,
        task_id: str,
        timeout: float = 600,
        poll_interval: float | None = None,
    ) -> ExportTask:
        interval = poll_interval if poll_interval is not None else self._poll_interval
        started = time.time()

        # Polling follows the server task state machine and stops only on terminal states.
        while True:
            if time.time() - started > timeout:
                raise TimeoutError(f"wait timeout after {timeout} seconds")

            task = self.get(task_id)
            if task.status in TERMINAL_STATUSES:
                if task.status in {"FAILED", "CANCELED"}:
                    raise APIError(
                        Problem(
                            type="TASK_TERMINAL_FAILURE",
                            title="Task failed",
                            status=422,
                            detail=task.error or f"Task ended with status {task.status}",
                            error_code="TASK_TERMINAL_FAILURE",
                        )
                    )
                return task

            time.sleep(interval)
