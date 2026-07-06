import re
import unicodedata
from fastapi import HTTPException, status

# Patterns that indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?(?:previous|above|prior)\s+(?:instructions|prompts?|context)",
    r"(?:system|admin|root)\s*(?:prompt|instruction|message)",
    r"(?:you\s+are\s+now|you\s+must\s+now)\s+(?:a|an)?\s*(?:different|evil|harmful)",
    r"forget\s+(?:all|your|previous|everything)",
    r"(?:act|pretend|roleplay)\s+as\s+(?:a\s+)?(?:different|evil|harmful|jailbreak)",
    r"\bDAN\b|jailbreak|prompt\s+injection",
    r"<script[^>]*>",
    r"javascript:",
    r"\\n\\n(?:Human|Assistant|System):",
    r"---\s*(?:END|STOP)\s*(?:OF)?\s*(?:PROMPT|INSTRUCTION)",
    r"(?:override|bypass|ignore)\s+(?:safety|security|filter|guard)",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE | re.UNICODE) for p in INJECTION_PATTERNS]

def detect_injection(text: str) -> bool:
    """Return True if the text contains prompt injection patterns."""
    for pattern in COMPILED_PATTERNS:
        if pattern.search(text):
            return True
    return False

def sanitize_for_agent(text: str) -> str:
    """Remove/escape prompt injection patterns from text."""
    # Normalize unicode to prevent homoglyph attacks
    text = unicodedata.normalize("NFKC", text)
    # Remove detected patterns
    for pattern in COMPILED_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    # Limit consecutive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def validate_emergency_text(text: str) -> str:
    """Validate and sanitize emergency report text."""
    if not text or not text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Description cannot be empty")
    if len(text) > 2000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Description too long (max 2000 chars)")
    if detect_injection(text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input detected. Please provide a genuine emergency description."
        )
    return sanitize_for_agent(text)
