import pytest

from app.services.ai.safety import is_potential_emergency


@pytest.mark.parametrize(
    "message",
    [
        "I have severe chest pain radiating to my arm",
        "My father is unconscious and not responding",
        "I can't breathe properly since this morning",
        "She is showing signs of a stroke with slurred speech",
        "I think I'm having a heart attack",
        "I have been coughing up blood",
        "I am having suicidal thoughts",
    ],
)
def test_detects_emergency_language(message: str) -> None:
    assert is_potential_emergency(message) is True


@pytest.mark.parametrize(
    "message",
    [
        "What is diabetes?",
        "Which foods help with iron deficiency?",
        "Can you explain how asthma works?",
        "I want to understand my cholesterol report",
        "",
    ],
)
def test_ignores_non_emergency_language(message: str) -> None:
    assert is_potential_emergency(message) is False


def test_detection_is_case_insensitive() -> None:
    assert is_potential_emergency("SEVERE CHEST PAIN") is True
