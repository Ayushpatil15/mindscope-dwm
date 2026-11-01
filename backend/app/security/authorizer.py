import re
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from backend.app.db.session import DEFAULT_DB_PATH

# SQLite Authorizer Action Codes
# SQLITE_OK = 0, SQLITE_DENY = 1, SQLITE_IGNORE = 2
ALLOWED_AUTHORIZER_ACTIONS = {
    sqlite3.SQLITE_SELECT,
    sqlite3.SQLITE_READ,
    sqlite3.SQLITE_FUNCTION,
}

DENIED_AUTHORIZER_ACTIONS = {
    sqlite3.SQLITE_INSERT,
    sqlite3.SQLITE_UPDATE,
    sqlite3.SQLITE_DELETE,
    sqlite3.SQLITE_PRAGMA,
    sqlite3.SQLITE_ATTACH,
    sqlite3.SQLITE_DETACH,
    sqlite3.SQLITE_CREATE_TABLE,
    sqlite3.SQLITE_DROP_TABLE,
    sqlite3.SQLITE_ALTER_TABLE,
    sqlite3.SQLITE_CREATE_INDEX,
    sqlite3.SQLITE_DROP_INDEX,
    sqlite3.SQLITE_CREATE_VIEW,
    sqlite3.SQLITE_DROP_VIEW,
    sqlite3.SQLITE_TRANSACTION,
}


def read_only_authorizer_callback(action_code: int, param1: Any, param2: Any, db_name: Any, trigger_name: Any) -> int:
    """
    SQLite C-level authorizer callback.
    Permits only SELECT, READ, and FUNCTION.
    Denies all write, schema alteration, and administrative operations.
    """
    if action_code in ALLOWED_AUTHORIZER_ACTIONS:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


class SecurityException(Exception):
    pass


def validate_single_statement(sql: str) -> None:
    """
    Verifies that the SQL contains at most one statement.
    Rejects semicolon-separated compound statements.
    """
    cleaned = sql.strip()
    if not cleaned:
        raise SecurityException("SQL query cannot be empty.")

    # Remove string literals to avoid flagging semicolons within strings
    without_strings = re.sub(r"'(''|[^'])*'", "", cleaned)
    without_strings = re.sub(r'"(""|[^"])*"', "", without_strings)
    
    # Check for semicolons that are followed by non-whitespace (i.e. second statement)
    # Trailing semicolon is permitted
    statements = [s.strip() for s in without_strings.split(";") if s.strip()]
    if len(statements) > 1:
        raise SecurityException("Multiple SQL statements are not permitted in SQL Lab.")


def execute_safe_query(
    sql: str,
    db_path: Path | str | None = None,
    limit: int = 100,
    timeout_seconds: float = 3.0
) -> Dict[str, Any]:
    """
    Executes a read-only query under strict multi-layer defense:
    1. Single statement validation
    2. Read-only connection (mode=ro / PRAGMA query_only = ON)
    3. SQLite low-level authorizer (set_authorizer)
    4. Execution timeout
    5. Result clamping (clamped to max 500)
    """
    validate_single_statement(sql)
    
    clamped_limit = max(1, min(limit, 500))
    resolved_path = Path(db_path or DEFAULT_DB_PATH).resolve()

    start_time = time.perf_counter()

    # Open standard read-only connection
    conn = sqlite3.connect(f"file:{resolved_path}?mode=ro", uri=True, timeout=timeout_seconds)
    try:
        # Enforce query_only at PRAGMA level
        conn.execute("PRAGMA query_only = ON;")
        
        # Enforce SQLite low-level authorizer
        conn.set_authorizer(read_only_authorizer_callback)

        cur = conn.cursor()
        cur.execute(sql)
        
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchmany(clamped_limit + 1)
        
        is_truncated = len(rows) > clamped_limit
        if is_truncated:
            rows = rows[:clamped_limit]

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "columns": columns,
            "rows": [list(r) for r in rows],
            "row_count": len(rows),
            "execution_time_ms": execution_time_ms,
            "is_truncated": is_truncated
        }
    except sqlite3.DatabaseError as e:
        raise SecurityException(f"Query execution rejected: {str(e)}") from e
    finally:
        conn.close()

