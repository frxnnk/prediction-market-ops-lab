import json
import time
from collections.abc import Callable, Mapping
from decimal import Decimal
from typing import Any
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

GAMMA_BASE_URL = "https://gamma-api.polymarket.com"
CLOB_BASE_URL = "https://clob.polymarket.com"
_ALLOWED_ENDPOINTS = {
    "gamma-api.polymarket.com": frozenset({"/markets"}),
    "clob.polymarket.com": frozenset({"/book"}),
}


class OutboundRequestRejected(ValueError):
    """Raised before I/O when a request is not an allowlisted public GET."""


class UpstreamClientError(RuntimeError):
    """A non-retryable upstream response caused by the request."""


class UpstreamUnavailable(RuntimeError):
    """A retryable upstream failure exhausted the bounded attempt budget."""


class UpstreamResponseInvalid(RuntimeError):
    """An upstream response did not match the documented public schema."""


class MarketSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    question: str
    condition_id: str = Field(alias="conditionId")
    clob_token_ids: list[str] = Field(alias="clobTokenIds")
    active: bool
    closed: bool

    @field_validator("clob_token_ids", mode="before")
    @classmethod
    def parse_token_ids(cls, value: object) -> object:
        if isinstance(value, str):
            return json.loads(value)
        return value


class OrderBookLevel(BaseModel):
    price: Decimal = Field(gt=0, lt=1)
    size: Decimal = Field(gt=0)


class OrderBookSnapshot(BaseModel):
    market: str
    asset_id: str
    timestamp: str
    hash: str
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    min_order_size: Decimal = Field(gt=0)
    tick_size: Decimal = Field(gt=0, le=1)
    neg_risk: bool
    last_trade_price: Decimal | None = Field(default=None, gt=0, lt=1)


class PolymarketReadClient:
    def __init__(
        self,
        *,
        transport: httpx.BaseTransport | None = None,
        retries: int = 2,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if retries < 0:
            raise ValueError("retries cannot be negative")
        self._client = httpx.Client(timeout=5.0, transport=transport)
        self._retries = retries
        self._sleep = sleep

    def close(self) -> None:
        self._client.close()

    def request_json(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, object] | None = None,
    ) -> Any:
        parsed = urlsplit(url)
        allowed_paths = _ALLOWED_ENDPOINTS.get(parsed.hostname or "", frozenset())
        if method != "GET" or parsed.scheme != "https" or parsed.path not in allowed_paths:
            raise OutboundRequestRejected("Only exact public HTTPS GET endpoints are allowed")

        for attempt in range(self._retries + 1):
            try:
                response = self._client.request(method, url, params=params)
            except httpx.RequestError as exc:
                if attempt == self._retries:
                    raise UpstreamUnavailable("Public upstream request failed") from exc
                self._sleep(0.05 * (2**attempt))
                continue

            if response.status_code >= 500:
                if attempt == self._retries:
                    raise UpstreamUnavailable(
                        f"Public upstream returned {response.status_code}"
                    )
                self._sleep(0.05 * (2**attempt))
                continue
            if response.status_code >= 400:
                raise UpstreamClientError(f"Public upstream returned {response.status_code}")
            try:
                return response.json()
            except ValueError as exc:
                raise UpstreamResponseInvalid("Public upstream returned invalid JSON") from exc

        raise AssertionError("retry loop must return or raise")

    def list_markets(self, *, limit: int = 10) -> list[MarketSummary]:
        payload = self.request_json(
            "GET",
            f"{GAMMA_BASE_URL}/markets",
            params={"active": "true", "closed": "false", "limit": limit},
        )
        if not isinstance(payload, list):
            raise UpstreamResponseInvalid("Gamma response did not contain a market list")
        try:
            return [MarketSummary.model_validate(market) for market in payload]
        except ValidationError as exc:
            raise UpstreamResponseInvalid("Gamma market response failed schema validation") from exc

    def get_order_book(self, token_id: str) -> OrderBookSnapshot:
        payload = self.request_json(
            "GET",
            f"{CLOB_BASE_URL}/book",
            params={"token_id": token_id},
        )
        try:
            return OrderBookSnapshot.model_validate(payload)
        except ValidationError as exc:
            raise UpstreamResponseInvalid("CLOB book response failed schema validation") from exc
