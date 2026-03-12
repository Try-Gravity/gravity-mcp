"""build_theme tool — generate slotProps that match the publisher's site design."""

from __future__ import annotations

import re

_HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def _validate_hex(value: str | None, param_name: str) -> str | None:
    """Return an error message if value is not a valid hex color, or None."""
    if value is None:
        return None
    if not _HEX_RE.match(value):
        return (
            f"Invalid hex color for {param_name}: '{value}'. "
            "Expected format: '#RGB' or '#RRGGBB' (e.g. '#FFF', '#1a1a2e')."
        )
    return None


def _parse_hex(hex_color: str) -> tuple[int, int, int]:
    """Parse a hex color string (#RGB, #RRGGBB) into (r, g, b)."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _relative_luminance(r: int, g: int, b: int) -> float:
    """WCAG 2.0 relative luminance."""

    def linearize(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def _is_dark(hex_color: str) -> bool:
    """Return True if the color is perceptually dark (luminance < 0.4)."""
    r, g, b = _parse_hex(hex_color)
    return _relative_luminance(r, g, b) < 0.4


def _contrast_text(bg_hex: str) -> str:
    """Return white or near-black text color for readable contrast against bg."""
    return "#FAFAFA" if _is_dark(bg_hex) else "#18181B"


def _muted_text(bg_hex: str) -> str:
    """Return a muted/secondary text color appropriate for the background."""
    return "#A1A1AA" if _is_dark(bg_hex) else "#71717A"


def _border_for_bg(bg_hex: str) -> str:
    """Return a subtle border color appropriate for the background."""
    return "#3F3F46" if _is_dark(bg_hex) else "#E4E4E7"


def build_theme(
    bg_color: str | None = None,
    text_color: str | None = None,
    accent_color: str | None = None,
    secondary_color: str | None = None,
    border_color: str | None = None,
    border_radius: int | None = None,
    font_family: str | None = None,
) -> dict:
    """Build GravityAd style + slotProps that match the publisher's site theme.

    Pass any combination of design tokens extracted from the publisher's
    CSS, Tailwind config, or component styles. All parameters are optional —
    omitted values are derived automatically for visual coherence.

    Args:
        bg_color: Site background color (e.g. "#FFFFFF", "#1a1a2e"). Drives
            automatic dark/light detection for all derived colors.
        text_color: Primary text color. Auto-derived from bg_color if omitted.
        accent_color: Brand/accent color used for CTA buttons.
        secondary_color: Secondary/muted text color for descriptions and labels.
        border_color: Border color for the ad container and label.
        border_radius: Border radius in pixels (e.g. 8, 12, 16).
        font_family: CSS font-family string (e.g. "Inter, sans-serif").

    Returns:
        Dict with `style`, `slotProps`, and `code_snippet` — a ready-to-use
        JSX prop block that can be spread onto `<GravityAd />`.
        Returns `error` key if any color parameter is not valid hex.
    """
    for name, val in [
        ("bg_color", bg_color),
        ("text_color", text_color),
        ("accent_color", accent_color),
        ("secondary_color", secondary_color),
        ("border_color", border_color),
    ]:
        err = _validate_hex(val, name)
        if err:
            return {"error": err}

    bg = bg_color or "#FFFFFF"
    dark = _is_dark(bg)

    primary = text_color or _contrast_text(bg)
    muted = secondary_color or _muted_text(bg)
    accent = accent_color or ("#3B82F6" if dark else "#2563EB")
    border = border_color or _border_for_bg(bg)
    radius = border_radius if border_radius is not None else 10
    font = font_family

    style: dict = {
        "background": bg,
        "color": primary,
        "border": f"1px solid {border}",
        "borderRadius": radius,
    }
    if dark:
        style["boxShadow"] = "0 2px 8px rgba(0,0,0,0.4)"
    else:
        style["boxShadow"] = "0 1px 3px rgba(0,0,0,0.08)"

    if font:
        style["fontFamily"] = font

    slot_props: dict = {
        "brand": {"style": {"color": primary}},
        "title": {"style": {"color": primary}},
        "text": {"style": {"color": muted}},
        "label": {"style": {"color": muted, "border": f"1px solid {border}"}},
        "cta": {"style": {"background": accent, "color": _contrast_text(accent)}},
    }

    style_lines = ",\n    ".join(
        f"{k}: {_jsx_val(v)}" for k, v in style.items()
    )
    slot_lines = []
    for slot_name, slot_val in slot_props.items():
        inner = ", ".join(
            f"{sk}: {_jsx_val(sv)}" for sk, sv in slot_val["style"].items()
        )
        slot_lines.append(f"    {slot_name}: {{ style: {{ {inner} }} }}")
    slot_block = ",\n".join(slot_lines)

    code_snippet = f"""\
  style={{{{
    {style_lines},
  }}}}
  slotProps={{{{
{slot_block},
  }}}}"""

    return {
        "style": style,
        "slotProps": slot_props,
        "code_snippet": code_snippet,
        "is_dark": dark,
    }


def _jsx_val(v: object) -> str:
    """Format a value for JSX: strings get quotes, numbers stay bare."""
    if isinstance(v, str):
        return f"'{v}'"
    return str(v)
