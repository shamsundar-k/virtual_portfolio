from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class JournalCreate(BaseModel):
    note: str


class JournalEntry(BaseModel):
    id: str = Field(alias="_id")
    note: str
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_mongo(cls, doc: dict) -> "JournalEntry":
        doc["_id"] = str(doc["_id"])
        return cls(**doc)
