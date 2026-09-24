from models import EntityFinding

class OutputValidator:
    def __init__(self, analyzer, allowlist):
        self.analyzer = analyzer
        self.allowlist = allowlist

    def validate(self, text):
        results = self.analyzer.analyze(text=text, language="en")
        findings = [EntityFinding(entity_type=r.entity_type, start=r.start, end=r.end, score=float(r.score), text_preview=text[r.start:r.end][:80]) for r in results]
        blocked = sorted({r.entity_type for r in results if not self.allowlist.is_allowed(r.entity_type)})
        return not blocked, findings, blocked
