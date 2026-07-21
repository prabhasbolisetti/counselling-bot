import asyncio
from time import time

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.core.config import settings
from app.services.conversation_service import process_message
from app.services.whatsapp_service import (
    send_text_message,
    send_typing_indicator,
)

router = APIRouter(tags=["WhatsApp"])

# Processed WhatsApp message IDs
PROCESSED_MESSAGES = {}
MESSAGE_TTL = 300  # seconds


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    if (
        hub_mode == "subscribe"
        and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN
    ):
        return PlainTextResponse(hub_challenge)

    raise HTTPException(
        status_code=403,
        detail="Verification failed",
    )


@router.post("/webhook")
async def receive_message(request: Request):

    try:
        payload = await request.json()

    except Exception:
        return {"status": "invalid_json"}

    try:

        value = (
            payload
            .get("entry", [{}])[0]
            .get("changes", [{}])[0]
            .get("value", {})
        )

        # Ignore delivery/read/status updates
        if "statuses" in value:
            return {"status": "ignored"}

        messages = value.get("messages")

        if not messages:
            return {"status": "ignored"}

        message = messages[0]

        message_id = message.get("id")

        if not message_id:
            return {"status": "ignored"}

        # Remove expired message IDs
        current_time = time()

        expired_ids = [
            msg_id
            for msg_id, ts in PROCESSED_MESSAGES.items()
            if current_time - ts > MESSAGE_TTL
        ]

        for msg_id in expired_ids:
            del PROCESSED_MESSAGES[msg_id]

        # Ignore duplicate webhook deliveries
        if message_id in PROCESSED_MESSAGES:
            print("\n" + "=" * 70)
            print("DUPLICATE MESSAGE IGNORED")
            print("=" * 70)
            print(f"Message ID: {message_id}")
            print("=" * 70)

            return {"status": "duplicate"}

        PROCESSED_MESSAGES[message_id] = current_time

        if message.get("type") != "text":
            return {"status": "ignored"}

        phone = message.get("from")

        text = (
            message
            .get("text", {})
            .get("body")
        )

        if not phone or not text:
            return {"status": "ignored"}

        text = text.strip()

        if not text:
            return {"status": "ignored"}

        print("\n" + "=" * 70)
        print("INCOMING MESSAGE")
        print("=" * 70)
        print("Phone      :", phone)
        print("Message ID :", message_id)
        print("Message    :", text)

        # Show typing indicator immediately
        await send_typing_indicator(message_id)

        await asyncio.sleep(1.5)

        reply = await process_message(
            phone,
            text,
        )

        print("Reply   :", reply)

        result = await send_text_message(
            phone,
            reply,
        )

        print("\nSEND RESULT")
        print(result)

    except Exception as e:

        print("\n" + "=" * 70)
        print("WEBHOOK ERROR")
        print("=" * 70)
        print(type(e).__name__)
        print(e)
        print("=" * 70)

    return {"status": "ok"}