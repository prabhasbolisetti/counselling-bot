import asyncio

import httpx

from app.core.config import settings


GRAPH_URL = (
    f"https://graph.facebook.com/"
    f"{settings.GRAPH_API_VERSION}/"
    f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
)

HEADERS = {
    "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

TIMEOUT = httpx.Timeout(20.0)

MAX_RETRIES = 3


async def _send(payload: dict):
    """
    Sends a request to the WhatsApp Cloud API.

    Retries temporary failures before raising an exception.
    """

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            async with httpx.AsyncClient(
                timeout=TIMEOUT,
            ) as client:

                response = await client.post(
                    GRAPH_URL,
                    headers=HEADERS,
                    json=payload,
                )

            print("\n" + "=" * 70)
            print(f"META REQUEST (Attempt {attempt})")
            print("=" * 70)
            print("Status :", response.status_code)
            print("Body   :", response.text)
            print("=" * 70 + "\n")

            if response.status_code < 500:
                return response.json()

        except (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.NetworkError,
        ) as e:

            last_error = e

            print("\nNETWORK ERROR")
            print(e)

        if attempt < MAX_RETRIES:
            await asyncio.sleep(attempt)

    if last_error:
        raise last_error

    raise RuntimeError(
        "Meta API request failed after retries."
    )


async def send_text_message(
    phone: str,
    message: str,
):

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message,
        },
    }

    return await _send(payload)


async def send_document(
    phone: str,
    document_url: str,
    filename: str,
):

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "document",
        "document": {
            "link": document_url,
            "filename": filename,
        },
    }

    return await _send(payload)


async def send_typing_indicator(
    message_id: str,
):
    """
    Shows WhatsApp typing indicator.
    Also marks the incoming message as read.
    """

    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
        "typing_indicator": {
            "type": "text",
        },
    }

    return await _send(payload)