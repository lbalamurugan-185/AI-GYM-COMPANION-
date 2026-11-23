# AI Gym Companion 🏋️

AI Gym Companion is a fitness web application I developed using Python and AI technologies. The main idea behind this project is to help users manage their fitness activities, get workout suggestions based on their goals, and keep track of their progress in one place.

## Features

- **User Login & Registration:** Users can create an account and access their personal fitness information.
- **My Profile:** Users can add and update their fitness details, goals, experience level, and workout preferences.
- **AI Workout Planner:** Generates workout plans based on the user's fitness profile and requirements.
- **AI Fitness Chat:** Users can ask fitness-related questions and get responses from an AI assistant.
- **Progress Tracker:** Users can record their weight and completed workouts and view their progress through charts.
- **User Data Management:** Each user has separate profile information, workout plans, and progress records.

## Technologies Used

- Python
- Streamlit
- Supabase (PostgreSQL)
- Groq API
- LangChain
- Pandas
- Plotly

## How It Works

Users first register or log in to the application. They can then update their fitness profile and generate workout plans according to their goals.

The AI features use the Groq API with LangChain to process user requests and generate responses. Supabase handles authentication and stores user profiles, workout plans, and progress records.

## Run the Project Locally

**1. Clone the repository**

```bash
git clone https://github.com/lbalamurugan-185/AI-GYM-COMPANION-.git
```

**2. Open the project folder**

```bash
cd AI-GYM-COMPANION-
```

**3. Install the required packages**

```bash
pip install -r requirements.txt
```

**4. Configure your Supabase and Groq credentials**

Add the required credentials to `.streamlit/secrets.toml`. Refer to the application's expected secret names. Do not upload this file to GitHub.

**5. Start the application**

```bash
streamlit run app.py
```

## Live Application

https://ai-powered-gym-companion.streamlit.app/

## Project Testing

I deployed the application using Streamlit Community Cloud and tested it with 5–6 users. The main features, including login, workout generation, AI chat, and progress tracking, were tested.

## Future Improvements

- Add nutrition and diet recommendations.
- Include exercise demonstration videos.
- Improve fitness analytics.
- Add workout reminders.

## Developer

**Balamurugan L**

B.Tech – Artificial Intelligence and Data Science

- GitHub: https://github.com/lbalamurugan-185
- LinkedIn: https://www.linkedin.com/in/balamurugan-15/
- Portfolio: https://lbalamurugan-185.github.io/BALAMURUGAN_PORTFOLIO/
