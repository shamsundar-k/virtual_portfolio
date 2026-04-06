from fastapi import APIRouter
from models.portfolio import Portfolio, PortfolioCreate, PortfolioDetail
from services.portfolio_service import (
    list_portfolios,
    create_portfolio,
    get_portfolio_detail,
    delete_portfolio,
)

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("", response_model=list[Portfolio])
async def get_portfolios():
    return await list_portfolios()


@router.post("", response_model=Portfolio, status_code=201)
async def create(data: PortfolioCreate):
    return await create_portfolio(data)


@router.get("/{portfolio_id}", response_model=PortfolioDetail)
async def get_detail(portfolio_id: str):
    return await get_portfolio_detail(portfolio_id)


@router.delete("/{portfolio_id}", status_code=204)
async def delete(portfolio_id: str):
    await delete_portfolio(portfolio_id)
