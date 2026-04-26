import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import logging
import random

logger = logging.getLogger(__name__)

ONTARIO_PARKS_BASE = "https://www.ontarioparks.com"
PARKS_API_URL = "https://www.ontarioparks.com/api/campgrounds"

ALL_ONTARIO_PARKS = [
    {"name": "Algonquin Provincial Park", "park_id": "algonquin", "region": "Central Ontario"},
    {"name": "Killarney Provincial Park", "park_id": "killarney", "region": "Northern Ontario"},
    {"name": "Presquile Provincial Park", "park_id": "presquile", "region": "Eastern Ontario"},
    {"name": "Pinery Provincial Park", "park_id": "pinery", "region": "Southwestern Ontario"},
    {"name": "Pukaskwa National Park", "park_id": "pukaskwa", "region": "Northern Ontario"},
    {"name": "Temagami Provincial Park", "park_id": "temagami", "region": "Northern Ontario"},
    {"name": "Quetico Provincial Park", "park_id": "quetico", "region": "Northwestern Ontario"},
    {"name": "Nipigon Provincial Park", "park_id": "nipigon", "region": "Northern Ontario"},
    {"name": "Grundy Lake Provincial Park", "park_id": "grundy", "region": "Central Ontario"},
    {"name": "Sturgeon Bay Provincial Park", "park_id": "sturgeon", "region": "Northern Ontario"},
    {"name": "Awenda Provincial Park", "park_id": "awenda", "region": "Central Ontario"},
    {"name": "Balsam Lake Provincial Park", "park_id": "balsam", "region": "Central Ontario"},
    {"name": "Cascade Falls Provincial Park", "park_id": "cascade", "region": "Eastern Ontario"},
    {"name": "Cat Lake Provincial Park", "park_id": "cat", "region": "Northwestern Ontario"},
    {"name": "Clyde Provincial Park", "park_id": "clyde", "region": "Northwestern Ontario"},
    {"name": "Driftwood Provincial Park", "park_id": "driftwood", "region": "Northern Ontario"},
    {"name": "Earl Rowe Provincial Park", "park_id": "earl_rowe", "region": "Central Ontario"},
    {"name": "Ferryland Provincial Park", "park_id": "ferryland", "region": "Central Ontario"},
    {"name": "Ganaraska Provincial Park", "park_id": "ganaraska", "region": "Eastern Ontario"},
    {"name": "Gowganda Provincial Park", "park_id": "gowganda", "region": "Northern Ontario"},
    {"name": "Greenwater Lake Provincial Park", "park_id": "greenwater", "region": "Central Ontario"},
    {"name": "Halibut Lake Provincial Park", "park_id": "halibut", "region": "Northern Ontario"},
    {"name": "Heyden Lake Provincial Park", "park_id": "heyden", "region": "Northwestern Ontario"},
    {"name": "Ignace Lake Provincial Park", "park_id": "ignace", "region": "Northwestern Ontario"},
    {"name": "Ivanhoe Lake Provincial Park", "park_id": "ivanhoe", "region": "Northern Ontario"},
    {"name": "Jack Lake Provincial Park", "park_id": "jack", "region": "Central Ontario"},
    {"name": "Kawartha Highlands Signature Site", "park_id": "kawartha", "region": "Central Ontario"},
    {"name": "Killbear Provincial Park", "park_id": "killbear", "region": "Central Ontario"},
    {"name": "Kiosk Provincial Park", "park_id": "kiosk", "region": "Central Ontario"},
    {"name": "Lady Evelyn-Smoothwater Provincial Park", "park_id": "lady_evelyn", "region": "Northern Ontario"},
    {"name": "Lake Superior Provincial Park", "park_id": "lake_superior", "region": "Northern Ontario"},
    {"name": "Long Lake Provincial Park", "park_id": "long_lake", "region": "Northern Ontario"},
    {"name": "MacGregor Point Provincial Park", "park_id": "macgregor", "region": "Southwestern Ontario"},
    {"name": "Mara Provincial Park", "park_id": "mara", "region": "Central Ontario"},
    {"name": "Mattice Lake Provincial Park", "park_id": "mattice", "region": "Northern Ontario"},
]


def fetch_all_parks():
    """Fetch all Ontario Parks"""
    try:
        logger.info(f"Fetching {len(ALL_ONTARIO_PARKS)} Ontario Parks")
        return ALL_ONTARIO_PARKS
    except Exception as e:
        logger.error(f"Error fetching parks: {e}")
        return []


def check_availability(park_id, check_in_date, check_out_date, site_type=None):
    """
    Check availability for a specific park and date range
    Returns: List of {site_id, site_name, date, available} dicts

    Note: Currently returns simulated data for testing.
    Real scraping of ontarioparks.com requires handling dynamic content.
    """
    try:
        availability_results = []

        logger.info(f"Checking availability for {park_id} from {check_in_date} to {check_out_date}")

        current_date = check_in_date
        site_count = 0

        while current_date <= check_out_date:
            try:
                for site_num in range(1, 151):
                    site_id = f"{park_id}_site_{site_num}"
                    site_name = f"{park_id} - Campsite {site_num}"

                    is_available = random.random() > 0.7

                    availability_results.append({
                        'site_id': site_id,
                        'site_name': site_name,
                        'date': current_date,
                        'available': is_available
                    })
                    site_count += 1

            except Exception as e:
                logger.warning(f"Error processing date {current_date}: {e}")

            current_date += timedelta(days=1)
            time.sleep(0.1)

        logger.info(f"Generated {site_count} availability records for {park_id}")
        return availability_results

    except Exception as e:
        logger.error(f"Error checking availability for {park_id}: {e}")
        return []


def parse_availability_html(html, park_id, check_in_date, check_out_date):
    """Parse availability HTML and extract available dates/sites"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        availability_grid = soup.find('div', class_='availability-grid')

        if availability_grid:
            available_cells = availability_grid.find_all('div', class_='available')

            for cell in available_cells:
                site_id = cell.get('data-site-id')
                date_str = cell.get('data-date')

                if site_id and date_str:
                    results.append({
                        'site_id': site_id,
                        'site_name': cell.get('data-site-name', 'Unknown Site'),
                        'date': date_str,
                        'available': True
                    })

        return results
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        return []


def seed_campgrounds(db):
    """
    Seed database with all Ontario Parks
    Returns: Number of parks added
    """
    from models import Campground

    try:
        parks = fetch_all_parks()
        added_count = 0

        for park in parks:
            existing = db.query(Campground).filter(Campground.name == park['name']).first()

            if not existing:
                db_park = Campground(
                    name=park['name'],
                    park_id=park['park_id'],
                    region=park['region'],
                    url=f"{ONTARIO_PARKS_BASE}/book-a-park/search?placeId={park['park_id']}"
                )
                db.add(db_park)
                added_count += 1

        db.commit()
        logger.info(f"Seeded {added_count} new campgrounds")
        return added_count

    except Exception as e:
        logger.error(f"Error seeding campgrounds: {e}")
        db.rollback()
        return 0
