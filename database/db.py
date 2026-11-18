import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "gym_companion.db"

def connect():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY CHECK(id=1), age INTEGER NOT NULL, height_cm REAL NOT NULL,
            weight_kg REAL NOT NULL, goal TEXT NOT NULL, experience TEXT NOT NULL,
            days_per_week INTEGER NOT NULL, equipment TEXT NOT NULL, limitations TEXT DEFAULT '')""")
        c.execute("""CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT, entry_date TEXT NOT NULL, weight_kg REAL NOT NULL,
            workouts_completed INTEGER NOT NULL DEFAULT 0, notes TEXT DEFAULT '')""")
        c.execute("""CREATE TABLE IF NOT EXISTS workout_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            plan_text TEXT NOT NULL)""")

def save_profile(age,height,weight,goal,experience,days,equipment,limitations):
    with connect() as c:
        c.execute("""INSERT INTO profile VALUES (1,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET age=excluded.age,height_cm=excluded.height_cm,
        weight_kg=excluded.weight_kg,goal=excluded.goal,experience=excluded.experience,
        days_per_week=excluded.days_per_week,equipment=excluded.equipment,limitations=excluded.limitations""",
        (age,height,weight,goal,experience,days,equipment,limitations))

def get_profile():
    with connect() as c:
        r=c.execute("SELECT * FROM profile WHERE id=1").fetchone()
        return dict(r) if r else None

def add_progress(entry_date,weight,workouts,notes):
    with connect() as c:
        c.execute("INSERT INTO progress(entry_date,weight_kg,workouts_completed,notes) VALUES(?,?,?,?)",
                  (entry_date,weight,workouts,notes))

def get_progress():
    with connect() as c:
        rows=c.execute("SELECT entry_date,weight_kg,workouts_completed,notes FROM progress ORDER BY entry_date").fetchall()
        return pd.DataFrame([dict(r) for r in rows])

def save_plan(plan_text):
    with connect() as c:
        c.execute("INSERT INTO workout_plans(plan_text) VALUES(?)",(plan_text,))

def get_latest_plan():
    with connect() as c:
        r=c.execute("SELECT created_at,plan_text FROM workout_plans ORDER BY id DESC LIMIT 1").fetchone()
        return dict(r) if r else None
