from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PortfolioCreate(BaseModel):
    name: str
    starting_amount: float


class Portfolio(BaseModel):
    id: str = Field(alias="_id")
    name: str
    starting_amount: float
    current_cash: float
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_mongo(cls, doc: dict) -> "Portfolio":
        doc["_id"] = str(doc["_id"])
        return cls(**doc)


class Holding(BaseModel):
    symbol: str
    quantity: float
    avg_buy_price: float
    current_price: Optional[float] = None
    unrealized_pnl: Optional[float] = None


class PortfolioDetail(BaseModel):
    id: str
    name: str
    starting_amount: float
    current_cash: float
    created_at: datetime
    holdings: list[Holding]
    total_value: float
    total_pnl: float
