import requests
from datetime import datetime, timedelta
import time
import logging
import json

logger = logging.getLogger(__name__)

PARK_IDS = {
    "presquile": -2147483302,
    "algonquin_tea_lake": -2147483171,
    "algonquin_lake_of_two_rivers": -2147483414,
    "algonquin_kiosk": -2147483415,
    "algonquin_mew_lake": -2147483378,
    "algonquin_canisbay_lake": -2147483562,
    "algonquin_brent": -2147483573,
    "algonquin_pog_lake": -2147483317,
    "algonquin_rock_lake": -2147483264,
    "pinery": -2147483334,
    "killarney": -2147483434,
    "bon_echo": -2147483590,
    "quetico": -2147483292,
    "sturgeon_bay": -2147483172,
    "grundy_lake": -2147483483,
    "awenda": -2147483623,
    "balsam_lake": -2147483614,
    "driftwood": -2147483535,
    "earl_rowe": -2147483531,
    "ivanhoe_lake": -2147483453,
    "killbear": -2147483428,
    "kawartha_highlands": -2147483441,
    "lake_superior": -2147483643,
    "macgregor_point": -2147483404,
    "mara": -2147483390,
    "aaron": -2147483648,
    "arrow_lake": -2147483122,
    "arrowhead": -2147483630,
    "bass_lake": -2147483602,
    "blue_lake": -2147483595,
    "bonnechere": -2147483577,
    "bronte_creek": -2147483572,
    "caliper_lake": -2147483565,
    "charleston_lake": -2147483558,
    "chutes": -2147483551,
    "craigleith": -2147483546,
    "darlington": -2147483540,
    "emily": -2147483518,
    "esker_lakes": -2147483511,
    "fairbank": -2147483505,
    "ferris": -2147483502,
    "finlayson_point": -2147483499,
    "fitzroy": -2147483493,
    "frontenac": -2147483489,
    "fushimi_lake": -2147483488,
    "halfway_lake": -2147483470,
    "inverhuron": -2147483458,
    "kakabeka_falls": -2147483446,
    "kettle_lakes": -2147483440,
    "lake_st_peter": -2147483410,
    "long_point": -2147483408,
    "marten_river": -2147483387,
    "mcrae_point": -2147483381,
    "mikisew": -2147483374,
    "mississagi": -2147483368,
    "murphys_point": -2147483364,
    "neys": -2147483355,
    "oastler_lake": -2147483351,
    "pancake_bay": -2147483342,
    "point_farms": -2147483311,
    "port_burwell": -2147483307,
    "rainbow_falls": -2147483284,
    "rene_brunelle": -2147483280,
    "restoule": -2147483275,
    "rideau_river": -2147483270,
    "rock_point": -2147483260,
    "rondeau": -2147483254,
    "rushing_river": -2147483250,
    "samuel_de_champlain": -2147483244,
    "sandbanks": -2147483239,
    "sandbar_lake": -2147483227,
    "sauble_falls": -2147483225,
    "selkirk": -2147483221,
    "sharbot_lake": -2147483215,
    "sibbald_point": -2147483210,
    "silent_lake": -2147483198,
    "silver_lake": -2147483193,
    "sioux_narrows": -2147483189,
    "six_mile_lake": -2147483186,
    "sleeping_giant": -2147483178,
    "turkey_point": -2147483170,
    "voyageur": -2147483165,
    "wakami_lake": -2147483159,
    "wheatley": -2147483154,
    "white_lake": -2147483148,
    "windy_lake": -2147483142,
}

AVAILABILITY_API = "https://reservations.ontarioparks.ca/api/availability/map"

