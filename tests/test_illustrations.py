import asyncio

import httpx

from indream import AsyncIndreamClient, IndreamClient


def test_search_illustrations_sync_supports_array_data() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == '/v1/illustrations'
        assert request.url.params['q'] == 'creative'
        return httpx.Response(
            200,
            json={
                'data': ['ICreativeThinking', 'IMegaphone'],
                'meta': {},
            },
        )

    client = IndreamClient(
        api_key='sk_indream_test',
        transport=httpx.MockTransport(handler),
    )

    items = client.illustrations.search('creative')
    assert items == ['ICreativeThinking', 'IMegaphone']


def test_search_illustrations_async_supports_array_data() -> None:
    async def run() -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == '/v1/illustrations'
            assert request.url.params['q'] == 'creative'
            return httpx.Response(
                200,
                json={
                    'data': ['ICreativeThinking'],
                    'meta': {},
                },
            )

        client = AsyncIndreamClient(
            api_key='sk_indream_test',
            transport=httpx.MockTransport(handler),
        )

        items = await client.illustrations.search('creative')
        assert items == ['ICreativeThinking']
        await client.aclose()

    asyncio.run(run())
