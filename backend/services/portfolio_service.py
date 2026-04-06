from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

from db import get_db
from models.portfolio import PortfolioCreate, Portfolio, PortfolioDetail, Holding


def _oid(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="Portfolio not found")


async def list_portfolios() -> list[Portfolio]:
    db = get_db()
    docs = await db.portfolios.find().sort("created_at", -1).to_list(None)
    return [Portfolio.from_mongo(d) for d in docs]


async def create_portfolio(data: PortfolioCreate) -> Portfolio:
    db = get_db()
    if await db.portfolios.count_documents({}) >= 10:
        raise HTTPException(status_code=400, detail="Maximum 10 portfolios allowed")
    doc = {
        "name": data.name,
        "starting_amount": data.starting_amount,
        "current_cash": data.starting_amount,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.portfolios.insert_one(doc)
    doc["_id"] = result.inserted_id
    return Portfolio.from_mongo(doc)


async def get_portfolio_detail(portfolio_id: str) -> PortfolioDetail:
    db = get_db()
    oid = _oid(portfolio_id)

    portfolio = await db.portfolios.find_one({"_id": oid})
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    trades = await db.trades.find({"portfolio_id": oid}).to_list(None)

    # Aggregate holdings from trades
    holdings_map: dict[str, dict] = {}
    for t in trades:
        sym = t["symbol"]
        if sym not in holdings_map:
            holdings_map[sym] = {"net_qty": 0.0, "buy_qty": 0.0, "total_cost": 0.0}
        if t["type"] == "BUY":
            holdings_map[sym]["net_qty"] += t["quantity"]
            holdings_map[sym]["buy_qty"] += t["quantity"]
            holdings_map[sym]["total_cost"] += t["quantity"] * t["price"]
        else:  # SELL
            holdings_map[sym]["net_qty"] -= t["quantity"]

    holdings = []
    holdings_value = 0.0

    for sym, data in holdings_map.items():
        qty = data["net_qty"]
        if qty <= 0:
            continue

        avg_buy = data["total_cost"] / data["buy_qty"] if data["buy_qty"] else 0.0

        cache = await db.stock_cache.find_one({"symbol": sym})
        current_price = cache["last_price"] if cache else None
        unrealized_pnl = (current_price - avg_buy) * qty if current_price is not None else None

        holdings.append(Holding(
            symbol=sym,
            quantity=qty,
            avg_buy_price=round(avg_buy, 2),
            current_price=current_price,
            unrealized_pnl=round(unrealized_pnl, 2) if unrealized_pnl is not None else None,
        ))
        holdings_value += (current_price * qty) if current_price is not None else (avg_buy * qty)

    total_value = portfolio["current_cash"] + holdings_value
    total_pnl = total_value - portfolio["starting_amount"]

    return PortfolioDetail(
        id=str(portfolio["_id"]),
        name=portfolio["name"],
        starting_amount=portfolio["starting_amount"],
        current_cash=portfolio["current_cash"],
        created_at=portfolio["created_at"],
        holdings=holdings,
        total_value=round(total_value, 2),
        total_pnl=round(total_pnl, 2),
    )


async def delete_portfolio(portfolio_id: str) -> None:
    db = get_db()
    oid = _oid(portfolio_id)
    result = await db.portfolios.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    # Remove associated trades too
    await db.trades.delete_many({"portfolio_id": oid})
