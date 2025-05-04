import requests
import feedparser
from datetime import datetime, timedelta
from utils.country_boundaries import CountryBoundaries
from utils.location_to_coordinates import LocationToCoordinates
from shapely.geometry import Point, shape

class FloodAlertFetcher:
    GDACS_RSS_URL = "https://www.gdacs.org/xml/rss_flood.xml"

    def __init__(self):
        self.country_boundaries = CountryBoundaries()
        self.location_converter = LocationToCoordinates()

    def fetch_alerts(self, location_name, location_type, time_periods=None, top_n=5):
        # Get polygon for filtering
        if location_type == 'country':
            region_info = self.country_boundaries.get_country_info(location_name)
            if not region_info:
                return {"error": f"Could not get boundary for {location_name}"}
            region_poly = shape(region_info['geometry'])
            region_name = region_info['name']
            region_iso = region_info.get('iso', '').lower()
        elif location_type in ('state', 'city'):
            region_info = self.location_converter.get_coordinates(location_name, location_type)
            if 'geometry' not in region_info:
                return {"error": f"Could not get geometry for {location_name}"}
            region_poly = shape(region_info['geometry'])
            region_name = region_info['name']
            region_iso = ''
        else:
            return {"error": f"Unsupported location type: {location_type}"}
        # Parse time period (default: next 7 days)
        starttime, endtime = self._parse_time_periods(time_periods)
        # Fetch GDACS RSS feed using feedparser
        feed = feedparser.parse(self.GDACS_RSS_URL)
        results = []
        for entry in feed.entries:
            title = entry.get('title', '')
            link = entry.get('link', '')
            pub_date = entry.get('published', '')
            description = entry.get('description', '')
            # Try to extract coordinates
            lat = entry.get('geo_lat') or entry.get('lat') or None
            lon = entry.get('geo_long') or entry.get('long') or None
            # Parse date
            try:
                alert_time = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
            except Exception:
                alert_time = None
            # Filter by time
            if alert_time and (alert_time < starttime or alert_time > endtime):
                continue
            # Coordinate-based filtering
            in_region = False
            if lat and lon:
                try:
                    point = Point(float(lon), float(lat))
                    if region_poly.contains(point):
                        in_region = True
                except Exception:
                    pass
            # Fallback: text-based filtering
            if not in_region:
                if region_name.lower() in title.lower() or region_name.lower() in description.lower():
                    in_region = True
                elif region_iso and (region_iso in title.lower() or region_iso in description.lower()):
                    in_region = True
            if not in_region:
                continue
            # Add to results
            results.append({
                'title': title,
                'link': link,
                'date': pub_date,
                'description': description
            })
        # Sort by date (most recent first)
        results.sort(key=lambda x: x['date'], reverse=True)
        return results[:top_n]

    def _parse_time_periods(self, time_periods):
        now = datetime.utcnow()
        # Default: next 7 days
        start = now
        end = now + timedelta(days=7)
        if time_periods:
            for period in time_periods:
                if 'next' in period and 'day' in period:
                    try:
                        n = int([s for s in period.split() if s.isdigit()][0])
                        end = now + timedelta(days=n)
                    except Exception:
                        pass
                elif 'from' in period and 'to' in period:
                    try:
                        parts = period.replace('from', '').replace('to', '').split()
                        start = datetime.strptime(parts[0], '%Y-%m-%d')
                        end = datetime.strptime(parts[1], '%Y-%m-%d')
                    except Exception:
                        pass
        return start, end 