import spacy
from geopy.geocoders import Nominatim
from config import LOCATION_TYPES

class LocationExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.geolocator = Nominatim(user_agent="disaster_assistant")

    def extract_location(self, query):
        doc = self.nlp(query)
        locations = []
        
        # Extract named entities that are locations
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:  # GPE = Geo-Political Entity, LOC = Location
                locations.append({
                    "text": ent.text,
                    "type": self._determine_location_type(ent.text)
                })
        
        return locations

    def _determine_location_type(self, location_text):
        try:
            location = self.geolocator.geocode(location_text)
            if location:
                # Check the type of location based on the address components
                address = location.address.split(',')
                if len(address) >= 3:  # City, State/Region, Country
                    return LOCATION_TYPES["CITY"]
                elif len(address) == 2:  # State/Region, Country
                    return LOCATION_TYPES["STATE"]
                else:
                    return LOCATION_TYPES["COUNTRY"]
        except Exception:
            pass
        return None 