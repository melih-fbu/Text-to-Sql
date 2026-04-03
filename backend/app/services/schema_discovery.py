"""Schema discovery service — auto-discovers tables and columns from databases."""

import sqlite3
import re
from typing import Optional
from app.config import settings


def _safe_identifier(name: str) -> str:
    """Sanitize a SQL identifier to prevent injection."""
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        raise ValueError(f"Invalid identifier: {name}")
    return name


async def discover_sqlite_schema(db_path: str) -> dict:
    """
    Discover all tables and columns from a SQLite database.

    Returns a dict like:
    {
        "tables": [
            {
                "table_name": "deals",
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False, "pk": True},
                    ...
                ],
                "row_count": 200,
                "sample_data": [...]
            }
        ]
    }
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        table_names = [row[0] for row in cursor.fetchall()]

        tables = []
        for table_name in table_names:
            if table_name.startswith("sqlite_"):
                continue

            safe_name = _safe_identifier(table_name)

            # Get column info
            cursor.execute(f"PRAGMA table_info([{safe_name}])")
            columns = []
            for col in cursor.fetchall():
                columns.append({
                    "name": col[1],
                    "type": col[2] or "TEXT",
                    "nullable": not col[3],
                    "pk": bool(col[5]),
                })

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM [{safe_name}]")
            row_count = cursor.fetchone()[0]

            # Get sample data (5 rows)
            cursor.execute(f"SELECT * FROM [{safe_name}] LIMIT 5")
            sample_rows = cursor.fetchall()
            col_names = [c["name"] for c in columns]
            sample_data = [dict(zip(col_names, row)) for row in sample_rows]

            tables.append({
                "table_name": table_name,
                "columns": columns,
                "row_count": row_count,
                "sample_data": sample_data,
            })

        return {"tables": tables}
    finally:
        conn.close()


def format_schema_for_prompt(schema: dict, business_contexts: Optional[dict] = None) -> str:
    """
    Format schema information into a string for the AI prompt.

    Args:
        schema: Schema dict from discover_sqlite_schema
        business_contexts: Optional dict of table.column -> description
    """
    lines = []
    for table in schema["tables"]:
        table_name = table["table_name"]
        row_count = table["row_count"]

        # Table-level context
        table_ctx = ""
        if business_contexts and table_name in business_contexts:
            table_ctx = f" -- {business_contexts[table_name]}"

        lines.append(f"\n📋 Tablo: {table_name} ({row_count:,} satır){table_ctx}")
        lines.append("-" * 60)

        for col in table["columns"]:
            pk = " [PK]" if col["pk"] else ""
            nullable = " NULL" if col["nullable"] else " NOT NULL"
            col_key = f"{table_name}.{col['name']}"
            col_ctx = ""
            if business_contexts and col_key in business_contexts:
                col_ctx = f" -- {business_contexts[col_key]}"
            lines.append(f"  • {col['name']}: {col['type']}{pk}{nullable}{col_ctx}")

        # Sample data preview
        if table["sample_data"]:
            lines.append(f"\n  Örnek veri ({min(3, len(table['sample_data']))} satır):")
            for row in table["sample_data"][:3]:
                preview = ", ".join(f"{k}={v}" for k, v in list(row.items())[:5])
                lines.append(f"    → {preview}")

    return "\n".join(lines)
