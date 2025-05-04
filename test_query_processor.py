import logging
import re
from utils.location_to_coordinates import LocationToCoordinates
from utils.country_boundaries import CountryBoundaries
from config import LOCATION_TYPES

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_location_info(query: str) -> tuple:
    """Extract location type and name from query"""
    # Define patterns for location types
    patterns = {
        LOCATION_TYPES["COUNTRY"]: [
            r"in\s+([A-Za-z\s]+)\s+country",
            r"of\s+([A-Za-z\s]+)\s+country",
            r"([A-Za-z\s]+)\s+country"
        ],
        LOCATION_TYPES["STATE"]: [
            r"in\s+([A-Za-z\s]+)\s+state",
            r"of\s+([A-Za-z\s]+)\s+state",
            r"([A-Za-z\s]+)\s+state"
        ],
        LOCATION_TYPES["CITY"]: [
            r"in\s+([A-Za-z\s]+)\s+city",
            r"of\s+([A-Za-z\s]+)\s+city",
            r"([A-Za-z\s]+)\s+city"
        ]
    }
    
    # Try each location type
    for location_type, type_patterns in patterns.items():
        for pattern in type_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                location_name = match.group(1).strip()
                return location_type, location_name
    
    return None, None

def process_query(query: str):
    """Process a query and show detailed information about the processing"""
    logger.info(f"\nProcessing query: '{query}'")
    
    # Initialize components
    location_converter = LocationToCoordinates()
    country_boundaries = CountryBoundaries()
    
    # Extract location information
    location_type, location_name = extract_location_info(query)
    
    if not location_type or not location_name:
        logger.warning("Could not determine location type or name from query")
        return
    
    logger.info(f"Detected location type: {location_type}")
    logger.info(f"Detected location name: {location_name}")
    
    # Get coordinates and geometry
    logger.info("\nFetching location information...")
    location_info = location_converter.get_coordinates(location_name, location_type)
    
    if "error" in location_info:
        logger.error(f"Error getting location info: {location_info['error']}")
        return
    
    logger.info("\nLocation Information:")
    logger.info(f"Type: {location_info['type']}")
    logger.info(f"Name: {location_info['name']}")
    
    if location_type == LOCATION_TYPES["COUNTRY"]:
        logger.info(f"ISO Code: {location_info.get('iso', 'N/A')}")
        logger.info(f"Center Point: {location_info['center']}")
        
        # Show risk zones
        logger.info("\nRisk Zones:")
        for disaster_type, zones in location_info['risk_zones'].items():
            logger.info(f"{disaster_type}: {len(zones)} zones")
            for zone in zones:
                logger.info(f"  - {zone['name']}")
    
    # Test some points
    logger.info("\nTesting points in location:")
    if location_type == LOCATION_TYPES["COUNTRY"]:
        # Test center point
        center = location_info['center']
        is_in = location_converter.is_point_in_location(
            center[0], center[1], location_name, location_type
        )
        logger.info(f"Center point ({center}) is in {location_name}: {is_in}")
        
        # Test a point outside
        outside_point = (center[0] + 10, center[1] + 10)  # Move 10 degrees away
        is_in = location_converter.is_point_in_location(
            outside_point[0], outside_point[1], location_name, location_type
        )
        logger.info(f"Outside point ({outside_point}) is in {location_name}: {is_in}")
    
    # Show geometry details
    logger.info("\nGeometry Details:")
    geometry = location_info['geometry']
    if geometry['type'] == 'Polygon':
        coords = geometry['coordinates'][0]
        logger.info(f"Polygon with {len(coords)} points")
        logger.info(f"First point: {coords[0]}")
        logger.info(f"Last point: {coords[-1]}")
    elif geometry['type'] == 'MultiPolygon':
        logger.info(f"MultiPolygon with {len(geometry['coordinates'])} parts")
        for i, part in enumerate(geometry['coordinates']):
            logger.info(f"Part {i+1}: {len(part[0])} points")

if __name__ == "__main__":
    # Example queries
    queries = [
        "What is the risk of earthquakes in India country",
        "Show me flood risks in California state",
        "Tell me about cyclones in Mumbai city",
        "What are the earthquake zones in India country",
        "Show me the flood prone areas in Maharashtra state",
        "Tell me about the cyclone risk in Chennai city"
    ]
    
    for query in queries:
        process_query(query)
        print("\n" + "="*80 + "\n") 