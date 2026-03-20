import asyncio

import httpx
import pytest

from indream import AsyncIndreamClient, IndreamClient
from indream.errors import ValidationError
from tests.helpers import build_minimal_editor_state


def test_editor_validate_rejects_invalid_editor_state_before_request() -> None:
    called = False

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(500, json={})

    client = IndreamClient(api_key="sk_indream_test", transport=httpx.MockTransport(handler))

    with pytest.raises(ValidationError) as error:
        client.editor.validate({})

    assert error.value.error_code == "EDITOR_SCHEMA_INVALID"
    assert called is False


def test_editor_validate_accepts_valid_editor_state() -> None:
    called = False

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(200, json={"data": {"valid": True, "errors": []}, "meta": {}})

    client = IndreamClient(api_key="sk_indream_test", transport=httpx.MockTransport(handler))
    result = client.editor.validate(build_minimal_editor_state())
    assert result.valid is True
    assert called is True


def test_async_editor_validate_rejects_invalid_editor_state_before_request() -> None:
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
            with pytest.raises(ValidationError) as error:
                await client.editor.validate({})
            assert error.value.error_code == "EDITOR_SCHEMA_INVALID"
        finally:
            await client.aclose()

    asyncio.run(run())
    assert called is False
