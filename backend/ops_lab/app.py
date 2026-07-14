from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from ops_lab.operations import MarketNotFound, OpsLabService, SyntheticDataUnavailable


class PaperRunRequest(BaseModel):
    market_id: str = Field(min_length=1)


class WalletProofRequest(BaseModel):
    challenge: str = Field(min_length=1, max_length=200)


def create_app(
    database: str | Path = "paper.db",
    *,
    synthetic_available: bool = True,
) -> FastAPI:
    app = FastAPI(
        title="Prediction Market Ops Lab",
        version="0.1.0",
        description="Paper-only operations API with synthetic data and public read adapters.",
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

    @app.get("/metrics", response_class=PlainTextResponse)
    def metrics() -> str:
        return service.metrics()

    return app
