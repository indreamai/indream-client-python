from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from indream.errors import Problem, ValidationError


@lru_cache(maxsize=1)
def _load_editor_state_validator() -> Draft202012Validator:
    schema_path = resources.files("indream.schemas").joinpath("editor-state.v1.schema.json")
    with schema_path.open("r", encoding="utf-8") as file:
        schema = json.load(file)
    return Draft202012Validator(schema)


def _to_json_path(error: JsonSchemaValidationError) -> str:
    path = "$"
    for part in error.absolute_path:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def _raise_editor_schema_error(*, path: str, message: str) -> None:
    raise ValidationError(
        Problem(
            type="EDITOR_SCHEMA_INVALID",
            title="Editor state schema validation failed",
            status=422,
            detail=f"{path}: {message}",
            error_code="EDITOR_SCHEMA_INVALID",
        )
    )


def validate_editor_state_or_raise(editor_state: Any) -> None:
    if not isinstance(editor_state, dict):
        _raise_editor_schema_error(path="$", message="editorState must be an object")

    validator = _load_editor_state_validator()
    errors = list(validator.iter_errors(editor_state))
    if not errors:
        return

    first_error = min(
        errors,
        key=lambda item: (len(item.absolute_path), list(item.absolute_path), item.message),
    )
    _raise_editor_schema_error(path=_to_json_path(first_error), message=first_error.message)
