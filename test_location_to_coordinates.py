import unittest
import os
import json
from utils.location_to_coordinates import LocationToCoordinates
from utils.country_boundaries import CountryBoundaries
from config import LOCATION_TYPES

class TestLocationToCoordinates(unittest.TestCase):
    def setUp(self):
        self.converter = LocationToCoordinates()
        self.country_boundaries = CountryBoundaries()
        
        # Clean up any existing test files
        if os.path.exists("data/country_boundaries.json"):
            os.remove("data/country_boundaries.json")

    def test_country_coordinates(self):
        # Test with known country
        result = self.converter.get_coordinates("India", LOCATION_TYPES["COUNTRY"])
        self.assertEqual(result["type"], "country")
        self.assertEqual(result["name"], "India")
        self.assertIn("geometry", result)
        self.assertIn("risk_zones", result)
        self.assertIn("center", result)
        
        # Test point in country
        center = result["center"]
        self.assertTrue(
            self.converter.is_point_in_location(
                center[0], center[1], "India", LOCATION_TYPES["COUNTRY"]
            )
        )
        
        # Test with unknown country
        result = self.converter.get_coordinates("UnknownCountry", LOCATION_TYPES["COUNTRY"])
        self.assertIn("error", result)

    def test_state_coordinates(self):
        # Test with known state
        result = self.converter.get_coordinates("California", LOCATION_TYPES["STATE"])
        self.assertEqual(result["type"], "state")
        self.assertEqual(result["name"], "California")
        self.assertIn("geometry", result)
        self.assertIn("center", result)
        
        # Test point in state
        center = result["center"]
        self.assertTrue(
            self.converter.is_point_in_location(
                center[0], center[1], "California", LOCATION_TYPES["STATE"]
            )
        )
        
        # Test with unknown state
        result = self.converter.get_coordinates("UnknownState", LOCATION_TYPES["STATE"])
        self.assertIn("error", result)

    def test_city_coordinates(self):
        # Test with known city
        result = self.converter.get_coordinates("Mumbai", LOCATION_TYPES["CITY"])
        self.assertEqual(result["type"], "city")
        self.assertEqual(result["name"], "Mumbai")
        self.assertIn("geometry", result)
        self.assertIn("center", result)
        
        # Test point in city
        center = result["center"]
        self.assertTrue(
            self.converter.is_point_in_location(
                center[0], center[1], "Mumbai", LOCATION_TYPES["CITY"]
            )
        )
        
        # Test with unknown city
        result = self.converter.get_coordinates("UnknownCity", LOCATION_TYPES["CITY"])
        self.assertIn("error", result)

    def test_cache(self):
        # First call should hit the API
        result1 = self.converter.get_coordinates("Delhi", LOCATION_TYPES["CITY"])
        self.assertIn("geometry", result1)
        
        # Second call should use cache
        result2 = self.converter.get_coordinates("Delhi", LOCATION_TYPES["CITY"])
        self.assertEqual(result1, result2)

    def test_point_in_location(self):
        # Test point in India
        self.assertTrue(
            self.converter.is_point_in_location(
                20.5937, 78.9629, "India", LOCATION_TYPES["COUNTRY"]
            )
        )
        
        # Test point outside India
        self.assertFalse(
            self.converter.is_point_in_location(
                35.8617, 104.1954, "India", LOCATION_TYPES["COUNTRY"]  # Point in China
            )
        )

    def test_country_boundaries(self):
        # Test country info retrieval
        info = self.country_boundaries.get_country_info("India")
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "India")
        self.assertIn("geometry", info)
        self.assertIn("risk_zones", info)
        self.assertIn("iso", info)
        
        # Test bounds retrieval
        geometry = self.country_boundaries._get_shapely_geometry("India")
        self.assertIsNotNone(geometry)
        
        # Test risk zones
        risk_zones = self.country_boundaries.get_risk_zones("India", "earthquake")
        self.assertIsInstance(risk_zones, list)

if __name__ == '__main__':
    unittest.main() 