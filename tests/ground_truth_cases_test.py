from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from authoring.records import GroundTruthRecord, write_records
from ground_truth_cases import (
    GroundTruthCase,
    GroundTruthRenderError,
    GroundTruthSourceLoadError,
    compare_case_lines,
)


class FakeExpression:
    def __init__(self, text: str) -> None:
        self.text = text

    def eval(self) -> str:
        return self.text


class GroundTruthCaseTest(unittest.TestCase):
    def _make_case(self, expected_lines: list[str], actual_lines: list[str]) -> GroundTruthCase:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        path = Path(tmpdir.name) / "sample.jsonl"
        records = [
            GroundTruthRecord(
                id=f"sample:{ordinal:04d}",
                source="sample",
                kind="historic",
                ordinal=ordinal,
                surface=line,
            )
            for ordinal, line in enumerate(expected_lines, start=1)
        ]
        write_records(path, records)
        return GroundTruthCase(
            name="sample",
            record_path=path,
            expressions=[FakeExpression(line) for line in actual_lines],
            kind="historic",
        )

    def test_compare_collects_extra_lines_after_matching_prefix(self) -> None:
        comparison = compare_case_lines(self._make_case(["line one"], ["line one", "line two"]))
        self.assertFalse(comparison.has_mismatch)
        self.assertEqual(comparison.extra_lines, ["line two"])

    def test_compare_reports_existing_mismatch(self) -> None:
        comparison = compare_case_lines(self._make_case(["line one"], ["different line"]))
        self.assertTrue(comparison.has_mismatch)
        self.assertEqual(comparison.mismatch_line_no, 1)
        self.assertEqual(comparison.mismatch_expected, "line one")
        self.assertEqual(comparison.mismatch_actual, "different line")

    def test_missing_jsonl_means_all_rendered_lines_are_unapproved(self) -> None:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        case = GroundTruthCase(
            name="sample",
            record_path=Path(tmpdir.name) / "missing.jsonl",
            expressions=[FakeExpression("line one")],
            kind="historic",
        )
        comparison = compare_case_lines(case)
        self.assertFalse(comparison.has_mismatch)
        self.assertEqual(comparison.extra_lines, ["line one"])

    def test_compare_raises_render_error_for_non_expression_items(self) -> None:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        case = GroundTruthCase(
            name="sample",
            record_path=Path(tmpdir.name) / "sample.jsonl",
            expressions=[("bad", "tuple")],
            kind="historic",
        )
        with self.assertRaises(GroundTruthRenderError) as ctx:
            compare_case_lines(case)
        self.assertEqual(ctx.exception.line_no, 1)
        self.assertEqual(type(ctx.exception.expr).__name__, "tuple")

    def test_compare_raises_source_load_error(self) -> None:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        case = GroundTruthCase(
            name="sample",
            record_path=Path(tmpdir.name) / "sample.jsonl",
            expressions=(),
            kind="historic",
            load_error=NameError("missing_name"),
        )
        with self.assertRaises(GroundTruthSourceLoadError) as ctx:
            compare_case_lines(case)
        self.assertEqual(type(ctx.exception.cause).__name__, "NameError")


if __name__ == "__main__":
    unittest.main()
