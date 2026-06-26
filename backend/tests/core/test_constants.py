from app.core.constants import MEDICAL_DISCLAIMER, append_disclaimer


def test_append_disclaimer_adds_disclaimer() -> None:
    result = append_disclaimer("Some educational answer.")
    assert MEDICAL_DISCLAIMER in result


def test_append_disclaimer_is_idempotent() -> None:
    once = append_disclaimer("Answer.")
    twice = append_disclaimer(once)
    assert once == twice
    assert twice.count(MEDICAL_DISCLAIMER) == 1
