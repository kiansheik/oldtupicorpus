from __future__ import annotations

import json
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dictionary.serve_dict import _load_json_request
from dictionary.tooltip_overrides import (
    TooltipOverrideStore,
    canonicalize_tags,
    tooltip_tag_key,
)


class TooltipOverrideStoreTest(unittest.TestCase):
    def test_tag_key_is_stable_for_same_tag_set(self) -> None:
        self.assertEqual(
            tooltip_tag_key(["ROOT", "VOCATIVE", "ROOT"]),
            tooltip_tag_key(["VOCATIVE", "ROOT"]),
        )
        self.assertEqual(
            canonicalize_tags([" ROOT ", "VOCATIVE"]), ["ROOT", "VOCATIVE"]
        )

    def test_save_and_delete_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = TooltipOverrideStore(Path(tmpdir) / "tooltips.sqlite3")
            saved = store.save_override(["ROOT", "VOCATIVE"], "Human note")
            self.assertIsNotNone(saved)
            self.assertEqual(saved["tags"], ["ROOT", "VOCATIVE"])
            self.assertEqual(saved["text"], "Human note")

            listed = store.list_overrides()
            self.assertEqual(len(listed), 1)
            self.assertEqual(listed[0]["text"], "Human note")

            deleted = store.save_override(["VOCATIVE", "ROOT"], "   ")
            self.assertIsNone(deleted)
            self.assertEqual(store.list_overrides(), [])


class TooltipOverrideRequestParsingTest(unittest.TestCase):
    class _FakeHandler:
        def __init__(self, payload: bytes) -> None:
            self.headers = {"Content-Length": str(len(payload))}
            self.rfile = BytesIO(payload)

    def test_load_json_request_parses_json_object(self) -> None:
        handler = self._FakeHandler(
            json.dumps({"tags": ["ROOT"], "text": "Human note"}).encode("utf-8")
        )
        parsed = _load_json_request(handler)
        self.assertEqual(parsed["tags"], ["ROOT"])
        self.assertEqual(parsed["text"], "Human note")

    def test_load_json_request_rejects_non_object_payload(self) -> None:
        handler = self._FakeHandler(json.dumps(["ROOT"]).encode("utf-8"))
        with self.assertRaises(ValueError):
            _load_json_request(handler)


if __name__ == "__main__":
    unittest.main()
