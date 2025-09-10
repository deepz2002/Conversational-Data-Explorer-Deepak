from __future__ import annotations
from pathlib import Path
from typing import Optional
import plotly.express as px
import pandas as pd

PLOT_DIR = Path(__file__).resolve().parent.parent / "static" / "plots"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

def plot_and_save(
    df: pd.DataFrame,
    x: str,
    y: str,
    kind: str = "line",
    agg: Optional[str] = None,
    filename: Optional[str] = None,
) -> str:
    if x not in df.columns or y not in df.columns:
        raise ValueError("Missing x or y column")
    data = df
    if agg:
        data = df.groupby(x)[y].agg(agg).reset_index()
    else:
        data = df[[x, y]].dropna()

    if kind == "bar":
        fig = px.bar(data, x=x, y=y)
    elif kind == "area":
        fig = px.area(data, x=x, y=y)
    else:
        fig = px.line(data, x=x, y=y)

    fname = filename or f"{x}_{y}_{kind}.png"
    out_path = PLOT_DIR / fname
    fig.write_image(str(out_path))  # requires kaleido
    return f"/plots/{fname}"