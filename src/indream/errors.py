from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Problem:
    type: str
    title: str
    status: int
    detail: str
    error_code: str | None = None


class APIError(Exception):
    def __init__(self, problem: Problem):
        super().__init__(problem.detail)
        self.problem = problem
        self.status = problem.status
        self.type = problem.type
        self.error_code = problem.error_code


class AuthError(APIError):
    pass


class ValidationError(APIError):
    pass


class RateLimitError(APIError):
    pass


def parse_problem(status: int, payload: Any) -> Problem:
    if isinstance(payload, dict):
        maybe_type = payload.get("type")
        maybe_title = payload.get("title")
        if isinstance(maybe_type, str) and isinstance(maybe_title, str):
            return Problem(
                type=maybe_type,
                title=maybe_title,
                status=int(payload.get("status") or status),
                detail=str(payload.get("detail") or maybe_title),
                error_code=payload.get("errorCode"),
            )

    return Problem(
        type="INTERNAL_ERROR",
        title="Internal server error",
        status=status,
        detail="Unexpected API response",
        error_code="SDK_UNEXPECTED_RESPONSE",
    )


def create_api_error(status: int, payload: Any) -> APIError:
    problem = parse_problem(status, payload)

    if status in (401, 403):
        return AuthError(problem)
    if status in (400, 422):
        return ValidationError(problem)
    if status == 429:
        return RateLimitError(problem)

    return APIError(problem)
