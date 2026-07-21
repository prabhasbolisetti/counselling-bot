import asyncio
from datetime import datetime, timezone

from app.core.supabase_client import supabase


def _upsert_user(phone: str, now: str):
    """
    Blocking Supabase calls, run inside a worker thread by save_user().

    - If the phone number doesn't exist -> insert a new row.
    - If it exists -> update last_seen and increment message_count.
    """

    existing = (
        supabase
        .table("users")
        .select("phone, message_count")
        .eq("phone", phone)
        .execute()
    )

    if existing.data:

        current_count = existing.data[0].get("message_count", 0) or 0

        supabase.table("users").update(
            {
                "last_seen": now,
                "message_count": current_count + 1,
            }
        ).eq("phone", phone).execute()

    else:

        supabase.table("users").insert(
            {
                "phone": phone,
                "first_seen": now,
                "last_seen": now,
                "message_count": 1,
            }
        ).execute()


async def save_user(phone: str):
    """
    Records that `phone` used the bot.

    Inserts a new row for a first-time phone number, or updates
    last_seen and increments message_count for a returning one.

    The actual Supabase client calls are synchronous, so they're run
    in a worker thread via asyncio.to_thread to avoid blocking the
    webhook's event loop. Failures are logged but never raised, so a
    Supabase hiccup can't break message processing.
    """

    now = datetime.now(timezone.utc).isoformat()

    try:

        await asyncio.to_thread(_upsert_user, phone, now)

    except Exception as e:

        print("\n" + "=" * 70)
        print("USER SERVICE ERROR")
        print("=" * 70)
        print(type(e).__name__)
        print(e)
        print("=" * 70)