from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class StockCache(BaseModel):
    id: str = Field(alias="_id")
    symbol: str
    last_price: float
    fetched_at: datetime

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_mongo(cls, doc: dict) -> "StockCache":
        doc["_id"] = str(doc["_id"])
        return cls(**doc)
