from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from authoring.source_annotations import annotations_by_source_line, source_entries


class SourceAnnotationTest(unittest.TestCase):
    def test_page_and_line_comments_attach_to_next_l_append(self) -> None:
        source = """\
l = [
    first,
]

# @page 25-26
# @line 25-34
l += second
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.tu.py"
            path.write_text(source, encoding="utf-8")
            entries = source_entries(path)
            annotations = annotations_by_source_line(path, entries)

        self.assertEqual([entry.source_line for entry in entries], [2, 7])
        location = annotations[7].locations[0]
        self.assertEqual(location.page_start, "25")
        self.assertEqual(location.page_end, "26")
        self.assertEqual(location.line_start, "25")
        self.assertEqual(location.line_end, "34")

    def test_directives_attach_to_a_list_entry_without_wrapping_expression(self) -> None:
        source = """\
l = [
    # @folio 10r
    # @line 4-7
    first,
    second,
]
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.tu.py"
            path.write_text(source, encoding="utf-8")
            entries = source_entries(path)
            annotations = annotations_by_source_line(path, entries)

        self.assertEqual([entry.source_line for entry in entries], [4, 5])
        location = annotations[4].locations[0]
        self.assertEqual(location.folio_start, "10r")
        self.assertEqual(location.line_start, "4")
        self.assertEqual(location.line_end, "7")
        self.assertNotIn(5, annotations)

    def test_unrecognized_directive_is_rejected(self) -> None:
        source = """\
l = []
# @place Madeira
l += first
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.tu.py"
            path.write_text(source, encoding="utf-8")
            entries = source_entries(path)
            with self.assertRaisesRegex(ValueError, "@place"):
                annotations_by_source_line(path, entries)


if __name__ == "__main__":
    unittest.main()
