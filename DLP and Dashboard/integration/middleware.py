"""Framework-neutral DLP integration adapter for the team's Person 1 proxy."""
from dataclasses import dataclass
import httpx

@dataclass
class DLPResult:
    text: str
    blocked: bool
    blocked_entities: list[str]

class DLPClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url.rstrip("/")

    def redact_input(self, text: str) -> str:
        r=httpx.post(f"{self.base_url}/v1/dlp/redact", json={"text":text,"source":"input"}, timeout=2)
        r.raise_for_status(); return r.json()["redacted_text"]

    def validate_output(self, text: str) -> DLPResult:
        r=httpx.post(f"{self.base_url}/v1/dlp/validate", json={"text":text}, timeout=2)
        r.raise_for_status(); data=r.json()
        return DLPResult(text=text, blocked=not data["allowed"], blocked_entities=data["blocked_entities"])

    def process(self, prompt: str, llm_call):
        safe_prompt=self.redact_input(prompt)
        response=llm_call(safe_prompt)
        result=self.validate_output(response)
        if result.blocked:
            raise ValueError(f"DLP blocked output entities: {result.blocked_entities}")
        return response
