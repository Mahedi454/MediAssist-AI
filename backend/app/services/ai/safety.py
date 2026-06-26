"""Lightweight safety checks for the medical chat.

These checks are intentionally conservative: the goal is to surface an
urgent-care notice when a message contains red-flag language, not to diagnose.
A keyword/phrase match keeps the check fast, offline, and predictable, and it
runs in addition to (not instead of) the model's own safety guidance.
"""

import re

# Red-flag phrases that may indicate a medical emergency. Word boundaries keep
# matches precise (e.g. "stroke" should not fire inside "keystroke").
_EMERGENCY_PATTERNS = (
    r"chest pain",
    r"can'?t breathe",
    r"cannot breathe",
    r"difficulty breathing",
    r"short(ness)? of breath",
    r"severe bleeding",
    r"unconscious",
    r"unresponsive",
    r"suicid(e|al)",
    r"kill (myself|himself|herself|themself)",
    r"want to die",
    r"heart attack",
    r"\bstroke\b",
    r"face droop",
    r"slurred speech",
    r"overdose",
    r"seizure",
    r"anaphylaxis",
    r"severe allergic reaction",
    r"coughing up blood",
    r"vomiting blood",
)

_EMERGENCY_REGEX = re.compile("|".join(_EMERGENCY_PATTERNS), re.IGNORECASE)


def is_potential_emergency(text: str) -> bool:
    """Return ``True`` if ``text`` contains red-flag language suggesting an emergency."""
    if not text:
        return False
    return _EMERGENCY_REGEX.search(text) is not None
