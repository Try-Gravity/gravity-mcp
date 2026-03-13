"""PostgreSQL persistence for placement records."""

from __future__ import annotations

import logging
import os

import psycopg

logger = logging.getLogger(__name__)

_conninfo: str | None = None

_ENSURE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS placements (
    placement_id TEXT PRIMARY KEY,
    placement TEXT NOT NULL DEFAULT 'below_response',
    style TEXT NOT NULL,
    type TEXT NOT NULL,
    framework TEXT NOT NULL,
    platform TEXT NOT NULL DEFAULT 'web',
    performance TEXT DEFAULT '',
    publisher_key_hash TEXT DEFAULT '',
    publisher_id TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

_MIGRATE_SQL = """
ALTER TABLE placements ADD COLUMN IF NOT EXISTS publisher_key_hash TEXT DEFAULT '';
ALTER TABLE placements ADD COLUMN IF NOT EXISTS publisher_id TEXT DEFAULT '';
"""

_INSERT_SQL = """
INSERT INTO placements (placement_id, placement, style, type, framework, platform, performance, publisher_key_hash, publisher_id, created_at)
VALUES (%(placement_id)s, %(placement)s, %(style)s, %(type)s, %(framework)s, %(platform)s, %(performance)s, %(publisher_key_hash)s, %(publisher_id)s, %(created_at)s)
ON CONFLICT (placement_id) DO UPDATE
SET publisher_id = CASE WHEN EXCLUDED.publisher_id <> '' THEN EXCLUDED.publisher_id
                        ELSE placements.publisher_id END,
    placement = EXCLUDED.placement
"""

_table_ready = False


def _get_conninfo() -> str:
    global _conninfo
    if _conninfo is None:
        _conninfo = os.environ.get("DATABASE_URL", "")
    return _conninfo


def _ensure_table(conn: psycopg.Connection) -> None:
    global _table_ready
    if not _table_ready:
        conn.execute(_ENSURE_TABLE_SQL)
        conn.execute(_MIGRATE_SQL)
        _table_ready = True


def write_placement(row: dict) -> None:
    conninfo = _get_conninfo()
    if not conninfo:
        return
    try:
        with psycopg.connect(conninfo) as conn:
            _ensure_table(conn)
            conn.execute(_INSERT_SQL, row)
    except Exception:
        logger.exception("Failed to write placement %s", row.get("placement_id"))
