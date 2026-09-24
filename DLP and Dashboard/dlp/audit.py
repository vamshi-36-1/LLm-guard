import json
import os
from datetime import datetime, timezone
from threading import Lock
from config import AUDIT_PATH

class AuditLogger:
    def __init__(self, path=AUDIT_PATH):
        self.path = path
        self.lock = Lock()
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

    def log(self, event_type, **data):
        event = {"timestamp": datetime.now(timezone.utc).isoformat(), "event_type": event_type, **data}
        with self.lock, open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event
