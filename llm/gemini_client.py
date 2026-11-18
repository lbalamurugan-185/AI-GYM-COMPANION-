from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import GOOGLE_API_KEY, GEMINI_MODEL, validate_api_key

def get_llm():
    validate_api_key()
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL, google_api_key=GOOGLE_API_KEY,
        temperature=0.35, max_retries=2, timeout=60
    )

def ask_fitness_coach(question, profile=None):
    context = "No profile provided."
    if profile:
        context = (
            f'Age {profile["age"]}; height {profile["height_cm"]} cm; '
            f'weight {profile["weight_kg"]} kg; goal {profile["goal"]}; '
            f'level {profile["experience"]}; limitations {profile["limitations"] or "not provided"}.'
        )
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a cautious fitness education assistant. Give general information, not diagnosis or treatment.
Avoid steroids, unregulated supplements, extreme diets, and training through pain. Encourage gradual progression,
warm-ups, recovery, hydration and technique. If the user mentions injury, illness, pregnancy, chest pain, dizziness,
or a medical condition, recommend advice from a qualified healthcare professional before changing exercise.
Do not promise results. User context: {context}"""),
        ("human", "{question}")
    ])
    return (prompt | get_llm() | StrOutputParser()).invoke({"context":context,"question":question})
