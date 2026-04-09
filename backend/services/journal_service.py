from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

from db import get_db
from models.journal import JournalCreate, JournalEntry


def _oid(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="Journal entry not found")


async def list_entries() -> list[JournalEntry]:
    db = get_db()
    docs = await db.journal.find().sort("created_at", -1).to_list(None)
    return [JournalEntry.from_mongo(d) for d in docs]


async def create_entry(data: JournalCreate) -> JournalEntry:
    db = get_db()
    doc = {
        "note": data.note,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.journal.insert_one(doc)
    doc["_id"] = result.inserted_id
    return JournalEntry.from_mongo(doc)


async def delete_entry(entry_id: str) -> None:
    db = get_db()
    oid = _oid(entry_id)
    result = await db.journal.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Journal entry not found")
