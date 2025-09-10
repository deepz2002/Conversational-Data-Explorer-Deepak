from __future__ import annotations
from typing import Dict, Optional
import pandas as pd

class DataRegistry:
    def __init__(self):
        self.tables: Dict[str, pd.DataFrame] = {}
        self.active: Optional[str] = None

    def put(self, name: str, df: pd.DataFrame):
        self.tables[name] = df
        self.active = name

    def get(self, name: Optional[str] = None) -> pd.DataFrame:
        key = name or self.active
        if not key or key not in self.tables:
            raise ValueError("No active dataset. Upload a CSV first.")
        return self.tables[key]