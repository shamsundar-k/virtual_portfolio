from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

from db import get_db
from models.trade import Trade, TradeRequest


def _oid(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="Portfolio not found")


async def _get_portfolio_or_404(db, oid: ObjectId) -> dict:
    portfolio = await db.portfolios.find_one({"_id": oid})
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


async def _get_holding_quantity(db, portfolio_oid: ObjectId, symbol: str) -> float:
    """Net quantity held for a symbol in a portfolio."""
    pipeline = [
        {"$match": {"portfolio_id": portfolio_oid, "symbol": symbol}},
        {
            "$group": {
                "_id": "$type",
                "total": {"$sum": "$quantity"},
            }
        },
    ]
    totals = {doc["_id"]: doc["total"] async for doc in db.trades.aggregate(pipeline)}
    return totals.get("BUY", 0.0) - totals.get("SELL", 0.0)


async def buy(portfolio_id: str, data: TradeRequest) -> Trade:
    db = get_db()
    oid = _oid(portfolio_id)
    portfolio = await _get_portfolio_or_404(db, oid)

    if data.quantity <= 0 or data.price <= 0:
        raise HTTPException(status_code=400, detail="Quantity and price must be positive")

    cost = data.quantity * data.price
    if portfolio["current_cash"] < cost:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient cash. Available: ₹{portfolio['current_cash']:.2f}, Required: ₹{cost:.2f}",
        )

    trade_doc = {
        "portfolio_id": oid,
        "symbol": data.symbol.upper(),
        "type": "BUY",
        "quantity": data.quantity,
        "price": data.price,
        "traded_at": datetime.now(timezone.utc),
    }
    result = await db.trades.insert_one(trade_doc)
    trade_doc["_id"] = result.inserted_id

    await db.portfolios.update_one({"_id": oid}, {"$inc": {"current_cash": -cost}})

    return Trade.from_mongo(trade_doc)


async def sell(portfolio_id: str, data: TradeRequest) -> Trade:
    db = get_db()
    oid = _oid(portfolio_id)
    await _get_portfolio_or_404(db, oid)

    if data.quantity <= 0 or data.price <= 0:
        raise HTTPException(status_code=400, detail="Quantity and price must be positive")

    symbol = data.symbol.upper()
    held = await _get_holding_quantity(db, oid, symbol)
    if held < data.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient holdings. Held: {held}, Requested: {data.quantity}",
        )

    trade_doc = {
        "portfolio_id": oid,
        "symbol": symbol,
        "type": "SELL",
        "quantity": data.quantity,
        "price": data.price,
        "traded_at": datetime.now(timezone.utc),
    }
    result = await db.trades.insert_one(trade_doc)
    trade_doc["_id"] = result.inserted_id

    proceeds = data.quantity * data.price
    await db.portfolios.update_one({"_id": oid}, {"$inc": {"current_cash": proceeds}})

    return Trade.from_mongo(trade_doc)


async def get_trades(portfolio_id: str) -> list[Trade]:
    db = get_db()
    oid = _oid(portfolio_id)
    await _get_portfolio_or_404(db, oid)

    docs = await db.trades.find({"portfolio_id": oid}).sort("traded_at", -1).to_list(None)
    return [Trade.from_mongo(d) for d in docs]
