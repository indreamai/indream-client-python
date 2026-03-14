import httpx

from indream import IndreamClient


def _create_payload() -> dict[str, object]:
    return {
        "editorState": {},
        "ratio": "16:9",
        "fps": 30,
        "scale": 1,
        "format": "mp4",
    }


def test_exports_create_without_idempotency_header_by_default() -> None:
    captured_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update({key.lower(): value for key, value in request.headers.items()})
        return httpx.Response(
            201,
            json={
                "data": {
                    "taskId": "2d531e48-d424-4acc-a3f7-88b0a4f9f73c",
                    "createdAt": "2026-02-15T00:00:00.000Z",
                    "durationSeconds": 120,
                    "billedStandardSeconds": 120,
                    "chargedCredits": "10",
                },
                "meta": {},
            },
        )

    client = IndreamClient(api_key="sk_indream_test", transport=httpx.MockTransport(handler))

    result = client.exports.create(_create_payload())

    assert "idempotency-key" not in captured_headers
    assert captured_headers.get("x-api-key") == "sk_indream_test"
    assert "authorization" not in captured_headers
    assert result.task_id == "2d531e48-d424-4acc-a3f7-88b0a4f9f73c"
    assert result.duration_seconds == 120
    assert result.billed_standard_seconds == 120
    assert result.charged_credits == "10"


def test_exports_create_forwards_idempotency_key_when_provided() -> None:
    captured_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update({key.lower(): value for key, value in request.headers.items()})
        return httpx.Response(
            201,
            json={
                "data": {
                    "taskId": "aa2dd4c4-c484-45e3-99e2-e84f7e474cc5",
                    "createdAt": "2026-02-15T00:00:00.000Z",
                    "durationSeconds": 120,
                    "billedStandardSeconds": 120,
                    "chargedCredits": "10",
                },
                "meta": {},
            },
        )

    client = IndreamClient(api_key="sk_indream_test", transport=httpx.MockTransport(handler))
    client.exports.create(_create_payload(), idempotency_key="idem_1")

    assert captured_headers.get("idempotency-key") == "idem_1"
