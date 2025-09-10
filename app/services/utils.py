from __future__ import annotations
import re
import difflib
from typing import Dict, List
import pandas as pd

def snake_case(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^\w\s\-\/]", "", s)
    s = s.replace("/", " ").replace("-", " ").replace(".", " ")
    s = re.sub(r"\s+", "_", s)
    return s.lower()

def infer_schema(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Infer simple schema buckets for generic behavior across any CSV."""
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    datetime_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
    categorical_cols: List[str] = []
    for c in df.columns:
        if c in numeric_cols or c in datetime_cols:
            continue
        if pd.api.types.is_string_dtype(df[c]) or pd.api.types.is_object_dtype(df[c]):
            try:
                # low-cardinality strings → categorical
                if df[c].nunique(dropna=True) <= max(50, int(len(df) * 0.2)):
                    categorical_cols.append(c)
            except Exception:
                pass
    return {"numeric": numeric_cols, "datetime": datetime_cols, "categorical": categorical_cols}

def smart_column_finder(df: pd.DataFrame, intent: str) -> Dict[str, str]:
    """Smart column finder based on common business terms and patterns."""
    cols = [c.lower() for c in df.columns]
    original_cols = list(df.columns)
    
    result = {}
    
    # Customer patterns
    customer_patterns = ['customer', 'client', 'user', 'buyer', 'name', 'account']
    for pattern in customer_patterns:
        matches = [original_cols[i] for i, col in enumerate(cols) if pattern in col]
        if matches and 'customer' not in result:
            result['customer'] = matches[0]
    
    # Sales/Revenue patterns
    sales_patterns = ['sales', 'revenue', 'amount', 'total', 'value', 'price', 'cost']
    for pattern in sales_patterns:
        matches = [original_cols[i] for i, col in enumerate(cols) if pattern in col]
        if matches and 'sales' not in result:
            result['sales'] = matches[0]
    
    # Quantity patterns
    quantity_patterns = ['quantity', 'qty', 'count', 'number', 'orders']
    for pattern in quantity_patterns:
        matches = [original_cols[i] for i, col in enumerate(cols) if pattern in col]
        if matches and 'quantity' not in result:
            result['quantity'] = matches[0]
    
    # Region/Location patterns
    region_patterns = ['region', 'location', 'city', 'state', 'country', 'area', 'territory']
    for pattern in region_patterns:
        matches = [original_cols[i] for i, col in enumerate(cols) if pattern in col]
        if matches and 'region' not in result:
            result['region'] = matches[0]
    
    # Category patterns
    category_patterns = ['category', 'type', 'class', 'group', 'segment', 'product']
    for pattern in category_patterns:
        matches = [original_cols[i] for i, col in enumerate(cols) if pattern in col]
        if matches and 'category' not in result:
            result['category'] = matches[0]
    
    # Date patterns
    date_patterns = ['date', 'time', 'created', 'updated', 'order_date', 'purchase']
    for pattern in date_patterns:
        matches = [original_cols[i] for i, col in enumerate(cols) if pattern in col]
        if matches and 'date' not in result:
            result['date'] = matches[0]
    
    return result

def resolve_column(df: pd.DataFrame, user_term: str) -> str | None:
    """Enhanced column resolution with smart mapping."""
    if not user_term:
        return None
        
    cols = list(df.columns)
    user_lower = user_term.lower()
    
    # Direct match first
    for c in cols:
        if c.lower() == user_lower:
            return c
    
    # Smart mapping for common terms
    smart_map = smart_column_finder(df, user_term)
    
    # Map common user terms to found columns
    if user_lower in ['customer', 'customers', 'client', 'clients'] and 'customer' in smart_map:
        return smart_map['customer']
    if user_lower in ['sales', 'revenue', 'amount', 'total'] and 'sales' in smart_map:
        return smart_map['sales']
    if user_lower in ['quantity', 'qty', 'count', 'orders'] and 'quantity' in smart_map:
        return smart_map['quantity']
    if user_lower in ['region', 'location', 'area'] and 'region' in smart_map:
        return smart_map['region']
    if user_lower in ['category', 'type', 'product'] and 'category' in smart_map:
        return smart_map['category']
    if user_lower in ['date', 'time'] and 'date' in smart_map:
        return smart_map['date']
    
    # Fuzzy match as fallback
    cand = difflib.get_close_matches(user_term, cols, n=1, cutoff=0.6)
    return cand[0] if cand else None

def closest(columns_source: List[str] | pd.DataFrame, name: str) -> List[str]:
    cols = list(columns_source.columns) if hasattr(columns_source, "columns") else list(columns_source)
    return difflib.get_close_matches(name, cols, n=5, cutoff=0.4)