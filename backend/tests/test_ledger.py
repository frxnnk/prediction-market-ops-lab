from decimal import Decimal

from ops_lab.ledger import PaperLedger
from ops_lab.models import PaperIntent


def make_intent(*, request_id: str = "paper-ledger-001") -> PaperIntent:
    return PaperIntent(
        request_id=request_id,
        mode="paper",
        market_id="synthetic-market-001",
        outcome="YES",
        size=Decimal("3.00"),
        limit_price=Decimal("0.40"),
    )


def test_ledger_is_idempotent_by_request_id(tmp_path) -> None:
    ledger = PaperLedger(tmp_path / "paper.db")
    intent = make_intent()

    assert ledger.record_fill(intent) is True
    assert ledger.record_fill(intent) is False

    fills = ledger.list_fills()
    assert len(fills) == 1
    assert fills[0].request_id == "paper-ledger-001"
    assert fills[0].market_id == "synthetic-market-001"
    assert fills[0].size == Decimal("3.00")


def test_ledger_persists_across_instances(tmp_path) -> None:
    database = tmp_path / "paper.db"
    first = PaperLedger(database)
    first.record_fill(make_intent(request_id="persisted-001"))

    reopened = PaperLedger(database)

    assert [fill.request_id for fill in reopened.list_fills()] == ["persisted-001"]
