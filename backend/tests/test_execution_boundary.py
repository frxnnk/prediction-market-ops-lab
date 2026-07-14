from decimal import Decimal

import pytest
from ops_lab.models import PaperIntent
from ops_lab.paper_executor import LiveExecutionDisabled, PaperExecutor


class RecordingLedger:
    def __init__(self) -> None:
        self.recorded_ids: list[str] = []

    def record_fill(self, intent: PaperIntent) -> None:
        self.recorded_ids.append(intent.request_id)


def test_paper_intent_is_accepted_and_recorded() -> None:
    ledger = RecordingLedger()
    executor = PaperExecutor(ledger)
    intent = PaperIntent(
        request_id="paper-demo-001",
        mode="paper",
        market_id="synthetic-market-001",
        outcome="YES",
        size=Decimal("5.00"),
        limit_price=Decimal("0.42"),
    )

    result = executor.execute(intent)

    assert result.request_id == "paper-demo-001"
    assert result.status == "simulated"
    assert ledger.recorded_ids == ["paper-demo-001"]


@pytest.mark.parametrize("mode", ["live", "prod", "production", "LIVE", ""])
def test_every_non_paper_mode_fails_before_persistence(mode: str) -> None:
    ledger = RecordingLedger()
    executor = PaperExecutor(ledger)
    intent = PaperIntent(
        request_id="blocked-001",
        mode=mode,
        market_id="synthetic-market-001",
        outcome="NO",
        size=Decimal("1.00"),
        limit_price=Decimal("0.55"),
    )

    with pytest.raises(LiveExecutionDisabled, match="paper-only"):
        executor.execute(intent)

    assert ledger.recorded_ids == []
