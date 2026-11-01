import time
from typing import Dict, Any, List
from sqlalchemy import text
from sqlalchemy.orm import Session
from .pivot_sanitizer import sanitize_records


class OLAPExecutor:
    """Executes generated OLAP queries, timing their performance and guaranteeing clean JSON responses."""

    @staticmethod
    def execute(
        session: Session,
        sql: str,
        params: Dict[str, Any] | None = None,
        operation: str = "custom"
    ) -> Dict[str, Any]:
        params = params or {}
        start_time = time.perf_counter()
        
        cursor = session.execute(text(sql), params)
        raw_rows = [dict(row) for row in cursor.mappings().all()]
        
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        sanitized_data = sanitize_records(raw_rows)
        columns = list(sanitized_data[0].keys()) if sanitized_data else []

        return {
            "operation": operation,
            "sql_query": sql.strip(),
            "parameters": params,
            "execution_time_ms": duration_ms,
            "row_count": len(sanitized_data),
            "columns": columns,
            "data": sanitized_data
        }

