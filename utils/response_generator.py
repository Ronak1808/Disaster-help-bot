from utils.safety_guidelines import get_safety_guidelines
import spacy
from config import QUERY_TYPES
from utils.earthquake_alert_fetcher import EarthquakeAlertFetcher
from utils.flood_alert_fetcher import FloodAlertFetcher

class ResponseGenerator:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        
        # Keywords for different phases
        self.phase_keywords = {
            "before": ["before", "preparation", "prepare", "prevent", "prevention", "measures"],
            "during": ["during", "while", "when", "happening", "occurring", "stay safe"],
            "after": ["after", "aftermath", "recovery", "post", "following"]
        }
        
        # Weather-specific keywords with more variations
        self.weather_types = {
            "heavy_rain": ["heavy rain", "downpour", "rainstorm", "torrential rain", "rainfall"],
            "flood": ["flood", "flooding", "flooded", "inundation", "deluge"],
            "tsunami": ["tsunami", "tidal wave", "seismic sea wave", "ocean wave"],
            "tornado": ["tornado", "twister", "cyclone", "whirlwind", "funnel cloud"],
            "hurricane": ["hurricane", "typhoon", "tropical storm", "cyclone", "storm surge"],
            "wildfire": ["wildfire", "bushfire", "forest fire", "brush fire", "wildland fire"],
            "heat_wave": ["heat wave", "heatwave", "extreme heat", "hot weather", "heat advisory"],
            "blizzard": ["blizzard", "snowstorm", "winter storm", "snow squall", "whiteout"],
            "drought": ["drought", "dry spell", "water shortage", "arid conditions", "water scarcity"]
        }

        self.earthquake_alert_fetcher = EarthquakeAlertFetcher()
        self.flood_alert_fetcher = FloodAlertFetcher()

    def _detect_phase(self, query):
        """Detect the phase of the disaster mentioned in the query"""
        doc = self.nlp(query.lower())
        for phase, keywords in self.phase_keywords.items():
            if any(keyword in doc.text for keyword in keywords):
                return phase
        return None

    def _detect_weather_type(self, query):
        """Detect specific type of weather event mentioned in the query"""
        query_lower = query.lower()
        # First check for exact matches
        for weather_type, keywords in self.weather_types.items():
            if any(keyword in query_lower for keyword in keywords):
                return weather_type
        
        # If no exact match, try semantic similarity
        doc = self.nlp(query_lower)
        for token in doc:
            for weather_type, keywords in self.weather_types.items():
                if token.text in keywords:
                    return weather_type
        
        return None

    def generate_response(self, query_type, disaster_type, query, locations=None, time_periods=None):
        """Generate response based on query type and disaster type"""
        if query_type == QUERY_TYPES["SAFETY_GUIDELINES"]:
            return self._generate_safety_response(disaster_type, query)
        elif query_type == 'future_alerts' and disaster_type == 'earthquake' and locations:
            # Support country, state, and city
            for loc in locations:
                if loc['type'] in ('country', 'state', 'city'):
                    try:
                        alerts = self.earthquake_alert_fetcher.fetch_alerts(loc['text'], loc['type'], time_periods)
                        if isinstance(alerts, dict) and 'error' in alerts:
                            return f"[USGS API Error] {alerts['error']}"
                        if not alerts:
                            return f"No significant earthquakes forecasted in {loc['text']} for the specified period."
                        if len(alerts) == 1:
                            response_lines = [f"Earthquake event in {loc['text']}:"]
                        else:
                            response_lines = [f"Top {len(alerts)} earthquake events in {loc['text']}:"]
                        for i, event in enumerate(alerts, 1):
                            response_lines.append(
                                f"{i}. Magnitude {event['magnitude']} at {event['place']} on {event['time']} (Depth: {event['depth']} km) [More info]({event['url']})"
                            )
                        return '\n'.join(response_lines)
                    except Exception as e:
                        return f"[Error fetching earthquake alerts: {str(e)}]"
        elif query_type == 'future_alerts' and disaster_type == 'flood' and locations:
            for loc in locations:
                if loc['type'] in ('country', 'state', 'city'):
                    try:
                        alerts = self.flood_alert_fetcher.fetch_alerts(loc['text'], loc['type'], time_periods)
                        if isinstance(alerts, dict) and 'error' in alerts:
                            return f"[GDACS API Error] {alerts['error']}"
                        if not alerts or len(alerts) == 0:
                            return f"No significant flood alerts forecasted in {loc['text']} for the specified period."
                        response_lines = [f"Top {len(alerts)} flood alerts in {loc['text']}:"]
                        for i, event in enumerate(alerts, 1):
                            response_lines.append(
                                f"{i}. {event['title']} on {event['date']}\n   {event['description']}\n   [More info]({event['link']})"
                            )
                        return '\n'.join(response_lines)
                    except Exception as e:
                        return f"[Error fetching flood alerts: {str(e)}]"
        # Add other query type handlers here
        return "I'm sorry, I can't process this type of query yet."

    def _generate_safety_response(self, disaster_type, query):
        """Generate safety guidelines response"""
        phase = self._detect_phase(query)
        # Always use the disaster_type directly for top-level types
        guidelines = get_safety_guidelines(disaster_type, phase)
        response = [f"Here are the safety guidelines for {disaster_type}"]
        response.append("")
        for i, guideline in enumerate(guidelines, 1):
            response.append(f"{i}. {guideline}")
        return "\n".join(response)

    def _generate_safety_response_old(self, disaster_type, query):
        """Generate safety guidelines response"""
        if disaster_type == "earthquake":
            phase = self._detect_phase(query)
            guidelines = get_safety_guidelines("earthquake", phase)
            
            response = ["Here are the safety guidelines for earthquakes"]
            if phase:
                response.append(f"({phase} the earthquake):")
            else:
                response.append(":")
            
            for i, guideline in enumerate(guidelines, 1):
                response.append(f"{i}. {guideline}")
            
            return "\n".join(response)
            
        elif disaster_type == "weather":
            weather_type = self._detect_weather_type(query)
            phase = self._detect_phase(query)
            
            response = ["Here are the safety guidelines"]
            if weather_type:
                response.append(f"for {weather_type.replace('_', ' ')}:")
            else:
                response.append("for weather emergencies:")
            
            if weather_type:
                guidelines = get_safety_guidelines("weather", weather_type)
            else:
                guidelines = get_safety_guidelines("weather", "general")
            
            for i, guideline in enumerate(guidelines, 1):
                response.append(f"{i}. {guideline}")
            
            return "\n".join(response)
        
        return "I'm sorry, I don't have safety guidelines for that type of disaster."

