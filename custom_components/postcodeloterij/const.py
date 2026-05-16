"""Constants for the Postcodeloterij integration."""
from homeassistant.const import Platform

DOMAIN = "postcodeloterij"
PLATFORMS = [Platform.SENSOR]

CONF_POSTCODE = "postcode"

API_URL = "https://www.postcodeloterij.nl/public/rest/drawresults/winnings/NPL/P_MT_P{}/?resultSize=10"
API_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/112.0.0.0 Safari/537.36"
    )
}

POLL_INTERVAL = 43200  # 12 hours in seconds
