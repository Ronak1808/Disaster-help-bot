from utils.query_classifier import QueryClassifier
from utils.location_extractor import LocationExtractor
from utils.response_generator import ResponseGenerator
from utils.time_period_extractor import TimePeriodExtractor
from utils.location_to_coordinates import LocationToCoordinates
from utils.country_boundaries import CountryBoundaries
from config import QUERY_TYPES, DISASTER_TYPES
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DisasterAssistant:
    def __init__(self):
        self.query_classifier = QueryClassifier()
        self.location_extractor = LocationExtractor()
        self.response_generator = ResponseGenerator()
        self.time_period_extractor = TimePeriodExtractor()
        self.location_converter = LocationToCoordinates()
        self.country_boundaries = CountryBoundaries()

    def process_query(self, query):
        # Classify the query
        classification = self.query_classifier.classify_query(query)
        
        # Extract locations
        locations = self.location_extractor.extract_location(query)
        
        # Extract time periods
        time_periods = self.time_period_extractor.extract_time_period(query)
        
        # Get detailed location information
        location_details = []
        for loc in locations:
            loc_info = self.location_converter.get_coordinates(loc['text'], loc['type'])
            if loc_info:
                location_details.append(loc_info)
        
        # Generate response
        response = self.response_generator.generate_response(
            classification["query_type"],
            classification["disaster_type"],
            query,
            locations=locations,
            time_periods=time_periods
        )
        
        # Prepare result
        result = {
            "query": query,
            "classification": classification,
            "locations": locations,
            "location_details": location_details,
            "time_periods": time_periods,
            "response": response
        }
        
        return result

    def format_response(self, result):
        """Format the response in a user-friendly way"""
        output = []
        output.append("\n" + "="*80)
        output.append(f"Query: {result['query']}")
        
        # Classification details
        if result['classification']['query_type']:
            output.append("\nAnalysis:")
            output.append(f"Query Type: {result['classification']['query_type']}")
            output.append(f"Disaster Type: {result['classification']['disaster_type']}")
            output.append(f"Confidence: {result['classification']['confidence']:.2f}")
            # If a country is present in location_details, show bounding box
            for loc in result.get('location_details', []):
                if loc['type'] == 'country':
                    cb = CountryBoundaries()
                    bbox = cb.get_bounding_box(loc['name'])
                    if bbox:
                        output.append("Bounding Box:")
                        output.append(f"  Min Longitude: {bbox['min_lon']:.6f}")
                        output.append(f"  Min Latitude: {bbox['min_lat']:.6f}")
                        output.append(f"  Max Longitude: {bbox['max_lon']:.6f}")
                        output.append(f"  Max Latitude: {bbox['max_lat']:.6f}")
        
        # Location details
        if result['location_details']:
            output.append("\nLocation Information:")
            for loc in result['location_details']:
                output.append(f"\n{loc['name']} ({loc['type'].title()})")
                if 'center' in loc:
                    output.append(f"Center Coordinates: {loc['center']}")
                if 'iso' in loc:
                    output.append(f"ISO Code: {loc['iso']}")
                
                # Show raw location data for cities
                if loc['type'] == 'city' and 'raw_location' in loc:
                    raw = loc['raw_location']
                    output.append(f"\nRaw Location Data:")
                    output.append(f"Address: {raw['address']}")
                    output.append(f"Latitude: {raw['latitude']:.6f}")
                    output.append(f"Longitude: {raw['longitude']:.6f}")
                
                # Risk zones
                if 'risk_zones' in loc and loc['risk_zones']:
                    output.append("\nRisk Zones:")
                    for disaster_type, zones in loc['risk_zones'].items():
                        output.append(f"{disaster_type.title()}:")
                        for zone in zones:
                            output.append(f"  - {zone['name']}")
                
                # Geometry details
                if 'geometry' in loc:
                    geometry = loc['geometry']
                    if loc['type'] == 'city':
                        # For cities, show buffer zone information
                        coords = geometry['coordinates'][0]
                        output.append(f"\nBuffer Zone: Circular area with {len(coords)} points")
                        output.append("(Approximately 10km radius around the center point)")
                    else:
                        # For countries and states, show boundary information
                        if geometry['type'] == 'Polygon':
                            coords = geometry['coordinates'][0]
                            output.append(f"\nBoundary: {len(coords)} points forming a closed polygon")
                            output.append(f"First/Last Point (lon, lat): [{coords[0][0]:.6f}, {coords[0][1]:.6f}]")
                            output.append(f"First/Last Point (lat, lon): [{coords[0][1]:.6f}, {coords[0][0]:.6f}]")
                            output.append("(Copy the second format to paste in Google Maps)")
                        elif geometry['type'] == 'MultiPolygon':
                            output.append(f"\nBoundary: MultiPolygon with {len(geometry['coordinates'])} parts")
                            first_poly = geometry['coordinates'][0][0]
                            output.append(f"First/Last Point (lon, lat): [{first_poly[0][0]:.6f}, {first_poly[0][1]:.6f}]")
                            output.append(f"First/Last Point (lat, lon): [{first_poly[0][1]:.6f}, {first_poly[0][0]:.6f}]")
                            output.append("(Copy the second format to paste in Google Maps)")
        
        # Time periods
        if result.get('time_periods'):
            output.append("\nTime Period:")
            # Only show the most specific time period
            if len(result['time_periods']) > 1:
                output.append(f"- {result['time_periods'][-1]}")
            else:
                output.append(f"- {result['time_periods'][0]}")
        
        # Final response
        output.append("\nResponse:")
        output.append(result['response'])
        output.append("="*80 + "\n")
        return "\n".join(output)

def main():
    assistant = DisasterAssistant()
    
    print("Welcome to the Natural Disaster Assistant!")
    print("Type 'exit' or 'quit' to end the session.")
    print("You can ask questions about earthquakes and weather conditions.")
    print("Example queries:")
    print("- What should I do in case of earthquake?")
    print("- How to stay safe during a flood?")
    print("- What are the safety measures before an earthquake?")
    print("- Tell me about past earthquakes in California")
    print("- Are there any upcoming weather alerts for New York?")
    print("\n" + "="*50 + "\n")
    
    while True:
        try:
            query = input("\nEnter your query: ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("\nThank you for using the Natural Disaster Assistant. Goodbye!")
                break
            
            if not query:
                print("Please enter a valid query.")
                continue
            
            result = assistant.process_query(query)
            print(assistant.format_response(result))
            
        except KeyboardInterrupt:
            print("\n\nThank you for using the Natural Disaster Assistant. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try again with a different query.")

if __name__ == "__main__":
    main() 