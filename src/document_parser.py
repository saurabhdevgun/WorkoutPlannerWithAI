"""
Document Parser: Extracts and scans text from PDF and TXT health/blood reports.
"""

import io
import re
from typing import Dict, List
import pypdf


def extract_text_from_upload(uploaded_file) -> str:
    """
    Extracts text from Streamlit UploadedFile object (.pdf or .txt).
    """
    if uploaded_file is None:
        return ""

    filename = uploaded_file.name.lower()
    content = ""

    try:
        if filename.endswith(".pdf"):
            pdf_bytes = uploaded_file.read()
            # Reset pointer in case it needs to be read again
            uploaded_file.seek(0)
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            pages_text = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(f"--- Page {i+1} ---\n" + page_text.strip())
            content = "\n\n".join(pages_text)

        elif filename.endswith(".txt") or filename.endswith(".csv"):
            raw_bytes = uploaded_file.read()
            uploaded_file.seek(0)
            try:
                content = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                content = raw_bytes.decode("latin-1", errors="replace")
        else:
            # Fallback attempt text decode
            raw_bytes = uploaded_file.read()
            uploaded_file.seek(0)
            content = raw_bytes.decode("utf-8", errors="replace")

    except Exception as e:
        return f"[Error parsing file {uploaded_file.name}: {str(e)}]"

    # Clean redundant whitespace
    cleaned = re.sub(r"\n{3,}", "\n\n", content).strip()
    # Safety limit to avoid context blowout (approx 15,000 characters is plenty for lab reports)
    if len(cleaned) > 15000:
        cleaned = cleaned[:15000] + "\n\n[Note: Report truncated to first 15,000 characters for optimal processing]"

    return cleaned


COMMON_BIOMARKER_PATTERNS = {
    "Lipids & Cholesterol": [r"\bcholesterol\b", r"\bldl\b", r"\bhdl\b", r"\btriglycerides?\b", r"\bvldl\b"],
    "Blood Sugar & Metabolic": [r"\bhba1c\b", r"\bglucose\b", r"\bfasting sugar\b", r"\binsulin\b"],
    "Vitamins & Minerals": [r"\bvitamin\s*d\b", r"\bvit\s*d3?\b", r"\bvitamin\s*b12\b", r"\bferritin\b", r"\biron\b", r"\bcalcium\b"],
    "Complete Blood Count (CBC)": [r"\bhemoglobin\b", r"\brbc\b", r"\bwbc\b", r"\bplatelets?\b", r"\bhematocrit\b"],
    "Liver & Kidney Function": [r"\bsgot\b", r"\bsgpt\b", r"\balt\b", r"\bast\b", r"\bcreatinine\b", r"\be?gfr\b", r"\buric acid\b", r"\bbun\b"],
    "Hormones & Thyroid": [r"\btsh\b", r"\bt3\b", r"\bt4\b", r"\btestosterone\b", r"\bcortisol\b"],
    "Inflammation": [r"\bhs-?crp\b", r"\bcrp\b", r"\besr\b"],
}


def quick_scan_biomarkers(report_text: str) -> Dict[str, List[str]]:
    """
    Scans report text for presence of prominent biomarker categories.
    Returns matched categories and terms.
    """
    if not report_text:
        return {}

    lower_text = report_text.lower()
    detected = {}

    for category, patterns in COMMON_BIOMARKER_PATTERNS.items():
        found = []
        for pat in patterns:
            match = re.search(pat, lower_text)
            if match:
                term = match.group(0).upper()
                if term not in found:
                    found.append(term)
        if found:
            detected[category] = found

    return detected
