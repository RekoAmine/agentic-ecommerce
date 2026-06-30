import json
from collections.abc import Mapping

import pytest

from fba_advisor.connectors.amazon.client import AmazonClient
from fba_advisor.connectors.amazon.exceptions import AmazonAPIError
from fba_advisor.connectors.amazon.models import AmazonCredentials
from fba_advisor.connectors.brightdata.client import BrightDataClient
from fba_advisor.connectors.brightdata.models import BrightDataCredentials, BrightDataTarget
from fba_advisor.connectors.keepa.client import KeepaClient
from fba_advisor.connectors.keepa.models import KeepaCredentials
from fba_advisor.connectors.openai.client import OpenAIClient
from fba_advisor.connectors.openai.models import OpenAICredentials


class _FakeGetTransport:
    def __init__(self, status: int, payload: dict[str, object]) -> None:
        self.status = status
        self.payload = payload
        self.url = ""
        self.headers: Mapping[str, str] = {}

    def get(self, url: str, headers: Mapping[str, str]) -> tuple[int, bytes]:
        self.url = url
        self.headers = headers
        return self.status, json.dumps(self.payload).encode("utf-8")


class _FakePostTransport:
    def __init__(self, status: int, payload: dict[str, object]) -> None:
        self.status = status
        self.payload = payload
        self.url = ""
        self.headers: Mapping[str, str] = {}
        self.body = b""

    def post(self, url: str, headers: Mapping[str, str], body: bytes) -> tuple[int, bytes]:
        self.url = url
        self.headers = headers
        self.body = body
        return self.status, json.dumps(self.payload).encode("utf-8")


def test_amazon_client_authenticates_calls_api_and_maps_products() -> None:
    transport = _FakeGetTransport(
        200,
        {"items": [{"asin": "B001", "title": "Test product", "price": 12.5, "currency": "USD"}]},
    )
    client = AmazonClient(
        AmazonCredentials(
            access_key="access",
            secret_key="secret",
            region="us-east-1",
            marketplace_id="ATVPDKIKX0DER",
        ),
        "https://amazon.example",
        transport,
    )

    response = client.search_products("coffee press")

    assert client.provider_name == "amazon"
    assert "q=coffee+press" in transport.url
    assert transport.headers["Authorization"] == "Amazon access:secret"
    assert response.products[0].asin == "B001"
    assert response.products[0].price == 12.5


def test_amazon_client_raises_api_error_on_unsuccessful_response() -> None:
    client = AmazonClient(
        AmazonCredentials(
            access_key="access",
            secret_key="secret",
            region="us-east-1",
            marketplace_id="ATVPDKIKX0DER",
        ),
        "https://amazon.example",
        _FakeGetTransport(500, {"items": []}),
    )

    with pytest.raises(AmazonAPIError):
        client.search_products("coffee")


def test_keepa_client_maps_products() -> None:
    transport = _FakeGetTransport(
        200,
        {"products": [{"asin": "B002", "title": "Keepa product", "salesRank": 1234}]},
    )
    client = KeepaClient(KeepaCredentials(api_key="token"), "https://keepa.example", transport)

    response = client.fetch("B002")

    assert "key=token" in transport.url
    assert response.items[0].sales_rank == 1234


def test_brightdata_client_supports_multiple_targets() -> None:
    transport = _FakeGetTransport(
        200,
        {"records": [{"id": "A1", "title": "Alibaba result", "url": "https://example.test/a1"}]},
    )
    client = BrightDataClient(
        BrightDataCredentials(api_token="token", zone="zone-a"),
        "https://brightdata.example",
        transport,
    )

    response = client.collect(BrightDataTarget.ALIBABA, "wireless charger")

    assert "target=alibaba" in transport.url
    assert "zone=zone-a" in transport.url
    assert transport.headers["Authorization"] == "Bearer token"
    assert response.records[0].target is BrightDataTarget.ALIBABA
    assert response.records[0].identifier == "A1"


def test_openai_client_posts_embedding_request_and_maps_vector() -> None:
    transport = _FakePostTransport(200, {"data": [{"embedding": [0.1, 2, -0.3]}]})
    client = OpenAIClient(
        OpenAICredentials(api_key="token", organization="org_123"),
        "https://api.openai.example/v1",
        "text-embedding-test",
        transport,
    )

    response = client.fetch("product title")

    assert transport.url.endswith("/embeddings")
    assert transport.headers["Authorization"] == "Bearer token"
    assert transport.headers["OpenAI-Organization"] == "org_123"
    assert json.loads(transport.body.decode("utf-8"))["input"] == "product title"
    assert response.items[0].vector == [0.1, 2.0, -0.3]
