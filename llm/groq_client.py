
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    validate_api_key
)


def get_llm():
    validate_api_key()

    return ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0.35,
        max_retries=2,
        timeout=60
    )


def ask_fitness_coach(question, profile=None):

    profile_text = "No user profile provided."

    if profile:
        profile_text = (
            f'Age: {profile["age"]}; '
            f'Height: {profile["height_cm"]} cm; '
            f'Weight: {profile["weight_kg"]} kg; '
            f'Goal: {profile["goal"]}; '
            f'Experience: {profile["experience"]}; '
            f'Limitations: {profile["limitations"] or "None provided"}.'
        )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a knowledgeable and responsible AI fitness
            education assistant.

            Provide general fitness information, exercise guidance,
            recovery advice and workout explanations.

            Avoid medical diagnosis, treatment recommendations,
            steroids, extreme diets and training through pain.

            Encourage proper warm-up, recovery and gradual progression.

            If users mention injuries or medical conditions,
            recommend consulting a qualified healthcare professional.

            User profile: {profile}"""
        ),
        ("human", "{question}")
    ])

    chain = prompt | get_llm() | StrOutputParser()

    return chain.invoke({
        "profile": profile_text,
        "question": question
    })
