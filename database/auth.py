
from database.supabase_client import get_supabase_client


def register_user(email: str, password: str):
    """Register a new user using Supabase Auth."""

    supabase = get_supabase_client()

    response = supabase.auth.sign_up({
        "email": email.strip(),
        "password": password
    })

    return response


def login_user(email: str, password: str):
    """Authenticate a user and return their session client."""

    supabase = get_supabase_client()

    response = supabase.auth.sign_in_with_password({
        "email": email.strip(),
        "password": password
    })

    return {
        "client": supabase,
        "user": response.user,
        "session": response.session
    }


def get_current_user(supabase):
    """Get the currently authenticated user."""

    try:
        response = supabase.auth.get_user()
        return response.user
    except Exception:
        return None


def logout_user(supabase):
    """Sign out the current user."""

    if supabase:
        supabase.auth.sign_out()
