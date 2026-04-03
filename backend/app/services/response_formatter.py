"""Response formatter — formats query results for Slack and web display."""

import json
from typing import Any


def format_number(value: Any) -> str:
    """Format a number for display."""
    if value is None:
        return "N/A"
    if isinstance(value, float):
        if abs(value) >= 1_000_000:
            return f"${value / 1_000_000:,.1f}M"
        elif abs(value) >= 1_000:
            return f"${value / 1_000:,.1f}K"
        else:
            return f"${value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def format_as_slack_blocks(result: dict) -> dict:
    """
    Format a query result as Slack Block Kit message.

    Args:
        result: Full result dict from BruinAgent.ask()
    """
    blocks = []

    if not result.get("success"):
        # Error message
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"❌ *Hata*\n{result.get('error', 'Bilinmeyen hata')}"
            }
        })
        return {"blocks": blocks}

    # Header
    blocks.append({
        "type": "header",
        "text": {"type": "plain_text", "text": "📊 Bruin Veri Yanıtı", "emoji": True}
    })

    # Interpretation
    if result.get("interpretation"):
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": result["interpretation"]}
        })

    # Data table (if present and small enough)
    query_result = result.get("result", {})
    columns = query_result.get("columns", [])
    rows = query_result.get("rows", [])

    if columns and rows and len(rows) <= 10:
        # Format as text table
        table_text = format_as_text_table(columns, rows)
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"```\n{table_text}\n```"}
        })
    elif rows and len(rows) > 10:
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"📋 Toplam {query_result.get('row_count', len(rows))} satır sonuç döndü. İlk 10 satır gösterildi."
            }]
        })

    # Metadata footer
    meta_parts = []
    if result.get("execution_time_ms"):
        meta_parts.append(f"⏱️ {result['execution_time_ms']:.0f}ms")
    if result.get("confidence"):
        confidence_pct = int(result["confidence"] * 100)
        meta_parts.append(f"🎯 %{confidence_pct} güven")

    if meta_parts:
        blocks.append({
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": " | ".join(meta_parts)}]
        })

    # SQL button
    if result.get("sql"):
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"🔍 SQL: `{result['sql'][:150]}{'...' if len(result.get('sql', '')) > 150 else ''}`"
            }]
        })

    return {"blocks": blocks}


def format_as_text_table(columns: list[str], rows: list[list], max_col_width: int = 20) -> str:
    """Format data as a plain text table."""
    if not columns or not rows:
        return "Veri bulunamadı."

    # Calculate column widths
    widths = []
    for i, col in enumerate(columns):
        col_values = [str(row[i]) if i < len(row) else "" for row in rows[:10]]
        max_val_width = max((len(v) for v in col_values), default=0)
        widths.append(min(max(len(col), max_val_width), max_col_width))

    # Header
    header = " | ".join(col.ljust(widths[i])[:widths[i]] for i, col in enumerate(columns))
    separator = "-+-".join("-" * widths[i] for i in range(len(columns)))

    # Rows
    row_lines = []
    for row in rows[:10]:
        cells = []
        for i, val in enumerate(row):
            if i < len(widths):
                cell = str(val) if val is not None else "NULL"
                cells.append(cell.ljust(widths[i])[:widths[i]])
        row_lines.append(" | ".join(cells))

    return f"{header}\n{separator}\n" + "\n".join(row_lines)


def format_for_web(result: dict) -> dict:
    """
    Format a query result for the web admin panel.
    Returns a clean JSON structure.
    """
    if not result.get("success"):
        return {
            "type": "error",
            "message": result.get("error", "Bilinmeyen hata"),
            "interpretation": result.get("interpretation"),
        }

    query_result = result.get("result", {})

    return {
        "type": "success",
        "question": result.get("question"),
        "interpretation": result.get("interpretation"),
        "sql": result.get("sql"),
        "explanation": result.get("explanation"),
        "visualization_hint": result.get("visualization_hint", "table"),
        "confidence": result.get("confidence", 0),
        "execution_time_ms": result.get("execution_time_ms", 0),
        "data": {
            "columns": query_result.get("columns", []),
            "rows": query_result.get("rows", []),
            "row_count": query_result.get("row_count", 0),
            "truncated": query_result.get("truncated", False),
        }
    }
