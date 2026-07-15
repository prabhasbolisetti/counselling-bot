import httpx

from app.core.config import settings


GRAPH_URL = (
    f"https://graph.facebook.com/"
    f"{settings.GRAPH_API_VERSION}/"
    f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
)


async def send_text_message(
    phone: str,
    message: str,
):
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message,
        },
    }

    async with httpx.AsyncClient(timeout=20) as client:

        response = await client.post(
            GRAPH_URL,
            headers=headers,
            json=payload,
        )

    print("\n" + "=" * 70)
    print("META SEND MESSAGE")
    print("=" * 70)
    print("Status Code :", response.status_code)
    print("Response    :", response.text)
    print("=" * 70 + "\n")

    return response.json()


async def send_document(
    phone: str,
    document_url: str,
    filename: str,
):
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "document",
        "document": {
            "link": document_url,
            "filename": filename,
        },
    }

    async with httpx.AsyncClient(timeout=20) as client:

        response = await client.post(
            GRAPH_URL,
            headers=headers,
            json=payload,
        )

    print("\n" + "=" * 70)
    print("META SEND DOCUMENT")
    print("=" * 70)
    print("Status Code :", response.status_code)
    print("Response    :", response.text)
    print("=" * 70 + "\n")

    return response.json()