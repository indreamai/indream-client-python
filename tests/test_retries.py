import httpx
import pytest

from indream import IndreamClient
from indream.errors import RateLimitError


def test_retries_for_429_then_success() -> None:
    state = {"count": 0}

    def handler(_: httpx.Request) -> httpx.Response:
        state["count"] += 1
        if state["count"] < 3:
            return httpx.Response(
                429,
                json={
                    "type": "RATE_LIMITED",
                    "title": "Too many requests",
                    "status": 429,
                    "detail": "retry later",
                    "errorCode": "OPEN_API_REQUEST_LIMIT_EXCEEDED",
                },
            )

        return httpx.Response(
            200,
            json={
                "data": {
                    "version": "2026-02-15",
                    "animations": [],
                    "captionAnimations": {
                        "in": [],
                        "out": [],
                        "loop": [],
                    },
                    "transitions": [],
                    "transitionPresets": [],
                    "effects": [],
                    "effectPresets": [],
                    "filters": [],
                    "filterPresets": [],
                    "shapes": [],
                    "backgroundPresets": {
                        "colors": [],
                        "gradients": [],
                        "images": [],
                        "blurLevels": [],
                    },
                },
                "meta": {},
            },
        )

    client = IndreamClient(
        api_key="sk_indream_test",
        transport=httpx.MockTransport(handler),
        max_retries=2,
    )

    result = client.editor.capabilities()
    assert result.version == "2026-02-15"
    assert state["count"] == 3


def test_retries_stop_after_max_retries_for_429() -> None:
    state = {"count": 0}

    def handler(_: httpx.Request) -> httpx.Response:
        state["count"] += 1
        return httpx.Response(
            429,
            json={
                "type": "RATE_LIMITED",
                "title": "Too many requests",
                "status": 429,
                "detail": "retry later",
                "errorCode": "OPEN_API_REQUEST_LIMIT_EXCEEDED",
            },
        )

    client = IndreamClient(
        api_key="sk_indream_test",
        transport=httpx.MockTransport(handler),
        max_retries=1,
    )

    with pytest.raises(RateLimitError):
        client.editor.capabilities()

    assert state["count"] == 2
