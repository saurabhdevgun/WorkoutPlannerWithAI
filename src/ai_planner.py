"""
AI Workout Planner: Interfaces with Gemini or Groq LLMs (configured via .env)
to generate personalized workout and exercise plans based on user biometrics,
health conditions/lab data, and fitness goals.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from groq import Groq
from google import genai
from google.genai import types

load_dotenv(override=True)


SYSTEM_PROMPT = """You are an expert Certified Strength & Conditioning Specialist (CSCS), Exercise Physiologist, and Clinical Fitness Coach.
Your job is to design a safe, highly effective, personalized workout and exercise program tailored to the user's biometrics, health status, medical/joint limitations, available equipment, and specific fitness goals.

Structure your response clearly in Markdown with the following sections:

1. **Executive Health & Biometric Assessment**
   - Briefly interpret their BMI, BMR/TDEE, experience level, and any health conditions, injuries, or biomarkers provided.
   - Highlight key physiological priorities (e.g., insulin sensitivity, joint preservation, progressive overload, cardiovascular conditioning, recovery).

2. **Weekly Workout Split Overview**
   - Provide a clear summary table of the 7-day weekly schedule matching their requested training days per week and session duration.

3. **Detailed Day-by-Day Exercise Plan**
   - For each training day, include:
     - **Warm-Up (5-8 mins)**: Dynamic mobility & activation specific to the session.
     - **Main Workout Table**: A Markdown table with columns: `Exercise`, `Target Muscle / System`, `Sets`, `Reps / Duration`, `Rest`, and `Coaching & Safety Cues` (specifically adapted to their health/joint limitations).
     - **Cool-Down (5 mins)**: Stretching or breathing work.

4. **Cardio, Conditioning & Recovery Protocol**
   - Specific heart-rate zone recommendations (e.g., Zone 2 vs HIIT), daily step targets, and active recovery guidance tailored to their health profile.

5. **Nutrition & Calorie Alignment**
   - Based on their estimated BMR and TDEE, recommend a daily calorie target and macronutrient split (Protein, Carbs, Fats) aligned with their primary goal and health markers.

6. **Safety Precautions & Progression Rules**
   - Red flags to watch out for, how to progress weights/reps week-over-week, and a brief medical disclaimer.
"""


def get_env_config() -> Dict[str, str]:
    """Reads model and API key configuration from .env / environment variables."""
    load_dotenv(override=False)
    return {
        "groq_api_key": os.getenv("GROQ_API_KEY", "").strip(),
        "groq_model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip() or "openai/gpt-oss-20b",
        "gemini_api_key": (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip(),
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash",
    }


def build_user_prompt(
    profile: Dict[str, Any],
    bmi_info: Dict[str, Any],
    metabolic_info: Dict[str, int],
    health_report_text: str = "",
) -> str:
    prompt_parts = [
        "Please create a comprehensive, personalized workout and exercise plan for the following user:",
        "",
        "### 1. User Biometrics & Profile",
        f"- **Age**: {profile.get('age')} years",
        f"- **Gender**: {profile.get('gender')}",
        f"- **Height**: {profile.get('height_cm')} cm",
        f"- **Weight**: {profile.get('weight_kg')} kg",
        f"- **Calculated BMI**: {bmi_info.get('bmi')} ({bmi_info.get('category')}) — {bmi_info.get('description')}",
        f"- **Estimated BMR**: {metabolic_info.get('bmr')} kcal/day",
        f"- **Estimated TDEE**: {metabolic_info.get('tdee')} kcal/day",
        f"- **Fitness Experience Level**: {profile.get('experience')}",
        "",
        "### 2. Fitness Goals & Logistics",
        f"- **Primary Goal**: {profile.get('primary_goal')}",
        f"- **Specific Goal Details / Target**: {profile.get('goal_detail') or 'General improvement'}",
        f"- **Training Frequency**: {profile.get('days_per_week')} days per week",
        f"- **Session Duration**: {profile.get('session_duration_min')} minutes per session",
        f"- **Available Equipment**: {profile.get('equipment')}",
        f"- **Preferred Workout Style**: {profile.get('workout_style', 'Balanced Strength & Conditioning')}",
        "",
        "### 3. Health Conditions, Injuries & Physical Limitations",
        f"- **Reported Conditions / Injuries**: {profile.get('limitations') or 'None reported'}",
        f"- **Sleep & Stress Profile**: Sleep ~{profile.get('sleep_hours', 7)} hrs/night | Stress Level: {profile.get('stress_level', 'Moderate')}",
    ]

    if health_report_text and health_report_text.strip():
        prompt_parts.extend([
            "",
            "### 4. Medical / Lab Report Data",
            "```text",
            health_report_text.strip(),
            "```",
            "Please explicitly factor any abnormal biomarkers or clinical findings from this report into the exercise selection, intensity, and recovery recommendations.",
        ])

    return "\n".join(prompt_parts)


def _call_llm(
    provider: str,
    system_prompt: str,
    user_prompt: str,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.6,
    max_tokens: int = 4096,
) -> str:
    """Unified helper to call either Gemini or Groq using .env defaults or explicit overrides."""
    cfg = get_env_config()
    provider_clean = provider.strip().lower()

    if provider_clean == "gemini":
        key = (api_key or cfg["gemini_api_key"]).strip()
        if not key:
            raise ValueError(
                "Missing GEMINI_API_KEY. Please add GEMINI_API_KEY to your .env file or enter it in the sidebar."
            )
        model = (model_name or cfg["gemini_model"]).strip()
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        content = response.text
        if not content:
            raise RuntimeError("Gemini returned an empty response. Please try again.")
        return content.strip()

    else:
        # Default to Groq
        key = (api_key or cfg["groq_api_key"]).strip()
        if not key:
            raise ValueError(
                "Missing GROQ_API_KEY. Please add GROQ_API_KEY to your .env file or enter it in the sidebar."
            )
        model = (model_name or cfg["groq_model"]).strip()
        client = Groq(api_key=key)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = completion.choices[0].message.content
        if not content:
            raise RuntimeError("Groq returned an empty response. Please try again.")
        return content.strip()


def generate_workout_plan(
    profile: Dict[str, Any],
    bmi_info: Dict[str, Any],
    metabolic_info: Dict[str, int],
    health_report_text: str = "",
    provider: str = "Groq",
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.6,
) -> str:
    """Generates the personalized workout plan using the selected provider (Gemini or Groq)."""
    user_prompt = build_user_prompt(profile, bmi_info, metabolic_info, health_report_text)
    return _call_llm(
        provider=provider,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        model_name=model_name,
        api_key=api_key,
        temperature=temperature,
        max_tokens=4096,
    )


def ask_followup_question(
    workout_plan: str,
    user_question: str,
    profile: Dict[str, Any],
    provider: str = "Groq",
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    """Allows the user to ask follow-up questions or request exercise swaps."""
    followup_system = (
        "You are an expert AI Fitness & Exercise Coach helping a user customize their workout plan. "
        "Keep answers practical, safe, and tailored to their health profile and goals."
    )
    followup_user = (
        f"User Profile Summary: {profile.get('age')}yo {profile.get('gender')}, "
        f"Goal: {profile.get('primary_goal')}, Limitations: {profile.get('limitations')}.\n\n"
        f"Current Generated Workout Plan:\n{workout_plan}\n\n"
        f"User Follow-up Request: {user_question}"
    )

    return _call_llm(
        provider=provider,
        system_prompt=followup_system,
        user_prompt=followup_user,
        model_name=model_name,
        api_key=api_key,
        temperature=0.6,
        max_tokens=2048,
    )
