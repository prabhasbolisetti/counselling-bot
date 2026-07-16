from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.core.config import settings
from app.services.conversation_service import process_message
from app.services.whatsapp_service import (
    send_document,
    send_text_message,
)

router = APIRouter(tags=["WhatsApp"])

BASE_URL = settings.PUBLIC_BASE_URL


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
        print("Phone   :", phone)
        print("Message :", text)

        reply = await process_message(
            phone,
            text,
        )

        print("Reply   :", reply)

        if reply == "__SEND_CUTOFF_PDF__":

            result = await send_document(
                phone=phone,
                document_url=f"{BASE_URL}/pdf/cutoff",
                filename="category_cutoff.pdf",
            )

        elif reply == "__SEND_DOCUMENTS_PDF__":

            result = await send_document(
                phone=phone,
                document_url=f"{BASE_URL}/pdf/documents",
                filename="documents.pdf",
            )

        else:

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