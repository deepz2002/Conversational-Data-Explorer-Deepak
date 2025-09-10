from __future__ import annotations

def detect_intent(text: str) -> str:
    t = text.lower()
    if "upload" in t or "csv" in t or "excel" in t:
        return "UPLOAD"
    if any(w in t for w in ["top", "largest", "by "]):
        return "TOP_K"
    if any(w in t for w in ["plot", "chart", "trend", "graph"]):
        return "PLOT"
    if any(w in t for w in ["describe", "summary", "stats"]):
        return "DESCRIBE"
    if any(w in t for w in ["filter", "where"]):
        return "FILTER"
    return "CHAT"