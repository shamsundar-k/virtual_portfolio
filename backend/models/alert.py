from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class AlertCreate(BaseModel):
    symbol: str
    target_price: float
    condition: Literal["ABOVE", "BELOW"]


class Alert(BaseModel):
    id: str = Field(alias="_id")
    symbol: str
    target_price: float
    condition: Literal["ABOVE", "BELOW"]
    is_active: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_mongo(cls, doc: dict) -> "Alert":
        doc["_id"] = str(doc["_id"])
        return cls(**doc)
