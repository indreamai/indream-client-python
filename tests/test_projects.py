import asyncio

import httpx

from indream import AsyncIndreamClient, IndreamClient
from tests.helpers import build_minimal_editor_state


def test_projects_create_validates_editor_state_and_forwards_idempotency_key() -> None:
    captured_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update({key.lower(): value for key, value in request.headers.items()})
        return httpx.Response(
            201,
            json={
                "data": {
                    "projectId": "93fb8aa8-c301-441d-bb8d-ea733cd72a7e",
                    "title": "Launch draft",
                    "description": None,
                    "createdAt": "2026-04-04T00:00:00.000Z",
                    "updatedAt": "2026-04-04T00:00:00.000Z",
                },
                "meta": {},
            },
        )

    client = IndreamClient(api_key="sk_indream_test", transport=httpx.MockTransport(handler))
    project = client.projects.create(
        {
            "title": "Launch draft",
            "editorState": build_minimal_editor_state(),
        },
        idempotency_key="project-create-1",
    )

    assert project.project_id == "93fb8aa8-c301-441d-bb8d-ea733cd72a7e"
    assert captured_headers.get("idempotency-key") == "project-create-1"


def test_projects_sync_uses_dedicated_endpoint() -> None:
    captured_url = ""

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_url
        captured_url = str(request.url)
        return httpx.Response(
            200,
            json={
                "data": {
                    "projectId": "93fb8aa8-c301-441d-bb8d-ea733cd72a7e",
                    "stateVersion": "v1",
                    "updatedAt": "2026-04-04T00:01:00.000Z",
                },
                "meta": {},
            },
        )

    client = IndreamClient(api_key="sk_indream_test", transport=httpx.MockTransport(handler))
    result = client.projects.sync(
        "93fb8aa8-c301-441d-bb8d-ea733cd72a7e",
        {"editorState": build_minimal_editor_state()},
    )

    assert captured_url.endswith("/v1/projects/93fb8aa8-c301-441d-bb8d-ea733cd72a7e/sync")
    assert result.state_version == "v1"


def test_async_projects_create_export_keeps_project_id() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            201,
            json={
                "data": {
                    "taskId": "07f64f26-3d43-4d2e-9954-1ea9482bcc79",
                    "projectId": "93fb8aa8-c301-441d-bb8d-ea733cd72a7e",
                    "createdAt": "2026-04-04T00:00:00.000Z",
                    "durationSeconds": 6,
                    "billedStandardSeconds": 6,
                    "chargedCredits": "1.000000000000",
                    "chargedCreditPool": "OPEN_API",
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
            created = await client.projects.create_export(
                "93fb8aa8-c301-441d-bb8d-ea733cd72a7e",
                {
                    "ratio": "16:9",
                    "scale": 1,
                    "fps": 30,
                    "format": "mp4",
                },
            )
            assert created.project_id == "93fb8aa8-c301-441d-bb8d-ea733cd72a7e"
        finally:
            await client.aclose()

    asyncio.run(run())
