import asyncio

import httpx
import pytest

from indream import AsyncIndreamClient
from indream.errors import APIError, ValidationError
from tests.helpers import build_minimal_editor_state


def test_async_exports_create_without_idempotency_header_by_default() -> None:
    captured_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update({key.lower(): value for key, value in request.headers.items()})
        return httpx.Response(
            201,
            json={
                "data": {
                    "taskId": "f73e3a79-21a3-406f-af67-ce3dd8c46139",
                    "createdAt": "2026-02-15T00:00:00.000Z",
                    "durationSeconds": 60,
                    "billedStandardSeconds": 60,
                    "chargedCredits": "3",
                },
                "meta": {},
            },
        )

    async def run() -> None:
        client = AsyncIndreamClient(
            api_key="sk_indream_test",
            transport=httpx.MockTransport(handler),
        )
        try:
            payload = {
                "editorState": build_minimal_editor_state(),
                "ratio": "16:9",
                "fps": 30,
                "scale": 1,
                "format": "mp4",
            }
            result = await client.exports.create(payload)
            assert result["taskId"] == "f73e3a79-21a3-406f-af67-ce3dd8c46139"
            assert result["durationSeconds"] == 60
            assert result["billedStandardSeconds"] == 60
        finally:
            await client.aclose()

    asyncio.run(run())

    assert "idempotency-key" not in captured_headers


def test_async_wait_terminal_failed_status_raises_api_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": {
                    "taskId": "ec17c4bc-3c4b-49c2-ab39-80dbdd49b156",
                    "clientTaskId": None,
                    "status": "FAILED",
                    "progress": 100,
                    "error": "render crashed",
                    "outputUrl": None,
                    "durationSeconds": 0,
                    "billedStandardSeconds": 0,
                    "chargedCredits": "0",
                    "callbackUrl": None,
                    "createdAt": "2026-02-15T00:00:00.000Z",
                    "completedAt": "2026-02-15T00:01:00.000Z",
                },
                "meta": {},
            },
        )

    async def run() -> None:
        client = AsyncIndreamClient(
            api_key="sk_indream_test",
            transport=httpx.MockTransport(handler),
            poll_interval=0.01,
        )
        try:
            with pytest.raises(APIError):
                await client.exports.wait(
                    "ec17c4bc-3c4b-49c2-ab39-80dbdd49b156", timeout=1, poll_interval=0.01
                )
        finally:
            await client.aclose()

    asyncio.run(run())


def test_async_exports_list_returns_items_and_next_page_cursor() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get("pageSize") == "1"
        assert request.url.params.get("pageCursor") == "cursor-1"
        assert request.url.params.get("createdByApiKeyId") == "69a962a0-96ad-40a3-a4bb-40f48fb09f59"
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "taskId": "4e34f885-7f35-4135-bd40-f3a920c6483a",
                        "createdByApiKeyId": "69a962a0-96ad-40a3-a4bb-40f48fb09f59",
                        "clientTaskId": None,
                        "status": "COMPLETED",
                        "progress": 100,
                        "error": None,
                        "outputUrl": "https://example.com/out.mp4",
                        "durationSeconds": 60,
                    "billedStandardSeconds": 60,
                        "chargedCredits": "3",
                        "callbackUrl": None,
                        "createdAt": "2026-02-15T00:00:00.000Z",
                        "completedAt": "2026-02-15T00:01:00.000Z",
                    }
                ],
                "meta": {"nextPageCursor": "cursor-next"},
            },
        )

    async def run() -> None:
        client = AsyncIndreamClient(
            api_key="sk_indream_test",
            transport=httpx.MockTransport(handler),
        )
        try:
            result = await client.exports.list(
                page_size=1,
                page_cursor="cursor-1",
                created_by_api_key_id="69a962a0-96ad-40a3-a4bb-40f48fb09f59",
            )
            assert result["nextPageCursor"] == "cursor-next"
            assert len(result["items"]) == 1
            assert result["items"][0]["taskId"] == "4e34f885-7f35-4135-bd40-f3a920c6483a"
            assert result["items"][0]["durationSeconds"] == 60
            assert result["items"][0]["billedStandardSeconds"] == 60
        finally:
            await client.aclose()

    asyncio.run(run())


def test_async_exports_create_rejects_invalid_editor_state_before_request() -> None:
    called = False

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(500, json={})

    async def run() -> None:
        client = AsyncIndreamClient(
            api_key="sk_indream_test",
            transport=httpx.MockTransport(handler),
        )
        try:
            payload = {
                "editorState": {},
                "ratio": "16:9",
                "fps": 30,
                "scale": 1,
                "format": "mp4",
            }
            with pytest.raises(ValidationError) as error:
                await client.exports.create(payload)
            assert error.value.error_code == "EDITOR_SCHEMA_INVALID"
        finally:
            await client.aclose()

    asyncio.run(run())
    assert called is False
