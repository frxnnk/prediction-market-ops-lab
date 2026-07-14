from fastapi.testclient import TestClient
from ops_lab.app import create_app
from ops_lab.polymarket import MarketSummary, OrderBookSnapshot


def make_client(tmp_path, *, synthetic_available: bool = True) -> TestClient:
    app = create_app(
        database=tmp_path / "paper.db",
        synthetic_available=synthetic_available,
    )
    return TestClient(app)


def test_overview_and_markets_are_explicitly_synthetic_and_paper_only(tmp_path) -> None:
    with make_client(tmp_path) as client:
        overview = client.get("/api/overview")
        markets = client.get("/api/markets")

    assert overview.status_code == 200
    assert overview.json() == {
        "mode": "paper",
        "live_execution_enabled": False,
        "data_source": "synthetic",
        "market_count": 3,
        "paper_fill_count": 0,
    }
    assert markets.status_code == 200
    assert len(markets.json()) == 3
    assert all(market["market_id"].startswith("synthetic-") for market in markets.json())


def test_paper_run_is_deterministic_and_recorded_once(tmp_path) -> None:
    with make_client(tmp_path) as client:
        first = client.post(
            "/api/paper/run",
            json={"market_id": "synthetic-weather-001"},
        )
        second = client.post(
            "/api/paper/run",
            json={"market_id": "synthetic-weather-001"},
        )
        overview = client.get("/api/overview")

    assert first.status_code == 200
    assert first.json() == {
        "request_id": "dummy-synthetic-weather-001-8",
        "status": "simulated",
    }
    assert second.status_code == 200
    assert overview.json()["paper_fill_count"] == 1


def test_wallet_proof_response_contains_only_public_result(tmp_path) -> None:
    with make_client(tmp_path) as client:
        response = client.post(
            "/api/wallet/verify",
            json={"challenge": "local-test-proof"},
        )

    assert response.status_code == 200
    assert set(response.json()) == {"address", "verified"}
    assert response.json()["verified"] is True


def test_health_readiness_diagnostics_and_metrics(tmp_path) -> None:
    with make_client(tmp_path) as client:
        client.post("/api/paper/run", json={"market_id": "synthetic-weather-001"})
        health = client.get("/healthz")
        readiness = client.get("/readyz")
        diagnostics = client.get("/api/diagnostics")
        metrics = client.get("/metrics")

    assert health.json() == {"status": "ok"}
    assert readiness.json() == {"status": "ready"}
    assert diagnostics.json()["execution_boundary"] == "paper-only"
    assert diagnostics.json()["synthetic_data"] == "ok"
    assert "paper_runs_total 1" in metrics.text
    assert "live_execution_enabled 0" in metrics.text


def test_synthetic_failure_injection_affects_readiness_not_liveness(tmp_path) -> None:
    with make_client(tmp_path, synthetic_available=False) as client:
        health = client.get("/healthz")
        readiness = client.get("/readyz")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert readiness.status_code == 503
    assert readiness.json() == {"status": "not_ready", "dependency": "synthetic_data"}


class FakePublicReadClient:
    def list_markets(self, *, limit: int) -> list[MarketSummary]:
        assert limit == 1
        return [
            MarketSummary.model_validate(
                {
                    "id": "public-market-1",
                    "question": "Public read-only market",
                    "conditionId": "condition-1",
                    "clobTokenIds": ["token-yes", "token-no"],
                    "active": True,
                    "closed": False,
                }
            )
        ]

    def get_order_book(self, token_id: str) -> OrderBookSnapshot:
        assert token_id == "token-yes"
        return OrderBookSnapshot.model_validate(
            {
                "market": "condition-1",
                "asset_id": token_id,
                "timestamp": "1234567890",
                "hash": "public-snapshot",
                "bids": [{"price": "0.45", "size": "100"}],
                "asks": [{"price": "0.46", "size": "150"}],
                "min_order_size": "1",
                "tick_size": "0.01",
                "neg_risk": False,
            }
        )


def test_public_reads_are_disabled_by_default(tmp_path) -> None:
    with make_client(tmp_path) as client:
        response = client.get("/api/public/markets?limit=1")

    assert response.status_code == 403
    assert response.json() == {"detail": "Optional public reads are disabled"}


def test_enabled_public_reads_use_the_read_only_adapter(tmp_path) -> None:
    app = create_app(
        database=tmp_path / "paper.db",
        public_reads_enabled=True,
        public_read_client=FakePublicReadClient(),
    )
    with TestClient(app) as client:
        markets = client.get("/api/public/markets?limit=1")
        order_book = client.get("/api/public/order-book/token-yes")

    assert markets.status_code == 200
    assert markets.json()[0]["condition_id"] == "condition-1"
    assert order_book.status_code == 200
    assert order_book.json()["asset_id"] == "token-yes"
    assert order_book.json()["bids"][0] == {"price": "0.45", "size": "100"}


def test_synthetic_failure_can_be_injected_with_non_secret_environment_flag(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("OPS_LAB_SYNTHETIC_AVAILABLE", "1")
    nominal_app = create_app(database=tmp_path / "nominal.db", synthetic_available=None)
    with TestClient(nominal_app) as client:
        assert client.get("/readyz").status_code == 200

    monkeypatch.setenv("OPS_LAB_SYNTHETIC_AVAILABLE", "0")
    failed_app = create_app(database=tmp_path / "failed.db", synthetic_available=None)
    with TestClient(failed_app) as client:
        assert client.get("/readyz").status_code == 503
