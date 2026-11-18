# AI Gym Companion — SB Admin-inspired Streamlit UI

This project adapts the uploaded Start Bootstrap SB Admin reference layout to a Streamlit fitness application.

## UI mapping from the reference
- Dark top navigation bar → AI Gym Companion top header
- Dark left sidenav → Dashboard, Profile, Workout Planner, Progress Tracker, AI Chat navigation
- Colored summary cards → Weight, height, BMI screening, fitness goal
- Chart panels → Weight progress and workout analytics
- Data table → Progress history

## Features
- Fitness profile form
- LangChain + Google Gemini weekly workout plan generation
- Exercise suggestions based on goal, experience, equipment and available days
- SQLite profile, workout-plan and progress storage
- Plotly weight-trend chart
- AI fitness Q&A chatbot

## Setup (Windows PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `.env` and add your own Gemini API key:
```env
GOOGLE_API_KEY=your_actual_api_key
GEMINI_MODEL=gemini-2.5-flash
```
Run:
```powershell
streamlit run app.py
```
Open the local URL shown in the terminal, usually http://localhost:8501.

## Important
- Do not share or commit your `.env` file.
- Gemini model access and quota depend on your Google AI API project.
- SQLite is suitable for local development. For deployment, use persistent storage or a managed database.
- BMI is a rough adult screening measure, not a diagnosis.
- AI-generated plans are general educational suggestions, not medical advice. Consult a qualified professional when injuries or medical conditions are involved.
