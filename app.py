import streamlit as st
import json
from pathlib import Path
from urllib.parse import quote_plus
from database.auth import (
    register_user,
    login_user,
    logout_user,
    get_current_user
)
from database.supabase_client import get_supabase_client
# Other imports...

# Define helper function BEFORE using it
def format_goals(goals):
    if isinstance(goals, list):
        return ", ".join(goals)
    if isinstance(goals, str):
        return goals
    return "Not specified"


# Other functions and sidebar code come below
import pandas as pd
import plotly.express as px
from datetime import date
from database.db import (
    init_db, save_profile, get_profile, add_progress, get_progress,
    save_plan, get_latest_plan
)
from modules.fitness_calculator import calculate_bmi, bmi_label
from modules.workout_generator import generate_workout_plan
from llm.groq_client import ask_fitness_coach

st.set_page_config(page_title="AI Gym Companion", page_icon="💪", layout="wide", initial_sidebar_state="expanded")
init_db()
# ---------------- EMAIL VERIFICATION CALLBACK ----------------

if "code" in st.query_params:
    try:
        supabase = get_supabase_client()

        code = st.query_params["code"]

        response = supabase.auth.exchange_code_for_session(code)

        st.session_state.auth_client = supabase
        st.session_state.auth_user = response.user

        st.query_params.clear()

        st.success("Email verified successfully!")
        st.rerun()

    except Exception as e:
        st.error(f"Email verification failed: {e}")
# ---------------- AUTHENTICATION GATE ----------------

if "auth_client" not in st.session_state:
    st.session_state.auth_client = None

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

