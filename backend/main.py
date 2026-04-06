from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import connect_db, close_db
from scheduler import start_scheduler, stop_scheduler
from routes import portfolio, trade, stock, alert, journal


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    start_scheduler()
    yield
    stop_scheduler()
    await close_db()


app = FastAPI(title="Stock Tracker", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router)
app.include_router(trade.router)
app.include_router(stock.router)
app.include_router(alert.router)
app.include_router(journal.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
