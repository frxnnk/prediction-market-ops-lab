from decimal import Decimal

from pydantic import BaseModel, Field


class PaperIntent(BaseModel):
    request_id: str = Field(min_length=1)
    mode: str
    market_id: str = Field(min_length=1)
    outcome: str = Field(min_length=1)
    size: Decimal = Field(gt=0)
    limit_price: Decimal = Field(gt=0, lt=1)


class PaperExecutionResult(BaseModel):
    request_id: str
    status: str
