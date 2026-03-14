import httpx
import pytest

from indream import IndreamClient
from indream.errors import AuthError, RateLimitError, ValidationError


@pytest.mark.parametrize(
    "status,error_cls",
    [
        (401, AuthError),
        (422, ValidationError),
        (429, RateLimitError),
    ],
)
def test_error_mapping(status: int, error_cls: type[Exception]) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status,
            json={
                "type": "ERROR",
                "title": "Request failed",
                "status": status,
                "detail": "failed",
                "errorCode": "TEST_ERROR",
            },
        )

    client = IndreamClient(
        api_key="sk_indream_test",
        transport=httpx.MockTransport(handler),
        max_retries=0,
    )

    with pytest.raises(error_cls):
        client.editor.validate({})
