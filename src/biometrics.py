"""
Biometric calculations: BMI, BMR, TDEE, and unit conversions.
"""

from typing import Dict, Any


def convert_weight_to_kg(val: float, unit: str) -> float:
    if unit.lower() in ["lbs", "lb", "pounds"]:
        return round(val * 0.453592, 2)
    return round(val, 2)


def convert_height_to_cm(val: float, unit: str, inches: float = 0.0) -> float:
    if unit.lower() in ["ft", "feet", "ft/in"]:
        total_inches = (val * 12.0) + inches
        return round(total_inches * 2.54, 2)
    return round(val, 2)


def calculate_bmi(weight_kg: float, height_cm: float) -> Dict[str, Any]:
    """Calculates BMI and returns classification and badge metadata."""
    if height_cm <= 0 or weight_kg <= 0:
        return {
            "bmi": 0.0,
            "category": "Unknown",
            "color": "#9ca3af",
            "description": "Please provide valid height and weight.",
        }

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        category = "Underweight"
        color = "#3b82f6"  # Blue
        desc = "Below standard range. Focus on progressive strength training and a caloric surplus."
    elif 18.5 <= bmi < 25.0:
        category = "Normal / Healthy"
        color = "#10b981"  # Emerald green
        desc = "Optimal biometric range. Focus on body recomposition, endurance, or muscle building."
    elif 25.0 <= bmi < 30.0:
        category = "Overweight"
        color = "#f59e0b"  # Amber
        desc = "Above standard range. Emphasize resistance training paired with moderate caloric deficit or metabolic conditioning."
    elif 30.0 <= bmi < 35.0:
        category = "Obese (Class I)"
        color = "#ef4444"  # Red
        desc = "Higher joint and cardiovascular stress. Emphasize low-impact cardio, progressive resistance, and metabolic health."
    else:
        category = "Obese (Class II/III)"
        color = "#b91c1c"  # Dark red
        desc = "Significant clinical attention advised. Focus on gentle, joint-friendly movement and doctor-aligned guidance."

    ideal_min_kg = round(18.5 * (height_m ** 2), 1)
    ideal_max_kg = round(24.9 * (height_m ** 2), 1)

    return {
        "bmi": bmi,
        "category": category,
        "color": color,
        "description": desc,
        "ideal_weight_range_kg": (ideal_min_kg, ideal_max_kg),
    }


def estimate_bmr_tdee(
    gender: str,
    age: int,
    weight_kg: float,
    height_cm: float,
    days_per_week: int = 3,
) -> Dict[str, int]:
    """Estimates BMR and TDEE using Mifflin-St Jeor formula."""
    if weight_kg <= 0 or height_cm <= 0 or age <= 0:
        return {"bmr": 0, "tdee": 0}

    # Base BMR
    if gender.lower() == "female":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    else:  # male or general default
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5

    # Activity multiplier based on days/week
    if days_per_week <= 1:
        mult = 1.2  # sedentary
    elif days_per_week <= 3:
        mult = 1.375  # light
    elif days_per_week <= 5:
        mult = 1.55  # moderate
    else:
        mult = 1.725  # very active

    tdee = bmr * mult
    return {"bmr": int(round(bmr)), "tdee": int(round(tdee))}
