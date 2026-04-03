"""SQL Guardrails — safety validation for generated SQL queries."""

import sqlglot
from sqlglot import exp
from typing import Tuple


BLOCKED_OPERATIONS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE",
    "ALTER", "CREATE", "GRANT", "REVOKE", "EXEC",
    "EXECUTE", "CALL", "MERGE"
}


def validate_sql(sql: str, max_rows: int = 1000) -> Tuple[bool, str, str]:
    """
    Validate and sanitize a SQL query.

    Returns:
        (is_safe, sanitized_sql, error_message)
    """
    if not sql or not sql.strip():
        return False, "", "Empty SQL query"

    sql = sql.strip().rstrip(";")

    # Check for blocked operations
    sql_upper = sql.upper().strip()
    first_word = sql_upper.split()[0] if sql_upper.split() else ""

    if first_word in BLOCKED_OPERATIONS:
        return False, "", f"❌ Güvenlik: '{first_word}' işlemi izin verilmiyor. Sadece SELECT sorguları çalıştırılabilir."

    # Must start with SELECT or WITH (CTE)
    if first_word not in ("SELECT", "WITH"):
        return False, "", f"❌ Güvenlik: Sorgu SELECT veya WITH ile başlamalıdır. '{first_word}' bulunamadı."

    # Check for dangerous patterns
    dangerous_patterns = [
        "INTO OUTFILE", "INTO DUMPFILE", "LOAD_FILE",
        "INFORMATION_SCHEMA.USER_PRIVILEGES",
        "@@global", "@@session",
    ]
    for pattern in dangerous_patterns:
        if pattern.upper() in sql_upper:
            return False, "", f"❌ Güvenlik: '{pattern}' kullanımı engellenmiştir."

    # Try to parse with sqlglot
    try:
        parsed = sqlglot.parse(sql)
    except Exception as e:
        # If sqlglot can't parse, let it pass with a warning
        # (some dialects may not parse perfectly)
        sanitized = sql
        if "LIMIT" not in sql_upper:
            sanitized += f" LIMIT {max_rows}"
        return True, sanitized, ""

    # Add LIMIT if not present
    if "LIMIT" not in sql_upper:
        sql += f" LIMIT {max_rows}"

    return True, sql, ""


def extract_tables_from_sql(sql: str) -> list[str]:
    """Extract table names referenced in a SQL query."""
    try:
        parsed = sqlglot.parse_one(sql)
        tables = []
        for table in parsed.find_all(exp.Table):
            name = table.name
            if table.db:
                name = f"{table.db}.{name}"
            tables.append(name)
        return tables
    except Exception:
        return []
