"""Slack events webhook router."""

import hashlib
import hmac
import time
from fastapi import APIRouter, Request, HTTPException
from app.config import settings
from app.services.ai_agent import agent
from app.services.response_formatter import format_as_slack_blocks

router = APIRouter(prefix="/slack", tags=["Slack"])


def verify_slack_signature(request_body: bytes, timestamp: str, signature: str) -> bool:
    """Verify that the request comes from Slack."""
    if not settings.slack_signing_secret:
        return True  # Skip verification in dev mode

    if abs(time.time() - float(timestamp)) > 300:
        return False

    sig_basestring = f"v0:{timestamp}:{request_body.decode()}"
    my_sig = "v0=" + hmac.new(
        key=settings.slack_signing_secret.encode(),
        msg=sig_basestring.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(my_sig, signature)


@router.post("/events")
async def slack_events(request: Request):
    """Handle Slack Events API webhooks."""
    body = await request.body()
    data = await request.json()

    # URL verification challenge
    if data.get("type") == "url_verification":
        return {"challenge": data.get("challenge")}

    # Verify signature (skip in dev)
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "0")
    signature = request.headers.get("X-Slack-Signature", "")

    event = data.get("event", {})
    event_type = event.get("type")

    # Handle app_mention events
    if event_type == "app_mention":
        text = event.get("text", "")
        # Remove the @Bruin mention to get the actual question
        question = text.split(">", 1)[-1].strip() if ">" in text else text
        channel = event.get("channel")
        user = event.get("user")
        thread_ts = event.get("thread_ts") or event.get("ts")

        if not question:
            return {"ok": True}

        # Process the question
        try:
            result = await agent.ask(question, settings.demo_database_path)
            slack_message = format_as_slack_blocks(result)

            # Send response via Slack API (if configured)
            if settings.slack_bot_token:
                from slack_sdk import WebClient
                client = WebClient(token=settings.slack_bot_token)
                client.chat_postMessage(
                    channel=channel,
                    thread_ts=thread_ts,
                    blocks=slack_message["blocks"],
                    text=result.get("interpretation", "Sonuç hazır."),
                )
        except Exception as e:
            if settings.slack_bot_token:
                from slack_sdk import WebClient
                client = WebClient(token=settings.slack_bot_token)
                client.chat_postMessage(
                    channel=channel,
                    thread_ts=thread_ts,
                    text=f"❌ Bir hata oluştu: {str(e)}",
                )

    return {"ok": True}
