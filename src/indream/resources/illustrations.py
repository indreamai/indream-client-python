from __future__ import annotations

from collections.abc import Callable
from typing import Any


class IllustrationsResource:
    def __init__(self, request: Callable[..., Any]) -> None:
        self._request = request

    def search(self, q: str | None = None) -> list[str]:
        suffix = f'?q={q}' if q and q.strip() else ''
        data = self._request('GET', f'/v1/illustrations{suffix}')
        if not isinstance(data, list):
            raise TypeError('Unexpected response payload')
        return [item for item in data if isinstance(item, str)]


class AsyncIllustrationsResource:
    def __init__(self, request: Callable[..., Any]) -> None:
        self._request = request

    async def search(self, q: str | None = None) -> list[str]:
        suffix = f'?q={q}' if q and q.strip() else ''
        data = await self._request('GET', f'/v1/illustrations{suffix}')
        if not isinstance(data, list):
            raise TypeError('Unexpected response payload')
        return [item for item in data if isinstance(item, str)]
