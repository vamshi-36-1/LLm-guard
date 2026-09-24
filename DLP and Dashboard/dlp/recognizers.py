from presidio_analyzer import Pattern, PatternRecognizer

class APIKeyRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern("OpenAI-like key", r"\bsk-[A-Za-z0-9_-]{20,}\b", 0.92),
            Pattern("Generic bearer", r"\bBearer\s+[A-Za-z0-9._-]{20,}\b", 0.88),
        ]
        super().__init__(supported_entity="API_KEY", patterns=patterns)

class GenericSecretRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern("secret assignment", r'(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*["\']?[A-Za-z0-9_./+=:-]{12,}', 0.82),
        ]
        super().__init__(supported_entity="SECRET", patterns=patterns)

def register_custom_recognizers(analyzer):
    analyzer.registry.add_recognizer(APIKeyRecognizer())
    analyzer.registry.add_recognizer(GenericSecretRecognizer())
    return analyzer
