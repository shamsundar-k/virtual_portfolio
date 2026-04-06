import logging

from telegram import Bot
from telegram.error import TelegramError

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

_bot: Bot | None = None


def _get_bot() -> Bot | None:
    global _bot
    if not TELEGRAM_TOKEN:
        return None
    if _bot is None:
        _bot = Bot(token=TELEGRAM_TOKEN)
    return _bot


async def send_alert_message(symbol: str, condition: str, target_price: float, current_price: float) -> bool:
    """
    Send a Telegram message when a price alert is triggered.
    Returns True on success, False if Telegram is not configured or the send fails.
    """
    bot = _get_bot()
    if bot is None or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured — skipping alert notification")
        return False

    direction = "above" if condition == "ABOVE" else "below"
    text = (
        f"Price Alert Triggered\n"
        f"Symbol: {symbol}\n"
        f"Condition: {direction} ₹{target_price:,.2f}\n"
        f"Current price: ₹{current_price:,.2f}"
    )

    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        logger.info("Telegram alert sent for %s", symbol)
        return True
    except TelegramError as exc:
        logger.error("Failed to send Telegram alert for %s: %s", symbol, exc)
        return False
