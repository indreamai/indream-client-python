import httpx
import pytest

from indream import IndreamClient
from indream.errors import APIError


def test_wait_until_completed() -> None:
    state = {"count": 0}

    def handler(_: httpx.Request) -> httpx.Response:
        state["count"] += 1
        status = "PROCESSING" if state["count"] < 3 else "COMPLETED"
        return httpx.Response(
            200,
            json={
                "data": {
                    "taskId": "4aa67b9c-acd0-446c-9c8e-4ea5d2ed584d",
                    "createdByApiKeyId": None,
                    "clientTaskId": None,
                    "status": status,
                    "progress": 50,
                    "error": None,
                    "outputUrl": "https://example.com/out.mp4" if status == "COMPLETED" else None,
                    "durationSeconds": 60,
                    "billedStandardSeconds": 60,
                    "chargedCredits": "5",
                    "callbackUrl": None,
                    "createdAt": "2026-02-15T00:00:00.000Z",
                    "completedAt": "2026-02-15T00:01:00.000Z" if status == "COMPLETED" else None,
                },
                "meta": {},
            },
        )

    client = IndreamClient(
        api_key="sk_indream_test",
        transport=httpx.MockTransport(handler),
        poll_interval=0.01,
    )

    task = client.exports.wait(
        "4aa67b9c-acd0-446c-9c8e-4ea5d2ed584d",
        timeout=1,
        poll_interval=0.01,
    )
    assert task.status == "COMPLETED"
    assert task.duration_seconds == 60
    assert task.billed_standard_seconds == 60
    assert state["count"] >= 3


def test_wait_timeout() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": {
                    "taskId": "3ee6546b-028a-4ccb-a3bd-b2d9f1ab4b95",
                    "createdByApiKeyId": None,
                    "clientTaskId": None,
                    "status": "PROCESSING",
                    "progress": 10,
                    "error": None,
                    "outputUrl": None,
                    "durationSeconds": 0,
                    "billedStandardSeconds": 0,
                    "chargedCredits": "0",
                    "callbackUrl": None,
                    "createdAt": "2026-02-15T00:00:00.000Z",
                    "completedAt": None,
                },
                "meta": {},
            },
        )

    client = IndreamClient(
        api_key="sk_indream_test",
        transport=httpx.MockTransport(handler),
        poll_interval=0.01,
    )

    with pytest.raises(TimeoutError):
        client.exports.wait(
            "3ee6546b-028a-4ccb-a3bd-b2d9f1ab4b95",
            timeout=0.02,
            poll_interval=0.01,
        )


def test_wait_terminal_failed_status_raises_api_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": {
                    "taskId": "4e01bff5-0a5f-4326-b6ce-4c811f0b6f6f",
                    "createdByApiKeyId": None,
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

    client = IndreamClient(api_key="sk_indream_test", transport=httpx.MockTransport(handler))

    with pytest.raises(APIError):
        client.exports.wait("4e01bff5-0a5f-4326-b6ce-4c811f0b6f6f", timeout=1, poll_interval=0.01)
