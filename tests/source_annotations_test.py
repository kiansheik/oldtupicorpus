from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from authoring.source_annotations import (
    annotations_by_source_line,
    source_entries,
    waterfall_locator_annotations,
)


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

    def test_directives_attach_to_a_list_entry_without_wrapping_expression(
        self,
    ) -> None:
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

    def test_page_section_and_subsection_waterfall_but_lines_do_not(self) -> None:
        source = """\
l = [
    # @page 25-26
    # @section 2
    # @subsection 2.1
    # @line 25-34
    first,
    # @line 35-39
    second,
    third,
    # @section 3
    fourth,
    # @subsection 3.1
    fifth,
    sixth,
]
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.tu.py"
            path.write_text(source, encoding="utf-8")
            entries = source_entries(path)
            annotations = waterfall_locator_annotations(
                entries, annotations_by_source_line(path, entries)
            )

        self.assertEqual(
            [entry.source_line for entry in entries], [6, 8, 9, 11, 13, 14]
        )

        first = annotations[6].locations[0]
        self.assertEqual((first.page_start, first.page_end), ("25", "26"))
        self.assertEqual((first.section, first.subsection), ("2", "2.1"))
        self.assertEqual((first.line_start, first.line_end), ("25", "34"))

        second = annotations[8].locations[0]
        self.assertEqual((second.page_start, second.page_end), ("26", None))
        self.assertEqual((second.section, second.subsection), ("2", "2.1"))
        self.assertEqual((second.line_start, second.line_end), ("35", "39"))

        third = annotations[9].locations[0]
        self.assertEqual((third.page_start, third.page_end), ("26", None))
        self.assertEqual((third.section, third.subsection), ("2", "2.1"))
        self.assertEqual((third.line_start, third.line_end), (None, None))

        fourth = annotations[11].locations[0]
        self.assertEqual((fourth.page_start, fourth.page_end), ("26", None))
        self.assertEqual((fourth.section, fourth.subsection), ("3", None))
        self.assertEqual((fourth.line_start, fourth.line_end), (None, None))

        fifth = annotations[13].locations[0]
        self.assertEqual((fifth.section, fifth.subsection), ("3", "3.1"))
        sixth = annotations[14].locations[0]
        self.assertEqual((sixth.section, sixth.subsection), ("3", "3.1"))
        self.assertEqual((sixth.line_start, sixth.line_end), (None, None))

    def test_direct_source_list_style_is_supported(self) -> None:
        source = """\
bettendorff_compendio = [
    # @page 10
    # @line 2-3
    first,
]
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bettendorff_compendio.tu.py"
            path.write_text(source, encoding="utf-8")
            entries = source_entries(path, source_name="bettendorff_compendio")
            annotations = annotations_by_source_line(path, entries)

        self.assertEqual([entry.source_line for entry in entries], [4])
        location = annotations[4].locations[0]
        self.assertEqual(location.page_start, "10")
        self.assertEqual(location.line_start, "2")
        self.assertEqual(location.line_end, "3")

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
