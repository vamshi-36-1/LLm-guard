import os

AUDIT_PATH = os.getenv("DLP_AUDIT_PATH", "audit.jsonl")
TOKEN_SECRET = os.getenv("DLP_TOKEN_SECRET", "development-only-secret")
MAX_TEXT_LENGTH = int(os.getenv("DLP_MAX_TEXT_LENGTH", "20000"))

DEFAULT_ALLOWED_ENTITIES = {"URL", "DATE_TIME", "NRP"}
