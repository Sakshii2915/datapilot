import time
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, List, Optional
from sqlalchemy import text, Engine
from backend.app.core.config import settings
from backend.app.core.logging import logger

def serialize_row_value(val: Any) -> Any:
    """Serializes SQL row values into JSON-compatible types."""
    if val is None:
        return None
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    return val

class QueryExecutor:
    def __init__(self, readonly_engine: Engine, timeout_seconds: int = 10, max_rows: int = 100):
        self.engine = readonly_engine
        self.timeout_seconds = timeout_seconds or settings.QUERY_TIMEOUT_SECONDS
        self.max_rows = max_rows or settings.MAX_RESULT_ROWS

    def execute_query(self, sanitized_sql: str) -> Dict[str, Any]:
        """
        Executes a validated, read-only SQL query against the database engine.
        Applies execution timeouts, returns structured JSON rows, and tracks duration.
        """
        start_time = time.perf_counter()
        is_postgres = "postgres" in str(self.engine.url).lower()

        try:
            with self.engine.connect() as conn:
                # Apply statement timeout for PostgreSQL
                if is_postgres:
                    timeout_ms = int(self.timeout_seconds * 1000)
                    conn.execute(text(f"SET statement_timeout = {timeout_ms}"))

                cursor_result = conn.execute(text(sanitized_sql))
                execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

                if cursor_result.returns_rows:
                    columns = list(cursor_result.keys())
                    raw_rows = cursor_result.fetchmany(self.max_rows)
                    rows = [
                        {col: serialize_row_value(row[i]) for i, col in enumerate(columns)}
                        for row in raw_rows
                    ]
                    row_count = len(rows)
                else:
                    columns = []
                    rows = []
                    row_count = 0

                return {
                    "status": "success",
                    "execution_time_ms": execution_time_ms,
                    "columns": columns,
                    "rows": rows,
                    "row_count": row_count,
                    "error": None
                }

        except Exception as e:
            execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            raw_err = str(e)
            logger.error(f"Query execution failed: {raw_err}")

            # Sanitize error to prevent leaking connection details or credentials
            sanitized_err = self._sanitize_error(raw_err)

            return {
                "status": "error",
                "execution_time_ms": execution_time_ms,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "error": sanitized_err
            }

    def _sanitize_error(self, error_str: str) -> str:
        """Removes internal connection strings or credentials from error messages."""
        # Clean SQLAlchemy driver prefixes
        msg = error_str
        if "(Background on this error at:" in msg:
            msg = msg.split("(Background on this error at:")[0].strip()
        if "postgresql://" in msg or "sqlite://" in msg:
            # Mask potential URLs
            import re
            msg = re.sub(r"://[^@]+@", "://***:***@", msg)
        return msg
