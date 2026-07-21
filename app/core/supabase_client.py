from supabase import create_client, Client

from app.core.config import settings


# ------------------------------------------------------------------
# Shared Supabase client used across services (user_service, etc).
#
# Requires SUPABASE_URL and SUPABASE_KEY to be defined in your
# settings (app/core/config.py) and in your .env file.
#
# Use the service_role key (not the anon key) if this client needs
# to bypass Row Level Security to write to the users table from
# your backend.
# ------------------------------------------------------------------

supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY,
)