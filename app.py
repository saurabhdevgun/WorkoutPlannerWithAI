"""
Streamlit Application: AI Workout & Exercise Planner
Generates personalized workout plans based on user biometrics, health conditions, lab reports, and fitness goals.
Supports both Gemini (GEMINI_MODEL / GEMINI_API_KEY) and Groq (GROQ_MODEL / GROQ_API_KEY) read from .env.
"""

import streamlit as st
from dotenv import load_dotenv

from src.biometrics import (
    convert_weight_to_kg,
    convert_height_to_cm,
    calculate_bmi,
    estimate_bmr_tdee,
)
from src.document_parser import extract_text_from_upload, quick_scan_biomarkers
from src.sample_data import SAMPLE_BLOOD_REPORTS
from src.ai_planner import (
    get_env_config,
    generate_workout_plan,
    ask_followup_question,
)

load_dotenv(override=True)

st.set_page_config(
    page_title="AI Workout & Health Planner",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling for cards and badges
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        color: #f8fafc;
        margin-bottom: 12px;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        margin: 4px 0;
    }
    .metric-sub {
        font-size: 0.85rem;
        color: #cbd5e1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "workout_plan" not in st.session_state:
    st.session_state.workout_plan = None
if "last_profile" not in st.session_state:
    st.session_state.last_profile = None
if "followup_history" not in st.session_state:
    st.session_state.followup_history = []

env_cfg = get_env_config()

# --- SIDEBAR: Model Settings & Presets ---
with st.sidebar:
    st.title("⚙️ Planner Settings")

    preset_name = st.selectbox(
        "📋 Load Sample Health Profile",
        options=list(SAMPLE_BLOOD_REPORTS.keys()),
        index=0,
        help="Choose a sample clinical/fitness persona to auto-fill inputs, or keep 'Custom / None' to enter your own.",
    )
    selected_preset = SAMPLE_BLOOD_REPORTS[preset_name]
    rec = selected_preset["recommended_profile"]

    if preset_name != "Custom / None (Enter Manually)":
        st.info(f"**{selected_preset['title']}**\n\n{selected_preset['description']}")

    st.divider()
    st.subheader("🤖 AI Provider & Model (.env)")

    provider = st.radio(
        "Select AI Provider",
        options=["Gemini", "Groq"],
        index=0 if env_cfg["gemini_api_key"] else 1,
        horizontal=True,
    )

    if provider == "Gemini":
        selected_model = st.text_input(
            "Gemini Model (from `GEMINI_MODEL` in `.env`)",
            value=env_cfg["gemini_model"],
            help="Loaded from GEMINI_MODEL in .env (e.g., gemini-2.5-flash, gemini-2.5-pro)",
        )
        api_key_input = st.text_input(
            "Gemini API Key (`GEMINI_API_KEY`)",
            value=env_cfg["gemini_api_key"],
            type="password",
            placeholder="Paste your Gemini API key or set GEMINI_API_KEY in .env",
            help="Loaded from GEMINI_API_KEY in .env. You can also enter or override it here.",
        )
        if env_cfg["gemini_api_key"]:
            st.caption(f"✅ Loaded `GEMINI_MODEL={env_cfg['gemini_model']}` & `GEMINI_API_KEY` from `.env`")
        elif api_key_input:
            st.caption("✅ Using Gemini API key entered above")
        else:
            st.warning("⚠️ Enter your `GEMINI_API_KEY` above or in `.env`")
    else:
        selected_model = st.text_input(
            "Groq Model (from `GROQ_MODEL` in `.env`)",
            value=env_cfg["groq_model"],
            help="Loaded from GROQ_MODEL in .env (e.g., openai/gpt-oss-20b, llama-3.3-70b-versatile)",
        )
        api_key_input = st.text_input(
            "Groq API Key (`GROQ_API_KEY`)",
            value=env_cfg["groq_api_key"],
            type="password",
            placeholder="Paste your Groq API key or set GROQ_API_KEY in .env",
            help="Loaded from GROQ_API_KEY in .env. You can also enter or override it here.",
        )
        if env_cfg["groq_api_key"]:
            st.caption(f"✅ Loaded `GROQ_MODEL={env_cfg['groq_model']}` & `GROQ_API_KEY` from `.env`")
        elif api_key_input:
            st.caption("✅ Using Groq API key entered above")
        else:
            st.warning("⚠️ Enter your `GROQ_API_KEY` above or in `.env`")

    temperature = st.slider(
        "Creativity / Temperature",
        min_value=0.1,
        max_value=1.0,
        value=0.6,
        step=0.1,
    )


# --- MAIN HEADER ---
st.title("🏋️ AI Personalized Workout & Exercise Planner")
st.markdown(
    "Generate a safe, science-backed exercise program tailored to your **biometrics**, **health conditions / lab markers**, and **fitness goals**."
)

# --- INPUT SECTIONS ---
col_bio, col_goals = st.columns([1, 1], gap="large")

with col_bio:
    st.subheader("1️⃣ Biometrics & Body Profile")

    b_col1, b_col2 = st.columns(2)
    with b_col1:
        age = st.number_input("Age (years)", min_value=14, max_value=100, value=int(rec["age"]))
        gender_options = ["Male", "Female", "Other"]
        default_gender_idx = gender_options.index(rec["gender"]) if rec["gender"] in gender_options else 0
        gender = st.selectbox("Gender", options=gender_options, index=default_gender_idx)

    with b_col2:
        exp_options = ["Beginner", "Intermediate", "Advanced"]
        default_exp_idx = 0
        for idx, opt in enumerate(exp_options):
            if opt.lower() in rec["experience"].lower():
                default_exp_idx = idx
                break
        experience = st.selectbox("Fitness Experience", options=exp_options, index=default_exp_idx)
        unit_system = st.radio("Measurement Units", options=["Metric (kg, cm)", "Imperial (lbs, ft/in)"], horizontal=True)

    u_col1, u_col2 = st.columns(2)
    if unit_system.startswith("Metric"):
        with u_col1:
            weight_val = st.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=float(rec["weight_kg"]), step=0.5)
            weight_kg = convert_weight_to_kg(weight_val, "kg")
        with u_col2:
            height_val = st.number_input("Height (cm)", min_value=100.0, max_value=230.0, value=float(rec["height_cm"]), step=0.5)
            height_cm = convert_height_to_cm(height_val, "cm")
    else:
        default_lbs = round(float(rec["weight_kg"]) / 0.453592, 1)
        total_in = float(rec["height_cm"]) / 2.54
        default_ft = int(total_in // 12)
        default_in = round(total_in % 12, 1)
        with u_col1:
            weight_lbs = st.number_input("Weight (lbs)", min_value=66.0, max_value=550.0, value=default_lbs, step=1.0)
            weight_kg = convert_weight_to_kg(weight_lbs, "lbs")
        with u_col2:
            f_col, i_col = st.columns(2)
            with f_col:
                height_ft = st.number_input("Feet", min_value=3, max_value=7, value=default_ft, step=1)
            with i_col:
                height_in = st.number_input("Inches", min_value=0.0, max_value=11.5, value=default_in, step=0.5)
            height_cm = convert_height_to_cm(height_ft, "ft", height_in)

with col_goals:
    st.subheader("2️⃣ Fitness Goals & Training Logistics")

    goal_options = [
        "Fat Loss & Metabolic Health",
        "Muscle Building & Strength",
        "Fat Loss & Insulin Sensitivity",
        "Endurance & Event Prep",
        "Mobility, Posture & Joint Health",
        "General Wellness & Longevity",
    ]
    default_goal_idx = 0
    for idx, g in enumerate(goal_options):
        if rec["primary_goal"].lower() in g.lower() or g.lower() in rec["primary_goal"].lower():
            default_goal_idx = idx
            break

    primary_goal = st.selectbox("Primary Fitness Goal", options=goal_options, index=default_goal_idx)
    goal_detail = st.text_input(
        "Specific Target or Goal Details",
        value=rec["goal_detail"],
        placeholder="e.g., Lose 8 kg, run a 5K without knee pain, build upper body strength...",
    )

    g_col1, g_col2 = st.columns(2)
    with g_col1:
        days_per_week = st.slider("Workout Days / Week", min_value=1, max_value=7, value=int(rec["days_per_week"]))
        equipment_options = [
            "Full Gym",
            "Dumbbells & Resistance Bands (Home)",
            "Bodyweight Only (No Equipment)",
            "Running Shoes, Dumbbells, Resistance Bands",
            "Kettlebells & Pull-up Bar",
        ]
        default_eq_idx = equipment_options.index(rec["equipment"]) if rec["equipment"] in equipment_options else 0
        equipment = st.selectbox("Available Equipment", options=equipment_options, index=default_eq_idx)

    with g_col2:
        session_duration_min = st.select_slider(
            "Session Duration (minutes)",
            options=[20, 30, 45, 60, 75, 90],
            value=int(rec["session_duration_min"]) if int(rec["session_duration_min"]) in [20, 30, 45, 60, 75, 90] else 45,
        )
        workout_style = st.selectbox(
            "Preferred Training Style",
            options=[
                "Balanced Strength & Conditioning",
                "Progressive Resistance / Hypertrophy",
                "Low-Impact Circuit & Zone 2 Cardio",
                "Athletic & Functional Movement",
                "Calisthenics & Mobility",
            ],
        )

# --- LIVE BIOMETRIC DASHBOARD ---
bmi_info = calculate_bmi(weight_kg, height_cm)
metabolic_info = estimate_bmr_tdee(gender, age, weight_kg, height_cm, days_per_week)
ideal_min, ideal_max = bmi_info.get("ideal_weight_range_kg", (0, 0))

st.markdown("#### 📊 Live Biometric Snapshot")
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.markdown(
        f"""
        <div class="metric-card" style="border-left: 5px solid {bmi_info['color']};">
            <div class="metric-label">Body Mass Index (BMI)</div>
            <div class="metric-value">{bmi_info['bmi']} <span style="font-size:1rem; color:{bmi_info['color']};">({bmi_info['category']})</span></div>
            <div class="metric-sub">{bmi_info['description']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col2:
    st.markdown(
        f"""
        <div class="metric-card" style="border-left: 5px solid #6366f1;">
            <div class="metric-label">Basal Metabolic Rate (BMR)</div>
            <div class="metric-value">{metabolic_info['bmr']:,} <span style="font-size:1rem; color:#94a3b8;">kcal / day</span></div>
            <div class="metric-sub">Resting energy expenditure (Mifflin-St Jeor) | Healthy Weight Range: {ideal_min}–{ideal_max} kg</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col3:
    st.markdown(
        f"""
        <div class="metric-card" style="border-left: 5px solid #10b981;">
            <div class="metric-label">Estimated TDEE ({days_per_week} days/wk)</div>
            <div class="metric-value">{metabolic_info['tdee']:,} <span style="font-size:1rem; color:#94a3b8;">kcal / day</span></div>
            <div class="metric-sub">Cut: ~{max(1200, metabolic_info['tdee'] - 450):,} kcal | Maintain: {metabolic_info['tdee']:,} kcal | Lean Bulk: ~{metabolic_info['tdee'] + 250:,} kcal</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# --- HEALTH CONDITIONS & LAB REPORT SECTION ---
st.subheader("3️⃣ Health Status, Physical Limitations & Lab Reports")

h_col1, h_col2 = st.columns([1, 1], gap="large")

with h_col1:
    health_tags = st.multiselect(
        "Select Any Active Health Conditions or Considerations",
        options=[
            "High Cholesterol / Elevated Triglycerides",
            "Pre-Diabetes / Insulin Resistance",
            "High Blood Pressure (Hypertension)",
            "Knee Pain / Osteoarthritis",
            "Lower Back Stiffness / Disc Sensitivity",
            "Shoulder Impingement / Wrist Pain",
            "Vitamin D or Iron Deficiency",
            "Asthma / Exercise-Induced Bronchospasm",
            "PCOS / Thyroid Condition",
        ],
        help="The AI coach will automatically modify exercise impact, heart-rate zones, and safety cues for selected conditions.",
    )

    limitations_text = st.text_area(
        "Injuries, Medical Advice, or Physical Limitations",
        value=rec["limitations"],
        height=90,
        placeholder="e.g., Avoid overhead pressing on left shoulder, mild lower back stiffness, doctor advised low-impact cardio...",
    )

    l_col1, l_col2 = st.columns(2)
    with l_col1:
        sleep_hours = st.slider("Avg Sleep (hrs/night)", min_value=4.0, max_value=10.0, value=7.0, step=0.5)
    with l_col2:
        stress_level = st.select_slider("Daily Stress Level", options=["Low", "Moderate", "High"], value="Moderate")

with h_col2:
    uploaded_report = st.file_uploader(
        "Optional: Upload Blood / Health Report (.pdf, .txt, .csv)",
        type=["pdf", "txt", "csv"],
        help="Upload a lab report to factor biomarkers (lipids, HbA1c, iron, vitamins) into your exercise plan.",
    )

    if uploaded_report is not None:
        extracted_text = extract_text_from_upload(uploaded_report)
    else:
        extracted_text = selected_preset["report_text"]

    health_report_text = st.text_area(
        "Lab Report / Clinical Notes Context (Editable)",
        value=extracted_text,
        height=155,
        placeholder="Paste any blood test results, lipid panel numbers, or clinical notes here (or select a sample profile in the sidebar)...",
    )

    if health_report_text.strip():
        detected_markers = quick_scan_biomarkers(health_report_text)
        if detected_markers:
            badges = [f"**{cat}**: {', '.join(terms)}" for cat, terms in detected_markers.items()]
            st.caption("🔬 **Detected Biomarker Categories:** " + " | ".join(badges))

# Combine selected health tags with custom limitations text
combined_limitations = []
if health_tags:
    combined_limitations.append("Conditions: " + ", ".join(health_tags))
if limitations_text and limitations_text.strip():
    combined_limitations.append(limitations_text.strip())
final_limitations_str = " | ".join(combined_limitations) if combined_limitations else "None"

user_profile = {
    "age": age,
    "gender": gender,
    "weight_kg": weight_kg,
    "height_cm": height_cm,
    "experience": experience,
    "primary_goal": primary_goal,
    "goal_detail": goal_detail,
    "days_per_week": days_per_week,
    "session_duration_min": session_duration_min,
    "equipment": equipment,
    "workout_style": workout_style,
    "limitations": final_limitations_str,
    "sleep_hours": sleep_hours,
    "stress_level": stress_level,
}

st.divider()

# --- GENERATE WORKOUT PLAN BUTTON ---
generate_btn = st.button(
    f"🚀 Generate My Personalized AI Workout Plan ({provider}: {selected_model})",
    type="primary",
    use_container_width=True,
)

if generate_btn:
    with st.spinner(f"🧠 Analyzing your biometrics, health markers, and goals with {provider} ({selected_model})..."):
        try:
            plan_md = generate_workout_plan(
                profile=user_profile,
                bmi_info=bmi_info,
                metabolic_info=metabolic_info,
                health_report_text=health_report_text,
                provider=provider,
                model_name=selected_model,
                api_key=api_key_input,
                temperature=temperature,
            )
            st.session_state.workout_plan = plan_md
            st.session_state.last_profile = user_profile
            st.session_state.followup_history = []
        except Exception as err:
            st.error(f"Error generating workout plan: {err}")

# --- DISPLAY GENERATED PLAN & INTERACTIVE COACH ---
if st.session_state.workout_plan:
    st.success("✅ Your personalized workout plan is ready!")

    dl_col1, dl_col2 = st.columns([4, 1])
    with dl_col2:
        st.download_button(
            label="📥 Download Plan (.md)",
            data=st.session_state.workout_plan,
            file_name="personalized_workout_plan.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with st.container(border=True):
        st.markdown(st.session_state.workout_plan)

    st.divider()
    st.subheader("💬 Ask Your AI Fitness Coach (Exercise Swaps & Adjustments)")
    st.caption(
        "Want to swap an exercise, adjust for a sore muscle, or ask about warm-up form? Ask below!"
    )

    for item in st.session_state.followup_history:
        with st.chat_message("user"):
            st.markdown(item["question"])
        with st.chat_message("assistant"):
            st.markdown(item["answer"])

    followup_q = st.chat_input("e.g., Can you replace barbell squats with a knee-friendly dumbbell alternative?")
    if followup_q:
        with st.chat_message("user"):
            st.markdown(followup_q)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = ask_followup_question(
                        workout_plan=st.session_state.workout_plan,
                        user_question=followup_q,
                        profile=st.session_state.last_profile or user_profile,
                        provider=provider,
                        model_name=selected_model,
                        api_key=api_key_input,
                    )
                    st.markdown(answer)
                    st.session_state.followup_history.append(
                        {"question": followup_q, "answer": answer}
                    )
                except Exception as err:
                    st.error(f"Failed to get response: {err}")
