"""Bruin — Conversational Data Assistant Backend."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.services.demo_data import create_demo_database
from app.routers import health, chat, schemas, queries, slack_events


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Initialize metadata database
    await init_db()
    print("✅ Metadata database initialized")

    # Create demo data if not exists
    if not os.path.exists(settings.demo_database_path):
        create_demo_database(settings.demo_database_path)
        print("✅ Demo database created with sample data")
    else:
        print("✅ Demo database already exists")

    yield

    print("👋 Bruin shutting down")


app = FastAPI(
    title="Bruin — Conversational Data Assistant",
    description="Doğal dil ile veri sorgulama API'si. Slack entegrasyonu ve web arayüzü destekler.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(schemas.router, prefix="/api/v1")
app.include_router(queries.router, prefix="/api/v1")
app.include_router(slack_events.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "Bruin",
        "tagline": "Doğal dil ile şirket verilerinizi sorgulayın 🤖",
        "docs": "/docs",
        "version": "1.0.0",
    }
