from utils.query_classifier import QueryClassifier
from utils.location_extractor import LocationExtractor
from utils.time_period_extractor import TimePeriodExtractor
from utils.response_generator import ResponseGenerator, generate_weather_response
from utils.weather_intent_parser import WeatherIntentParser
from utils.weather_fetcher import WeatherFetcher
from utils.weatherapi_com_fetcher import WeatherAPIComFetcher
from utils.historical_knowledge_base import HistoricalKnowledgeBase
from utils.helpline_knowledge_base import HelplineKnowledgeBase
import os

# Toggle between 'openweathermap' and 'weatherapi'
WEATHER_PROVIDER = 'weatherapi'  # Change to 'openweathermap' when ready

# Set your API keys here
OPENWEATHER_API_KEY = "78432e38d34f83f9f5b869c1415273da"
WEATHERAPI_COM_KEY = "b19c72b3c4224147b2c90511250405"

query_classifier = QueryClassifier()
location_extractor = LocationExtractor()
time_period_extractor = TimePeriodExtractor()
response_generator = ResponseGenerator()
weather_intent_parser = WeatherIntentParser()

if WEATHER_PROVIDER == 'openweathermap':
    weather_fetcher = WeatherFetcher(api_key=OPENWEATHER_API_KEY)
elif WEATHER_PROVIDER == 'weatherapi':
    weather_fetcher = WeatherAPIComFetcher(api_key=WEATHERAPI_COM_KEY)
else:
    raise ValueError(f"Unknown WEATHER_PROVIDER: {WEATHER_PROVIDER}")

historical_kb = HistoricalKnowledgeBase()
helpline_kb = HelplineKnowledgeBase()

def chatbot(query):
    # Step 1: Classify query
    classification = query_classifier.classify_query(query)
    disaster_type = classification["disaster_type"]
    query_type = classification["query_type"]
    # Step 2: Extract locations and time periods
    locations = location_extractor.extract_location(query)
    time_periods = time_period_extractor.extract_time_period(query)

    # Debug print: show extracted info
    print("[DEBUG] Classification:", classification)
    print("[DEBUG] Locations:", locations)
    print("[DEBUG] Time Periods:", time_periods)

    # Step 3: Route to appropriate handler
    if query_type == "helpline_info":
        loc_text = locations[0]["text"] if locations else None
        return helpline_kb.get_summary(region=loc_text, disaster_type=disaster_type, top_n=3)
    if query_type == "historical_info":
        # Use first location if available
        loc_text = locations[0]["text"] if locations else None
        return historical_kb.get_summary(disaster_type=disaster_type, location=loc_text, top_n=3)
    if disaster_type == "weather":
        # If it's a safety guidelines query, allow no location (return general weather safety)
        if query_type == "safety_guidelines":
            return response_generator.generate_response(
                query_type, disaster_type, query, locations=locations, time_periods=time_periods
            )
        # Otherwise, require a location for weather data/alerts
        intent = weather_intent_parser.parse(query)
        if not intent["location_name"] or not intent["location_type"]:
            return "Please specify a valid location (city, state, or country) in your weather query."
        weather_data = weather_fetcher.fetch_weather(
            intent["location_name"], intent["location_type"], intent["time_periods"]
        )
        return generate_weather_response(weather_data)
    else:
        return response_generator.generate_response(
            query_type, disaster_type, query, locations=locations, time_periods=time_periods
        )

if __name__ == "__main__":
    print("Disaster & Weather Chatbot (type 'exit' to quit)")
    while True:
        user_query = input("You: ")
        if user_query.strip().lower() == "exit":
            break
        response = chatbot(user_query)
        print(f"Bot: {response}\n") 