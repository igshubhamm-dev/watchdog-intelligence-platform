from apscheduler.schedulers.blocking import BlockingScheduler

from app.services.monitor_service import monitor_watchlist


scheduler = BlockingScheduler()


@scheduler.scheduled_job("interval", hours=24)
def run_watchdog():
    print("\nRunning scheduled watchlist monitor...\n")
    monitor_watchlist()


print("WATCHDOG Scheduler Started")
scheduler.start()
