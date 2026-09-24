from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from recognizers import register_custom_recognizers

class DLPRedactor:
    def __init__(self):
        self.analyzer = register_custom_recognizers(AnalyzerEngine())
        self.anonymizer = AnonymizerEngine()

    def analyze(self, text: str):
        return self.analyzer.analyze(text=text, language="en")

    def redact(self, text: str):
        results = self.analyze(text)
        operators = {"DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"})}
        for r in results:
            operators.setdefault(r.entity_type, OperatorConfig("replace", {"new_value": f"[REDACTED:{r.entity_type}]"}))
        anonymized = self.anonymizer.anonymize(text=text, analyzer_results=results, operators=operators)
        return anonymized.text, results
