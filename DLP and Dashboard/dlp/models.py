from typing import Literal
from pydantic import BaseModel, Field

class RedactRequest(BaseModel):
    text: str = Field(min_length=1)
    source: Literal["input", "output"] = "input"
    reversible: bool = False

class ValidationRequest(BaseModel):
    text: str = Field(min_length=1)

class ProcessRequest(BaseModel):
    text: str = Field(min_length=1)
    direction: Literal["input", "output"] = "input"

class EntityFinding(BaseModel):
    entity_type: str
    start: int
    end: int
    score: float
    text_preview: str

class RedactResponse(BaseModel):
    redacted_text: str
    findings: list[EntityFinding]
    tokens: dict[str, str] = {}

class ValidationResponse(BaseModel):
    allowed: bool
    findings: list[EntityFinding]
    blocked_entities: list[str]

class AllowlistRequest(BaseModel):
    entity_types: list[str]
