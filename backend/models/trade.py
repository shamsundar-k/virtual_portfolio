from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class TradeRequest(BaseModel):
    symbol: str
    quantity: float
    price: float


class Trade(BaseModel):
    id: str = Field(alias="_id")
    portfolio_id: str
    symbol: str
    type: Literal["BUY", "SELL"]
    quantity: float
    price: float
    traded_at: datetime

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_mongo(cls, doc: dict) -> "Trade":
        doc["_id"] = str(doc["_id"])
        doc["portfolio_id"] = str(doc["portfolio_id"])
        return cls(**doc)
