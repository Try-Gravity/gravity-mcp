"""troubleshoot tool — diagnose common Gravity ad integration issues."""

from __future__ import annotations

import re

from data.troubleshoot_kb import TROUBLESHOOT_KB

_STOP_WORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "my", "i", "me", "we", "our", "it", "its", "this", "that", "these",
    "to", "of", "in", "on", "at", "for", "with", "from", "by", "as",
    "and", "or", "but", "not", "so", "if", "when", "how", "what", "why",
    "do", "does", "did", "have", "has", "had", "get", "got", "getting",
    "just", "very", "too", "also", "only", "even", "still", "any", "some",
})


def _tokenize(text: str) -> set[str]:
    """Extract meaningful lowercase tokens, filtering stop words."""
    words = set(re.findall(r"[a-z0-9_]+", text.lower()))
    return words - _STOP_WORDS


def _format_entry(entry: dict[str, str]) -> dict[str, str]:
    return {
        "symptom": entry["symptom"],
        "cause": entry["cause"],
        "fix": entry["fix"],
        "reference_url": entry["reference_url"],
    }


def troubleshoot(symptom: str) -> dict:
    """Diagnose a Gravity ad integration issue based on the described symptom.

    Uses phrase-level substring matching first (high confidence), then falls
    back to word-level scoring for natural-language descriptions.

    Args:
        symptom: Description of the problem (e.g. "no ads showing", "401 error", "CORS").

    Returns:
        Matching KB entry with symptom, cause, fix, and reference_url.
        If no match, returns a generic response with common symptom list.
    """
    symptom_lower = symptom.lower()

    for entry in TROUBLESHOOT_KB:
        keywords = [kw.strip().lower() for kw in entry["keywords"].split(",")]
        if any(kw in symptom_lower for kw in keywords):
            return _format_entry(entry)

    symptom_tokens = _tokenize(symptom)
    if not symptom_tokens:
        return _fallback(symptom)

    best_entry = None
    best_score = 0.0

    for entry in TROUBLESHOOT_KB:
        entry_tokens = set()
        for kw in entry["keywords"].split(","):
            entry_tokens.update(_tokenize(kw))
        entry_tokens.update(_tokenize(entry["symptom"]))

        overlap = symptom_tokens & entry_tokens
        if not overlap:
            continue

        score = len(overlap) / max(len(symptom_tokens), 1)

        if score > best_score:
            best_score = score
            best_entry = entry

    if best_entry and best_score >= 0.25:
        return _format_entry(best_entry)

    return _fallback(symptom)


def _fallback(symptom: str) -> dict[str, str]:
    common = [entry["symptom"] for entry in TROUBLESHOOT_KB[:5]]
    return {
        "symptom": symptom,
        "cause": "No matching diagnosis found.",
        "fix": (
            "Contact Gravity support at https://trygravity.ai/support. "
            "Common issues include:\n"
            + "\n".join(f"  - {s}" for s in common)
        ),
        "reference_url": "https://docs.trygravity.ai",
    }
