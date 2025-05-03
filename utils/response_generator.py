from utils.safety_guidelines import get_safety_guidelines
import spacy
from config import QUERY_TYPES

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

    def generate_response(self, query_type, disaster_type, query):
        """Generate response based on query type and disaster type"""
        if query_type == QUERY_TYPES["SAFETY_GUIDELINES"]:
            return self._generate_safety_response(disaster_type, query)
        # Add other query type handlers here
        return "I'm sorry, I can't process this type of query yet."

    def _generate_safety_response(self, disaster_type, query):
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