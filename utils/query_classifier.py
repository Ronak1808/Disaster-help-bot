from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from config import QUERY_TYPES, DISASTER_TYPES
from textblob import TextBlob

class QueryClassifier:
    def __init__(self):
        # Load a pre-trained model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        
        # Expanded reference queries for each type with more variations and common typos
        self.reference_queries = {
            QUERY_TYPES["SAFETY_GUIDELINES"]: [
                "what should i do during an earthquake",
                "how to stay safe in an earthquake",
                "earthquake safety measures",
                "what are the safety guidelines for earthquakes",
                "how to protect yourself during an earthquake",
                "what actions to take during an earthquake",
                "earthquake safety procedures",
                "how to survive an earthquake",
                "earthquake emergency response",
                "earthquake preparedness tips",
                "what should one do in case of earthquake",
                "safety tips for earthquakes",
                "how to be safe during an earthquake",
                "what to do when there is an earthquake",
                "earthquake safety instructions",
                "what should i do in case of wild fire",
                "how to stay safe during a wildfire",
                "wildfire safety measures",
                "what are the safety guidelines for wildfires",
                "how to protect yourself during a wildfire",
                "what actions to take during a wildfire",
                "wildfire safety procedures",
                "how to survive a wildfire",
                "wildfire emergency response",
                "wildfire preparedness tips",
                # Common typos and variations
                "what shuold i do during an earthquake",
                "what shuld i do during an earthquake",
                "what should i do in case of an earthquake",
                "how to stay safe during an earthquke",
                "what to do in case of earthquke",
                "how to be safe in an earthquake",
                "what to do if earthquake happens",
                "what to do if there is an earthquake",
                "what to do during earthquake",
                "what to do in earthquake"
            ],
            QUERY_TYPES["HISTORICAL_INFO"]: [
                "tell me about past earthquakes",
                "what are some famous earthquakes",
                "historical earthquake information",
                "major earthquakes in history",
                "famous past earthquakes",
                "significant earthquake events",
                "notable earthquakes in the past",
                "earthquake history",
                "major seismic events",
                "famous earthquake incidents",
                # Variations
                "tell me about previous earthquakes",
                "earthquake events in the past",
                "earthquake records",
                "earthquake statistics",
                "earthquake data from previous years"
            ],
            QUERY_TYPES["FUTURE_ALERTS"]: [
                "are there any upcoming earthquake alerts",
                "future earthquake warnings",
                "earthquake predictions",
                "next earthquake alerts",
                "upcoming earthquake warnings",
                "earthquake forecast",
                "seismic activity predictions",
                "future earthquake risks",
                "earthquake early warnings",
                "seismic hazard alerts",
                # Variations
                "is there any earthquake alert for india",
                "is there any earthquake alert for next 10 days",
                "earthquake alert for this week",
                "earthquake alert for today",
                "earthquake alert for tomorrow",
                "any earthquake warning for my area"
            ]
        }
        
        # Pre-compute embeddings for reference queries
        self.reference_embeddings = {}
        for query_type, queries in self.reference_queries.items():
            self.reference_embeddings[query_type] = self._get_embeddings(queries)

    def _get_embeddings(self, texts):
        """Get embeddings for a list of texts"""
        encoded_input = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        # Use mean pooling to get sentence embeddings
        embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
        return embeddings

    def _mean_pooling(self, model_output, attention_mask):
        """Mean pooling to get sentence embeddings"""
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def _cosine_similarity(self, a, b):
        """Calculate cosine similarity between two tensors"""
        return F.cosine_similarity(a.unsqueeze(0), b.unsqueeze(0)).item()

    def classify_query(self, query):
        # Step 1: Spell correction (general, not hand-crafted)
        corrected_query = str(TextBlob(query).correct())
        # Initialize result
        result = {
            "query_type": None,
            "disaster_type": None,
            "confidence": 0.0
        }
        
        # Step 2: Get embedding for the input query
        query_embedding = self._get_embeddings([corrected_query])[0]
        
        # Step 3: Disaster type detection (embedding + fallback keyword)
        disaster_terms = {
            "earthquake": ["earthquake", "quake", "tremor", "seismic", "tectonic", "epicenter"],
            "weather": ["storm", "hurricane", "tornado", "flood", "cyclone", "typhoon", 
                       "wildfire", "bushfire", "forest fire", "heat wave", "blizzard", 
                       "tsunami", "drought", "heavy rain"]
        }
        # Try exact matching
        query_lower = corrected_query.lower()
        for disaster, terms in disaster_terms.items():
            if any(term in query_lower for term in terms):
                result["disaster_type"] = disaster
                break
        # If no exact match, try semantic similarity with disaster terms
        if not result["disaster_type"]:
            disaster_embeddings = {
                disaster: self._get_embeddings(terms)
                for disaster, terms in disaster_terms.items()
            }
            max_similarity = 0.5  # Threshold
            for disaster, embeddings in disaster_embeddings.items():
                similarity = self._cosine_similarity(query_embedding, embeddings[0])
                if similarity > max_similarity:
                    max_similarity = similarity
                    result["disaster_type"] = disaster
        # Step 4: Query type detection (max similarity)
        similarities = {}
        for query_type, ref_embeddings in self.reference_embeddings.items():
            # Use max similarity instead of mean
            similarity = max([
                self._cosine_similarity(query_embedding, ref_embedding)
                for ref_embedding in ref_embeddings
            ])
            similarities[query_type] = similarity
        # Get the best matching query type
        if similarities:
            best_type = max(similarities.items(), key=lambda x: x[1])
            threshold = 0.4  # Tuned threshold for better accuracy
            if best_type[1] > threshold:
                result["query_type"] = best_type[0]
                result["confidence"] = best_type[1]
            else:
                # Fallback: keyword matching for query type
                safety_keywords = ["should i do", "safety", "guidelines", "how to stay safe", "what to do", "protect yourself", "survive", "emergency response", "preparedness tips"]
                hist_keywords = ["past", "history", "historical", "previous", "records", "statistics", "data"]
                alert_keywords = ["alert", "warning", "forecast", "prediction", "upcoming", "next", "early warning"]
                if any(kw in query_lower for kw in safety_keywords):
                    result["query_type"] = QUERY_TYPES["SAFETY_GUIDELINES"]
                    result["confidence"] = 0.35
                elif any(kw in query_lower for kw in hist_keywords):
                    result["query_type"] = QUERY_TYPES["HISTORICAL_INFO"]
                    result["confidence"] = 0.35
                elif any(kw in query_lower for kw in alert_keywords):
                    result["query_type"] = QUERY_TYPES["FUTURE_ALERTS"]
                    result["confidence"] = 0.35
        return result

# For manual testing

def correct_spelling(query):
    return str(TextBlob(query).correct()) 