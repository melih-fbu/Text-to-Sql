"""Query history router."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_session, QueryLog

router = APIRouter(prefix="/queries", tags=["Queries"])


@router.get("/history")
async def get_query_history(
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """Get query history with optional filtering."""
    query = select(QueryLog).order_by(desc(QueryLog.created_at))

    if status:
        query = query.where(QueryLog.status == status)

    query = query.offset(offset).limit(limit)
    result = await session.execute(query)
    logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "user_name": log.user_name,
            "channel": log.channel,
            "question": log.question,
            "generated_sql": log.generated_sql,
            "result_summary": log.result_summary,
            "row_count": log.row_count,
            "execution_time_ms": log.execution_time_ms,
            "status": log.status,
            "error_message": log.error_message,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@router.get("/stats")
async def get_query_stats(session: AsyncSession = Depends(get_session)):
    """Get query statistics for the dashboard."""
    # Total queries
    total = await session.execute(select(func.count(QueryLog.id)))
    total_count = total.scalar() or 0

    # Successful queries
    success = await session.execute(
        select(func.count(QueryLog.id)).where(QueryLog.status == "success")
    )
    success_count = success.scalar() or 0

    # Failed queries
    error = await session.execute(
        select(func.count(QueryLog.id)).where(QueryLog.status == "error")
    )
    error_count = error.scalar() or 0

    # Average execution time
    avg_time = await session.execute(
        select(func.avg(QueryLog.execution_time_ms)).where(QueryLog.status == "success")
    )
    avg_execution_time = round(avg_time.scalar() or 0, 2)

    return {
        "total_queries": total_count,
        "successful_queries": success_count,
        "failed_queries": error_count,
        "success_rate": round(success_count / max(total_count, 1) * 100, 1),
        "avg_execution_time_ms": avg_execution_time,
    }
