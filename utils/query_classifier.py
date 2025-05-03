from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from config import QUERY_TYPES, DISASTER_TYPES

class QueryClassifier:
    def __init__(self):
        # Load a pre-trained model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        
        # Define reference queries for each type with more variations
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
                "wildfire preparedness tips"
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
                "famous earthquake incidents"
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
                "seismic hazard alerts"
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
        # Initialize result
        result = {
            "query_type": None,
            "disaster_type": None,
            "confidence": 0.0
        }
        
        # Get embedding for the input query
        query_embedding = self._get_embeddings([query])[0]
        
        # Check for disaster type using keyword matching and semantic similarity
        disaster_terms = {
            "earthquake": ["earthquake", "quake", "tremor", "seismic", "tectonic", "epicenter"],
            "weather": ["storm", "hurricane", "tornado", "flood", "cyclone", "typhoon", 
                       "wildfire", "bushfire", "forest fire", "heat wave", "blizzard", 
                       "tsunami", "drought", "heavy rain"]
        }
        
        # First try exact matching
        query_lower = query.lower()
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
        
        # Calculate similarity with each query type
        similarities = {}
        for query_type, ref_embeddings in self.reference_embeddings.items():
            # Calculate cosine similarity between query and all reference queries
            similarity = torch.mean(torch.tensor([
                self._cosine_similarity(query_embedding, ref_embedding)
                for ref_embedding in ref_embeddings
            ])).item()
            similarities[query_type] = similarity
        
        # Get the best matching query type
        if similarities:
            best_type = max(similarities.items(), key=lambda x: x[1])
            if best_type[1] > 0.3:  # Lowered threshold to be more lenient
                result["query_type"] = best_type[0]
                result["confidence"] = best_type[1]
        
        return result 