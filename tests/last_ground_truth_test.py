from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from authoring.last_ground_truth import choose_source, display
from authoring.records import GroundTruthRecord, write_records


class LastGroundTruthTest(unittest.TestCase):
    def test_selects_newest_source_and_only_saved_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            historic = root / "historic"
            historic.mkdir()
            older = historic / "older.tu.py"
            older.write_text("older = [first]\n", encoding="utf-8")
            newest = historic / "newest.tu.py"
            newest.write_text(
                "l = [first]\nl += second\nl += unsaved\nnewest = l\n",
                encoding="utf-8",
            )
            os.utime(older, ns=(1, 1))
            os.utime(newest, ns=(2, 2))
            records = root / "ground_truth" / "records" / "historic" / "newest.jsonl"
            write_records(
                records,
                [
                    GroundTruthRecord("newest:0001", "newest", "historic", 1, "one"),
                    GroundTruthRecord("newest:0002", "newest", "historic", 2, "two"),
                ],
            )

            self.assertEqual(choose_source(root, ""), newest)
            output = display(root, count=1)
            self.assertIn("newest:0002", output)
            self.assertIn("l += second", output)
            self.assertIn("→ two", output)
            self.assertNotIn("newest:0001", output)
            self.assertIn("1 source command(s) have no saved", output)
            self.assertEqual(choose_source(root, "historic/newest.tu.py"), newest)

    def test_rejects_invalid_count(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive integer"):
            display(Path("."), count=0)


if __name__ == "__main__":
    unittest.main()
