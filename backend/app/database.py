"""SQLite metadata database setup with SQLAlchemy async."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from datetime import datetime, timezone

from app.config import settings


engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class DBConnection(Base):
    """Registered database connections."""
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    db_type = Column(String(50), nullable=False)  # bigquery, postgresql, mysql, sqlite
    connection_string = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    extra_config = Column(JSON, nullable=True)


class SchemaTable(Base):
    """Discovered tables and their metadata."""
    __tablename__ = "schema_tables"

    id = Column(Integer, primary_key=True, autoincrement=True)
    connection_id = Column(Integer, nullable=False)
    schema_name = Column(String(200), nullable=True)
    table_name = Column(String(200), nullable=False)
    business_context = Column(Text, nullable=True)
    is_accessible = Column(Boolean, default=True)
    row_count = Column(Integer, nullable=True)
    discovered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SchemaColumn(Base):
    """Column metadata for discovered tables."""
    __tablename__ = "schema_columns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, nullable=False)
    column_name = Column(String(200), nullable=False)
    data_type = Column(String(100), nullable=False)
    is_nullable = Column(Boolean, default=True)
    is_primary_key = Column(Boolean, default=False)
    business_context = Column(Text, nullable=True)


class QueryLog(Base):
    """Log of all queries processed by Bruin."""
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=True)
    user_name = Column(String(200), nullable=True)
    channel = Column(String(100), nullable=True)  # slack channel or 'web'
    question = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=True)
    result_summary = Column(Text, nullable=True)
    result_data = Column(JSON, nullable=True)
    row_count = Column(Integer, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    status = Column(String(50), default="pending")  # pending, success, error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get an async database session."""
    async with async_session() as session:
        yield session
