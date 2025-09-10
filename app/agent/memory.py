from __future__ import annotations
from typing import Any, Dict, List
from app.services.data_registry import DataRegistry

class SessionMemory:
    def __init__(self):
        self.prefs: Dict[str, Any] = {}  # e.g., {"date_col": "created_at"}
        self.history: List[Dict[str, Any]] = []
        self.registry = DataRegistry()

    def remember(self, k, v):
        self.prefs[k] = v

    def recall(self, k, default=None):
        return self.prefs.get(k, default)