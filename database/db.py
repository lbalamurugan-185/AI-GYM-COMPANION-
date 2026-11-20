
import pandas as pd


def init_db():
    """Supabase tables are created through the Supabase SQL Editor."""
    pass


def get_profile(supabase, user_id):
    """Fetch the logged-in user's profile."""
    response = (
        supabase.table("profiles")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    rows = response.data or []
    return rows[0] if rows else None


def save_profile(
    supabase,
    user_id,
    age,
    height,
    weight,
    goal,
    experience,
    days,
    equipment,
    limitations
):
    """Create or update the logged-in user's profile."""

    profile_data = {
        "user_id": user_id,
        "age": age,
        "height_cm": height,
        "weight_kg": weight,
        "goal": goal if isinstance(goal, list) else [goal],
        "experience": experience,
        "days_per_week": days,
        "equipment": equipment,
        "limitations": limitations
    }

    return (
        supabase.table("profiles")
        .upsert(profile_data, on_conflict="user_id")
        .execute()
    )


def add_progress(supabase, user_id, entry_date, weight, workouts, notes):
    """Save progress for the logged-in user."""

    progress_data = {
        "user_id": user_id,
        "entry_date": str(entry_date),
        "weight_kg": weight,
        "workouts_completed": workouts,
        "notes": notes
    }

    return (
        supabase.table("progress")
        .insert(progress_data)
        .execute()
    )


def get_progress(supabase, user_id):
    """Fetch only the logged-in user's progress."""

    response = (
        supabase.table("progress")
        .select("entry_date, weight_kg, workouts_completed, notes")
        .eq("user_id", user_id)
        .order("entry_date")
        .execute()
    )

    return pd.DataFrame(
        response.data or [],
        columns=[
            "entry_date",
            "weight_kg",
            "workouts_completed",
            "notes"
        ]
    )


def save_plan(supabase, user_id, plan_text):
    """Save a workout plan for the logged-in user."""

    return (
        supabase.table("workout_plans")
        .insert({
            "user_id": user_id,
            "plan_text": plan_text
        })
        .execute()
    )


def get_latest_plan(supabase, user_id):
    """Fetch the logged-in user's latest workout plan."""

    response = (
        supabase.table("workout_plans")
        .select("created_at, plan_text")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    rows = response.data or []
    return rows[0] if rows else None
