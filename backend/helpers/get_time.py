from datetime import datetime

import pycountry
import pytz


def get_time_by_country(country: str):
    try:
        country_code = pycountry.countries.search_fuzzy(country)[0].alpha_2
        tz_name = pytz.country_timezones.get(country_code.upper())[0]
        tz = pytz.timezone(tz_name)
        current_time = datetime.now(tz)
        return current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    except (KeyError, TypeError, IndexError):
        return "error: unknown country"
