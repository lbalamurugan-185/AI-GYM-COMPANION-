
import json
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from llm.groq_client import get_llm


def _extract_json(raw_text):
    """Extract a JSON object from the AI response."""

    if not raw_text:
        raise ValueError("The AI returned an empty workout response.")

    text = raw_text.strip()

    # Remove Markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")

    if start == -1:
        raise ValueError("No JSON object found in the AI response.")

    try:
        plan, _ = json.JSONDecoder().raw_decode(text[start:])
        return plan

    except json.JSONDecodeError as exc:
        print("\n========== JSON DEBUG ==========")
        print("Error:", exc)
        print("Line:", exc.lineno)
        print("Column:", exc.colno)
        print("Response length:", len(text))
        print("Response ending:", repr(text[-500:]))
        print("========== END JSON DEBUG ==========")

        raise ValueError(
            f"Invalid JSON at line {exc.lineno}, "
            f"column {exc.colno}. The response may be incomplete."
        ) from exc


def _validate_plan(plan):
    """Validate the workout plan structure."""

    if not isinstance(plan, dict):
        raise ValueError("Workout plan must be a JSON object.")

    if not isinstance(plan.get("days"), list) or not plan["days"]:
        raise ValueError("Workout plan is missing its days list.")

    required_fields = [
        "name",
        "muscle_group",
        "sets",
        "reps",
        "rest",
        "instructions",
        "common_mistakes",
        "alternatives"
    ]

    for day in plan["days"]:

        if not isinstance(day, dict):
            raise ValueError("Invalid workout day structure.")

        if not day.get("day"):
            raise ValueError("A workout day is missing its name.")

        exercises = day.get("exercises")

        if not isinstance(exercises, list) or not exercises:
            raise ValueError(
                f"Exercises are missing for {day.get('day')}."
            )

        for exercise in exercises:

            if not isinstance(exercise, dict):
                raise ValueError("Invalid exercise structure.")

            for field in required_fields:
                if field not in exercise:
                    raise ValueError(
                        f"{exercise.get('name', 'Exercise')} "
                        f"is missing the field: {field}"
                    )

            for field in [
                "instructions",
                "common_mistakes",
                "alternatives"
            ]:
                if not isinstance(exercise[field], list):
                    raise ValueError(
                        f"{field} must be a list for "
                        f"{exercise.get('name', 'an exercise')}."
                    )

    return plan


def generate_workout_plan(profile, additional_context=""):

    prompt = ChatPromptTemplate.from_messages([

        (
            "system",
            """
You are an experienced personal fitness coach.

Create safe and personalized workout plans using the user's
age, gender, fitness experience, goals, equipment and limitations.

Return exactly one valid JSON object.
Never return Markdown, code fences or explanations outside JSON.
Use double quotes for JSON keys and string values.
Do not leave any strings or brackets unfinished.
Keep exercise instructions concise and practical.
"""
        ),

        (
            "human",
            """
Create a personalized weekly workout plan.

USER PROFILE:

Age: {age}
Gender: {gender}
Height: {height} cm
Weight: {weight} kg
Goals: {goal}
Experience: {level}
Training days: {days}
Equipment: {equipment}
Limitations: {limitations}
Additional preferences: {preferences}

Return ONLY this JSON structure:

{{
    "title": "Personalized Weekly Workout Plan",
    "overview": "Short plan summary",
    "weekly_schedule": [
        {{
            "day": "Monday",
            "focus": "Push - Chest, Shoulders and Triceps",
            "duration": "45-60 minutes"
        }}
    ],
    "days": [
        {{
            "day": "Monday",
            "focus": "Training focus",
            "warmup": "5-10 minute warm-up",
            "exercises": [
                {{
                    "name": "Exercise name",
                    "muscle_group": "Target muscles",
                    "equipment": "Equipment",
                    "sets": 3,
                    "reps": "8-12",
                    "rest": "60-90 seconds",
                    "instructions": [
                        "Step 1",
                        "Step 2"
                    ],
                    "common_mistakes": [
                        "Mistake 1",
                        "Mistake 2"
                    ],
                    "alternatives": [
                        "Suitable alternative"
                    ],
                    "image_key": "exercise_name"
                }}
            ],
            "cooldown": "Cool-down guidance"
        }}
    ],
    "recovery": ["Recovery recommendation"],
    "progression": ["Progression recommendation"],
    "coach_advice": ["Practical tip"],
    "safety_notes": ["Safety reminder"]
}}

WORKOUT RULES:

1. Respect the user's available training days.
2. Beginner: use manageable full-body sessions and adequate recovery.
3. Intermediate: use suitable upper/lower or push/pull/legs splits.
4. Advanced: use an appropriate structured training split.
5. Combine muscle groups logically, such as:
   Push = Chest, Shoulders and Triceps.
   Pull = Back and Biceps.
   Legs = Quadriceps, Hamstrings, Glutes and Calves.
6. Do not intensely train the same muscle group on consecutive days.
7. Every exercise must include sets, reps and rest.
8. Include exactly 2 short technique instructions per exercise.
9. Include exactly 2 common mistakes per exercise.
10. Include at least 1 suitable alternative per exercise.
11. Match exercises to available equipment.
12. Respect injuries and physical limitations.
13. Include warm-up and cooldown guidance.
14. Include progression and recovery recommendations.
15. Gender is optional context. Never determine exercise intensity from gender alone.
16. Never encourage training through pain.
17. Keep each instruction short and clear.
18. Use approximately 4-6 exercises per strength-training day.
19. Do not fill every available day with intense strength training.
20. Include suitable recovery, mobility or light cardio days when needed.

JSON REQUIREMENTS:

- Return valid JSON only.
- Use double quotes for every key and string.
- No trailing commas.
- No comments.
- No Markdown.
- Close every bracket and quotation mark.
- Keep the response complete, concise and within the output limit.
"""
        )
    ])

    # Enable Groq JSON mode and increase the completion limit.
    llm = get_llm().bind(
        response_format={"type": "json_object"},
        max_completion_tokens=8192,
        reasoning_format="hidden"
    )

    chain = prompt | llm | StrOutputParser()

    inputs = {
        "age": profile.get("age", "Not provided"),
        "gender": profile.get("gender") or "Prefer not to say",
        "height": profile.get("height_cm", "Not provided"),
        "weight": profile.get("weight_kg", "Not provided"),
        "goal": profile.get("goal", "Not specified"),
        "level": profile.get("experience", "Beginner"),
        "days": profile.get("days_per_week", 3),
        "equipment": profile.get("equipment", "Not specified"),
        "limitations": profile.get("limitations") or "None provided",
        "preferences": additional_context or "None"
    }

    last_error = None

    for attempt in range(2):

        try:
            raw = chain.invoke(inputs)

            print(f"\nWorkout generation attempt: {attempt + 1}")
            print("AI response received.")
            print("Response length:", len(raw))

            plan = _extract_json(raw)
            plan = _validate_plan(plan)

            print("Workout JSON validation successful.")

            return json.dumps(plan, ensure_ascii=False)

        except (ValueError, TypeError, json.JSONDecodeError) as exc:

            last_error = exc

            print(
                f"Workout generation attempt {attempt + 1} failed: {exc}"
            )

    raise ValueError(
        "Unable to generate a valid workout plan after 2 attempts. "
        f"Please try again. Details: {last_error}"
    )
