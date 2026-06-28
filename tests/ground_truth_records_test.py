from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from authoring.records import (
    GroundTruthRecord,
    append_records,
    load_records,
    records_from_legacy_text,
    replace_record_surface,
    write_records,
)


class GroundTruthRecordTest(unittest.TestCase):
    def test_legacy_text_gets_stable_contiguous_record_ids(self) -> None:
        records = records_from_legacy_text(
            "first line.\n\nsecond line!\n",
            source="demo",
            kind="historic",
        )
        self.assertEqual([record.id for record in records], ["demo:0001", "demo:0002"])
        self.assertEqual([record.expected_surface for record in records], ["first line", "second line"])

    def test_structured_record_round_trip_preserves_editorial_fields(self) -> None:
        record = GroundTruthRecord(
            id="demo:0001",
            source="demo",
            kind="historic",
            ordinal=1,
            surface="source spelling",
            normalized_target="modern spelling",
            translation="translation",
            analysis="analysis",
            status="human_review",
            notes=("note",),
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.jsonl"
            write_records(path, [record])
            loaded = load_records(path, source="demo", kind="historic")
        self.assertEqual(loaded, [record])
        self.assertEqual(loaded[0].expected_surface, "modern spelling")

    def test_append_and_replace_keep_record_identity(self) -> None:
        records = records_from_legacy_text("one\n", source="demo", kind="historic")
        records = append_records(records, ["two"], source="demo", kind="historic")
        replaced = replace_record_surface(records, 2, "changed")
        self.assertEqual(replaced[1].id, "demo:0002")
        self.assertEqual(replaced[1].expected_surface, "changed")


if __name__ == "__main__":
    unittest.main()
