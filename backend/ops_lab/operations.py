from pathlib import Path

from ops_lab.demo_policy import build_demo_intent
from ops_lab.ledger import PaperLedger
from ops_lab.models import PaperExecutionResult
from ops_lab.paper_executor import PaperExecutor
from ops_lab.synthetic import SyntheticMarketSnapshot, synthetic_markets
from ops_lab.wallet_verifier import WalletProofResult, verify_ephemeral_wallet


class SyntheticDataUnavailable(RuntimeError):
    pass


class MarketNotFound(LookupError):
    pass


class OpsLabService:
    def __init__(self, database: str | Path, *, synthetic_available: bool = True) -> None:
        self._ledger = PaperLedger(database)
        self._executor = PaperExecutor(self._ledger)
        self._synthetic_available = synthetic_available
        self._markets = synthetic_markets()
        self._paper_runs_total = 0

    def markets(self) -> list[SyntheticMarketSnapshot]:
        self._require_synthetic_data()
        return self._markets

    def overview(self) -> dict[str, object]:
        return {
            "mode": "paper",
            "live_execution_enabled": False,
            "data_source": "synthetic",
            "market_count": len(self.markets()),
            "paper_fill_count": self._ledger.count_fills(),
        }

    def run_paper(self, market_id: str) -> PaperExecutionResult:
        market = next((item for item in self.markets() if item.market_id == market_id), None)
        if market is None:
            raise MarketNotFound(market_id)
        result = self._executor.execute(build_demo_intent(market))
        self._paper_runs_total += 1
        return result

    def verify_wallet(self, challenge: str) -> WalletProofResult:
        return verify_ephemeral_wallet(challenge)

    def is_ready(self) -> bool:
        return self._synthetic_available

    def diagnostics(self) -> dict[str, str]:
        return {
            "execution_boundary": "paper-only",
            "synthetic_data": "ok" if self._synthetic_available else "failed",
            "ledger": "ok",
            "outbound_access": "public-read-only",
        }

    def metrics(self) -> str:
        return (
            "# TYPE paper_runs_total counter\n"
            f"paper_runs_total {self._paper_runs_total}\n"
            "# TYPE live_execution_enabled gauge\n"
            "live_execution_enabled 0\n"
            f"paper_fills_total {self._ledger.count_fills()}\n"
        )

    def _require_synthetic_data(self) -> None:
        if not self._synthetic_available:
            raise SyntheticDataUnavailable("Synthetic fixture provider is unavailable")
