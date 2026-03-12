"""generate_code tool — produce paired server + client integration code."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Literal

from data.db import write_placement
from data.style_type_map import STYLE_TYPE_MAP
from resources.format_catalog import FORMAT_CATALOG
from tools.build_theme import build_theme as _build_theme, _jsx_val

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


logger = logging.getLogger(__name__)


def _strip_jsx_prop(code: str, prop_name: str) -> str:
    """Remove a JSX prop block like style={{...}} or slotProps={{...}}."""
    pattern = f"{prop_name}={{"
    idx = code.find(pattern)
    if idx == -1:
        return code

    line_start = code.rfind("\n", 0, idx)
    if line_start == -1:
        line_start = idx

    brace_start = idx + len(pattern)
    depth = 2
    i = brace_start
    while i < len(code):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                return code[:line_start] + code[end:]
        i += 1

    return code


def _build_style_jsx(style: dict) -> str:
    """Build a JSX style={{...}} prop string."""
    lines = ",\n    ".join(f"{k}: {_jsx_val(v)}" for k, v in style.items())
    return f"style={{{{\n    {lines},\n  }}}}"


def _build_slot_props_jsx(slot_props: dict) -> str:
    """Build a JSX slotProps={{...}} prop string."""
    slot_lines = []
    for slot_name, slot_val in slot_props.items():
        inner = ", ".join(
            f"{sk}: {_jsx_val(sv)}" for sk, sv in slot_val["style"].items()
        )
        slot_lines.append(f"    {slot_name}: {{ style: {{ {inner} }} }}")
    block = ",\n".join(slot_lines)
    return f"slotProps={{{{\n{block},\n  }}}}"


def _inject_theme_into_jsx(format_code: str, theme_result: dict) -> str:
    """Merge theme style/slotProps directly into the GravityAd JSX.

    Removes existing style/slotProps blocks and injects themed replacements
    before the closing />. Preserves format-specific layout props (like
    maxWidth, display, paddingLeft) by merging them under theme colors.
    """
    if "<AdText" in format_code:
        return format_code

    existing_style: dict = {}
    style_match = re.search(
        r"style=\{\{([\s\S]*?)\}\}", format_code
    )
    if style_match:
        raw = style_match.group(1)
        for m in re.finditer(r"(\w+):\s*(.+?)(?:,\s*$|$)", raw, re.MULTILINE):
            existing_style[m.group(1)] = m.group(2).strip().rstrip(",")

    existing_slots: dict = {}
    slot_match = re.search(
        r"slotProps=\{\{([\s\S]*?)\}\}\n", format_code
    )
    if slot_match:
        raw = slot_match.group(1)
        for m in re.finditer(r"(\w+):\s*\{\s*style:\s*\{([^}]*)\}", raw):
            slot_name = m.group(1)
            inner_raw = m.group(2)
            props = {}
            for p in re.finditer(r"(\w+):\s*(.+?)(?:,\s*|$)", inner_raw):
                props[p.group(1)] = p.group(2).strip().rstrip(",")
            existing_slots[slot_name] = props

    merged_style = {}
    for k, v in existing_style.items():
        merged_style[k] = v
    for k, v in theme_result["style"].items():
        merged_style[k] = _jsx_val(v) if not isinstance(v, str) or not v.startswith("'") else v

    theme_slots = theme_result["slotProps"]
    merged_slot_props = {}
    all_slot_names = set(list(existing_slots.keys()) + list(theme_slots.keys()))
    for slot_name in all_slot_names:
        merged_inner = {}
        if slot_name in existing_slots:
            merged_inner.update(existing_slots[slot_name])
        if slot_name in theme_slots:
            for sk, sv in theme_slots[slot_name]["style"].items():
                merged_inner[sk] = _jsx_val(sv)
        merged_slot_props[slot_name] = merged_inner

    code = _strip_jsx_prop(format_code, "style")
    code = _strip_jsx_prop(code, "slotProps")

    style_lines = ",\n    ".join(f"{k}: {v}" for k, v in merged_style.items())
    style_jsx = f"  style={{{{\n    {style_lines},\n  }}}}"

    slot_lines = []
    for sn, inner in merged_slot_props.items():
        inner_str = ", ".join(f"{sk}: {sv}" for sk, sv in inner.items())
        slot_lines.append(f"    {sn}: {{ style: {{ {inner_str} }} }}")
    slot_jsx = f"  slotProps={{{{\n" + ",\n".join(slot_lines) + ",\n  }}}}"

    close_idx = code.rfind("/>")
    if close_idx == -1:
        return format_code

    before = code[:close_idx].rstrip()
    return f"{before}\n{style_jsx}\n{slot_jsx}\n/>"


_PLACEMENT_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def generate_code(
    format: str,
    placement_id: str,
    framework: Literal["fastapi", "nextjs"] = "fastapi",
    streaming: bool = True,
    placement: Placement = "below_response",
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
    format_code = format_entry["code"]

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

        format_code = _inject_theme_into_jsx(format_code, theme_result)

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

    write_placement(
        {
            "placement_id": placement_id,
            "placement": placement,
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
    if theme_result and "error" not in theme_result:
        result["theme_applied"] = {
            "style": theme_result["style"],
            "slotProps": theme_result["slotProps"],
            "is_dark": theme_result["is_dark"],
        }
    return result
