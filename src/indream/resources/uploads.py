from __future__ import annotations

from collections.abc import Callable
from typing import Any

from indream.types import Asset


class UploadsResource:
    def __init__(self, request: Callable[..., Any]) -> None:
        self._request = request

    def upload(
        self,
        content: bytes | bytearray | memoryview,
        *,
        filename: str,
        content_type: str,
        project_id: str | None = None,
    ) -> Asset:
        headers = {
            "Content-Type": content_type,
            "x-file-name": filename,
        }
        if project_id:
            headers["x-project-id"] = project_id

        data = self._request(
            "POST",
            "/v1/uploads",
            content=content,
            headers=headers,
            skip_retry=True,
        )
        return Asset.model_validate(data)


class AsyncUploadsResource:
    def __init__(self, request: Callable[..., Any]) -> None:
        self._request = request

    async def upload(
        self,
        content: bytes | bytearray | memoryview,
        *,
        filename: str,
        content_type: str,
        project_id: str | None = None,
    ) -> Asset:
        headers = {
            "Content-Type": content_type,
            "x-file-name": filename,
        }
        if project_id:
            headers["x-project-id"] = project_id

        data = await self._request(
            "POST",
            "/v1/uploads",
            content=content,
            headers=headers,
            skip_retry=True,
        )
        return Asset.model_validate(data)
