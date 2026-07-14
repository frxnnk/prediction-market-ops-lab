from decimal import Decimal

from pydantic import BaseModel, Field


class SyntheticMarketSnapshot(BaseModel):
    market_id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    sequence: int = Field(ge=0)
    yes_price: Decimal = Field(gt=0, lt=1)
    no_price: Decimal = Field(gt=0, lt=1)


def synthetic_markets() -> list[SyntheticMarketSnapshot]:
    return [
        SyntheticMarketSnapshot(
            market_id="synthetic-weather-001",
            question="Will the demo sensor report a clear day?",
            sequence=8,
            yes_price=Decimal("0.44"),
            no_price=Decimal("0.56"),
        ),
        SyntheticMarketSnapshot(
            market_id="synthetic-launch-002",
            question="Will the sample payload launch before Friday?",
            sequence=11,
            yes_price=Decimal("0.61"),
            no_price=Decimal("0.39"),
        ),
        SyntheticMarketSnapshot(
            market_id="synthetic-grid-003",
            question="Will the local grid drill stay within its test window?",
            sequence=14,
            yes_price=Decimal("0.52"),
            no_price=Decimal("0.48"),
        ),
    ]
