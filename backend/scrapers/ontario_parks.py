import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import logging
import json

logger = logging.getLogger(__name__)

ONTARIO_PARKS_BASE = "https://www.ontarioparks.com"

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
    logger.info(f"Loading {len(ALL_ONTARIO_PARKS)} Ontario Parks")
    return ALL_ONTARIO_PARKS


def check_availability(park_id, check_in_date, check_out_date, site_type=None):
    """
    Check real availability from Ontario Parks website.
    Returns: List of {site_id, site_name, date, available} dicts
    """
    try:
        logger.info(f"Checking real availability for {park_id} from {check_in_date} to {check_out_date}")

        availability_results = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        booking_url = f"https://www.ontarioparks.com/book-a-park/{park_id}"

        response = requests.get(booking_url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for availability data in page
        # Try to find sites and their availability
        site_containers = soup.find_all('div', class_=['site', 'campsite', 'site-item'])

        if not site_containers:
            logger.warning(f"Could not find site containers for {park_id}, trying alternative selectors")
            site_containers = soup.find_all(['li', 'div'], attrs={'data-siteid': True})

        logger.info(f"Found {len(site_containers)} site containers for {park_id}")

        current_date = check_in_date
        while current_date <= check_out_date:
            for container in site_containers:
                try:
                    site_id = container.get('data-siteid') or container.get('id', '')
                    site_name = container.get('data-name') or container.find('h3', 'h4').text.strip() if container.find('h3') or container.find('h4') else f"{park_id} - Site {site_id}"

                    # Look for availability status
                    available_indicator = container.find(['span', 'div'], class_=['available', 'open', 'available-site'])
                    is_available = available_indicator is not None

                    if site_id:
                        availability_results.append({
                            'site_id': f"{park_id}_{site_id}",
                            'site_name': site_name,
                            'date': current_date,
                            'available': is_available
                        })
                except Exception as e:
                    logger.debug(f"Error parsing site: {e}")
                    continue

            current_date += timedelta(days=1)
            time.sleep(0.5)

        logger.info(f"Found {len(availability_results)} availability records for {park_id}")
        return availability_results

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error checking {park_id}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error checking availability for {park_id}: {e}")
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
                    url=f"{ONTARIO_PARKS_BASE}/book-a-park/{park['park_id']}"
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
