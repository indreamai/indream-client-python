import httpx

from indream import IndreamClient


def test_exports_list_returns_items_and_next_page_cursor() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get("pageSize") == "2"
        assert request.url.params.get("pageCursor") == "cursor-1"
        assert request.url.params.get("createdByApiKeyId") == "30edf957-a26b-4591-9df2-22976ea1416a"
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "taskId": "8c1d9ff0-4212-43f5-9258-6eb42a05b56e",
                        "createdByApiKeyId": "30edf957-a26b-4591-9df2-22976ea1416a",
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

    client = IndreamClient(api_key="sk_indream_test", transport=httpx.MockTransport(handler))
    result = client.exports.list(
        page_size=2,
        page_cursor="cursor-1",
        created_by_api_key_id="30edf957-a26b-4591-9df2-22976ea1416a",
    )

    assert result.next_page_cursor == "cursor-next"
    assert len(result.items) == 1
    assert result.items[0].task_id == "8c1d9ff0-4212-43f5-9258-6eb42a05b56e"
    assert result.items[0].created_by_api_key_id == "30edf957-a26b-4591-9df2-22976ea1416a"
    assert result.items[0].duration_seconds == 60
    assert result.items[0].billed_standard_seconds == 60
    assert result.items[0].charged_credits == "3"
