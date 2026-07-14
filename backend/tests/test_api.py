from fastapi.testclient import TestClient
from ops_lab.app import create_app


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
