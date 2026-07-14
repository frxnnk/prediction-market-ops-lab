import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Protocol

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from ops_lab.operations import MarketNotFound, OpsLabService, SyntheticDataUnavailable
from ops_lab.polymarket import (
    MarketSummary,
    OrderBookSnapshot,
    PolymarketReadClient,
    UpstreamClientError,
    UpstreamResponseInvalid,
    UpstreamUnavailable,
)


class PaperRunRequest(BaseModel):
    market_id: str = Field(min_length=1)


class WalletProofRequest(BaseModel):
    challenge: str = Field(min_length=1, max_length=200)


class PublicReadAdapter(Protocol):
    def list_markets(self, *, limit: int) -> list[MarketSummary]: ...

    def get_order_book(self, token_id: str) -> OrderBookSnapshot: ...


def create_app(
    database: str | Path | None = None,
    *,
    synthetic_available: bool | None = None,
    public_reads_enabled: bool | None = None,
    public_read_client: PublicReadAdapter | None = None,
) -> FastAPI:
    database = database or os.getenv("OPS_LAB_DATABASE", "paper.db")
    if synthetic_available is None:
        synthetic_available = os.getenv("OPS_LAB_SYNTHETIC_AVAILABLE", "1") == "1"
    if public_reads_enabled is None:
        public_reads_enabled = os.getenv("OPS_LAB_PUBLIC_READS", "0") == "1"
    owns_public_client = public_reads_enabled and public_read_client is None
    if owns_public_client:
        public_read_client = PolymarketReadClient()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        if owns_public_client and isinstance(public_read_client, PolymarketReadClient):
            public_read_client.close()

    app = FastAPI(
        title="Prediction Market Ops Lab",
        version="0.1.0",
        description="Paper-only operations API with synthetic data and public read adapters.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    service = OpsLabService(database, synthetic_available=synthetic_available)

    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", response_model=None)
    def readiness() -> dict[str, str] | JSONResponse:
        if not service.is_ready():
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "dependency": "synthetic_data"},
            )
        return {"status": "ready"}

    @app.get("/api/overview")
    def overview() -> dict[str, object]:
        try:
            return service.overview()
        except SyntheticDataUnavailable as exc:
            raise HTTPException(status_code=503, detail="Synthetic data unavailable") from exc

    @app.get("/api/markets")
    def markets() -> list[dict[str, object]]:
        try:
            return [market.model_dump(mode="json") for market in service.markets()]
        except SyntheticDataUnavailable as exc:
            raise HTTPException(status_code=503, detail="Synthetic data unavailable") from exc

    @app.post("/api/paper/run")
    def run_paper(request: PaperRunRequest) -> dict[str, str]:
        try:
            return service.run_paper(request.market_id).model_dump()
        except MarketNotFound as exc:
            raise HTTPException(status_code=404, detail="Synthetic market not found") from exc
        except SyntheticDataUnavailable as exc:
            raise HTTPException(status_code=503, detail="Synthetic data unavailable") from exc

    @app.post("/api/wallet/verify")
    def verify_wallet(request: WalletProofRequest) -> dict[str, object]:
        return service.verify_wallet(request.challenge).model_dump()

    @app.get("/api/diagnostics")
    def diagnostics() -> dict[str, str]:
        return service.diagnostics()

    def require_public_client() -> PublicReadAdapter:
        if not public_reads_enabled or public_read_client is None:
            raise HTTPException(status_code=403, detail="Optional public reads are disabled")
        return public_read_client

    @app.get("/api/public/markets")
    def public_markets(limit: int = Query(default=5, ge=1, le=20)) -> list[dict[str, object]]:
        try:
            return [
                market.model_dump(mode="json")
                for market in require_public_client().list_markets(limit=limit)
            ]
        except (UpstreamClientError, UpstreamResponseInvalid, UpstreamUnavailable) as exc:
            raise HTTPException(status_code=502, detail="Public market read failed") from exc

    @app.get("/api/public/order-book/{token_id}")
    def public_order_book(token_id: str) -> dict[str, object]:
        try:
            return require_public_client().get_order_book(token_id).model_dump(mode="json")
        except (UpstreamClientError, UpstreamResponseInvalid, UpstreamUnavailable) as exc:
            raise HTTPException(status_code=502, detail="Public order-book read failed") from exc

    @app.get("/metrics", response_class=PlainTextResponse)
    def metrics() -> str:
        return service.metrics()

    return app
