# Natural Disaster Assistant Chatbot

A chatbot that assists users with information about natural disasters, specifically focusing on earthquakes and unnatural weather conditions.

## Features

- Query classification using NLP
- Information about past natural disasters
- Real-time alerts and warnings for specific locations
- Support for various query types:
  - Safety guidelines during disasters
  - Historical disaster information
  - Future alerts and warnings

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download required spaCy model:
```bash
python -m spacy download en_core_web_sm
```

4. Create a `.env` file with your API keys (if needed)

## Usage

Run the main script:
```bash
python main.py
```

## Project Structure

- `main.py`: Main application entry point
- `config.py`: Configuration settings
- `utils/`: Helper functions and modules
  - `query_classifier.py`: NLP-based query classification
  - `location_extractor.py`: Location extraction from queries
  - `api_handler.py`: API interactions for real-time data

## Dependencies

- spaCy: For NLP and query classification
- Transformers: For advanced NLP tasks
- Requests: For API interactions
- Geopy: For location handling
- Pandas & NumPy: For data processing 