"""
Scheduled jobs — APScheduler price fetch + alert check job.
Runs every 5 minutes (configured in scheduler.py).
"""

import logging
from datetime import datetime, timezone

from db import get_db
from services.stock_service import fetch_and_cache_price
from services.telegram_service import send_alert_message

logger = logging.getLogger(__name__)


async def fetch_prices_and_check_alerts() -> None:
    """
    1. Fetch all active alerts from DB.
    2. For each unique symbol, fetch and cache the latest price via yfinance.
    3. Check each alert condition — trigger if met, then deactivate.
    """
    db = get_db()

    # 1. Load all active alerts
    active_alerts = await db.alerts.find({"is_active": True}).to_list(None)
    if not active_alerts:
        logger.info("price_alert_job: no active alerts, skipping")
        return

    # 2. Fetch prices for each unique symbol
    symbols = {alert["symbol"] for alert in active_alerts}
    prices: dict[str, float | None] = {}
    for symbol in symbols:
        prices[symbol] = await fetch_and_cache_price(symbol)

    # 3. Check each alert
    triggered = 0
    for alert in active_alerts:
        symbol: str = alert["symbol"]
        current_price = prices.get(symbol)

        if current_price is None:
            logger.warning("price_alert_job: could not fetch price for %s — skipping", symbol)
            continue

        target_price: float = alert["target_price"]
        condition: str = alert["condition"]

        hit = (condition == "ABOVE" and current_price >= target_price) or \
              (condition == "BELOW" and current_price <= target_price)

        if hit:
            await send_alert_message(symbol, condition, target_price, current_price)
            await db.alerts.update_one(
                {"_id": alert["_id"]},
                {"$set": {"is_active": False, "triggered_at": datetime.now(timezone.utc)}},
            )
            triggered += 1
            logger.info(
                "price_alert_job: triggered alert for %s %s ₹%.2f (current ₹%.2f)",
                symbol, condition, target_price, current_price,
            )

    logger.info(
        "price_alert_job: checked %d alerts across %d symbols — %d triggered",
        len(active_alerts), len(symbols), triggered,
    )
