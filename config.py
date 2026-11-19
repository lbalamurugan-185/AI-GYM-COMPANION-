import os
from dotenv import load_dotenv
load_dotenv()

NEW_API_KEY = os.getenv("NEW_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

def validate_api_key():
    if not NEW_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is missing. Copy .env.example to .env and add your Gemini API key.")
