from threading import RLock
from config import DEFAULT_ALLOWED_ENTITIES

class AllowlistManager:
    def __init__(self):
        self._allowed = set(DEFAULT_ALLOWED_ENTITIES)
        self._lock = RLock()

    def list(self):
        with self._lock:
            return sorted(self._allowed)

    def add(self, entity_types):
        with self._lock:
            self._allowed.update(entity_types)
            return self.list()

    def remove(self, entity_type):
        with self._lock:
            self._allowed.discard(entity_type)
            return self.list()

    def is_allowed(self, entity_type):
        with self._lock:
            return entity_type in self._allowed
