import asyncio
from datetime import datetime, timezone

from app.core.supabase_client import supabase


def _insert_if_new(phone: str, now: str):
    """
    Blocking Supabase calls, run inside a worker thread by
    save_user_if_new().

    - If the phone number already exists -> do nothing.
    - If it doesn't -> insert a single row with first_seen.
    """

    existing = (
        supabase
        .table("users")
        .select("phone")
        .eq("phone", phone)
        .execute()
    )

    if existing.data:
        return

    supabase.table("users").insert(
        {
            "phone": phone,
            "first_seen": now,
        }
    ).execute()


async def save_user_if_new(phone: str):
    """
    Records `phone` in the users table exactly once.

    Call this only when a user starts/restarts a conversation (e.g.
    on "hi"/"hello"/"start"), not on every message - so one user ends
    up with exactly one row no matter how many messages they send.

    The actual Supabase client calls are synchronous, so they're run
    in a worker thread via asyncio.to_thread to avoid blocking the
    webhook's event loop. Failures are logged but never raised, so a
    Supabase hiccup can't break message processing.
    """

    now = datetime.now(timezone.utc).isoformat()

    try:

        await asyncio.to_thread(_insert_if_new, phone, now)

    except Exception as e:

        print("\n" + "=" * 70)
        print("USER SERVICE ERROR")
        print("=" * 70)
        print(type(e).__name__)
        print(e)
        print("=" * 70)