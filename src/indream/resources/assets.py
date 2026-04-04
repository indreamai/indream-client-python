from __future__ import annotations

from collections.abc import Callable
from typing import Any

from indream.types import Asset, AssetDeleteResponse


class AssetsResource:
    def __init__(self, request: Callable[..., Any]) -> None:
        self._request = request

    def get(self, asset_id: str) -> Asset:
        data = self._request("GET", f"/v1/assets/{asset_id}")
        return Asset.model_validate(data)

    def delete(self, asset_id: str) -> AssetDeleteResponse:
        data = self._request("DELETE", f"/v1/assets/{asset_id}")
        return AssetDeleteResponse.model_validate(data)


class AsyncAssetsResource:
    def __init__(self, request: Callable[..., Any]) -> None:
        self._request = request

    async def get(self, asset_id: str) -> Asset:
        data = await self._request("GET", f"/v1/assets/{asset_id}")
        return Asset.model_validate(data)

    async def delete(self, asset_id: str) -> AssetDeleteResponse:
        data = await self._request("DELETE", f"/v1/assets/{asset_id}")
        return AssetDeleteResponse.model_validate(data)
