# AI Personalized Workout & Exercise Planner

A Streamlit application powered by **Google Gemini** (`google-genai`) and **Groq** LLMs that creates personalized, health-aware workout and exercise routines based on:
- **User Biometrics**: Age, Gender, Weight & Height (Metric or Imperial), Experience Level, live BMI classification, BMR, and TDEE calculations.
- **Fitness Goals & Schedule**: Primary goal, specific targets, days per week, session duration, and available equipment.
- **Health & Lab Context**: Physical/joint limitations, health conditions, sleep/stress profile, and optional PDF/TXT blood report parsing.

## Getting Started (After Cloning)

### 1. Clone the Repository
```bash
git clone https://github.com/saurabhdevgun/WorkoutPlannerWithAI.git
cd WorkoutPlannerWithAI
```

### 2. Install Dependencies with `uv`
Run `uv sync` to create the virtual environment (`.venv`) and install all locked dependencies from `pyproject.toml` and `uv.lock`:
```bash
uv sync
```

### 3. Configure Environment Variables (`.env`)
Copy `.env.sample` to `.env` and add your API key(s) and preferred model names:
```bash
cp .env.sample .env
```

```env
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=openai/gpt-oss-20b

GEMINI_API_KEY=<your-gemini-api-key>
GEMINI_MODEL=gemini-2.5-flash
```
*(You can also switch between **Gemini** and **Groq**, edit the model name, or enter your API key directly in the Streamlit sidebar.)*

### 4. Run the Streamlit App
```bash
uv run streamlit run app.py
```
