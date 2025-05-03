from utils.query_classifier import QueryClassifier
from utils.location_extractor import LocationExtractor
from utils.response_generator import ResponseGenerator
from utils.time_period_extractor import TimePeriodExtractor
from config import QUERY_TYPES, DISASTER_TYPES

class DisasterAssistant:
    def __init__(self):
        self.query_classifier = QueryClassifier()
        self.location_extractor = LocationExtractor()
        self.response_generator = ResponseGenerator()
        self.time_period_extractor = TimePeriodExtractor()

    def process_query(self, query):
        # Classify the query
        classification = self.query_classifier.classify_query(query)
        
        # Extract locations
        locations = self.location_extractor.extract_location(query)
        
        # Extract time periods
        time_periods = self.time_period_extractor.extract_time_period(query)
        
        # Generate response
        response = self.response_generator.generate_response(
            classification["query_type"],
            classification["disaster_type"],
            query
        )
        
        # Prepare result
        result = {
            "query": query,
            "classification": classification,
            "locations": locations,
            "time_periods": time_periods,
            "response": response
        }
        
        return result

    def format_response(self, result):
        """Format the response in a user-friendly way"""
        output = []
        output.append("\n" + "="*50)
        output.append(f"Query: {result['query']}")
        
        if result['classification']['query_type']:
            output.append("\nAnalysis:")
            output.append(f"Query Type: {result['classification']['query_type']}")
            output.append(f"Disaster Type: {result['classification']['disaster_type']}")
            output.append(f"Confidence: {result['classification']['confidence']:.2f}")
        
        if result['locations']:
            output.append("\nLocations Found:")
            for loc in result['locations']:
                output.append(f"- {loc['text']} ({loc['type']})")
        
        if result.get('time_periods'):
            output.append("\nTime Periods Found:")
            for period in result['time_periods']:
                output.append(f"- {period}")
        
        output.append("\nResponse:")
        output.append(result['response'])
        output.append("="*50 + "\n")
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