from utils.location_extractor import LocationExtractor
from utils.time_period_extractor import TimePeriodExtractor

class WeatherIntentParser:
    def __init__(self):
        self.location_extractor = LocationExtractor()
        self.time_period_extractor = TimePeriodExtractor()

    def parse(self, query):
        # Extract location
        locations = self.location_extractor.extract_location(query)
        location_name = None
        location_type = None
        if locations:
            location_name = locations[0]["text"]
            location_type = locations[0]["type"]
        # Extract time period
        time_periods = self.time_period_extractor.extract_time_period(query)
        # Determine weather type (current or forecast)
        query_lower = query.lower()
        if any(word in query_lower for word in ["tomorrow", "next", "forecast", "coming days", "in "]):
            weather_type = "forecast"
        else:
            weather_type = "current"
        # If time_periods mention more than today, treat as forecast
        for period in time_periods:
            if any(word in period for word in ["next", "tomorrow", "days", "weeks", "months"]):
                weather_type = "forecast"
        return {
            "location_name": location_name,
            "location_type": location_type,
            "time_periods": time_periods,
            "weather_type": weather_type
        } 