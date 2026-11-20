
from supabase import create_client, Client
from config import get_config


def get_supabase_client() -> Client:
    """Create and return a Supabase client."""

    supabase_url = get_config("SUPABASE_URL")
    supabase_key = get_config("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise RuntimeError(
            "Supabase credentials are missing. "
            "Check SUPABASE_URL and SUPABASE_KEY in your .env file."
        )

    if not supabase_url.startswith("https://"):
        raise ValueError("Invalid Supabase project URL.")

    return create_client(supabase_url, supabase_key)