ALL_ONTARIO_PARKS = [
    {"name": "Algonquin Provincial Park - Tea Lake", "park_id": "algonquin_tea_lake", "region": "Central Ontario"},
    {"name": "Algonquin Provincial Park - Lake of Two Rivers", "park_id": "algonquin_lake_of_two_rivers", "region": "Central Ontario"},
    {"name": "Algonquin Provincial Park - Kiosk", "park_id": "algonquin_kiosk", "region": "Central Ontario"},
    {"name": "Algonquin Provincial Park - Mew Lake", "park_id": "algonquin_mew_lake", "region": "Central Ontario"},
    {"name": "Algonquin Provincial Park - Canisbay Lake", "park_id": "algonquin_canisbay_lake", "region": "Central Ontario"},
    {"name": "Algonquin Provincial Park - Brent", "park_id": "algonquin_brent", "region": "Central Ontario"},
    {"name": "Algonquin Provincial Park - Pog Lake", "park_id": "algonquin_pog_lake", "region": "Central Ontario"},
    {"name": "Algonquin Provincial Park - Rock Lake", "park_id": "algonquin_rock_lake", "region": "Central Ontario"},
    {"name": "Presquile Provincial Park", "park_id": "presquile", "region": "Eastern Ontario"},
    {"name": "Pinery Provincial Park", "park_id": "pinery", "region": "Southwestern Ontario"},
    {"name": "Killarney Provincial Park", "park_id": "killarney", "region": "Northern Ontario"},
    {"name": "Bon Echo Provincial Park", "park_id": "bon_echo", "region": "Eastern Ontario"},
    {"name": "Quetico Provincial Park", "park_id": "quetico", "region": "Northwestern Ontario"},
    {"name": "Sturgeon Bay Provincial Park", "park_id": "sturgeon_bay", "region": "Northern Ontario"},
    {"name": "Grundy Lake Provincial Park", "park_id": "grundy_lake", "region": "Central Ontario"},
    {"name": "Awenda Provincial Park", "park_id": "awenda", "region": "Central Ontario"},
    {"name": "Balsam Lake Provincial Park", "park_id": "balsam_lake", "region": "Central Ontario"},
    {"name": "Driftwood Provincial Park", "park_id": "driftwood", "region": "Northern Ontario"},
    {"name": "Earl Rowe Provincial Park", "park_id": "earl_rowe", "region": "Central Ontario"},
    {"name": "Ivanhoe Lake Provincial Park", "park_id": "ivanhoe_lake", "region": "Northern Ontario"},
    {"name": "Killbear Provincial Park", "park_id": "killbear", "region": "Central Ontario"},
    {"name": "Kawartha Highlands Signature Site", "park_id": "kawartha_highlands", "region": "Central Ontario"},
    {"name": "Lake Superior Provincial Park", "park_id": "lake_superior", "region": "Northern Ontario"},
    {"name": "MacGregor Point Provincial Park", "park_id": "macgregor_point", "region": "Southwestern Ontario"},
    {"name": "Mara Provincial Park", "park_id": "mara", "region": "Central Ontario"},
    {"name": "Aaron Provincial Park", "park_id": "aaron", "region": "Eastern Ontario"},
    {"name": "Arrowhead Provincial Park", "park_id": "arrowhead", "region": "Central Ontario"},
    {"name": "Bass Lake Provincial Park", "park_id": "bass_lake", "region": "Northern Ontario"},
    {"name": "Blue Lake Provincial Park", "park_id": "blue_lake", "region": "Northwestern Ontario"},
    {"name": "Bonnechere Provincial Park", "park_id": "bonnechere", "region": "Eastern Ontario"},
    {"name": "Bronte Creek Provincial Park", "park_id": "bronte_creek", "region": "Central Ontario"},
    {"name": "Charleston Lake Provincial Park", "park_id": "charleston_lake", "region": "Eastern Ontario"},
    {"name": "Chutes Provincial Park", "park_id": "chutes", "region": "Northern Ontario"},
    {"name": "Craigleith Provincial Park", "park_id": "craigleith", "region": "Central Ontario"},
    {"name": "Darlington Provincial Park", "park_id": "darlington", "region": "Central Ontario"},
    {"name": "Emily Provincial Park", "park_id": "emily", "region": "Central Ontario"},
    {"name": "Esker Lakes Provincial Park", "park_id": "esker_lakes", "region": "Northern Ontario"},
    {"name": "Fairbank Provincial Park", "park_id": "fairbank", "region": "Central Ontario"},
    {"name": "Finlayson Point Provincial Park", "park_id": "finlayson_point", "region": "Northern Ontario"},
    {"name": "Fitzroy Provincial Park", "park_id": "fitzroy", "region": "Central Ontario"},
    {"name": "Frontenac Provincial Park", "park_id": "frontenac", "region": "Eastern Ontario"},
    {"name": "Halfway Lake Provincial Park", "park_id": "halfway_lake", "region": "Northern Ontario"},
    {"name": "Inverhuron Provincial Park", "park_id": "inverhuron", "region": "Southwestern Ontario"},
    {"name": "Kakabeka Falls Provincial Park", "park_id": "kakabeka_falls", "region": "Northwestern Ontario"},
    {"name": "Kettle Lakes Provincial Park", "park_id": "kettle_lakes", "region": "Central Ontario"},
    {"name": "Lake St. Peter Provincial Park", "park_id": "lake_st_peter", "region": "Eastern Ontario"},
    {"name": "Long Point Provincial Park", "park_id": "long_point", "region": "Southwestern Ontario"},
    {"name": "Marten River Provincial Park", "park_id": "marten_river", "region": "Northern Ontario"},
    {"name": "McRae Point Provincial Park", "park_id": "mcrae_point", "region": "Northern Ontario"},
    {"name": "Mikisew Provincial Park", "park_id": "mikisew", "region": "Northwestern Ontario"},
    {"name": "Mississagi Provincial Park", "park_id": "mississagi", "region": "Northern Ontario"},
    {"name": "Murphys Point Provincial Park", "park_id": "murphys_point", "region": "Eastern Ontario"},
    {"name": "Neys Provincial Park", "park_id": "neys", "region": "Northern Ontario"},
    {"name": "Oastler Lake Provincial Park", "park_id": "oastler_lake", "region": "Northern Ontario"},
    {"name": "Pancake Bay Provincial Park", "park_id": "pancake_bay", "region": "Northern Ontario"},
    {"name": "Point Farms Provincial Park", "park_id": "point_farms", "region": "Southwestern Ontario"},
    {"name": "Port Burwell Provincial Park", "park_id": "port_burwell", "region": "Southwestern Ontario"},
    {"name": "Rainbow Falls Provincial Park", "park_id": "rainbow_falls", "region": "Northern Ontario"},
    {"name": "Rene Brunelle Provincial Park", "park_id": "rene_brunelle", "region": "Northern Ontario"},
    {"name": "Restoule Provincial Park", "park_id": "restoule", "region": "Northern Ontario"},
    {"name": "Rideau River Provincial Park", "park_id": "rideau_river", "region": "Eastern Ontario"},
    {"name": "Rock Point Provincial Park", "park_id": "rock_point", "region": "Southwestern Ontario"},
    {"name": "Rondeau Provincial Park", "park_id": "rondeau", "region": "Southwestern Ontario"},
    {"name": "Rushing River Provincial Park", "park_id": "rushing_river", "region": "Northwestern Ontario"},
    {"name": "Samuel de Champlain Provincial Park", "park_id": "samuel_de_champlain", "region": "Northern Ontario"},
    {"name": "Sandbanks Provincial Park", "park_id": "sandbanks", "region": "Eastern Ontario"},
    {"name": "Sandbar Lake Provincial Park", "park_id": "sandbar_lake", "region": "Northwestern Ontario"},
    {"name": "Sauble Falls Provincial Park", "park_id": "sauble_falls", "region": "Southwestern Ontario"},
    {"name": "Selkirk Provincial Park", "park_id": "selkirk", "region": "Eastern Ontario"},
    {"name": "Sharbot Lake Provincial Park", "park_id": "sharbot_lake", "region": "Eastern Ontario"},
    {"name": "Sibbald Point Provincial Park", "park_id": "sibbald_point", "region": "Central Ontario"},
    {"name": "Silent Lake Provincial Park", "park_id": "silent_lake", "region": "Central Ontario"},
    {"name": "Silver Lake Provincial Park", "park_id": "silver_lake", "region": "Central Ontario"},
    {"name": "Sioux Narrows Provincial Park", "park_id": "sioux_narrows", "region": "Northwestern Ontario"},
    {"name": "Six Mile Lake Provincial Park", "park_id": "six_mile_lake", "region": "Central Ontario"},
    {"name": "Sleeping Giant Provincial Park", "park_id": "sleeping_giant", "region": "Northwestern Ontario"},
    {"name": "Turkey Point Provincial Park", "park_id": "turkey_point", "region": "Southwestern Ontario"},
    {"name": "Voyageur Provincial Park", "park_id": "voyageur", "region": "Northwestern Ontario"},
    {"name": "Wakami Lake Provincial Park", "park_id": "wakami_lake", "region": "Northern Ontario"},
    {"name": "Wheatley Provincial Park", "park_id": "wheatley", "region": "Southwestern Ontario"},
    {"name": "White Lake Provincial Park", "park_id": "white_lake", "region": "Southwestern Ontario"},
    {"name": "Windy Lake Provincial Park", "park_id": "windy_lake", "region": "Northern Ontario"},
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

        park_map_id = PARK_IDS[park_id]
        availability_results = []

        # Create session and prime it to bypass Azure WAF
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-CA,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        })

        # Prime session by loading main page (establishes WAF cookies)
        try:
            logger.debug(f"Priming session with main page...")
            session.get('https://reservations.ontarioparks.ca/', timeout=10)
            logger.debug(f"Session primed successfully")
        except Exception as e:
            logger.warning(f"Session priming failed: {e}, continuing anyway")

        # Query API for each day in the range
        current_date = check_in_date
        while current_date <= check_out_date:
            try:
                # Build API URL with query parameters
                api_url = (
                    f"https://reservations.ontarioparks.ca/api/availability/map?"
                    f"mapId={park_map_id}&"
                    f"startDate={current_date.strftime('%Y-%m-%d')}&"
                    f"endDate={current_date.strftime('%Y-%m-%d')}&"
                    f"bookingCategoryId=0&"
                    f"equipmentCategoryId=-32768&"
                    f"boatLength=0&boatDraft=0&boatWidth=0"
                )

                logger.debug(f"Querying API for {park_id} on {current_date}")

                response = session.get(api_url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"API response received for {current_date}")

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

                    logger.info(f"Found {len([a for a in availability_results if a['date'] == current_date and a['available']])} available sites on {current_date}")
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
