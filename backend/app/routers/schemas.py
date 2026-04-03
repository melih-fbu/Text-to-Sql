"""Schema management router."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_session, SchemaTable, SchemaColumn
from app.services.schema_discovery import discover_sqlite_schema

router = APIRouter(prefix="/schemas", tags=["Schemas"])


@router.get("/discover")
async def discover_schema():
    """Discover schema from the demo database."""
    schema = await discover_sqlite_schema(settings.demo_database_path)
    return schema


@router.get("/tables")
async def list_tables(session: AsyncSession = Depends(get_session)):
    """List all registered tables."""
    result = await session.execute(select(SchemaTable).order_by(SchemaTable.table_name))
    tables = result.scalars().all()
    return [
        {
            "id": t.id,
            "table_name": t.table_name,
            "schema_name": t.schema_name,
            "business_context": t.business_context,
            "is_accessible": t.is_accessible,
            "row_count": t.row_count,
        }
        for t in tables
    ]


@router.get("/tables/{table_name}/columns")
async def get_table_columns(table_name: str):
    """Get columns for a specific table from the demo database."""
    schema = await discover_sqlite_schema(settings.demo_database_path)
    for table in schema["tables"]:
        if table["table_name"] == table_name:
            return table
    return {"error": f"Table '{table_name}' not found"}
