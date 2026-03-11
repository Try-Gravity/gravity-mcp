"""troubleshoot tool — diagnose common Gravity ad integration issues."""

from __future__ import annotations

from data.troubleshoot_kb import TROUBLESHOOT_KB


def troubleshoot(symptom: str) -> dict:
    """Diagnose a Gravity ad integration issue based on the described symptom.

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
            return {
                "symptom": entry["symptom"],
                "cause": entry["cause"],
                "fix": entry["fix"],
                "reference_url": entry["reference_url"],
            }

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
