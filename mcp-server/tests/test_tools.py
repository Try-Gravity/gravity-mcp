"""Unit tests for all 3 MCP tools — runs without the server process."""

from __future__ import annotations

import csv
import uuid
from pathlib import Path

import pytest

from tools.build_theme import build_theme
from tools.search_formats import search_formats
from tools.generate_code import generate_code
from tools.troubleshoot import troubleshoot
from data.troubleshoot_kb import TROUBLESHOOT_KB

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "placements.csv"


@pytest.fixture(autouse=True)
def _clean_csv():
    """Remove placements.csv before each test so generate_code tests are isolated."""
    CSV_PATH.unlink(missing_ok=True)
    yield
    CSV_PATH.unlink(missing_ok=True)


# ── search_formats ───────────────────────────────────────────────────────────


class TestSearchFormats:
    def test_names_returns_25(self):
        r = search_formats(detail="names")
        assert isinstance(r, list)
        assert len(r) == 25
        assert all(isinstance(name, str) for name in r)

    def test_summary_has_required_fields(self):
        r = search_formats(detail="summary")
        assert len(r) == 25
        for entry in r:
            assert "name" in entry
            assert "description" in entry
            assert "type" in entry
            assert "code" not in entry

    def test_full_has_code(self):
        r = search_formats(detail="full")
        assert len(r) == 25
        for entry in r:
            assert "code" in entry
            assert "omits" in entry

    def test_filter_by_category(self):
        r = search_formats(category="card", detail="summary")
        assert len(r) > 0
        assert all(e["type"] == "card" for e in r)
        names = [e["name"] for e in r]
        assert "card" in names
        assert "floating" in names

    def test_filter_by_query(self):
        r = search_formats(query="notification", detail="summary")
        assert len(r) >= 1
        assert any("notification" in e["name"] for e in r)

    def test_empty_results(self):
        r = search_formats(query="xyznonexistent", detail="names")
        assert r == []


# ── generate_code ────────────────────────────────────────────────────────────


class TestGenerateCode:
    def test_returns_paired_code(self):
        r = generate_code(format="floating", framework="fastapi", streaming=True)
        assert "server_code" in r
        assert "client_code" in r
        assert len(r["server_code"]) > 50
        assert len(r["client_code"]) > 50

    def test_placement_id_is_uuid(self):
        r = generate_code(format="card", framework="fastapi", streaming=True)
        pid = r["placement_id"]
        parsed = uuid.UUID(pid, version=4)
        assert str(parsed) == pid

    def test_csv_write(self):
        r = generate_code(format="banner", framework="nextjs", streaming=False)
        assert CSV_PATH.exists()
        with open(CSV_PATH) as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1
        assert rows[0]["style"] == "banner"
        assert rows[0]["framework"] == "nextjs"
        assert rows[0]["platform"] == "web"

    def test_placement_id_in_server_code(self):
        r = generate_code(format="card", framework="fastapi", streaming=True)
        assert r["placement_id"] in r["server_code"]

    def test_unknown_format_rejected(self):
        r = generate_code(format="nonexistent", framework="fastapi", streaming=True)
        assert "error" in r

    def test_dark_theme_includes_dark_styles(self):
        r = generate_code(format="card", framework="fastapi", streaming=False, theme="dark")
        assert "#18181B" in r["client_code"]
        assert "theme_applied" in r
        assert r["theme_applied"]["is_dark"] is True

    def test_site_theme_tokens_applied(self):
        r = generate_code(
            format="card", framework="fastapi", streaming=False,
            bg_color="#1a1a2e", accent_color="#E11D48", border_radius=16,
        )
        assert "theme_applied" in r
        assert r["theme_applied"]["style"]["background"] == "#1a1a2e"
        assert r["theme_applied"]["style"]["borderRadius"] == 16
        assert r["theme_applied"]["slotProps"]["cta"]["style"]["background"] == "#E11D48"
        assert r["theme_applied"]["is_dark"] is True
        assert "#1a1a2e" in r["client_code"]

    def test_site_tokens_override_dark_preset(self):
        r = generate_code(
            format="card", framework="fastapi", streaming=False,
            theme="dark", accent_color="#E11D48",
        )
        assert r["theme_applied"]["slotProps"]["cta"]["style"]["background"] == "#E11D48"
        assert r["theme_applied"]["style"]["background"] == "#18181B"

    def test_no_theme_when_no_tokens(self):
        r = generate_code(format="card", framework="fastapi", streaming=False)
        assert "theme_applied" not in r

    def test_all_framework_streaming_combos(self):
        combos = [
            ("fastapi", True),
            ("fastapi", False),
            ("nextjs", True),
            ("nextjs", False),
        ]
        for framework, streaming in combos:
            r = generate_code(format="card", framework=framework, streaming=streaming)
            assert "server_code" in r, f"{framework}/streaming={streaming} missing server_code"
            assert "client_code" in r, f"{framework}/streaming={streaming} missing client_code"
            assert "placement_id" in r, f"{framework}/streaming={streaming} missing placement_id"