def generate_weather_response(weather_data, user_query_location=None):
    if not weather_data or "error" in weather_data:
        return weather_data.get("error", "Sorry, I couldn't fetch the weather information.")
    resolved_location = weather_data.get('location')
    location_line = ""
    if user_query_location and resolved_location and resolved_location.lower() != user_query_location.lower():
        location_line = f"Showing weather for **{resolved_location}** (nearest to {user_query_location}):\n"
    elif resolved_location:
        location_line = f"Current weather in **{resolved_location}**:\n"
    wind_speed = weather_data.get('wind_speed')
    try:
        wind_speed = float(wind_speed)
        wind_speed = f"{wind_speed:.2f}"
    except Exception:
        wind_speed = weather_data.get('wind_speed')
    if weather_data["type"] == "current":
        return (
            f"{location_line}"
            f"- {weather_data['weather']}\n"
            f"- Temperature: {weather_data['temperature']}°C\n"
            f"- Humidity: {weather_data['humidity']}%\n"
            f"- Wind speed: {wind_speed} m/s\n"
            f"- Time: {weather_data['time']}"
        )
    elif weather_data["type"] == "forecast":
        lines = [location_line + "Weather forecast:"]
        for day in weather_data["days"]:
            lines.append(
                f"{day['date']}: {day['weather']}, "
                f"Min: {day['temperature_min']}°C, Max: {day['temperature_max']}°C, "
                f"Avg Humidity: {day['humidity_avg']:.0f}%, Avg Wind: {day['wind_speed_avg']:.1f} m/s"
            )
        return '\n'.join(lines)
    else:
        return "Sorry, I couldn't understand the weather data format." 