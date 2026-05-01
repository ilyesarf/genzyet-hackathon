import os
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from scraper import run_scrape

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def start_scheduler():
    scrape_time = os.getenv('SCRAPE_TIME', '07:00')
    try:
        hour, minute = map(int, scrape_time.split(':'))
    except ValueError:
        logger.error(f"Invalid SCRAPE_TIME format '{scrape_time}', expected HH:MM. Defaulting to 07:00")
        hour, minute = 7, 0

    scheduler = BackgroundScheduler()
    # Schedule the scrape once daily at the configured time
    scheduler.add_job(run_scrape, 'cron', hour=hour, minute=minute)
    scheduler.start()
    logger.info(f"Scheduler started. Next scrape scheduled daily at {hour:02d}:{minute:02d}.")
    return scheduler

if __name__ == '__main__':
    scheduler = start_scheduler()
    try:
        # Keep main thread alive
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
