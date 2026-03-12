"""generate_code tool — produce paired server + client integration code."""

from __future__ import annotations

import csv
import fcntl
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from data.style_type_map import STYLE_TYPE_MAP
from resources.format_catalog import FORMAT_CATALOG
from tools.build_theme import build_theme as _build_theme

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CSV_PATH = _DATA_DIR / "placements.csv"
_CSV_FIELDS = [
    "placement_id",
    "style",
    "type",
    "framework",
    "platform",
    "performance",
    "created_at",
]

_DARK_PRESET = {
    "bg_color": "#18181B",
    "text_color": "#FAFAFA",
    "accent_color": "#3B82F6",
    "secondary_color": "#A1A1AA",
    "border_color": "#3F3F46",
}

_TEMPLATE_MAP: dict[tuple[str, bool], str] = {
    ("fastapi", True): "templates.fastapi_streaming",
    ("fastapi", False): "templates.fastapi_nonstreaming",
    ("nextjs", True): "templates.nextjs_streaming",
    ("nextjs", False): "templates.nextjs_nonstreaming",
}


def _load_template(framework: str, streaming: bool) -> tuple[str, str]:
    """Dynamically import and return (SERVER_CODE, CLIENT_CODE) for the combo."""
    key = (framework, streaming)
    module_path = _TEMPLATE_MAP.get(key)
    if module_path is None:
        raise ValueError(f"No template for framework={framework}, streaming={streaming}")

    import importlib

    mod = importlib.import_module(module_path)
    return mod.SERVER_CODE, mod.CLIENT_CODE


def _write_csv_row(row: dict[str, str]) -> None:
    """Append a row to placements.csv with file locking."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = _CSV_PATH.exists()
    with open(_CSV_PATH, "a", newline="") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def generate_code(
    format: str,
    framework: Literal["fastapi", "nextjs"] = "fastapi",
    streaming: bool = True,
    theme: Literal["light", "dark"] | None = None,
    bg_color: str | None = None,
    text_color: str | None = None,
    accent_color: str | None = None,
    secondary_color: str | None = None,
    border_color: str | None = None,
    border_radius: int | None = None,
    font_family: str | None = None,
) -> dict:
    """Generate paired server + client integration code for Gravity ads.

    The generated code automatically matches the publisher's site theme.
    Pass design tokens extracted from the publisher's CSS/Tailwind config
    so the ad blends in natively. If no tokens are provided and theme is
    not set, the ad uses sensible defaults for a light background.

    Args:
        format: One of the 25 ad format names (e.g. "floating", "card", "banner").
        framework: Server framework — "fastapi" or "nextjs".
        streaming: True for SSE streaming, False for JSON response.
        theme: Preset — "dark" auto-fills dark palette tokens. Individual
            color params override preset values when both are provided.
        bg_color: Site background color (e.g. "#FFFFFF", "#1a1a2e").
        text_color: Primary text color.
        accent_color: Brand/accent color for CTA buttons.
        secondary_color: Secondary/muted text color.
        border_color: Border color.
        border_radius: Border radius in pixels.
        font_family: CSS font-family string.

    Returns:
        Dict with placement_id, style, type, framework, platform, performance,
        server_code, client_code, and theme_applied (the resolved theme props).
    """
    if format not in STYLE_TYPE_MAP:
        return {
            "error": f"Unknown format: '{format}'. "
            f"Available formats: {', '.join(sorted(STYLE_TYPE_MAP.keys()))}"
        }

    style_type = STYLE_TYPE_MAP[format]
    format_entry = FORMAT_CATALOG[format]
    format_code = format_entry["code"]

    try:
        server_template, client_template = _load_template(framework, streaming)
    except ValueError as e:
        return {"error": str(e)}

    placement_id = str(uuid.uuid4())

    server_code = server_template.format(
        placement_id=placement_id,
        format_code=format_code,
    )
    client_code = client_template.format(
        placement_id=placement_id,
        format_code=format_code,
    )

    has_explicit_tokens = any(
        v is not None
        for v in [bg_color, text_color, accent_color, secondary_color,
                   border_color, border_radius, font_family]
    )

    theme_result = None
    if theme == "dark" or has_explicit_tokens:
        base = dict(_DARK_PRESET) if theme == "dark" else {}
        overrides = {
            k: v for k, v in {
                "bg_color": bg_color,
                "text_color": text_color,
                "accent_color": accent_color,
                "secondary_color": secondary_color,
                "border_color": border_color,
                "border_radius": border_radius,
                "font_family": font_family,
            }.items() if v is not None
        }
        base.update(overrides)
        theme_result = _build_theme(**base)
        client_code += f"\n\n// Theme overrides (auto-matched to site):\n"
        client_code += f"// Apply these props to <GravityAd /> above:\n"
        client_code += theme_result["code_snippet"]

    _write_csv_row(
        {
            "placement_id": placement_id,
            "style": format,
            "type": style_type,
            "framework": framework,
            "platform": "web",
            "performance": "",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    result = {
        "placement_id": placement_id,
        "style": format,
        "type": style_type,
        "framework": framework,
        "platform": "web",
        "performance": "",
        "server_code": server_code,
        "client_code": client_code,
    }
    if theme_result:
        result["theme_applied"] = {
            "style": theme_result["style"],
            "slotProps": theme_result["slotProps"],
            "is_dark": theme_result["is_dark"],
        }
    return result
