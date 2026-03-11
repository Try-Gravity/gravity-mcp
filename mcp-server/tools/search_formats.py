"""search_formats tool — discover Gravity ad formats with progressive disclosure."""

from __future__ import annotations

from typing import Literal

from resources.format_catalog import FORMAT_CATALOG


def search_formats(
    query: str | None = None,
    category: str | None = None,
    detail: Literal["names", "summary", "full"] = "summary",
) -> list:
    """Search available Gravity ad formats.

    Args:
        query: Natural language or keyword filter (substring match on name + description).
        category: Filter by SDK variant type (e.g. "card", "inline", "banner").
        detail: Level of detail — "names" (list of strings), "summary" (name/description/type),
                or "full" (includes code and omits).

    Returns:
        List of format names (detail="names"), summary dicts, or full dicts.
    """
    entries = list(FORMAT_CATALOG.values())

    if category:
        entries = [e for e in entries if e["type"] == category]

    if query:
        q = query.lower()
        entries = [
            e
            for e in entries
            if q in e["name"].lower() or q in e["description"].lower()
        ]

    if detail == "names":
        return [e["name"] for e in entries]
    elif detail == "summary":
        return [
            {"name": e["name"], "description": e["description"], "type": e["type"]}
            for e in entries
        ]
    else:
        return [
            {
                "name": e["name"],
                "description": e["description"],
                "type": e["type"],
                "code": e["code"],
                "omits": e["omits"],
            }
            for e in entries
        ]
