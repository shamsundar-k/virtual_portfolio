from fastapi import APIRouter, HTTPException, Query
from services.stock_service import search_stocks, fetch_and_cache_price, get_price

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/search")
async def search(q: str = Query(..., min_length=1)):
    results = await search_stocks(q)
    return results


@router.get("/{symbol}/price")
async def get_stock_price(symbol: str):
    sym = symbol.upper()
    price = await get_price(sym)
    if price is None:
        raise HTTPException(status_code=404, detail=f"Price not available for {sym}")
    return {"symbol": sym, "price": price}


@router.post("/{symbol}/refresh")
async def refresh_price(symbol: str):
    """Force-fetch latest price from yfinance and update cache."""
    sym = symbol.upper()
    price = await fetch_and_cache_price(sym)
    if price is None:
        raise HTTPException(status_code=404, detail=f"Could not fetch price for {sym}")
    return {"symbol": sym, "price": price}
