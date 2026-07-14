from decimal import Decimal

from ops_lab.demo_policy import build_demo_intent
from ops_lab.synthetic import SyntheticMarketSnapshot


def test_demo_policy_is_deterministic_and_has_fixed_paper_risk() -> None:
    snapshot = SyntheticMarketSnapshot(
        market_id="synthetic-weather-001",
        question="Will the demo sensor report a clear day?",
        sequence=8,
        yes_price=Decimal("0.44"),
        no_price=Decimal("0.56"),
    )

    first = build_demo_intent(snapshot)
    second = build_demo_intent(snapshot)

    assert first == second
    assert first.request_id == "dummy-synthetic-weather-001-8"
    assert first.mode == "paper"
    assert first.outcome == "YES"
    assert first.size == Decimal("1.00")
    assert first.limit_price == Decimal("0.44")


def test_demo_policy_alternates_by_sequence_not_financial_signal() -> None:
    snapshot = SyntheticMarketSnapshot(
        market_id="synthetic-weather-001",
        question="Will the demo sensor report a clear day?",
        sequence=9,
        yes_price=Decimal("0.44"),
        no_price=Decimal("0.56"),
    )

    intent = build_demo_intent(snapshot)

    assert intent.outcome == "NO"
    assert intent.limit_price == Decimal("0.56")
