from datetime import datetime, timezone

import yfinance as yf

from db import get_db


async def get_cached_price(symbol: str) -> float | None:
    """Return last_price from stock_cache, or None if not cached."""
    db = get_db()
    doc = await db.stock_cache.find_one({"symbol": symbol})
    return doc["last_price"] if doc else None


async def fetch_and_cache_price(symbol: str) -> float | None:
    """Fetch current price from yfinance, upsert into stock_cache, return price."""
    ticker = yf.Ticker(symbol)
    info = ticker.fast_info
    price: float | None = None

    try:
        price = float(info.last_price)
    except Exception:
        pass

    if price is None or price <= 0:
        return None

    db = get_db()
    await db.stock_cache.update_one(
        {"symbol": symbol},
        {
            "$set": {
                "symbol": symbol,
                "last_price": price,
                "fetched_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )
    return price


async def get_price(symbol: str) -> float | None:
    """Return cached price if available, else fetch live from yfinance."""
    cached = await get_cached_price(symbol)
    if cached is not None:
        return cached
    return await fetch_and_cache_price(symbol)


async def search_stocks(query: str) -> list[dict]:
    """
    Search NSE/BSE stocks via yfinance.Search.
    Returns list of {symbol, name, exchange} dicts.
    """
    results = []
    try:
        search = yf.Search(query, max_results=10, news_count=0)
        quotes = search.quotes or []
        for q in quotes:
            exchange = q.get("exchange", "")
            # Filter to NSE (NSI) and BSE (BSE) only
            if exchange not in ("NSI", "BSE"):
                continue
            symbol = q.get("symbol", "")
            name = q.get("shortname") or q.get("longname") or symbol
            results.append({"symbol": symbol, "name": name, "exchange": exchange})
    except Exception:
        pass
    return results
