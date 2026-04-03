"""Query executor — runs SQL queries against different database backends."""

import sqlite3
import time
from typing import Any
from app.config import settings


class QueryResult:
    """Structured query result."""

    def __init__(
        self,
        columns: list[str],
        rows: list[list[Any]],
        row_count: int,
        execution_time_ms: float,
        truncated: bool = False,
    ):
        self.columns = columns
        self.rows = rows
        self.row_count = row_count
        self.execution_time_ms = execution_time_ms
        self.truncated = truncated

    def to_dict(self) -> dict:
        return {
            "columns": self.columns,
            "rows": self.rows,
            "row_count": self.row_count,
            "execution_time_ms": self.execution_time_ms,
            "truncated": self.truncated,
        }

    def to_table_data(self) -> list[dict]:
        """Convert to list of dicts for easier formatting."""
        return [dict(zip(self.columns, row)) for row in self.rows]


def execute_sqlite_query(db_path: str, sql: str, max_rows: int = 1000) -> QueryResult:
    """Execute a read-only SQL query against a SQLite database."""
    start = time.perf_counter()

    # Open database in read-only mode via URI
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=10)
    conn.execute("PRAGMA query_only = ON")

    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        all_rows = cursor.fetchall()

        truncated = len(all_rows) > max_rows
        rows = [list(row) for row in all_rows[:max_rows]]

        elapsed = (time.perf_counter() - start) * 1000

        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(all_rows),
            execution_time_ms=round(elapsed, 2),
            truncated=truncated,
        )
    except Exception as e:
        raise Exception(f"SQL Execution Error: {str(e)}")
    finally:
        conn.close()


def execute_query(connection_type: str, connection_string: str, sql: str, max_rows: int = 1000) -> QueryResult:
    """Execute a query based on connection type."""
    if connection_type == "sqlite":
        return execute_sqlite_query(connection_string, sql, max_rows)
    elif connection_type == "bigquery":
        raise NotImplementedError("BigQuery executor coming soon. Use SQLite demo for now.")
    elif connection_type == "postgresql":
        raise NotImplementedError("PostgreSQL executor coming soon. Use SQLite demo for now.")
    elif connection_type == "mysql":
        raise NotImplementedError("MySQL executor coming soon. Use SQLite demo for now.")
    else:
        raise ValueError(f"Unknown connection type: {connection_type}")
