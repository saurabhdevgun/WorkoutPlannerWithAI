"""
Sample blood reports and profile presets for testing and demonstration.
"""

SAMPLE_BLOOD_REPORTS = {
    "Custom / None (Enter Manually)": {
        "title": "Custom User Input",
        "description": "Enter your own biometrics, health conditions, and fitness goals.",
        "recommended_profile": {
            "age": 30,
            "gender": "Male",
            "weight_kg": 75.0,
            "height_cm": 175.0,
            "experience": "Intermediate",
            "primary_goal": "Muscle Building & Strength",
            "is_event": False,
            "goal_detail": "Build lean muscle, improve posture and core strength",
            "days_per_week": 4,
            "session_duration_min": 45,
            "equipment": "Full Gym",
            "limitations": "None",
        },
        "report_text": "",
    },
    "High Cholesterol & Low Vitamin D": {
        "title": "Lipid & Vitamin Panel - Borderline High Cholesterol & Low Vit D",
        "description": "Common sedentary profile with elevated LDL/Triglycerides and Vitamin D deficiency.",
        "recommended_profile": {
            "age": 34,
            "gender": "Male",
            "weight_kg": 84.0,
            "height_cm": 178.0,
            "experience": "Beginner",
            "primary_goal": "Fat Loss & Metabolic Health",
            "is_event": False,
            "goal_detail": "Reduce visceral fat, improve cardiovascular stamina, lower LDL cholesterol",
            "days_per_week": 4,
            "session_duration_min": 45,
            "equipment": "Full Gym",
            "limitations": "Mild lower back stiffness from sitting 9 hours/day",
        },
        "report_text": """LABORATORY DIAGNOSTIC REPORT
Patient Name: John Doe | Age: 34 | Gender: Male
LIPID PANEL:
- Total Cholesterol: 238 mg/dL (Desirable: <200) -> HIGH
- Triglycerides: 215 mg/dL (Normal: <150) -> HIGH
- HDL Cholesterol: 41 mg/dL (Normal: >40) -> BORDERLINE
- LDL Cholesterol: 154 mg/dL (Optimal: <100) -> HIGH
METABOLIC & GLYCEMIC:
- Fasting Blood Sugar: 98 mg/dL (Normal: 70-99) -> NORMAL
- HbA1c: 5.6% (Normal: <5.7%) -> BORDERLINE NORMAL
VITAMINS & MINERALS:
- 25-Hydroxy Vitamin D: 16.2 ng/mL (Deficient: <20, Optimal: 30-100) -> DEFICIENT
- Vitamin B12: 380 pg/mL (Normal: 200-900) -> NORMAL
Clinical Impression: Elevated atherogenic lipids (LDL and Triglycerides) and Vitamin D deficiency. Moderate aerobic exercise and progressive resistance training recommended.""",
    },
    "Pre-Diabetic & Knee Sensitivity": {
        "title": "Metabolic Panel - Elevated Fasting Glucose & Joint Sensitivity",
        "description": "Metabolic stress profile showing elevated blood sugar and mild right knee discomfort.",
        "recommended_profile": {
            "age": 42,
            "gender": "Male",
            "weight_kg": 96.0,
            "height_cm": 175.0,
            "experience": "Beginner",
            "primary_goal": "Fat Loss & Insulin Sensitivity",
            "is_event": False,
            "goal_detail": "Improve blood glucose control, increase daily energy, lose 10 kg safely",
            "days_per_week": 4,
            "session_duration_min": 45,
            "equipment": "Dumbbells & Resistance Bands (Home)",
            "limitations": "Right knee discomfort during deep squats or high-impact jumping",
        },
        "report_text": """METABOLIC & COMPREHENSIVE HEALTH PANEL
Patient Age: 42 | Gender: Male
GLYCEMIC & METABOLIC:
- Fasting Blood Glucose: 114 mg/dL (Normal: 70-99, Pre-diabetes: 100-125) -> ELEVATED
- HbA1c: 6.1% (Normal: <5.7%, Pre-diabetes: 5.7%-6.4%) -> ELEVATED
- Fasting Serum Insulin: 18.5 uIU/mL (Normal: 2.6-24.9) -> ELEVATED
LIPID PROFILE:
- Triglycerides: 230 mg/dL (Normal: <150) -> ELEVATED
- HDL: 38 mg/dL (Desirable: >40) -> LOW
INFLAMMATORY MARKERS:
- hs-CRP: 3.4 mg/L (Low Risk: <1.0, High Risk: >3.0) -> ELEVATED
Notes: Structured low-impact Zone 2 cardio and resistance training strongly advised to improve insulin sensitivity while protecting knee joints.""",
    },
    "Endurance Runner (Half Marathon Prep)": {
        "title": "Athletic Screen - Borderline Low Ferritin / Iron Stores",
        "description": "Intermediate runner preparing for a Half Marathon with borderline low iron stores.",
        "recommended_profile": {
            "age": 28,
            "gender": "Female",
            "weight_kg": 58.0,
            "height_cm": 168.0,
            "experience": "Intermediate",
            "primary_goal": "Endurance & Event Prep",
            "is_event": True,
            "goal_detail": "Half Marathon (21.1 km) in 10 weeks, aiming for strong finish without overtraining",
            "days_per_week": 5,
            "session_duration_min": 60,
            "equipment": "Running Shoes, Dumbbells, Resistance Bands",
            "limitations": "Tight hamstrings and borderline low ferritin (needs smart recovery)",
        },
        "report_text": """ENDURANCE SPORTS HEMATOLOGY PANEL
Patient Age: 28 | Gender: Female
HEMATOLOGY / IRON STATUS:
- Hemoglobin: 12.2 g/dL (Normal: 12.0-15.5) -> LOW NORMAL
- Serum Ferritin: 18 ng/mL (Normal: 15-150, Optimal for endurance: >35) -> BORDERLINE LOW
- Creatine Kinase (CK): 260 U/L (Normal: 30-200) -> ELEVATED (Recent training load)
VITAMINS & HORMONES:
- Vitamin D: 42 ng/mL (Optimal: 30-100) -> OPTIMAL
- TSH: 1.85 mIU/L (Normal: 0.4-4.0) -> NORMAL
Recommendation: Smart recovery scheduling and strength work to prevent injury and overtraining.""",
    },
}

