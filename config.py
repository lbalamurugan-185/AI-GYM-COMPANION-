
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)


def get_config(key, default=""):
    # First check Streamlit Cloud Secrets
    try:
        value = st.secrets.get(key, None)
        if value:
            return str(value).strip()
    except Exception:
        pass

    # Fallback to local .env
    return os.getenv(key, default).strip()


GROQ_API_KEY = get_config("GROQ_API_KEY")

GROQ_MODEL = get_config(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)


def validate_api_key():
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is missing. "
            "Add it to your .env file or Streamlit Secrets."
        )
