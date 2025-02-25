from apscheduler.schedulers.asyncio import AsyncIOScheduler
from coffeeapp.tasks.cleanup import cleanup_unverified_users

def setup_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cleanup_unverified_users, 'interval', hours=24)
    return scheduler 