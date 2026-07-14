import httpx
import pytest
from ops_lab.polymarket import (
    OutboundRequestRejected,
    PolymarketReadClient,
    UpstreamClientError,
    UpstreamResponseInvalid,
)


def market_payload() -> list[dict[str, object]]:
    return [
        {
            "id": "public-market-1",
            "question": "Will the synthetic check pass?",
            "conditionId": "condition-1",
            "clobTokenIds": '["token-yes", "token-no"]',
            "active": True,
            "closed": False,
        }
    ]


def test_gamma_market_request_is_get_only_and_uses_five_second_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url == (
            "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=2"
        )
        assert request.extensions["timeout"] == {
            "connect": 5.0,
            "read": 5.0,
            "write": 5.0,
            "pool": 5.0,
        }
        return httpx.Response(200, json=market_payload())

    client = PolymarketReadClient(transport=httpx.MockTransport(handler))

    markets = client.list_markets(limit=2)

    assert markets[0].condition_id == "condition-1"
    assert markets[0].clob_token_ids == ["token-yes", "token-no"]


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("POST", "https://clob.polymarket.com/order"),
        ("DELETE", "https://clob.polymarket.com/order/123"),
        ("GET", "https://clob.polymarket.com.evil.example/book"),
        ("GET", "http://clob.polymarket.com/book"),
        ("GET", "https://example.com/markets"),
        ("GET", "https://clob.polymarket.com/data/orders"),
        ("GET", "https://gamma-api.polymarket.com/public-search"),
    ],
)
def test_mutating_methods_and_unapproved_hosts_are_rejected(method: str, url: str) -> None:
    client = PolymarketReadClient(
        transport=httpx.MockTransport(lambda request: pytest.fail(f"sent {request}"))
    )

    with pytest.raises(OutboundRequestRejected):
        client.request_json(method, url)


@pytest.mark.parametrize("first_failure", ["timeout", "server_error"])
def test_timeout_and_server_error_are_retried(first_failure: str) -> None:
    attempts = 0
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1 and first_failure == "timeout":
            raise httpx.ReadTimeout("upstream was slow", request=request)
        if attempts == 1:
            return httpx.Response(503, request=request)
        return httpx.Response(200, json=market_payload(), request=request)

    client = PolymarketReadClient(
        transport=httpx.MockTransport(handler),
        retries=2,
        sleep=sleeps.append,
    )

    markets = client.list_markets(limit=1)

    assert markets[0].id == "public-market-1"
    assert attempts == 2
    assert sleeps == [0.05]


def test_client_error_is_not_retried() -> None:
    attempts = 0
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(404, request=request)

    client = PolymarketReadClient(
        transport=httpx.MockTransport(handler),
        retries=2,
        sleep=sleeps.append,
    )

    with pytest.raises(UpstreamClientError, match="404"):
        client.list_markets(limit=1)

    assert attempts == 1
    assert sleeps == []


def test_clob_order_book_response_is_schema_validated() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://clob.polymarket.com/book?token_id=token-yes"
        return httpx.Response(
            200,
            json={
                "market": "condition-1",
                "asset_id": "token-yes",
                "timestamp": "1234567890",
                "hash": "snapshot-hash",
                "bids": [{"price": "0.45", "size": "100"}],
                "asks": [{"price": "0.46", "size": "150"}],
                "min_order_size": "1",
                "tick_size": "0.01",
                "neg_risk": False,
                "last_trade_price": "0.45",
            },
            request=request,
        )

    client = PolymarketReadClient(transport=httpx.MockTransport(handler))

    book = client.get_order_book("token-yes")

    assert str(book.bids[0].price) == "0.45"
    assert str(book.asks[0].size) == "150"
    assert book.neg_risk is False


def test_invalid_order_book_schema_is_reported_without_leaking_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "market": "condition-1",
                "asset_id": "token-yes",
                "timestamp": "1234567890",
                "hash": "snapshot-hash",
                "bids": [{"price": "1.50", "size": "100"}],
                "asks": [],
                "min_order_size": "1",
                "tick_size": "0.01",
                "neg_risk": False,
            },
            request=request,
        )

    client = PolymarketReadClient(transport=httpx.MockTransport(handler))

    with pytest.raises(UpstreamResponseInvalid) as caught:
        client.get_order_book("token-yes")

    assert "1.50" not in str(caught.value)