# ── troubleshoot ─────────────────────────────────────────────────────────────


class TestTroubleshoot:
    def test_known_symptom_match(self):
        r = troubleshoot(symptom="no ads")
        assert "key" in r["cause"].lower() or "api" in r["cause"].lower()

    def test_case_insensitive(self):
        r_lower = troubleshoot(symptom="no ads")
        r_upper = troubleshoot(symptom="NO ADS")
        assert r_lower == r_upper

    def test_unknown_symptom_fallback(self):
        r = troubleshoot(symptom="my cat walked on the keyboard")
        assert "contact" in r["fix"].lower() or "support" in r["fix"].lower()

    def test_all_entries_reachable(self):
        for entry in TROUBLESHOOT_KB:
            keywords = [kw.strip() for kw in entry["keywords"].split(",")]
            reached = any(
                entry["symptom"].lower() in troubleshoot(symptom=kw)["symptom"].lower()
                for kw in keywords
            )
            assert reached, f"KB entry unreachable: {entry['symptom']}"


# ── build_theme ─────────────────────────────────────────────────────────────


class TestBuildTheme:
    def test_dark_bg_detected(self):
        r = build_theme(bg_color="#18181B")
        assert r["is_dark"] is True
        assert r["style"]["background"] == "#18181B"
        assert r["slotProps"]["title"]["style"]["color"] == "#FAFAFA"

    def test_light_bg_detected(self):
        r = build_theme(bg_color="#FFFFFF")
        assert r["is_dark"] is False
        assert r["slotProps"]["title"]["style"]["color"] == "#18181B"

    def test_accent_color_flows_to_cta(self):
        r = build_theme(accent_color="#E11D48")
        assert r["slotProps"]["cta"]["style"]["background"] == "#E11D48"

    def test_border_radius_applied(self):
        r = build_theme(border_radius=20)
        assert r["style"]["borderRadius"] == 20

    def test_font_family_applied(self):
        r = build_theme(font_family="Inter, sans-serif")
        assert r["style"]["fontFamily"] == "Inter, sans-serif"

    def test_code_snippet_present(self):
        r = build_theme(bg_color="#1E293B", accent_color="#F59E0B")
        assert "style={{" in r["code_snippet"]
        assert "slotProps={{" in r["code_snippet"]
        assert "#1E293B" in r["code_snippet"]
        assert "#F59E0B" in r["code_snippet"]

    def test_defaults_when_no_args(self):
        r = build_theme()
        assert r["is_dark"] is False
        assert r["style"]["background"] == "#FFFFFF"
        assert "code_snippet" in r

    def test_cta_text_contrast(self):
        r = build_theme(accent_color="#FFFF00")
        assert r["slotProps"]["cta"]["style"]["color"] == "#18181B"
        r = build_theme(accent_color="#000080")
        assert r["slotProps"]["cta"]["style"]["color"] == "#FAFAFA"
