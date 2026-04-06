from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def start_scheduler():
    from jobs import fetch_prices_and_check_alerts
    scheduler.add_job(fetch_prices_and_check_alerts, "interval", minutes=5, id="price_alert_job")
    scheduler.start()
    print("Scheduler started")


def stop_scheduler():
    scheduler.shutdown(wait=False)
