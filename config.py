"""
Global Space OSINT Operating Centre — Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
N2YO_API_KEY = os.getenv("N2YO_API_KEY", "")

# Server
HOST = "0.0.0.0"
PORT = 8900

# Cache TTLs (seconds)
CACHE_TTL_SATELLITES = 30
CACHE_TTL_TLE_CATALOG = 14400      # 4 hours
CACHE_TTL_LAUNCHES = 300            # 5 minutes
CACHE_TTL_WEATHER = 60              # 1 minute
CACHE_TTL_KP = 900                  # 15 minutes
CACHE_TTL_NEO = 21600               # 6 hours
CACHE_TTL_NEWS = 600                # 10 minutes
CACHE_TTL_ASTRONAUTS = 3600         # 1 hour
CACHE_TTL_DONKI = 3600              # 1 hour

# Satellite groups to fetch from CelesTrak
SAT_GROUPS = ["stations", "active"]

# Notable satellites to always show (NORAD IDs)
NOTABLE_SATS = {
    25544: "ISS (ZARYA)",
    48274: "CSS (TIANHE)",
    20580: "HUBBLE",
    43013: "NOAA-20",
    27424: "XMM-NEWTON",
    36516: "SDO",
}
