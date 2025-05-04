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
import re
import spacy

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

pending_query = None  # Stores dict: {'query': ..., 'missing': ..., 'classification': ..., 'locations': ..., 'time_periods': ...}

nlp = spacy.load("en_core_web_sm")

def is_likely_location(text):
    doc = nlp(text)
    # If the text is a single entity of type GPE/LOC, or a short phrase, treat as location
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC", "FAC"):
            return True
    # If it's a short phrase (e.g., "Japan", "Delhi"), treat as location
    if len(doc) <= 3 and all(token.pos_ in ("PROPN", "NOUN") for token in doc):
        return True
    return False

def split_into_subqueries(query):
    # Split on '?', '.', ';' but keep the delimiter for context
    parts = re.split(r'([?.;])', query)
    subqueries = []
    current = ''
    for part in parts:
        if part.strip() == '':
            continue
        current += part
        if part in ['?', '.', ';']:
            if current.strip():
                subqueries.append(current.strip())
            current = ''
    if current.strip():
        subqueries.append(current.strip())
    # Remove empty or trivial subqueries
    return [q for q in subqueries if len(q) > 2]

def chatbot(query, pending=None, skip_split=False):
    global pending_query
    # If this is a follow-up to a pending query, try to fill missing info
    if pending:
        if is_likely_location(query):
            locations = location_extractor.extract_location(query)
            if locations:
                orig_query = pending['query']
                merged_query = orig_query
                if '[LOCATION]' in orig_query:
                    merged_query = orig_query.replace('[LOCATION]', locations[0]['text'])
                else:
                    merged_query = orig_query + ' ' + locations[0]['text']
                print("[DEBUG] Merged query for pending:", merged_query)
                # Do not split merged follow-up
                return chatbot(merged_query, skip_split=True)
            return f"Sorry, I still need the missing information: {pending['missing']}"
        else:
            # Treat as a new query
            return chatbot(query)

    if not skip_split:
        subqueries = split_into_subqueries(query)
        if len(subqueries) > 1:
            responses = []
            for i, subq in enumerate(subqueries, 1):
                resp = chatbot(subq)
                responses.append(f"Q{i}: {subq}\nA{i}: {resp}")
            return "\n\n".join(responses)
    classification = query_classifier.classify_query(query)
    disaster_type = classification["disaster_type"]
    query_type = classification["query_type"]
    locations = location_extractor.extract_location(query)
    time_periods = time_period_extractor.extract_time_period(query)
    print("[DEBUG] Classification:", classification)
    print("[DEBUG] Locations:", locations)
    print("[DEBUG] Time Periods:", time_periods)
    if query_type in ["helpline_info", "historical_info", "future_alerts"] and not locations:
        pending_query = {
            'query': query,
            'missing': 'location',
            'classification': classification,
            'locations': locations,
            'time_periods': time_periods
        }
        return "Please specify a location (city, state, or country) for your query."
    if disaster_type == "weather" and not locations:
        pending_query = {
            'query': query,
            'missing': 'location',
            'classification': classification,
            'locations': locations,
            'time_periods': time_periods
        }
        return "Please specify a location (city, state, or country) for your weather query."
    if query_type in ["helpline_info", "historical_info", "future_alerts"] and locations:
        responses = []
        for loc in locations[:3]:
            if query_type == "helpline_info":
                resp = helpline_kb.get_summary(region=loc["text"], disaster_type=disaster_type, top_n=3)
                responses.append(resp)
            elif query_type == "historical_info":
                resp = historical_kb.get_summary(disaster_type=disaster_type, location=loc["text"], top_n=3)
                responses.append(resp)
            elif query_type == "future_alerts" and disaster_type == "earthquake":
                resp = response_generator.generate_response(
                    query_type, disaster_type, query, locations=[loc], time_periods=time_periods
                )
                if not resp or not str(resp).strip():
                    resp = f"No significant earthquake alerts forecasted in {loc['text']} for the specified period."
                responses.append(resp)
            elif query_type == "future_alerts" and disaster_type == "flood":
                resp = response_generator.generate_response(
                    query_type, disaster_type, query, locations=[loc], time_periods=time_periods
                )
                if not resp or not str(resp).strip():
                    resp = f"No significant flood alerts forecasted in {loc['text']} for the specified period."
                responses.append(resp)
        return "\n\n".join(responses)
    if disaster_type == "weather" and locations:
        responses = []
        for loc in locations[:3]:
            intent = weather_intent_parser.parse(f"weather in {loc['text']}")
            if not intent["location_name"] or not intent["location_type"]:
                responses.append(f"[{loc['text']}]:\nPlease specify a valid location (city, state, or country) in your weather query.")
                continue
            weather_data = weather_fetcher.fetch_weather(
                intent["location_name"], intent["location_type"], intent["time_periods"]
            )
            responses.append(generate_weather_response(weather_data, loc['text']))
        return "\n\n".join(responses)
    if query_type == "helpline_info":
        loc_text = locations[0]["text"] if locations else None
        return helpline_kb.get_summary(region=loc_text, disaster_type=disaster_type, top_n=3)
    if query_type == "historical_info":
        loc_text = locations[0]["text"] if locations else None
        return historical_kb.get_summary(disaster_type=disaster_type, location=loc_text, top_n=3)
    if disaster_type == "weather":
        if query_type == "safety_guidelines":
            return response_generator.generate_response(
                query_type, disaster_type, query, locations=locations, time_periods=time_periods
            )
        intent = weather_intent_parser.parse(query)
        if not intent["location_name"] or not intent["location_type"]:
            return "Please specify a valid location (city, state, or country) in your weather query."
        weather_data = weather_fetcher.fetch_weather(
            intent["location_name"], intent["location_type"], intent["time_periods"]
        )
        return generate_weather_response(weather_data, query)
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
        if pending_query:
            response = chatbot(user_query, pending=pending_query)
            # If the pending query is resolved, clear it
            if "Please specify" not in response:
                pending_query = None
        else:
            response = chatbot(user_query)
        print(f"Bot: {response}\n") 