if st.session_state.auth_user is None:

    st.markdown("## 💪 AI Gym Companion")
    st.subheader("Welcome! Login or create your account")

    login_tab, signup_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email address", key="login_email")
            password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )
            login_button = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if login_button:
            try:
                result = login_user(email, password)

                st.session_state.auth_client = result["client"]
                st.session_state.auth_user = result["user"]

                st.success("Login successful!")
                st.rerun()

            except Exception:
                st.error("Login failed. Check your email and password.")

    with signup_tab:
        with st.form("signup_form"):
            new_email = st.text_input("Email address", key="signup_email")
            new_password = st.text_input(
                "Password (minimum 8 characters)",
                type="password",
                key="signup_password"
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            signup_button = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

        if signup_button:
            if len(new_password) < 8:
                st.error("Password must contain at least 8 characters.")

            elif new_password != confirm_password:
                st.error("Passwords do not match.")

            else:
                try:
                    result = register_user(new_email, new_password)

                    if result["session"] is not None:
                        st.session_state.auth_client = result["client"]
                        st.session_state.auth_user = result["user"]

                        st.success("Account created successfully! Welcome!")
                        st.rerun()

                    else:
                        st.success("Account created. Please check your email.")

                except Exception as e:
                     st.error(f"Registration failed: {str(e)}")

    st.stop()

# ---------------- AUTHENTICATED USER ----------------
# Show authenticated user details
auth_user = st.session_state.auth_user

st.sidebar.markdown("---")
st.sidebar.caption("ACCOUNT")
st.sidebar.write(f"Logged in: {auth_user.email}")

if st.sidebar.button("Logout", use_container_width=True):
    try:
        logout_user(st.session_state.auth_client)
    finally:
        st.session_state.auth_client = None
        st.session_state.auth_user = None
        st.rerun()


# SB Admin-inspired layout: dark top bar + dark side navigation + content cards.
st.markdown("""
<style>
:root { --gym-blue:#0d6efd; --gym-dark:#212529; --gym-bg:#f5f6fa; }
html, body, [data-testid="stAppViewContainer"] { background:var(--gym-bg); }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stSidebar"] { background:#212529; }
[data-testid="stSidebar"] * { color:#e9ecef !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding:7px 10px; border-radius:7px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#343a40; }
.block-container { padding-top:1.1rem; padding-bottom:2rem; max-width:1500px; }
.topbar { background:#212529; color:white; padding:13px 22px; border-radius:9px; margin-bottom:22px;
          display:flex; align-items:center; justify-content:space-between; }
.brand { font-size:20px; font-weight:700; letter-spacing:.2px; }
.topbar-sub { color:#adb5bd; font-size:12px; }
.page-title { color:#212529; font-size:29px; font-weight:650; margin:4px 0 2px 0; }
.breadcrumb { color:#6c757d; font-size:13px; margin-bottom:20px; }
.kpi { border-radius:8px; padding:16px 18px; color:white; min-height:112px; box-shadow:0 2px 7px rgba(0,0,0,.08); }
.kpi-label { font-size:13px; opacity:.9; }
.kpi-value { font-size:26px; font-weight:700; margin-top:8px; }
.kpi-foot { font-size:11px; opacity:.85; margin-top:4px; }
.kpi-blue { background:#0d6efd; } .kpi-yellow { background:#f0ad4e; }
.kpi-green { background:#198754; } .kpi-red { background:#dc3545; }
.panel { background:white; border:1px solid #dee2e6; border-radius:8px; padding:16px 18px; margin-bottom:16px; }
.panel-title { color:#343a40; font-weight:650; font-size:16px; border-bottom:1px solid #e9ecef; padding-bottom:10px; margin-bottom:12px; }
.small-muted { color:#6c757d; font-size:12px; }
div[data-testid="stForm"] { background:white; padding:18px; border:1px solid #dee2e6; border-radius:8px; }
.stButton>button[kind="primary"] { background:#0d6efd; border-color:#0d6efd; }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
  <div class="brand">💪 AI GYM COMPANION <span class="topbar-sub">/ PERSONAL FITNESS DASHBOARD</span></div>
  <div class="topbar-sub">SMART WORKOUTS · TRACK YOUR PROGRESS</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 💪 Gym Companion")
    st.caption("FITNESS MANAGEMENT")
    page = st.radio(
        "Navigation",
        ["Dashboard", "My Profile", "AI Workout Planner", "Progress Tracker", "AI Fitness Chat"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("ACCOUNT")
    profile_sidebar = get_profile(
        st.session_state.auth_client,
        st.session_state.auth_user.id
)
    if profile_sidebar:
        st.write("👤 Profile configured")
        st.caption(f'Goals: {format_goals(profile_sidebar["goal"])}')
    else:
        st.caption("Complete your profile to begin.")
    st.markdown("---")
    st.caption("Powered by Streamlit + LangChain + Groq")

profile = get_profile(
    st.session_state.auth_client,
    st.session_state.auth_user.id
)

def heading(title, crumb):
    st.markdown(f'<div class="page-title">{title}</div><div class="breadcrumb">Home&nbsp; / &nbsp;{crumb}</div>', unsafe_allow_html=True)

def metric_card(label, value, foot, color):
    st.markdown(
        f'<div class="kpi {color}"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-foot">{foot}</div></div>',
        unsafe_allow_html=True
    )



def require_profile():
    if not profile:
        st.warning("Please complete **My Profile** before using this section.")
        return False
    return True


def render_workout_plan(plan_text):
    """Render structured workout JSON; retain support for older Markdown plans."""
    try:
        plan = json.loads(plan_text) if isinstance(plan_text, str) else plan_text
    except (json.JSONDecodeError, TypeError):
        st.markdown(plan_text)
        return
    if not isinstance(plan, dict) or not isinstance(plan.get("days"), list):
        st.markdown(plan_text)
        return

    st.subheader(plan.get("title", "Your Personalized Weekly Workout Plan"))
    st.caption(plan.get("overview", "Personalized workout schedule"))
    if plan.get("weekly_schedule"):
        st.markdown("### Weekly schedule")
        st.dataframe(plan["weekly_schedule"], use_container_width=True, hide_index=True)

    for day in plan.get("days", []):
        with st.expander(f'{day.get("day", "Training day")} – {day.get("focus", "Workout")}', expanded=False):
            if day.get("warmup"):
                st.markdown("**Warm-up**")
                st.write(day["warmup"])
            for idx, exercise in enumerate(day.get("exercises", []), 1):
                st.markdown(f'#### {idx}. {exercise.get("name", "Exercise")}')
                st.caption(
                    f'{exercise.get("muscle_group", "Full body")} · '
                    f'{exercise.get("sets", "—")} sets × {exercise.get("reps", "—")} · '
                    f'Rest: {exercise.get("rest", "—")}'
                )
                slug = exercise.get("image_key") or exercise.get("name", "").lower().replace(" ", "_")
                image_files = [
                    Path("assets") / "exercises" / f"{slug}.jpg",
                    Path("assets") / "exercises" / f"{slug}.png",
                ]
                local_image = next((p for p in image_files if p.exists()), None)
                if local_image:
                    st.image(str(local_image), width=360)
                else:
                    image_url = "https://www.google.com/search?tbm=isch&q=" + quote_plus(
                        exercise.get("name", "") + " exercise demonstration"
                    )
                    st.markdown(f"[Find exercise image]({image_url})")
                c1, c2 = st.columns(2)
                c1.markdown(f'**Target muscles:** {exercise.get("muscle_group", "Not specified")}')
                c2.markdown(f'**Equipment:** {exercise.get("equipment", "Not specified")}')
                st.markdown("**How to perform**")
                for item in exercise.get("instructions", []):
                    st.markdown(f"- {item}")
                if exercise.get("common_mistakes"):
                    st.markdown("**Common mistakes to avoid**")
                    for item in exercise["common_mistakes"]:
                        st.markdown(f"- {item}")
                if exercise.get("alternatives"):
                    st.markdown("**Alternatives**")
                    for item in exercise["alternatives"]:
                        st.markdown(f"- {item}")
                video_query = quote_plus(exercise.get("name", "") + " proper form exercise tutorial")
                st.markdown(f"[▶ Watch demonstration video](https://www.youtube.com/results?search_query={video_query})")
                st.divider()
            if day.get("cooldown"):
                st.markdown("**Cool-down**")
                st.write(day["cooldown"])

    for heading, key in [
        ("Recovery recommendations", "recovery"),
        ("Progression strategy", "progression"),
        ("Coach's advice", "coach_advice"),
        ("Safety notes", "safety_notes"),
    ]:
        content = plan.get(key)
        if content:
            st.markdown(f"### {heading}")
            if isinstance(content, list):
                for item in content:
                    st.markdown(f"- {item}")
            else:
                st.write(content)


if page == "Dashboard":
    heading("Dashboard", "Overview")
    if profile:
        bmi = calculate_bmi(profile["weight_kg"], profile["height_cm"])
        c1,c2,c3,c4 = st.columns(4)
        with c1: metric_card("CURRENT WEIGHT", f'{profile["weight_kg"]:.1f} kg', "Latest profile weight", "kpi-blue")
        with c2: metric_card("HEIGHT", f'{profile["height_cm"]:.0f} cm', "Saved profile", "kpi-yellow")
        with c3: metric_card("BMI SCREENING", f"{bmi:.1f}", bmi_label(bmi), "kpi-green")
        with c4: metric_card(
                        "FITNESS GOALS",
                        format_goals(profile["goal"]),
                        profile["experience"] + " level",
                        "kpi-red"
                    )
        st.write("")
        left, right = st.columns([1.55,1])
        with left:
            st.markdown('<div class="panel"><div class="panel-title">📈 Weight Progress</div>', unsafe_allow_html=True)
            progress = get_progress(
                st.session_state.auth_client,
                st.session_state.auth_user.id
)
            if not progress.empty:
                fig = px.line(progress, x="entry_date", y="weight_kg", markers=True,
                              labels={"entry_date":"Date","weight_kg":"Weight (kg)"})
                fig.update_layout(height=300, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="white", plot_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No progress entries yet. Add your first entry in Progress Tracker.")
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown('<div class="panel"><div class="panel-title">🎯 Training Snapshot</div>', unsafe_allow_html=True)
            st.metric("Training days / week", f'{profile["days_per_week"]} days')
            st.write("**Experience:**", profile["experience"])
            st.write("**Equipment:**", profile["equipment"])
            st.write("**Goals:**", format_goals(profile["goal"]))
            st.markdown("</div>", unsafe_allow_html=True)
        latest = get_latest_plan(
            st.session_state.auth_client,
            st.session_state.auth_user.id
)
        st.markdown('<div class="panel"><div class="panel-title">🏋️ Latest AI Workout Plan</div>', unsafe_allow_html=True)
        if latest:
            st.caption(f'Generated: {latest["created_at"]}')
            render_workout_plan(latest["plan_text"])
        else:
            st.info("No workout plan generated yet. Open AI Workout Planner to create one.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Welcome! Start by opening **My Profile** and entering your fitness details.")
        st.markdown('<div class="panel"><div class="panel-title">Getting Started</div>1. Create your profile<br>2. Generate your weekly workout plan<br>3. Record progress regularly<br>4. Ask the AI fitness companion questions</div>', unsafe_allow_html=True)

elif page == "My Profile":
    heading("My Profile", "Fitness Profile")
    if "profile_notice" in st.session_state:
        notice = st.session_state.pop("profile_notice")
        st.success(notice)
        st.toast(notice, icon="✅")
    st.markdown("Set up your basic fitness information so the AI can tailor general workout suggestions.")
    defaults = profile or {}
    with st.form("profile_form"):
        a,b = st.columns(2)
        with a:
            age = st.number_input("Age", 16, 100, int(defaults.get("age",25)))
            height = st.number_input("Height (cm)", 100.0, 230.0, float(defaults.get("height_cm",170.0)), 0.5)
            weight = st.number_input("Current weight (kg)", 30.0, 300.0, float(defaults.get("weight_kg",70.0)), 0.5)
            gender_options = ["Prefer not to say", "Female", "Male", "Other"]
            saved_gender = defaults.get("gender") or "Prefer not to say"
            gender = st.selectbox(
                "Gender (optional)",
                gender_options,
                index=gender_options.index(saved_gender) if saved_gender in gender_options else 0,
                help="Optional context only. Workout recommendations are primarily based on goals, experience, ability, equipment and limitations."
            )
           
            goal_options = [
                "Muscle gain",
                "Fat loss",
                "General fitness",
                "Strength development",
                "Improve endurance",
                "Improve flexibility",
                "Weight maintenance"
            ]

            saved_goals = defaults.get("goal", ["Muscle gain"])

            if isinstance(saved_goals, str):
                saved_goals = [saved_goals]

            valid_saved_goals = [
                g for g in saved_goals
                if g in goal_options
            ]

            goal = st.multiselect(
                "Fitness Goals (Select one or more)",
                options=goal_options,
                default=valid_saved_goals,
                placeholder="Choose your fitness goals",
                help="You can select multiple fitness goals."
            )

        with b:
            levels = ["Beginner","Intermediate","Advanced"]
            experience = st.selectbox("Experience level", levels, index=levels.index(defaults.get("experience","Beginner")))
            day_options = [2,3,4,5,6]
            days = st.selectbox("Available training days per week", day_options, index=day_options.index(int(defaults.get("days_per_week",3))))
            equipment_options = ["Full gym","Dumbbells only","Bodyweight only","Home gym"]
            equipment = st.selectbox("Available equipment", equipment_options, index=equipment_options.index(defaults.get("equipment","Full gym")))
            limitations = st.text_area("Injuries, pain, or exercise limitations (optional)", value=defaults.get("limitations",""))
        
            if st.form_submit_button("💾 Save Profile", type="primary"):

                if not goal:
                    st.error("Please select at least one fitness goal.")

                else:
                    is_update = profile is not None

                   
                    save_profile(
                        st.session_state.auth_client,
                        st.session_state.auth_user.id,
                        age,
                        height,
                        weight,
                        goal,
                        experience,
                        days,
                        equipment,
                        limitations,
                        gender
)


                    if is_update:
                        st.session_state["profile_notice"] = (
                            "Your fitness profile has been updated successfully!"
                        )
                    else:
                        st.session_state["profile_notice"] = (
                            "Your fitness profile has been saved successfully!"
                        )

                    st.rerun()




elif page == "AI Workout Planner":
    heading("AI Workout Planner", "Workout Recommendations")

    if require_profile():
        st.markdown("### Generate a Personalized Weekly Plan")

        st.markdown(
            f"**Goals:** {format_goals(profile.get('goal'))} "
            f"| **Level:** {profile.get('experience')} "
            f"| **Days:** {profile.get('days_per_week')}"
        )

        with st.form("workout_form"):
            additional_context = st.text_area(
                "Additional preferences (optional)",
                placeholder="Example: prefer 45-minute sessions."
            )

            generate_button = st.form_submit_button(
                "Generate Workout Plan",
                type="primary"
            )

        if generate_button:
            try:
                with st.spinner("Generating your workout plan..."):
                    result = generate_workout_plan(
                        profile,
                        additional_context
                    )

                    save_plan(
                        st.session_state.auth_client,
                        st.session_state.auth_user.id,
                        result
                    )

                st.success("Workout plan generated successfully!")
                render_workout_plan(result)

            except Exception as exc:
                st.error(f"Workout generation failed: {exc}")

        else:
            previous = get_latest_plan(
                st.session_state.auth_client,
                st.session_state.auth_user.id
            )

            if previous:
                with st.expander("View saved workout plan"):
                    render_workout_plan(previous["plan_text"])
            else:
                st.info("No workout plan generated yet.")



elif page == "Progress Tracker":
    heading("Progress Tracker", "Fitness Analytics")
    if require_profile():
        with st.form("progress_form"):
            st.markdown("#### Add a progress entry")
            a,b = st.columns(2)
            with a:
                entry_date = st.date_input("Entry date", date.today())
                weight = st.number_input("Weight (kg)", 30.0, 300.0, float(profile["weight_kg"]), 0.1)
            with b:
                workouts = st.number_input("Workouts completed this week", 0, 14, 0)
                notes = st.text_input("Notes (optional)", placeholder="Energy, consistency, personal bests...")
            if st.form_submit_button("Save Progress", type="primary"):
                add_progress(
                    st.session_state.auth_client,
                    st.session_state.auth_user.id,
                    entry_date.isoformat(),
                    weight,
                    int(workouts),
                    notes
)
                st.success("Progress entry saved.")
                st.rerun()
        data = get_progress(
            st.session_state.auth_client,
            st.session_state.auth_user.id
)
        if not data.empty:
            st.markdown('<div class="panel"><div class="panel-title">📊 Progress Overview</div>', unsafe_allow_html=True)
            x,y,z = st.columns(3)
            x.metric("Latest weight",f'{data.iloc[-1]["weight_kg"]:.1f} kg')
            y.metric("Entries",len(data))
            z.metric("Total workouts logged",int(data["workouts_completed"].sum()))
            fig = px.line(data,x="entry_date",y="weight_kg",markers=True,labels={"entry_date":"Date","weight_kg":"Weight (kg)"})
            fig.update_layout(height=330,margin=dict(l=10,r=10,t=15,b=10),paper_bgcolor="white",plot_bgcolor="white")
            st.plotly_chart(fig,use_container_width=True)
            st.markdown("</div>",unsafe_allow_html=True)
            st.markdown("#### Progress History")
            st.dataframe(data,use_container_width=True,hide_index=True)
        else:
            st.info("No entries yet. Save your first progress record above.")


elif page == "AI Fitness Chat":
    heading("AI Fitness Chat", "AI Assistant")

    st.markdown(
        "Ask general questions about exercise selection, "
        "training structure, recovery, nutrition and consistency."
    )

    # Isolate chat history for each authenticated user
    user_id = str(st.session_state.auth_user.id)
    chat_key = f"chat_messages_{user_id}"

    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    # Display this user's chat history
    for message in st.session_state[chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask your fitness companion...")

    if question:
        st.session_state[chat_key].append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = ask_fitness_coach(
                        question,
                        profile or {}
                    )
                except Exception as exc:
                    answer = f"AI service error: {exc}"

                st.markdown(answer)

        st.session_state[chat_key].append({
            "role": "assistant",
            "content": answer
        })
