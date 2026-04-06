from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

from db import get_db
from models.alert import Alert, AlertCreate


def _oid(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="Alert not found")


async def list_alerts() -> list[Alert]:
    db = get_db()
    docs = await db.alerts.find().sort("created_at", -1).to_list(None)
    return [Alert.from_mongo(d) for d in docs]


async def create_alert(data: AlertCreate) -> Alert:
    db = get_db()
    doc = {
        "symbol": data.symbol.upper(),
        "target_price": data.target_price,
        "condition": data.condition,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "triggered_at": None,
    }
    result = await db.alerts.insert_one(doc)
    doc["_id"] = result.inserted_id
    return Alert.from_mongo(doc)


async def delete_alert(alert_id: str) -> None:
    db = get_db()
    oid = _oid(alert_id)
    result = await db.alerts.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
