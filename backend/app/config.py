"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Gemini AI
    gemini_api_key: str = "demo-key"

    # Slack (optional)
    slack_bot_token: Optional[str] = None
    slack_signing_secret: Optional[str] = None

    # BigQuery (optional)
    google_project_id: Optional[str] = None
    google_application_credentials: Optional[str] = None

    # Database
    database_url: str = "sqlite+aiosqlite:///./bruin.db"
    demo_database_path: str = "./demo_data.db"

    # Settings
    max_query_rows: int = 1000
    schema_refresh_hours: int = 6

    # Frontend
    frontend_url: str = "http://localhost:5173"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
