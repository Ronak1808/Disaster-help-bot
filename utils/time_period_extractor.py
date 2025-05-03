import re
import spacy

class TimePeriodExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        # Regex for common time period phrases
        self.patterns = [
            r"next \d+ (days|weeks|months|years)",
            r"last \d+ (days|weeks|months|years)",
            r"in \d{4}",
            r"for \d+ (days|weeks|months|years)",
            r"until \d{4}",
            r"from \d{4} to \d{4}",
            r"between \d{4} and \d{4}"
        ]

    def extract_time_period(self, query):
        periods = []
        # Regex-based extraction
        for pat in self.patterns:
            for match in re.findall(pat, query, re.IGNORECASE):
                periods.append(match)
        # spaCy DATE entity extraction
        doc = self.nlp(query)
        for ent in doc.ents:
            if ent.label_ == "DATE" and ent.text not in periods:
                periods.append(ent.text)
        return periods 