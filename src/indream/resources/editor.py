from __future__ import annotations

from collections.abc import Callable
from typing import Any

from indream.editor_state_validator import validate_editor_state_or_raise
from indream.types import EditorCapabilities, EditorValidationResult


class EditorResource:
    def __init__(self, request: Callable[..., dict[str, Any]]) -> None:
        self._request = request

    def capabilities(self) -> EditorCapabilities:
        data = self._request("GET", "/v1/editor/capabilities")
        return EditorCapabilities.model_validate(data)

    def validate(self, editor_state: dict[str, Any]) -> EditorValidationResult:
        validate_editor_state_or_raise(editor_state)
        data = self._request(
            "POST",
            "/v1/editor/validate",
            json={"editorState": editor_state},
            skip_retry=True,
        )
        return EditorValidationResult.model_validate(data)


class AsyncEditorResource:
    def __init__(self, request: Callable[..., Any]) -> None:
        self._request = request

    async def capabilities(self) -> EditorCapabilities:
        data = await self._request("GET", "/v1/editor/capabilities")
        return EditorCapabilities.model_validate(data)

    async def validate(self, editor_state: dict[str, Any]) -> EditorValidationResult:
        validate_editor_state_or_raise(editor_state)
        data = await self._request(
            "POST",
            "/v1/editor/validate",
            json={"editorState": editor_state},
            skip_retry=True,
        )
        return EditorValidationResult.model_validate(data)
