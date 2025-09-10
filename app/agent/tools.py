from __future__ import annotations
import io
import re
from typing import Any, Dict, List, Optional

import pandas as pd
from agno.tools import tool
from app.agent.memory import SessionMemory
from app.services.plotting import plot_and_save, PLOT_DIR
from app.services.utils import snake_case, infer_schema, resolve_column, closest, smart_column_finder

# This dict is injected by FastAPI at startup so tools can access sessions.
SESSIONS: Dict[str, SessionMemory] = {}

def get_or_create_session(session_id: str) -> SessionMemory:
    if session_id not in SESSIONS:
        SESSIONS[session_id] = SessionMemory()
    return SESSIONS[session_id]

@tool
def tool_load_csv(session_id: str, file_bytes: bytes, name: str = "dataset") -> Dict[str, Any]:
    """Load a CSV or Excel into the active session (schema-agnostic)."""
    mem = get_or_create_session(session_id)

    # Try CSV
    try:
        buf = io.BytesIO(file_bytes); buf.seek(0)
        df = pd.read_csv(buf)
    except Exception:
        # Fallback to Excel
        buf = io.BytesIO(file_bytes); buf.seek(0)
        df = pd.read_excel(buf, sheet_name=0)

    # Normalize headers
    df.columns = [snake_case(c) for c in df.columns]

    # Opportunistic typing: dates & numerics (safe, non-destructive)
    for c in df.columns:
        # date-like
        if any(tok in c for tok in ["date", "time", "timestamp"]):
            try:
                df[c] = pd.to_datetime(df[c], errors="ignore")
            except Exception:
                pass
        # numeric coercion for string/object columns
        if df[c].dtype == object:
            try:
                coerced = pd.to_numeric(df[c], errors="coerce")
                if coerced.notna().sum() > max(10, int(0.5 * len(df))):
                    df[c] = coerced
            except Exception:
                pass

    mem.registry.put(name, df)
    schema = infer_schema(df)
    return {"session_id": session_id, "name": name, "rows": len(df), "cols": list(df.columns), "schema": schema}

@tool
def tool_smart_explore(session_id: str) -> Dict[str, Any]:
    """Smart data exploration - automatically identifies key columns and provides insights."""
    mem = get_or_create_session(session_id)
    df = mem.registry.get()
    
    # Get smart column mapping
    smart_cols = smart_column_finder(df, "explore")
    schema = infer_schema(df)
    
    # Generate insights
    insights = []
    insights.append(f"Dataset has {len(df)} rows and {len(df.columns)} columns.")
    
    # Identify key business columns
    key_columns = []
    if 'customer' in smart_cols:
        key_columns.append(f"Customer column: {smart_cols['customer']}")
    if 'sales' in smart_cols:
        key_columns.append(f"Sales/Revenue column: {smart_cols['sales']}")
    if 'quantity' in smart_cols:
        key_columns.append(f"Quantity column: {smart_cols['quantity']}")
    if 'region' in smart_cols:
        key_columns.append(f"Region column: {smart_cols['region']}")
    if 'category' in smart_cols:
        key_columns.append(f"Category column: {smart_cols['category']}")
    if 'date' in smart_cols:
        key_columns.append(f"Date column: {smart_cols['date']}")
    
    return {
        "smart_columns": smart_cols,
        "schema": schema,
        "insights": insights,
        "key_columns": key_columns,
        "columns": list(df.columns)
    }

@tool
def tool_describe(session_id: str, columns: Optional[List[str]] = None) -> Dict[str, Any]:
    mem = get_or_create_session(session_id)
    df = mem.registry.get()
    sel_cols = []
    if columns:
        for col in columns:
            resolved = col if col in df.columns else resolve_column(df, col)
            if resolved:
                sel_cols.append(resolved)
    sel = df if not sel_cols else df[sel_cols]
    desc = sel.describe(include="all", datetime_is_numeric=True).fillna("")
    return {"table": desc.reset_index().to_dict(orient="records")}

@tool
def tool_top_k(session_id: str, metric: str, group_by: str, k: int = 5, agg: str = "sum") -> Dict[str, Any]:
    """Top-k groups by a numeric metric (sum/mean). Works with any CSV via dynamic resolution."""
    mem = get_or_create_session(session_id)
    df = mem.registry.get()

    mcol = metric if metric in df.columns else resolve_column(df, metric)
    gcol = group_by if group_by in df.columns else resolve_column(df, group_by)

    if not mcol:
        return {"error": f"Metric '{metric}' not found.", "candidates": closest(df, metric)}
    if not gcol:
        return {"error": f"Group '{group_by}' not found.", "candidates": closest(df, group_by)}
    if not pd.api.types.is_numeric_dtype(df[mcol]):
        return {"error": f"Column '{mcol}' is not numeric.", "numeric_candidates": infer_schema(df)["numeric"]}

    try:
        series = df.groupby(gcol)[mcol]
        out = (series.mean(numeric_only=True) if agg == "mean" else series.sum(numeric_only=True))
        out = out.sort_values(ascending=False).head(k).reset_index()
    except Exception as e:
        return {"error": str(e)}

    return {"table": out.to_dict(orient="records"), "used": {"metric": mcol, "group_by": gcol, "agg": agg}}

