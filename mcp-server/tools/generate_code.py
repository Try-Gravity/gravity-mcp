"""generate_code tool — produce paired server + client integration code."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Literal

import httpx

from data.db import write_placement
from data.style_type_map import STYLE_TYPE_MAP
from resources.format_catalog import FORMAT_CATALOG
from tools.build_theme import build_theme as _build_theme, _jsx_val

logger = logging.getLogger(__name__)
_ENGINE_BASE = "https://server.trygravity.ai"


def _register_placement(api_key: str, placement_id: str, placement: str) -> str:
    """Call the engine to register a placement. Returns publisher_id or empty string."""
    try:
        resp = httpx.post(
            f"{_ENGINE_BASE}/api/v1/placements",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"placement_id": placement_id, "placement": placement},
            timeout=5.0,
        )
        if resp.status_code == 200:
            return resp.json().get("publisher_id", "")
    except Exception:
        logger.debug("Engine placement registration failed", exc_info=True)
    return ""


_DARK_PRESET = {
    "bg_color": "#18181B",
    "text_color": "#FAFAFA",
    "accent_color": "#3B82F6",
    "secondary_color": "#A1A1AA",
    "border_color": "#3F3F46",
}

Placement = Literal[
    "above_response",
    "below_response",
    "inline_response",
    "left_response",
    "right_response",
    "search_result",
    "center_page",
    "top_page",
    "bottom_page",
    "left_page",
    "right_page",
]

_VALID_PLACEMENTS: frozenset[str] = frozenset(Placement.__args__)

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


def _render_style_prop(style: dict) -> str:
    """Render a JSX style={{...}} prop block from a dict."""
    lines = ",\n    ".join(f"{k}: {_jsx_val(v)}" for k, v in style.items())
    return f"  style={{{{\n    {lines},\n  }}}}"


def _render_slot_props_prop(slot_props: dict) -> str:
    """Render a JSX slotProps={{...}} prop block from a dict of slot -> css dict."""
    slot_lines = []
    for slot_name, css_dict in slot_props.items():
        inner = ", ".join(f"{k}: {_jsx_val(v)}" for k, v in css_dict.items())
        slot_lines.append(f"    {slot_name}: {{ style: {{ {inner} }} }}")
    return f"  slotProps={{{{\n" + ",\n".join(slot_lines) + ",\n  }}"


def render_format_jsx(format_entry: dict, theme_result: dict | None = None) -> str:
    """Build a GravityAd/AdText JSX string from structured catalog data.

    Merges format base props with optional theme props. Format layout props
    (maxWidth, display, padding, gap, etc.) are preserved as the base layer;
    theme color/font props overlay on top.
    """
    component = format_entry["component"]
    variant = format_entry["variant"]
    extra_props = format_entry.get("extra_props", {})
    base_style = dict(format_entry.get("base_style", {}))
    base_slots = {k: dict(v) for k, v in format_entry.get("base_slot_props", {}).items()}

    if component == "AdText":
        return format_entry["code"]

    merged_style = dict(base_style)
    merged_slots = {k: dict(v) for k, v in base_slots.items()}

    if theme_result:
        for k, v in theme_result["style"].items():
            merged_style[k] = v
        for slot_name, slot_val in theme_result["slotProps"].items():
            if slot_name not in merged_slots:
                merged_slots[slot_name] = {}
            for sk, sv in slot_val["style"].items():
                merged_slots[slot_name][sk] = sv

    lines = [f"<{component}"]
    lines.append("  ad={ad}")
    if variant:
        lines.append(f'  variant="{variant}"')

    for prop_name, prop_val in extra_props.items():
        if isinstance(prop_val, bool):
            lines.append(f"  {prop_name}={{{str(prop_val).lower()}}}")
        elif isinstance(prop_val, str):
            lines.append(f'  {prop_name}="{prop_val}"')
        else:
            lines.append(f"  {prop_name}={{{prop_val}}}")

    if merged_style:
        lines.append(_render_style_prop(merged_style))
    if merged_slots:
        lines.append(_render_slot_props_prop(merged_slots))

    lines.append("/>")
    return "\n".join(lines)


_PLACEMENT_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def generate_code(
    format: str,
    placement_id: str,
    framework: Literal["fastapi", "nextjs"] = "fastapi",
    streaming: bool = True,
    placement: Placement = "below_response",
    api_key: str | None = None,
    publisher_key_hash: str = "",
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

    **Important:** Always confirm `placement` and `placement_id` with the
    publisher before calling this tool. The `placement_id` is a stable
    tracking identifier used for analytics and per-slot revenue attribution
    — it must be consistent across code regenerations.

    Args:
        format: One of the 25 ad format names (e.g. "floating", "card", "banner").
        framework: Server framework — "fastapi" or "nextjs".
        streaming: True for SSE streaming, False for JSON response.
        placement: Ad placement position. One of: above_response, below_response,
            inline_response, left_response, right_response.
        placement_id: Stable tracking ID for this ad slot (e.g. "main",
            "sidebar-1", "bottom-ad"). Must be unique per slot, alphanumeric
            with hyphens/underscores, max 64 chars. Confirmed by the publisher.
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

    if placement not in _VALID_PLACEMENTS:
        return {
            "error": f"Invalid placement: '{placement}'. "
            f"Valid placements: {', '.join(sorted(_VALID_PLACEMENTS))}"
        }

    if not _PLACEMENT_ID_RE.match(placement_id):
        return {
            "error": f"Invalid placement_id: '{placement_id}'. "
            "Must be 1-64 alphanumeric characters, hyphens, or underscores."
        }

    style_type = STYLE_TYPE_MAP[format]
    format_entry = FORMAT_CATALOG[format]

    try:
        server_template, client_template = _load_template(framework, streaming)
    except ValueError as e:
        return {"error": str(e)}

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

        if "error" in theme_result:
            return theme_result

    format_code = render_format_jsx(format_entry, theme_result)

    server_code = server_template.format(
        placement_id=placement_id,
        placement=placement,
        format_code=format_code,
    )
    client_code = client_template.format(
        placement_id=placement_id,
        placement=placement,
        format_code=format_code,
    )

    publisher_id = ""
    if api_key:
        publisher_id = _register_placement(api_key, placement_id, placement)

    write_placement(
        {
            "placement_id": placement_id,
            "placement": placement,
            "style": format,
            "type": style_type,
            "framework": framework,
            "platform": "web",
            "performance": "",
            "publisher_key_hash": publisher_key_hash,
            "publisher_id": publisher_id,
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
    if theme_result and "error" not in theme_result:
        result["theme_applied"] = {
            "style": theme_result["style"],
            "slotProps": theme_result["slotProps"],
            "is_dark": theme_result["is_dark"],
        }
    if not api_key:
        result["warning"] = (
            "No GRAVITY_API_KEY detected. The generated code will work but "
            "ads will not serve without a valid key. Set GRAVITY_API_KEY in your "
            "environment or pass it via Authorization: Bearer <key> header."
        )
    return result
