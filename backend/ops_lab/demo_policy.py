from decimal import Decimal

from ops_lab.models import PaperIntent
from ops_lab.synthetic import SyntheticMarketSnapshot


def build_demo_intent(snapshot: SyntheticMarketSnapshot) -> PaperIntent:
    """Return an intentionally non-strategic paper intent for a synthetic snapshot."""
    outcome = "YES" if snapshot.sequence % 2 == 0 else "NO"
    limit_price = snapshot.yes_price if outcome == "YES" else snapshot.no_price
    return PaperIntent(
        request_id=f"dummy-{snapshot.market_id}-{snapshot.sequence}",
        mode="paper",
        market_id=snapshot.market_id,
        outcome=outcome,
        size=Decimal("1.00"),
        limit_price=limit_price,
    )
