import json
import os
from typing import List, Optional

class HistoricalKnowledgeBase:
    def __init__(self, json_path=None):
        if json_path is None:
            json_path = os.path.join("data", "historical_disasters.json")
        with open(json_path, "r") as f:
            self.data = json.load(f)

    def search(self, disaster_type: Optional[str] = None, location: Optional[str] = None, keyword: Optional[str] = None, top_n: int = 3) -> List[dict]:
        results = self.data
        if disaster_type:
            results = [e for e in results if e["disaster_type"].lower() == disaster_type.lower()]
        if location:
            results = [e for e in results if location.lower() in e["location"].lower()]
        if keyword:
            results = [e for e in results if keyword.lower() in e["name"].lower() or keyword.lower() in e["description"].lower()]
        # Sort by date descending
        results = sorted(results, key=lambda x: x["date"], reverse=True)
        return results[:top_n]

    def format_event(self, event: dict) -> str:
        s = f"{event['name']} ({event['date']}, {event['location']}): "
        if event.get('magnitude'):
            s += f"Magnitude {event['magnitude']}. "
        if event.get('casualties'):
            s += f"Casualties: {event['casualties']}. "
        s += event['description']
        if event.get('sources'):
            s += f" [Source]({event['sources'][0]})"
        return s

    def get_summary(self, disaster_type=None, location=None, keyword=None, top_n=3) -> str:
        events = self.search(disaster_type, location, keyword, top_n)
        if not events:
            return "No historical events found for your query."
        lines = [self.format_event(e) for e in events]
        return "\n".join(lines) 