import os
import requests
from datetime import datetime, timedelta
from utils.location_to_coordinates import LocationToCoordinates

class WeatherFetcher:
    BASE_URL = "https://api.openweathermap.org/data/2.5/"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key not set. Set OPENWEATHER_API_KEY in your environment or pass as argument.")
        self.location_converter = LocationToCoordinates()

    def fetch_weather(self, location_name, location_type, time_periods=None):
        # Get coordinates for the location
        loc_info = self.location_converter.get_coordinates(location_name, location_type)
        if "center" not in loc_info:
            return {"error": f"Could not get coordinates for {location_name}"}
        lat, lon = loc_info["center"]
        # Determine if forecast or current weather is needed
        forecast_days = self._parse_time_periods(time_periods)
        if forecast_days > 1:
            return self._fetch_forecast(lat, lon, forecast_days)
        else:
            return self._fetch_current(lat, lon)

    def _fetch_current(self, lat, lon):
        url = f"{self.BASE_URL}weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            return {"error": f"OpenWeatherMap API error: {resp.status_code}"}
        data = resp.json()
        return {
            "type": "current",
            "location": data.get("name"),
            "weather": data["weather"][0]["description"].capitalize() if data.get("weather") else None,
            "temperature": data["main"]["temp"] if "main" in data else None,
            "humidity": data["main"].get("humidity") if "main" in data else None,
            "wind_speed": data["wind"].get("speed") if "wind" in data else None,
            "time": datetime.utcfromtimestamp(data["dt"]).strftime('%Y-%m-%d %H:%M UTC') if "dt" in data else None
        }

    def _fetch_forecast(self, lat, lon, days):
        url = f"{self.BASE_URL}forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            return {"error": f"OpenWeatherMap API error: {resp.status_code}"}
        data = resp.json()
        # Group forecast by day
        forecast = {}
        for entry in data.get("list", []):
            dt = datetime.utcfromtimestamp(entry["dt"])
            day = dt.date()
            if day not in forecast:
                forecast[day] = []
            forecast[day].append(entry)
        # Summarize each day
        results = []
        today = datetime.utcnow().date()
        for i in range(days):
            day = today + timedelta(days=i)
            if day not in forecast:
                continue
            day_entries = forecast[day]
            temps = [e["main"]["temp"] for e in day_entries if "main" in e]
            weather_descs = [e["weather"][0]["description"] for e in day_entries if e.get("weather")]
            humidity = [e["main"].get("humidity") for e in day_entries if "main" in e]
            wind = [e["wind"].get("speed") for e in day_entries if "wind" in e]
            results.append({
                "date": str(day),
                "weather": max(set(weather_descs), key=weather_descs.count) if weather_descs else None,
                "temperature_min": min(temps) if temps else None,
                "temperature_max": max(temps) if temps else None,
                "humidity_avg": sum(humidity)/len(humidity) if humidity else None,
                "wind_speed_avg": sum(wind)/len(wind) if wind else None
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
                    return min(n, 5)  # OpenWeatherMap free API supports up to 5 days forecast
                except Exception:
                    pass
            elif "tomorrow" in period:
                return 2
        return 1 