"""Chat/test endpoint — test Bruin without Slack."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.config import settings
from app.database import get_session, QueryLog
from app.services.ai_agent import agent
from app.services.response_formatter import format_for_web

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    type: str
    question: str | None = None
    interpretation: str | None = None
    sql: str | None = None
    explanation: str | None = None
    visualization_hint: str = "table"
    confidence: float = 0
    execution_time_ms: float = 0
    data: dict | None = None
    message: str | None = None


@router.post("/ask", response_model=ChatResponse)
async def ask_bruin(req: ChatRequest, session: AsyncSession = Depends(get_session)):
    """
    Ask Bruin a question in natural language.
    This is the main web-based testing endpoint.
    """
    # Run the AI pipeline
    result = await agent.ask(req.question, settings.demo_database_path)

    # Log the query
    log = QueryLog(
        user_name="web_user",
        channel="web",
        question=req.question,
        generated_sql=result.get("sql"),
        result_summary=result.get("interpretation"),
        result_data=result.get("result"),
        row_count=result.get("result", {}).get("row_count") if result.get("result") else None,
        execution_time_ms=result.get("execution_time_ms"),
        status="success" if result.get("success") else "error",
        error_message=result.get("error"),
        created_at=datetime.now(timezone.utc),
    )
    session.add(log)
    await session.commit()

    # Format for web
    return format_for_web(result)
