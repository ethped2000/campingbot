import requests
from datetime import datetime, timedelta
import time
import logging
import json

logger = logging.getLogger(__name__)

PARK_IDS = {
    "algonquin": -2147483559,
    "presquile": -2147483563,
    "killarney": -2147483548,
    "pinery": -2147483551,
    "pukaskwa": -2147483555,
    "temagami": -2147483560,
    "quetico": -2147483549,
    "nipigon": -2147483552,
    "grundy": -2147483556,
    "sturgeon": -2147483554,
    "awenda": -2147483557,
    "balsam": -2147483558,
    "cascade": -2147483550,
    "cat": -2147483546,
    "clyde": -2147483547,
    "driftwood": -2147483561,
    "earl_rowe": -2147483562,
    "ferryland": -2147483564,
    "ganaraska": -2147483565,
    "gowganda": -2147483566,
}

AVAILABILITY_API = "https://reservations.ontarioparks.ca/api/availability/map"

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
    Check real availability from Ontario Parks API.
    Returns: List of {site_id, site_name, date, available} dicts
    """
    try:
        logger.info(f"Checking availability for {park_id} from {check_in_date} to {check_out_date}")

        if park_id not in PARK_IDS:
            logger.warning(f"Park {park_id} not in PARK_IDS mapping")
            return []

        park_resource_id = PARK_IDS[park_id]
        availability_results = []

        # Query API for each day in the range
        current_date = check_in_date
        while current_date <= check_out_date:
            try:
                # Build API request payload
                payload = {
                    "transactionLocationId": -2147483559,
                    "resourceLocationId": park_resource_id,
                    "startDate": current_date.strftime('%Y-%m-%d'),
                    "endDate": current_date.strftime('%Y-%m-%d'),
                    "equipmentTypeId": None
                }

                logger.debug(f"Querying API for {park_id} on {current_date}: {payload}")

                response = requests.post(
                    AVAILABILITY_API,
                    json=payload,
                    timeout=10,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"API response for {current_date}: {json.dumps(data, indent=2)}")

                    # Parse availability data
                    if 'mapLinkAvailabilities' in data:
                        for site_id_str, availability_codes in data['mapLinkAvailabilities'].items():
                            try:
                                site_id = int(site_id_str)
                                # Availability code meanings: 0=booked, 6=available, etc
                                is_available = 6 in availability_codes or any(code > 0 for code in availability_codes)

                                availability_results.append({
                                    'site_id': f"{park_id}_{site_id}",
                                    'site_name': f"Site {site_id}",
                                    'date': current_date,
                                    'available': is_available
                                })
                            except Exception as e:
                                logger.debug(f"Error parsing site {site_id_str}: {e}")
                                continue

                    logger.info(f"Found {len(availability_results)} available sites on {current_date}")
                else:
                    logger.warning(f"API returned {response.status_code} for {park_id} on {current_date}")

            except requests.exceptions.Timeout:
                logger.warning(f"API timeout for {park_id} on {current_date}")
            except Exception as e:
                logger.error(f"Error querying API for {park_id} on {current_date}: {e}")

            current_date += timedelta(days=1)
            time.sleep(0.5)  # Rate limiting

        logger.info(f"Found {len(availability_results)} total availability records for {park_id}")
        return availability_results

    except Exception as e:
        logger.error(f"Error checking availability for {park_id}: {e}", exc_info=True)
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
