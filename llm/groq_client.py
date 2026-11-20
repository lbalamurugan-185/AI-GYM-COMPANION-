
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    validate_api_key
)

from llm.prompts import FITNESS_CHAT_SYSTEM_PROMPT


# ==========================================
# GROQ MODEL CONNECTION
# ==========================================

def get_llm():

    validate_api_key()

    return ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0.35,
        max_retries=2,
        timeout=60
    )


# ==========================================
# FORMAT USER FITNESS PROFILE
# ==========================================

def format_profile(profile):

    if not profile:
        return "No fitness profile has been provided."

    goals = profile.get("goal", "Not specified")

    if isinstance(goals, list):
        goals = ", ".join(goals)

    return f"""
USER FITNESS PROFILE:

Age: {profile.get("age", "Not provided")}
Height: {profile.get("height_cm", "Not provided")} cm
Weight: {profile.get("weight_kg", "Not provided")} kg
Fitness Goals: {goals}
Experience: {profile.get("experience", "Not provided")}
Training Days: {profile.get("days_per_week", "Not provided")}
Equipment: {profile.get("equipment", "Not provided")}
Limitations: {profile.get("limitations") or "None provided"}

Use this information to personalize your advice.
Never invent missing profile information.
"""


# ==========================================
# AI FITNESS CHAT - LANGCHAIN
# ==========================================

def ask_fitness_coach(question, profile=None):

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            FITNESS_CHAT_SYSTEM_PROMPT
            + "\n\nAdditional user context:\n{profile}"
        ),
        ("human", "{question}")
    ])

    chain = prompt | get_llm() | StrOutputParser()

    response = chain.invoke({
        "profile": format_profile(profile),
        "question": question
    })

    return response.strip()
