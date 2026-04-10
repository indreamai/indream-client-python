import asyncio
import json
from pathlib import Path

import httpx
import pytest

from indream import AsyncIndreamClient, IndreamClient
from indream.errors import ValidationError
from tests.helpers import build_minimal_editor_state

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "openapi" / "examples"
STRICT_VALID_EXAMPLES = [
    "editor-state.valid.caption.json",
    "editor-state.valid.caption-offset.json",
    "editor-state.valid.chart.json",
    "editor-state.valid.runtime.json",
    "editor-state.valid.text-template.json",
]
STRICT_INVALID_EXAMPLES = [
    "editor-state.invalid.caption.json",
    "editor-state.invalid.caption-offset.json",
    "editor-state.invalid.chart.json",
    "editor-state.invalid.deleted-asset.json",
]


def read_editor_state_example(filename: str) -> dict[str, object]:
    return json.loads((EXAMPLES_DIR / filename).read_text(encoding="utf-8"))


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


@pytest.mark.parametrize("filename", STRICT_VALID_EXAMPLES)
def test_editor_validate_accepts_strict_valid_examples(filename: str) -> None:
    called = False

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(200, json={"data": {"valid": True, "errors": []}, "meta": {}})

    client = IndreamClient(api_key="sk_indream_test", transport=httpx.MockTransport(handler))
    result = client.editor.validate(read_editor_state_example(filename))

    assert result.valid is True
    assert called is True


@pytest.mark.parametrize("filename", STRICT_INVALID_EXAMPLES)
def test_editor_validate_rejects_strict_invalid_examples_before_request(filename: str) -> None:
    called = False

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(500, json={})

    client = IndreamClient(api_key="sk_indream_test", transport=httpx.MockTransport(handler))

    with pytest.raises(ValidationError):
        client.editor.validate(read_editor_state_example(filename))

    assert called is False


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
