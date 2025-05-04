import json
import os
from typing import List, Optional
from geopy.geocoders import Nominatim

class HelplineKnowledgeBase:
    def __init__(self, json_path=None):
        if json_path is None:
            json_path = os.path.join("data", "helplines.json")
        with open(json_path, "r") as f:
            self.data = json.load(f)
        self.geolocator = Nominatim(user_agent="helpline_kb")

    def _city_to_state(self, city: str) -> Optional[str]:
        try:
            location = self.geolocator.geocode(f"{city}, India", addressdetails=True)
            if location and hasattr(location, 'raw') and 'address' in location.raw:
                address = location.raw['address']
                # Try state, then state_district
                return address.get('state') or address.get('state_district')
        except Exception:
            pass
        return None

    def search(self, region: Optional[str] = None, disaster_type: Optional[str] = None, top_n: int = 3) -> List[dict]:
        results = self.data
        # Always include national helplines
        national = [e for e in results if e["region"].lower() == "india"]
        region_results = []
        state_results = []
        state_name = None
        if region:
            region_lower = region.lower()
            region_results = [e for e in results if region_lower in e["region"].lower() and e["region"].lower() != "india"]
            # If no region results and region is likely a city, try to get the state
            if not region_results:
                state_name = self._city_to_state(region)
                if state_name:
                    state_results = [e for e in results if state_name.lower() in e["region"].lower() and e["region"].lower() != "india"]
        # Combine and deduplicate
        combined = national + region_results + state_results
        seen = set()
        unique = []
        for e in combined:
            key = (e["region"], e["helpline_name"], e["phone"])
            if key not in seen:
                seen.add(key)
                unique.append(e)
            if len(unique) == top_n:
                break
        return unique

    def format_helpline(self, entry: dict) -> str:
        s = f"{entry['helpline_name']} ({entry['region']}): {entry['phone']}\n{entry['description']}\n[Source]({entry['source']})"
        return s

    def get_summary(self, region=None, disaster_type=None, top_n=3) -> str:
        helplines = self.search(region, disaster_type, top_n)
        if not helplines:
            return "No helpline numbers found for your query."
        lines = [self.format_helpline(e) for e in helplines]
        return "\n\n".join(lines) 