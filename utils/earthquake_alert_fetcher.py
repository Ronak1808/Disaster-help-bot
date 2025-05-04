import requests
from datetime import datetime, timedelta
from shapely.geometry import Point, shape
from utils.country_boundaries import CountryBoundaries
from utils.location_to_coordinates import LocationToCoordinates
import difflib

class EarthquakeAlertFetcher:
    USGS_API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    def __init__(self):
        self.country_boundaries = CountryBoundaries()
        self.location_converter = LocationToCoordinates()

    def fetch_alerts(self, location_name, location_type, time_periods=None, top_n=5):
        # --- Country-level (existing logic) ---
        if location_type == 'country':
            bbox = self.country_boundaries.get_bounding_box(location_name)
            polygon = shape(self.country_boundaries.get_country_info(location_name)['geometry'])
            if not bbox or not polygon:
                return {"error": f"Could not get boundary for {location_name}"}
            starttime, endtime = self._parse_time_periods(time_periods)
            params = {
                'format': 'geojson',
                'minlatitude': bbox['min_lat'],
                'maxlatitude': bbox['max_lat'],
                'minlongitude': bbox['min_lon'],
                'maxlongitude': bbox['max_lon'],
                'starttime': starttime.strftime('%Y-%m-%d'),
                'endtime': endtime.strftime('%Y-%m-%d'),
                'orderby': 'magnitude',
                'limit': 100
            }
            response = requests.get(self.USGS_API_URL, params=params)
            if response.status_code != 200:
                return {"error": f"USGS API error: {response.status_code}"}
            data = response.json()
            events = data.get('features', [])
            filtered = []
            for event in events:
                coords = event['geometry']['coordinates']
                lon, lat = coords[0], coords[1]
                if polygon.contains(Point(lon, lat)):
                    filtered.append(event)
            return self._format_results(filtered, top_n, location_name)
        # --- City-level (new logic) ---
        elif location_type == 'city':
            city_info = self.location_converter.get_coordinates(location_name, 'city')
            if 'center' not in city_info:
                return {"error": f"Could not get coordinates for city: {location_name}"}
            lat, lon = city_info['center']
            starttime, endtime = self._parse_time_periods(time_periods)
            params = {
                'format': 'geojson',
                'latitude': lat,
                'longitude': lon,
                'maxradiuskm': 100,  # 100 km radius
                'starttime': starttime.strftime('%Y-%m-%d'),
                'endtime': endtime.strftime('%Y-%m-%d'),
                'orderby': 'magnitude',
                'limit': 100
            }
            response = requests.get(self.USGS_API_URL, params=params)
            if response.status_code != 200:
                return {"error": f"USGS API error: {response.status_code}"}
            data = response.json()
            events = data.get('features', [])
            # Optionally, filter by city buffer polygon
            if 'geometry' in city_info:
                city_poly = shape(city_info['geometry'])
                filtered = [e for e in events if city_poly.contains(Point(e['geometry']['coordinates'][0], e['geometry']['coordinates'][1]))]
            else:
                filtered = events
            return self._format_results(filtered, top_n, location_name)
        # --- State-level (new logic) ---
        elif location_type == 'state':
            state_info = self.location_converter.get_coordinates(location_name, 'state')
            if 'geometry' not in state_info:
                return {"error": f"Could not get geometry for state: {location_name}"}
            # Use bounding box for API
            coords = state_info['geometry']['coordinates'][0]
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            min_lon, max_lon = min(lons), max(lons)
            min_lat, max_lat = min(lats), max(lats)
            starttime, endtime = self._parse_time_periods(time_periods)
            params = {
                'format': 'geojson',
                'minlatitude': min_lat,
                'maxlatitude': max_lat,
                'minlongitude': min_lon,
                'maxlongitude': max_lon,
                'starttime': starttime.strftime('%Y-%m-%d'),
                'endtime': endtime.strftime('%Y-%m-%d'),
                'orderby': 'magnitude',
                'limit': 100
            }
            response = requests.get(self.USGS_API_URL, params=params)
            if response.status_code != 200:
                return {"error": f"USGS API error: {response.status_code}"}
            data = response.json()
            events = data.get('features', [])
            # Filter by state polygon
            state_poly = shape(state_info['geometry'])
            filtered = [e for e in events if state_poly.contains(Point(e['geometry']['coordinates'][0], e['geometry']['coordinates'][1]))]
            return self._format_results(filtered, top_n, location_name)
        else:
            return {"error": f"Unsupported location type: {location_type}"}

    def _format_results(self, events, top_n, location_name):
        # 5. Sort and select top N
        events.sort(key=lambda e: e['properties'].get('mag', 0), reverse=True)
        top_events = events[:top_n]
        # 6. Format results
        results = []
        for event in top_events:
            prop = event['properties']
            coords = event['geometry']['coordinates']
            results.append({
                'magnitude': prop.get('mag'),
                'place': prop.get('place'),
                'time': datetime.utcfromtimestamp(prop.get('time')/1000).strftime('%Y-%m-%d %H:%M UTC'),
                'depth': coords[2],
                'url': prop.get('url'),
            })
        return results

    def _parse_time_periods(self, time_periods):
        now = datetime.utcnow()
        # Default: next 7 days
        start = now
        end = now + timedelta(days=7)
        if time_periods:
            for period in time_periods:
                # Example: 'next 10 days'
                if 'next' in period and 'day' in period:
                    try:
                        n = int([s for s in period.split() if s.isdigit()][0])
                        end = now + timedelta(days=n)
                    except Exception:
                        pass
                # Example: 'from 2024-05-01 to 2024-05-10'
                elif 'from' in period and 'to' in period:
                    try:
                        parts = period.replace('from', '').replace('to', '').split()
                        start = datetime.strptime(parts[0], '%Y-%m-%d')
                        end = datetime.strptime(parts[1], '%Y-%m-%d')
                    except Exception:
                        pass
        return start, end

    def _normalize_country_name(self, name: str) -> str:
        name_lower = name.strip().lower()
        if name_lower in self.country_boundaries.aliases:
            return self.country_boundaries.aliases[name_lower]
        # Try direct match
        if name in self.country_boundaries.boundaries:
            return name
        # Try fuzzy match (case-insensitive, lower cutoff)
        all_names = list(self.country_boundaries.boundaries.keys())
        best = difflib.get_close_matches(name, all_names, n=1, cutoff=0.7)
        if best:
            return best[0]
        best = difflib.get_close_matches(name_lower, [n.lower() for n in all_names], n=1, cutoff=0.7)
        if best:
            idx = [n.lower() for n in all_names].index(best[0])
            return all_names[idx]
        return name 