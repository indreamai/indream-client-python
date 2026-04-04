from __future__ import annotations

from collections.abc import Callable
from typing import Any

from indream.editor_state_validator import validate_editor_state_or_raise
from indream.types import (
    AssetListResponse,
    ExportCreateResponse,
    ProjectAssetBindingResponse,
    ProjectAssetDeleteResponse,
    ProjectDeleteResponse,
    ProjectDetail,
    ProjectListResponse,
    ProjectMetadataResponse,
    ProjectSummary,
    ProjectSyncResponse,
)


class ProjectsResource:
    def __init__(self, request: Callable[..., Any]) -> None:
        self._request = request

    def create(
        self,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> ProjectSummary:
        validate_editor_state_or_raise(payload.get("editorState"))
        data = self._request(
            "POST",
            "/v1/projects",
            json=payload,
            idempotency_key=idempotency_key,
        )
        return ProjectSummary.model_validate(data)

    def list(
        self,
        page_size: int | None = None,
        page_cursor: str | None = None,
    ) -> ProjectListResponse:
        query: list[str] = []
        if page_size is not None:
            query.append(f"pageSize={page_size}")
        if page_cursor is not None:
            query.append(f"pageCursor={page_cursor}")

        suffix = f"?{'&'.join(query)}" if query else ""
        envelope = self._request("GET", f"/v1/projects{suffix}", unwrap_data=False)
        raw_items = envelope.get("data")
        meta = envelope.get("meta")

        if not isinstance(raw_items, list) or not isinstance(meta, dict):
            raise TypeError("Unexpected response payload")

        next_page_cursor = meta.get("nextPageCursor")
        if next_page_cursor is not None and not isinstance(next_page_cursor, str):
            raise TypeError("Unexpected response payload")

        items = [ProjectSummary.model_validate(item) for item in raw_items]
        return ProjectListResponse(items=items, nextPageCursor=next_page_cursor)

    def get(self, project_id: str) -> ProjectDetail:
        data = self._request("GET", f"/v1/projects/{project_id}")
        return ProjectDetail.model_validate(data)

    def update(self, project_id: str, payload: dict[str, Any]) -> ProjectMetadataResponse:
        data = self._request("PATCH", f"/v1/projects/{project_id}", json=payload)
        return ProjectMetadataResponse.model_validate(data)

    def sync(self, project_id: str, payload: dict[str, Any]) -> ProjectSyncResponse:
        validate_editor_state_or_raise(payload.get("editorState"))
        data = self._request("POST", f"/v1/projects/{project_id}/sync", json=payload)
        return ProjectSyncResponse.model_validate(data)

    def delete(self, project_id: str) -> ProjectDeleteResponse:
        data = self._request("DELETE", f"/v1/projects/{project_id}")
        return ProjectDeleteResponse.model_validate(data)

    def list_assets(
        self,
        project_id: str,
        page_size: int | None = None,
        page_cursor: str | None = None,
    ) -> AssetListResponse:
        query: list[str] = []
        if page_size is not None:
            query.append(f"pageSize={page_size}")
        if page_cursor is not None:
            query.append(f"pageCursor={page_cursor}")

        suffix = f"?{'&'.join(query)}" if query else ""
        envelope = self._request(
            "GET",
            f"/v1/projects/{project_id}/assets{suffix}",
            unwrap_data=False,
        )
        raw_items = envelope.get("data")
        meta = envelope.get("meta")

        if not isinstance(raw_items, list) or not isinstance(meta, dict):
            raise TypeError("Unexpected response payload")

        next_page_cursor = meta.get("nextPageCursor")
        if next_page_cursor is not None and not isinstance(next_page_cursor, str):
            raise TypeError("Unexpected response payload")

        return AssetListResponse(items=raw_items, nextPageCursor=next_page_cursor)

    def add_asset(self, project_id: str, asset_id: str) -> ProjectAssetBindingResponse:
        data = self._request(
            "POST",
            f"/v1/projects/{project_id}/assets",
            json={"assetId": asset_id},
        )
        return ProjectAssetBindingResponse.model_validate(data)

    def remove_asset(self, project_id: str, asset_id: str) -> ProjectAssetDeleteResponse:
        data = self._request("DELETE", f"/v1/projects/{project_id}/assets/{asset_id}")
        return ProjectAssetDeleteResponse.model_validate(data)

    def create_export(
        self,
        project_id: str,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> ExportCreateResponse:
        data = self._request(
            "POST",
            f"/v1/projects/{project_id}/exports",
            json=payload,
            idempotency_key=idempotency_key,
        )
        return ExportCreateResponse.model_validate(data)


class AsyncProjectsResource:
    def __init__(self, request: Callable[..., Any]) -> None:
        self._request = request

    async def create(
        self,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> ProjectSummary:
        validate_editor_state_or_raise(payload.get("editorState"))
        data = await self._request(
            "POST",
            "/v1/projects",
            json=payload,
            idempotency_key=idempotency_key,
        )
        return ProjectSummary.model_validate(data)

    async def list(
        self,
        page_size: int | None = None,
        page_cursor: str | None = None,
    ) -> ProjectListResponse:
        query: list[str] = []
        if page_size is not None:
            query.append(f"pageSize={page_size}")
        if page_cursor is not None:
            query.append(f"pageCursor={page_cursor}")

        suffix = f"?{'&'.join(query)}" if query else ""
        envelope = await self._request("GET", f"/v1/projects{suffix}", unwrap_data=False)
        raw_items = envelope.get("data")
        meta = envelope.get("meta")

        if not isinstance(raw_items, list) or not isinstance(meta, dict):
            raise TypeError("Unexpected response payload")

        next_page_cursor = meta.get("nextPageCursor")
        if next_page_cursor is not None and not isinstance(next_page_cursor, str):
            raise TypeError("Unexpected response payload")

        items = [ProjectSummary.model_validate(item) for item in raw_items]
        return ProjectListResponse(items=items, nextPageCursor=next_page_cursor)

    async def get(self, project_id: str) -> ProjectDetail:
        data = await self._request("GET", f"/v1/projects/{project_id}")
        return ProjectDetail.model_validate(data)

    async def update(self, project_id: str, payload: dict[str, Any]) -> ProjectMetadataResponse:
        data = await self._request("PATCH", f"/v1/projects/{project_id}", json=payload)
        return ProjectMetadataResponse.model_validate(data)

    async def sync(self, project_id: str, payload: dict[str, Any]) -> ProjectSyncResponse:
        validate_editor_state_or_raise(payload.get("editorState"))
        data = await self._request("POST", f"/v1/projects/{project_id}/sync", json=payload)
        return ProjectSyncResponse.model_validate(data)

    async def delete(self, project_id: str) -> ProjectDeleteResponse:
        data = await self._request("DELETE", f"/v1/projects/{project_id}")
        return ProjectDeleteResponse.model_validate(data)

    async def list_assets(
        self,
        project_id: str,
        page_size: int | None = None,
        page_cursor: str | None = None,
    ) -> AssetListResponse:
        query: list[str] = []
        if page_size is not None:
            query.append(f"pageSize={page_size}")
        if page_cursor is not None:
            query.append(f"pageCursor={page_cursor}")

        suffix = f"?{'&'.join(query)}" if query else ""
        envelope = await self._request(
            "GET", f"/v1/projects/{project_id}/assets{suffix}", unwrap_data=False
        )
        raw_items = envelope.get("data")
        meta = envelope.get("meta")

        if not isinstance(raw_items, list) or not isinstance(meta, dict):
            raise TypeError("Unexpected response payload")

        next_page_cursor = meta.get("nextPageCursor")
        if next_page_cursor is not None and not isinstance(next_page_cursor, str):
            raise TypeError("Unexpected response payload")

        return AssetListResponse(items=raw_items, nextPageCursor=next_page_cursor)

    async def add_asset(self, project_id: str, asset_id: str) -> ProjectAssetBindingResponse:
        data = await self._request(
            "POST", f"/v1/projects/{project_id}/assets", json={"assetId": asset_id}
        )
        return ProjectAssetBindingResponse.model_validate(data)

    async def remove_asset(self, project_id: str, asset_id: str) -> ProjectAssetDeleteResponse:
        data = await self._request("DELETE", f"/v1/projects/{project_id}/assets/{asset_id}")
        return ProjectAssetDeleteResponse.model_validate(data)

    async def create_export(
        self,
        project_id: str,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> ExportCreateResponse:
        data = await self._request(
            "POST",
            f"/v1/projects/{project_id}/exports",
            json=payload,
            idempotency_key=idempotency_key,
        )
        return ExportCreateResponse.model_validate(data)
