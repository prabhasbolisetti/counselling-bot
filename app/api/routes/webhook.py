from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.core.config import settings
from app.services.conversation_service import process_message
from app.services.whatsapp_service import (
    send_document,
    send_text_message,
)

router = APIRouter(tags=["WhatsApp"])


BASE_URL = "https://savior-renewal-quiet.ngrok-free.dev"


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

    payload = await request.json()

    print("\n" + "=" * 70)
    print("INCOMING PAYLOAD")
    print("=" * 70)
    print(payload)
    print("=" * 70)

    try:

        value = payload["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return {"status": "ignored"}

        message = value["messages"][0]

        if message["type"] != "text":
            return {"status": "ignored"}

        phone = message["from"]
        text = message["text"]["body"]

        print(f"Phone   : {phone}")
        print(f"Message : {text}")

        reply = await process_message(
            phone,
            text,
        )

        print(f"Reply   : {reply}")

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

        print("\nWEBHOOK ERROR")
        print(e)

    return {"status": "ok"}