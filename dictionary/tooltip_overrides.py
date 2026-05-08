from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = ROOT / "var" / "tooltip_overrides.sqlite3"


def canonicalize_tags(tags: Iterable[str]) -> list[str]:
    unique = {
        str(tag).strip() for tag in tags if isinstance(tag, str) and str(tag).strip()
    }
    return sorted(unique)


def tooltip_tag_key(tags: Iterable[str]) -> str:
    return json.dumps(
        canonicalize_tags(tags),
        ensure_ascii=False,
        separators=(",", ":"),
    )


class TooltipOverrideStore:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tooltip_overrides (
                    tag_key TEXT PRIMARY KEY,
                    tags_json TEXT NOT NULL,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def list_overrides(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT tag_key, tags_json, text, created_at, updated_at
                FROM tooltip_overrides
                ORDER BY LENGTH(tags_json) DESC, updated_at DESC, tag_key ASC
                """
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def save_override(self, tags: Iterable[str], text: str) -> dict[str, object] | None:
        canonical_tags = canonicalize_tags(tags)
        if not canonical_tags:
            raise ValueError("Tooltip overrides require at least one tag.")

        tag_key = tooltip_tag_key(canonical_tags)
        cleaned_text = str(text or "").strip()

        with self._connect() as connection:
            if not cleaned_text:
                connection.execute(
                    "DELETE FROM tooltip_overrides WHERE tag_key = ?",
                    (tag_key,),
                )
                return None

            tags_json = json.dumps(canonical_tags, ensure_ascii=False)
            connection.execute(
                """
                INSERT INTO tooltip_overrides (
                    tag_key,
                    tags_json,
                    text,
                    created_at,
                    updated_at
                )
                VALUES (
                    ?,
                    ?,
                    ?,
                    strftime('%Y-%m-%dT%H:%M:%SZ', 'now'),
                    strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
                )
                ON CONFLICT(tag_key) DO UPDATE SET
                    tags_json = excluded.tags_json,
                    text = excluded.text,
                    updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
                """,
                (tag_key, tags_json, cleaned_text),
            )
            row = connection.execute(
                """
                SELECT tag_key, tags_json, text, created_at, updated_at
                FROM tooltip_overrides
                WHERE tag_key = ?
                """,
                (tag_key,),
            ).fetchone()

        return self._row_to_dict(row) if row is not None else None

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict[str, object]:
        return {
            "tag_key": row["tag_key"],
            "tags": json.loads(row["tags_json"]),
            "text": row["text"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
