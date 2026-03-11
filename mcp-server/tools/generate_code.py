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

DARK_MODE_SNIPPET = """\

// Dark mode styling
// Append these slotProps to your <GravityAd /> for dark backgrounds:
//
// style={{
//   background: '#18181B',
//   color: '#FAFAFA',
//   border: '1px solid #3F3F46',
//   boxShadow: '0 2px 8px rgba(0,0,0,0.4)',
// }}
// slotProps={{
//   brand: { style: { color: '#FAFAFA' } },
//   title: { style: { color: '#FAFAFA' } },
//   text:  { style: { color: '#A1A1AA' } },
//   label: { style: { color: '#A1A1AA', border: '1px solid #3F3F46' } },
//   cta:   { style: { background: '#3B82F6' } },
// }}
"""

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
    customizations: str | None = None,
) -> dict:
    """Generate paired server + client integration code for Gravity ads.

    Args:
        format: One of the 25 ad format names (e.g. "floating", "card", "banner").
        framework: Server framework — "fastapi" or "nextjs".
        streaming: True for SSE streaming, False for JSON response.
        theme: Optional "dark" to append dark mode styling recipe.
        customizations: Natural language style description (informational, for LLM context).

    Returns:
        Dict with placement_id, style, type, framework, platform, performance,
        server_code, and client_code.
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

    if theme == "dark":
        client_code += DARK_MODE_SNIPPET

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

    return {
        "placement_id": placement_id,
        "style": format,
        "type": style_type,
        "framework": framework,
        "platform": "web",
        "performance": "",
        "server_code": server_code,
        "client_code": client_code,
    }
