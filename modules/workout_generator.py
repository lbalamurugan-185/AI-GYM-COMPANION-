from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm.groq_client import get_llm
from llm.prompts import WORKOUT_SYSTEM_PROMPT

def generate_workout_plan(profile, additional_context=""):
    prompt = ChatPromptTemplate.from_messages([
        ("system", WORKOUT_SYSTEM_PROMPT),
        ("human", """Create a weekly plan from this profile:
Age: {age}; Height: {height} cm; Weight: {weight} kg
Goal: {goal}; Experience: {level}; Training days/week: {days}
Equipment: {equipment}; Limitations: {limitations}; Preferences: {preferences}

Return Markdown with:
1. Short overview and assumptions.
2. Weekly split using no more than the available training days.
3. For each session: exercise, sets, reps/duration, rest.
4. Warm-up, cool-down, rest days and recovery.
5. Beginner-friendly alternatives and gradual progression.
6. Avoid exercises that may aggravate stated limitations.
7. No rigid calorie prescription.
8. Safety reminders: stop for pain, dizziness, chest discomfort or unusual symptoms.""")
    ])
    return (prompt | get_llm() | StrOutputParser()).invoke({
        "age":profile["age"], "height":profile["height_cm"], "weight":profile["weight_kg"],
        "goal":profile["goal"], "level":profile["experience"], "days":profile["days_per_week"],
        "equipment":profile["equipment"], "limitations":profile["limitations"] or "None provided",
        "preferences":additional_context or "None"
    })