@tool
def tool_filter_preview(session_id: str, query: str, limit: int = 20) -> Dict[str, Any]:
    """Apply a basic pandas query; return a small preview or error + suggestions."""
    mem = get_or_create_session(session_id)
    df = mem.registry.get()
    try:
        # Safety: allow only a restricted character set
        if not re.fullmatch(r"[\w\s\=\!\<\>\&\|\'\"\-\:\.\,\(\)]+", query):
            return {"error": "Query contains unsupported characters."}
        out = df.query(query)
        sample = out.head(limit)
        return {"rows": sample.to_dict(orient="records"), "count": len(out)}
    except Exception as e:
        return {"error": f"Bad filter: {e}", "candidates": [
            "pick a valid column like: " + ", ".join(df.columns[:5]),
            "example: col_a > 10 & col_b == 'X'",
        ]}

@tool
def tool_plot(session_id: str, x: str, y: str, kind: str = "line", agg: Optional[str] = None, filename: Optional[str] = None) -> Dict[str, Any]:
    """Create a Plotly chart data for rendering in UI. Dynamically resolves columns. Returns chart data, table, and description."""
    mem = get_or_create_session(session_id)
    df = mem.registry.get()

    xcol = x if x in df.columns else resolve_column(df, x)
    ycol = y if y in df.columns else resolve_column(df, y)

    if not xcol or not ycol:
        missing = []
        if not xcol: missing.append(f"x:'{x}'")
        if not ycol: missing.append(f"y:'{y}'")
        return {"error": f"Column(s) not found: {', '.join(missing)}", "have": list(df.columns)}

    try:
        # Prepare data for the plot (aggregated if needed)
        plot_data = df.copy()
        if agg and agg in ["sum", "mean", "count"]:
            if agg == "sum":
                plot_data = df.groupby(xcol)[ycol].sum().reset_index()
            elif agg == "mean":
                plot_data = df.groupby(xcol)[ycol].mean().reset_index()
            elif agg == "count":
                plot_data = df.groupby(xcol)[ycol].count().reset_index()
        
        # Get the data table (limit to reasonable size)
        table_data = plot_data[[xcol, ycol]].head(50).to_dict(orient="records")
        
        # Store chart data in session memory for frontend to retrieve
        chart_info = {
            "x": xcol,
            "y": ycol, 
            "kind": kind,
            "data": table_data
        }
        mem.remember("last_chart", chart_info)
        
        # Generate description
        total_points = len(plot_data)
        y_values = plot_data[ycol]
        
        description = f"{kind.title()} chart showing {ycol} by {xcol}. "
        description += f"Dataset contains {total_points} data points. "
        
        if pd.api.types.is_numeric_dtype(y_values):
            description += f"{ycol} ranges from {y_values.min():.2f} to {y_values.max():.2f} "
            description += f"with an average of {y_values.mean():.2f}."
        
        if agg:
            description += f" Data is aggregated using {agg}."
            
        return {
            "success": f"Created {kind} chart with {total_points} data points",
            "table": table_data,
            "description": description,
            "used": {"x": xcol, "y": ycol, "agg": agg, "kind": kind},
            "total_rows": total_points
        }
    except Exception as e:
        return {"error": str(e), "have": list(df.columns)}

@tool
def tool_suggest_analysis(session_id: str) -> Dict[str, Any]:
    """Suggest specific analysis options when user request is vague."""
    mem = get_or_create_session(session_id)
    df = mem.registry.get()
    smart_cols = smart_column_finder(df, "suggest")
    schema = infer_schema(df)
    
    suggestions = []
    
    # Suggest based on available data
    if 'customer' in smart_cols and 'sales' in smart_cols:
        suggestions.append("Top customers by sales/revenue")
    
    if 'category' in smart_cols and 'sales' in smart_cols:
        suggestions.append("Sales breakdown by category/product type")
    
    if 'region' in smart_cols and 'sales' in smart_cols:
        suggestions.append("Regional sales analysis")
    
    if 'date' in smart_cols and 'sales' in smart_cols:
        suggestions.append("Sales trends over time")
    
    if schema['numeric']:
        suggestions.append(f"Statistical summary of key metrics like {', '.join(schema['numeric'][:3])}")
    
    if schema['categorical']:
        suggestions.append(f"Distribution analysis of {', '.join(schema['categorical'][:2])}")
    
@tool
def tool_fallback_help(session_id: str, error_context: str) -> Dict[str, Any]:
    """Provide helpful alternatives when other tools fail."""
    mem = get_or_create_session(session_id)
    df = mem.registry.get()
    smart_cols = smart_column_finder(df, "fallback")
    
    alternatives = []
    
    if "column" in error_context.lower():
        alternatives.append("Available columns: " + ", ".join(df.columns))
        if smart_cols:
            alternatives.append("Key business columns found: " + ", ".join([f"{k}={v}" for k, v in smart_cols.items()]))
    
    if "plot" in error_context.lower() or "chart" in error_context.lower():
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if numeric_cols:
            alternatives.append(f"Try plotting these numeric columns: {', '.join(numeric_cols[:3])}")
    
    if "filter" in error_context.lower():
        alternatives.append("Try basic filters like: column_name > value or column_name == 'text'")
    
    # Always suggest basic data exploration
    alternatives.extend([
        "Try 'describe the data' to see data structure",
        "Ask for 'top 10 rows' to see sample data",
        "Request 'data summary' for key statistics"
    ])
    
    return {
        "alternatives": alternatives,
        "available_data": {
            "columns": list(df.columns),
            "smart_columns": smart_cols,
            "shape": f"{len(df)} rows × {len(df.columns)} columns"
        }
    }