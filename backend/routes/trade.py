from fastapi import APIRouter
from models.trade import Trade, TradeRequest
from services.trade_service import buy, sell, get_trades

router = APIRouter(prefix="/portfolios", tags=["trades"])


@router.post("/{portfolio_id}/buy", response_model=Trade, status_code=201)
async def buy_stock(portfolio_id: str, data: TradeRequest):
    return await buy(portfolio_id, data)


@router.post("/{portfolio_id}/sell", response_model=Trade, status_code=201)
async def sell_stock(portfolio_id: str, data: TradeRequest):
    return await sell(portfolio_id, data)


@router.get("/{portfolio_id}/trades", response_model=list[Trade])
async def trade_history(portfolio_id: str):
    return await get_trades(portfolio_id)
