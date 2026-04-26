from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import logging

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


def get_chrome_driver():
    """Create and return a Selenium Chrome WebDriver"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    return driver


def fetch_all_parks():
    """Fetch all Ontario Parks"""
    logger.info(f"Loading {len(ALL_ONTARIO_PARKS)} Ontario Parks")
    return ALL_ONTARIO_PARKS


def check_availability(park_id, check_in_date, check_out_date, site_type=None):
    """
    Check real availability from Ontario Parks reservation system using Selenium.
    Returns: List of {site_id, site_name, date, available} dicts
    """
    driver = None
    try:
        logger.info(f"Checking availability for {park_id} from {check_in_date} to {check_out_date}")

        if park_id not in PARK_IDS:
            logger.warning(f"Park {park_id} not in PARK_IDS mapping")
            return []

        park_resource_id = PARK_IDS[park_id]

        # Build reservation URL
        url = (
            f"https://reservations.ontarioparks.ca/create-booking/results?"
            f"transactionLocationId=-2147483559&resourceLocationId={park_resource_id}&"
            f"startDate={check_in_date.strftime('%Y-%m-%d')}&"
            f"endDate={check_out_date.strftime('%Y-%m-%d')}"
        )

        logger.info(f"Loading URL: {url}")

        driver = get_chrome_driver()
        driver.get(url)

        # Wait for page to load - try multiple selectors
        wait = WebDriverWait(driver, 15)
        page_loaded = False
        selectors_to_try = [
            (By.CLASS_NAME, "site-item"),
            (By.CLASS_NAME, "campsite"),
            (By.CLASS_NAME, "site"),
            (By.XPATH, "//div[@class*='site']"),
            (By.TAG_NAME, "body"),  # At least wait for body to exist
        ]

        for selector in selectors_to_try:
            try:
                wait.until(EC.presence_of_element_located(selector))
                logger.debug(f"Found element with selector: {selector}")
                page_loaded = True
                break
            except:
                continue

        # Give additional time for dynamic content
        time.sleep(3)

        # Parse page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Log page title and body content for debugging
        logger.debug(f"Page title: {soup.title}")
        logger.debug(f"Page source length: {len(driver.page_source)} chars")

        availability_results = []

        # Try multiple selectors to find sites
        site_items = soup.find_all('div', class_='site-item')
        if not site_items:
            site_items = soup.find_all('div', class_='campsite')
        if not site_items:
            site_items = soup.find_all('div', class_='site')
        if not site_items:
            site_items = soup.find_all('li', class_=True)  # Any li with a class
        if not site_items:
            # Log all divs to see structure
            all_divs = soup.find_all('div')
            logger.warning(f"Could not find site items, found {len(all_divs)} total divs")
            logger.debug(f"First 5 divs: {[div.get('class') for div in all_divs[:5]]}")

        logger.info(f"Found {len(site_items)} site items for {park_id}")

        # For each site, check availability across all dates
        for idx, site_item in enumerate(site_items):
            try:
                # Extract site ID and name
                site_id = site_item.get('data-site-id') or site_item.get('id', f'site_{idx}')
                site_name = site_item.get('data-site-name') or site_item.get('title', f'Site {site_id}')

                # Check if site is available (look for available class or status)
                available_class = site_item.get('class', [])
                is_available = 'available' in available_class or 'open' in available_class

                # Alternative: check for availability indicator elements
                if not is_available:
                    available_indicator = site_item.find(['span', 'div'], class_=['available', 'open'])
                    is_available = available_indicator is not None

                if site_id:
                    availability_results.append({
                        'site_id': f"{park_id}_{site_id}",
                        'site_name': site_name,
                        'date': check_in_date,
                        'available': is_available
                    })

            except Exception as e:
                logger.debug(f"Error parsing site item: {e}")
                continue

        logger.info(f"Found {len(availability_results)} availability records for {park_id}")
        return availability_results

    except Exception as e:
        logger.error(f"Error checking availability for {park_id}: {e}", exc_info=True)
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


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
