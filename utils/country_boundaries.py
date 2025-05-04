import json
import os
from typing import Dict, List, Union
from shapely.geometry import Point, Polygon, MultiPolygon, shape
from shapely.ops import unary_union
import requests
import logging
import geopandas as gpd
from pathlib import Path
import difflib

class CountryBoundaries:
    def __init__(self):
        self.boundaries_file = "data/country_boundaries.json"
        self.logger = logging.getLogger(__name__)
        self.boundaries = self._load_boundaries()
        self._geometry_cache = {}  # Cache for parsed geometries
        
        # Download Natural Earth Data if not exists
        self.natural_earth_file = "data/ne_110m_admin_0_countries.geojson"
        self._ensure_natural_earth_data()
        
        # Add example risk zones for India
        self._add_example_risk_zones()

    def _add_example_risk_zones(self):
        """Add example risk zones for India"""
        india_data = self.get_country_info("India")
        if india_data and "risk_zones" not in india_data:
            india_data["risk_zones"] = {
                "earthquake": [
                    {
                        "name": "Himalayan Region",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [75.0, 30.0], [80.0, 30.0],
                                [80.0, 35.0], [75.0, 35.0],
                                [75.0, 30.0]
                            ]]
                        }
                    },
                    {
                        "name": "Western Coast",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [72.0, 15.0], [75.0, 15.0],
                                [75.0, 20.0], [72.0, 20.0],
                                [72.0, 15.0]
                            ]]
                        }
                    }
                ],
                "flood": [
                    {
                        "name": "Ganges Basin",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [80.0, 20.0], [85.0, 20.0],
                                [85.0, 25.0], [80.0, 25.0],
                                [80.0, 20.0]
                            ]]
                        }
                    },
                    {
                        "name": "Brahmaputra Basin",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [90.0, 25.0], [95.0, 25.0],
                                [95.0, 30.0], [90.0, 30.0],
                                [90.0, 25.0]
                            ]]
                        }
                    }
                ],
                "cyclone": [
                    {
                        "name": "Eastern Coast",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [80.0, 10.0], [85.0, 10.0],
                                [85.0, 15.0], [80.0, 15.0],
                                [80.0, 10.0]
                            ]]
                        }
                    },
                    {
                        "name": "Western Coast",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [72.0, 15.0], [75.0, 15.0],
                                [75.0, 20.0], [72.0, 20.0],
                                [72.0, 15.0]
                            ]]
                        }
                    }
                ]
            }
            self._save_boundaries()

    def _ensure_natural_earth_data(self):
        """Download Natural Earth Data if not exists"""
        if not os.path.exists(self.natural_earth_file):
            os.makedirs(os.path.dirname(self.natural_earth_file), exist_ok=True)
            url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(self.natural_earth_file, 'w') as f:
                    f.write(response.text)
                self.logger.info(f"Downloaded Natural Earth Data to {self.natural_earth_file}")
            except Exception as e:
                self.logger.error(f"Error downloading Natural Earth Data: {str(e)}")
                # Create a minimal dataset with just India for testing
                minimal_data = {
                    "type": "FeatureCollection",
                    "features": [{
                        "type": "Feature",
                        "properties": {"NAME": "India", "ISO_A2": "IN"},
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[[68.1766451354, 7.96553477623], [97.34882107351, 7.96553477623], 
                                          [97.34882107351, 35.4940095078], [68.1766451354, 35.4940095078], 
                                          [68.1766451354, 7.96553477623]]]
                        }
                    }]
                }
                with open(self.natural_earth_file, 'w') as f:
                    json.dump(minimal_data, f)

    def _load_boundaries(self) -> Dict:
        """Load country boundaries from file or create empty if not exists"""
        if not os.path.exists(self.boundaries_file):
            os.makedirs(os.path.dirname(self.boundaries_file), exist_ok=True)
            with open(self.boundaries_file, 'w') as f:
                json.dump({}, f, indent=2)
            return {}
        
        with open(self.boundaries_file, 'r') as f:
            return json.load(f)

    def _get_country_from_natural_earth(self, country_name: str) -> Dict:
        """Get country geometry from Natural Earth Data"""
        try:
            # Read GeoJSON file
            with open(self.natural_earth_file, 'r') as f:
                data = json.load(f)
            
            # Find matching country
            for feature in data['features']:
                if feature['properties']['NAME'].lower() == country_name.lower():
                    return {
                        "type": "country",
                        "name": feature['properties']['NAME'],
                        "geometry": feature['geometry'],
                        "iso": feature['properties'].get('ISO_A2', ''),
                        "risk_zones": {}
                    }
        except Exception as e:
            self.logger.error(f"Error reading Natural Earth Data: {str(e)}")
        return None

    def _get_shapely_geometry(self, country_name: str) -> Union[Polygon, MultiPolygon, None]:
        """Convert GeoJSON geometry to Shapely geometry"""
        if country_name in self._geometry_cache:
            return self._geometry_cache[country_name]

        country_data = self.get_country_info(country_name)
        if not country_data or 'geometry' not in country_data:
            return None

        try:
            geometry = shape(country_data['geometry'])
            self._geometry_cache[country_name] = geometry
            return geometry
        except Exception as e:
            self.logger.error(f"Error converting geometry: {str(e)}")
            return None

    def _save_boundaries(self):
        """Save boundaries to file"""
        with open(self.boundaries_file, 'w') as f:
            json.dump(self.boundaries, f, indent=2)

    def is_point_in_country(self, country_name: str, lat: float, lon: float) -> bool:
        """Check if a point is within country boundaries"""
        geometry = self._get_shapely_geometry(country_name)
        if not geometry:
            return False
        
        point = Point(lon, lat)
        return geometry.contains(point)

    def _normalize_country_name(self, name: str) -> str:
        """Normalize country names using a lookup table and fuzzy matching."""
        # Common aliases and alternative names
        aliases = {
            'usa': 'United States of America',
            'us': 'United States of America',
            'united states': 'United States of America',
            'uk': 'United Kingdom',
            'england': 'United Kingdom',
            'russia': 'Russian Federation',
            'south korea': 'Korea, Republic of',
            'north korea': "Korea, Democratic People's Republic of",
            'iran': 'Iran (Islamic Republic of)',
            'vietnam': 'Viet Nam',
            'laos': "Lao People's Democratic Republic",
            'czech republic': 'Czechia',
            'ivory coast': "Côte d'Ivoire",
            'brunei': 'Brunei Darussalam',
            'syria': 'Syrian Arab Republic',
            'moldova': 'Moldova, Republic of',
            'venezuela': 'Venezuela (Bolivarian Republic of)',
            'tanzania': 'Tanzania, United Republic of',
            'bolivia': 'Bolivia (Plurinational State of)',
            'palestine': 'Palestine, State of',
            'macedonia': 'North Macedonia',
            'myanmar': 'Myanmar',
            'burma': 'Myanmar',
            'cape verde': 'Cabo Verde',
            'swaziland': 'Eswatini',
            'east timor': 'Timor-Leste',
            'slovak republic': 'Slovakia',
            'republic of the congo': 'Congo',
            'democratic republic of the congo': 'Congo, Democratic Republic of the',
        }
        name_lower = name.strip().lower()
        if name_lower in aliases:
            return aliases[name_lower]
        # Try direct match
        if name in self.boundaries:
            return name
        # Try fuzzy match
        all_names = list(self.boundaries.keys())
        best = difflib.get_close_matches(name, all_names, n=1, cutoff=0.8)
        if best:
            return best[0]
        # Try fuzzy match on lowercased
        best = difflib.get_close_matches(name_lower, [n.lower() for n in all_names], n=1, cutoff=0.8)
        if best:
            idx = [n.lower() for n in all_names].index(best[0])
            return all_names[idx]
        return name

    def get_country_info(self, country_name: str) -> Dict:
        norm_name = self._normalize_country_name(country_name)
        if norm_name in self.boundaries:
            return self.boundaries[norm_name]
        # Try to get from Natural Earth Data
        country_data = self._get_country_from_natural_earth(norm_name)
        if country_data:
            self.boundaries[norm_name] = country_data
            self._save_boundaries()
            return country_data
        return None

    def get_approximate_center(self, country_name: str) -> Union[tuple, None]:
        """Get the centroid of the country"""
        geometry = self._get_shapely_geometry(country_name)
        if geometry:
            centroid = geometry.centroid
            return (centroid.y, centroid.x)  # Return as (lat, lon)
        return None

    def get_risk_zones(self, country_name: str, disaster_type: str) -> List[Dict]:
        """Get risk zones for a specific disaster type in a country"""
        country_data = self.get_country_info(country_name)
        if country_data and "risk_zones" in country_data:
            return country_data["risk_zones"].get(disaster_type, [])
        return []

    def add_risk_zone(self, country_name: str, disaster_type: str, zone_name: str, 
                     coordinates: List[List[float]]) -> bool:
        """Add a risk zone for a specific disaster type"""
        country_data = self.get_country_info(country_name)
        if not country_data:
            return False
            
        if "risk_zones" not in country_data:
            country_data["risk_zones"] = {}
            
        if disaster_type not in country_data["risk_zones"]:
            country_data["risk_zones"][disaster_type] = []
            
        zone = {
            "name": zone_name,
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
            }
        }
        
        country_data["risk_zones"][disaster_type].append(zone)
        self._save_boundaries()
        return True

    def get_bounding_box(self, country_name: str):
        norm_name = self._normalize_country_name(country_name)
        country_info = self.get_country_info(norm_name)
        if not country_info or 'geometry' not in country_info:
            return None
        from shapely.geometry import shape
        polygon = shape(country_info['geometry'])
        min_lon, min_lat, max_lon, max_lat = polygon.bounds
        return {
            'min_lon': min_lon,
            'min_lat': min_lat,
            'max_lon': max_lon,
            'max_lat': max_lat
        } 