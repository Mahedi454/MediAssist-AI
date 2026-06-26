MEDICAL_DISCLAIMER = (
    "This information is for educational purposes only and is not a substitute "
    "for professional medical advice, diagnosis, or treatment. Please consult "
    "a qualified healthcare professional for personal medical concerns."
)

EMERGENCY_NOTICE = (
    "**Important:** Your message mentions symptoms that can signal a medical "
    "emergency. If this is urgent, call your local emergency number or go to the "
    "nearest emergency department now. Do not wait for an online response."
)


def append_disclaimer(text: str) -> str:
    """Append the standard medical disclaimer unless the text already contains it."""
    if MEDICAL_DISCLAIMER.lower() in text.lower():
        return text
    return f"{text}\n\n_Disclaimer: {MEDICAL_DISCLAIMER}_"

