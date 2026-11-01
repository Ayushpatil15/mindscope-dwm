import math
from typing import Any, Dict, List


def sanitize_cell_value(val: Any) -> Any:
    """Replaces non-compliant float NaN or inf values with None."""
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
    return val


def sanitize_record(row: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitizes all cell values in a single row mapping."""
    return {k: sanitize_cell_value(v) for k, v in row.items()}


def sanitize_records(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sanitizes a list of dictionary records for clean JSON serialization."""
    return [sanitize_record(r) for r in rows]

