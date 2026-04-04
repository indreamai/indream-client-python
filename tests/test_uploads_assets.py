import asyncio

import httpx

from indream import AsyncIndreamClient, IndreamClient


def test_uploads_uploads_raw_body_once() -> None:
    calls: list[tuple[str, str, bytes, dict[str, str]]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, str(request.url), request.content, dict(request.headers)))

        return httpx.Response(
            201,
            json={
                "data": {
                    "assetId": "0dff5af3-1477-4cda-8406-df04285e060e",
                    "type": "IMAGE",
                    "source": "UPLOAD",
                    "filename": "demo.png",
                    "mimetype": "image/png",
                    "size": 1024,
                    "fileUrl": "https://cdn.example.com/uploads/demo.png",
                    "fileKey": "uploads/demo.png",
                    "width": 1920,
                    "height": 1080,
                    "duration": None,
                },
                "meta": {},
            },
        )

    client = IndreamClient(api_key="sk_indream_test", transport=httpx.MockTransport(handler))
    asset = client.uploads.upload(
        b"demo",
        filename="demo.png",
        content_type="image/png",
        project_id="ea517bbd-d6ad-4db8-aa71-8228f39d1820",
    )

    assert asset.file_key == "uploads/demo.png"
    assert calls[0][0] == "POST"
    assert calls[0][1].endswith("/v1/uploads")
    assert calls[0][2] == b"demo"
    assert calls[0][3]["x-file-name"] == "demo.png"
    assert calls[0][3]["content-type"] == "image/png"
    assert calls[0][3]["x-project-id"] == "ea517bbd-d6ad-4db8-aa71-8228f39d1820"


def test_async_assets_get_and_delete() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "data": {
                        "assetId": "0dff5af3-1477-4cda-8406-df04285e060e",
                        "type": "IMAGE",
                        "source": "UPLOAD",
                        "filename": "demo.png",
                        "mimetype": "image/png",
                        "size": 1024,
                        "fileUrl": "https://cdn.example.com/uploads/demo.png",
                        "fileKey": "uploads/demo.png",
                        "width": 1920,
                        "height": 1080,
                        "duration": None,
                    },
                    "meta": {},
                },
            )

        return httpx.Response(
            200,
            json={
                "data": {
                    "assetId": "0dff5af3-1477-4cda-8406-df04285e060e",
                    "deleted": True,
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
            asset = await client.assets.get("0dff5af3-1477-4cda-8406-df04285e060e")
            deleted = await client.assets.delete("0dff5af3-1477-4cda-8406-df04285e060e")
            assert asset.asset_id == "0dff5af3-1477-4cda-8406-df04285e060e"
            assert deleted.deleted is True
        finally:
            await client.aclose()

    asyncio.run(run())
