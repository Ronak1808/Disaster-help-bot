from typing import Dict, Union
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import logging
from config import LOCATION_TYPES
from .country_boundaries import CountryBoundaries
from shapely.geometry import Point, box

class LocationToCoordinates:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="disaster_assistant")
        self.cache = {}  # Simple in-memory cache
        self.logger = logging.getLogger(__name__)
        self.country_boundaries = CountryBoundaries()

    def get_coordinates(self, location: str, location_type: str) -> Dict:
        """Get coordinates for a location based on its type"""
        # Check cache first
        cache_key = f"{location}_{location_type}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            if location_type == LOCATION_TYPES["COUNTRY"]:
                result = self._get_country_coordinates(location)
            elif location_type == LOCATION_TYPES["STATE"]:
                result = self._get_state_coordinates(location)
            else:  # CITY
                result = self._get_city_coordinates(location)
            
            # Cache the result
            self.cache[cache_key] = result
            return result

        except Exception as e:
            self.logger.error(f"Error getting coordinates for {location}: {str(e)}")
            return {
                "error": f"Could not get coordinates for {location}",
                "location": location,
                "type": location_type
            }

    def _get_country_coordinates(self, country: str) -> Dict:
        """Get geometry for a country"""
        country_info = self.country_boundaries.get_country_info(country)
        if country_info:
            return {
                "type": "country",
                "name": country,
                "geometry": country_info["geometry"],
                "risk_zones": country_info.get("risk_zones", {}),
                "center": self.country_boundaries.get_approximate_center(country)
            }
        
        return {
            "error": f"Could not find coordinates for country: {country}",
            "location": country,
            "type": "country"
        }

    def _get_state_coordinates(self, state: str) -> Dict:
        """Get coordinates for a state/region with polygon boundary"""
        try:
            # Use Nominatim to get state boundary
            location = self.geolocator.geocode(state, exactly_one=True)
            if location:
                # Create a buffer around the point (approximately 50km)
                center_point = Point(location.longitude, location.latitude)
                buffer_degrees = 0.5  # roughly 50km at equator
                buffer_box = box(
                    location.longitude - buffer_degrees,
                    location.latitude - buffer_degrees,
                    location.longitude + buffer_degrees,
                    location.latitude + buffer_degrees
                )
                
                return {
                    "type": "state",
                    "name": state,
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [list(buffer_box.exterior.coords)]
                    },
                    "center": (location.latitude, location.longitude)
                }
        except GeocoderTimedOut:
            time.sleep(1)
            return self._get_state_coordinates(state)
        
        return {
            "error": f"Could not find coordinates for state: {state}",
            "location": state,
            "type": "state"
        }

    def _get_city_coordinates(self, city: str) -> Dict:
        """Get coordinates for a city with circular buffer zone"""
        try:
            # Add country name to improve accuracy
            location = self.geolocator.geocode(f"{city}, India", exactly_one=True)
            if location:
                # Create a circular buffer (approximately 10km)
                center_point = Point(location.longitude, location.latitude)
                buffer_degrees = 0.1  # roughly 10km at equator
                # Increase resolution of the buffer
                buffer_circle = center_point.buffer(buffer_degrees, resolution=32)  # 32 segments for smoother circle
                
                # Verify the coordinates are in India
                if not self.country_boundaries.is_point_in_country("India", location.latitude, location.longitude):
                    self.logger.warning(f"City {city} coordinates appear to be outside India")
                
                return {
                    "type": "city",
                    "name": city,
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [list(buffer_circle.exterior.coords)]
                    },
                    "center": (location.latitude, location.longitude),
                    "raw_location": {
                        "address": location.address,
                        "latitude": location.latitude,
                        "longitude": location.longitude
                    }
                }
        except GeocoderTimedOut:
            time.sleep(1)
            return self._get_city_coordinates(city)
        
        return {
            "error": f"Could not find coordinates for city: {city}",
            "location": city,
            "type": "city"
        }

    def is_point_in_location(self, lat: float, lon: float, location: str, location_type: str) -> bool:
        """Check if a point is within the location boundaries"""
        if location_type == LOCATION_TYPES["COUNTRY"]:
            return self.country_boundaries.is_point_in_country(location, lat, lon)
        
        # For states and cities, get the location info and check if point is in geometry
        location_info = self.get_coordinates(location, location_type)
        if "error" not in location_info and "geometry" in location_info:
            point = Point(lon, lat)
            from shapely.geometry import shape
            location_shape = shape(location_info["geometry"])
            return location_shape.contains(point)
        
        return False 