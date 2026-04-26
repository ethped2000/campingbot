from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from models import Search, Availability
from scrapers.ontario_parks import check_availability

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
last_run_time = None


def run_scraper_job():
    """Main scraper job that runs every 30 minutes"""
    global last_run_time

    try:
        start_time = datetime.now()
        logger.info(f"[{start_time}] Starting scraper job...")

        db = SessionLocal()
        active_searches = db.query(Search).filter(Search.status == 'active').all()

        logger.info(f"Found {len(active_searches)} active searches")

        total_availability_records = 0

        for search in active_searches:
            try:
                campground = search.campground
                logger.info(f"Checking {campground.name} ({search.check_in_date} to {search.check_out_date})")

                availability_data = check_availability(
                    campground.park_id,
                    search.check_in_date,
                    search.check_out_date,
                    search.site_type
                )

                # Group by site_id to check if available for entire date range
                sites_by_id = {}
                for site in availability_data:
                    site_id = site['site_id'].split('_')[0] + '_site_' + site['site_id'].split('_')[-1]
                    if site_id not in sites_by_id:
                        sites_by_id[site_id] = {'site_name': site['site_name'], 'dates': []}
                    sites_by_id[site_id]['dates'].append({'date': site['date'], 'available': site['available']})

                # Only store sites that are available for ALL dates in the range
                for site_id, site_data in sites_by_id.items():
                    all_available = all(d['available'] for d in site_data['dates'])

                    # Store a single record per site indicating if available for entire range
                    existing = db.query(Availability).filter(
                        Availability.search_id == search.id,
                        Availability.site_id == site_id
                    ).first()

                    if existing:
                        existing.available = all_available
                        existing.last_checked = datetime.now()
                    else:
                        db_availability = Availability(
                            search_id=search.id,
                            site_id=site_id,
                            site_name=site_data['site_name'],
                            date=search.check_in_date,
                            available=all_available
                        )
                        db.add(db_availability)

                    total_availability_records += 1

            except Exception as e:
                logger.error(f"Error processing search {search.id}: {e}")
                continue

        db.commit()
        db.close()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        last_run_time = end_time

        logger.info(
            f"[{end_time}] Scraper completed successfully. "
            f"Added/updated {total_availability_records} availability records in {duration:.2f}s"
        )

    except Exception as e:
        logger.error(f"Scraper job failed: {e}", exc_info=True)


def get_last_run_time():
    """Get the timestamp of the last successful scraper run"""
    return last_run_time


def start_scheduler():
    """Start the background scheduler"""
    try:
        if not scheduler.running:
            scheduler.add_job(run_scraper_job, 'interval', minutes=30, id='ontario_parks_scraper')
            scheduler.start()
            logger.info("Scheduler started. Scraper will run every 30 minutes.")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")


def stop_scheduler():
    """Stop the background scheduler"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Scheduler stopped.")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
