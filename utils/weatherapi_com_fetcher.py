import requests
from datetime import datetime, timedelta
from utils.location_to_coordinates import LocationToCoordinates

class WeatherAPIComFetcher:
    BASE_URL = "http://api.weatherapi.com/v1/"

    def __init__(self, api_key="b19c72b3c4224147b2c90511250405"):
        self.api_key = api_key
        self.location_converter = LocationToCoordinates()

    def fetch_weather(self, location_name, location_type, time_periods=None):
        # Get coordinates for the location
        loc_info = self.location_converter.get_coordinates(location_name, location_type)
        if "center" not in loc_info:
            return {"error": f"Could not get coordinates for {location_name}"}
        lat, lon = loc_info["center"]
        forecast_days = self._parse_time_periods(time_periods)
        if forecast_days > 1:
            return self._fetch_forecast(lat, lon, forecast_days)
        else:
            return self._fetch_current(lat, lon)

    def _fetch_current(self, lat, lon):
        url = f"{self.BASE_URL}current.json"
        params = {
            "key": self.api_key,
            "q": f"{lat},{lon}"
        }
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            return {"error": f"WeatherAPI.com error: {resp.status_code}"}
        data = resp.json()
        current = data.get("current", {})
        location = data.get("location", {})
        return {
            "type": "current",
            "location": location.get("name"),
            "weather": current.get("condition", {}).get("text"),
            "temperature": current.get("temp_c"),
            "humidity": current.get("humidity"),
            "wind_speed": current.get("wind_kph", 0) / 3.6,  # convert kph to m/s
            "time": location.get("localtime") + " (local time)" if location.get("localtime") else None
        }

    def _fetch_forecast(self, lat, lon, days):
        url = f"{self.BASE_URL}forecast.json"
        params = {
            "key": self.api_key,
            "q": f"{lat},{lon}",
            "days": min(days, 10)  # WeatherAPI.com free tier supports up to 10 days
        }
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            return {"error": f"WeatherAPI.com error: {resp.status_code}"}
        data = resp.json()
        forecast_days = data.get("forecast", {}).get("forecastday", [])
        results = []
        for day in forecast_days:
            day_info = day.get("day", {})
            results.append({
                "date": day.get("date"),
                "weather": day_info.get("condition", {}).get("text"),
                "temperature_min": day_info.get("mintemp_c"),
                "temperature_max": day_info.get("maxtemp_c"),
                "humidity_avg": day_info.get("avghumidity"),
                "wind_speed_avg": day_info.get("maxwind_kph", 0) / 3.6  # convert kph to m/s
            })
        return {"type": "forecast", "days": results}

    def _parse_time_periods(self, time_periods):
        # Default: 1 (current)
        if not time_periods:
            return 1
        for period in time_periods:
            if "next" in period and "day" in period:
                try:
                    n = int([s for s in period.split() if s.isdigit()][0])
                    return min(n, 10)  # WeatherAPI.com free supports up to 10 days
                except Exception:
                    pass
            elif "tomorrow" in period:
                return 2
        return 1 