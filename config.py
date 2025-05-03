import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
USGS_API_BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
WEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Query Types
QUERY_TYPES = {
    "SAFETY_GUIDELINES": "safety_guidelines",
    "HISTORICAL_INFO": "historical_info",
    "FUTURE_ALERTS": "future_alerts"
}

# Location Types
LOCATION_TYPES = {
    "CITY": "city",
    "STATE": "state",
    "COUNTRY": "country"
}

# Time Period Keywords
TIME_PERIODS = {
    "DAYS": ["day", "days"],
    "WEEKS": ["week", "weeks"],
    "MONTHS": ["month", "months"]
}

# Disaster Types
DISASTER_TYPES = {
    "EARTHQUAKE": "earthquake",
    "WEATHER": "weather"
} 