from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from ground_truth_cases import (
    GroundTruthCase,
    GroundTruthRenderError,
    GroundTruthSourceLoadError,
    compare_case_lines,
)
from run_tests import _review_case_by_name, _review_case_updates


class FakeExpression:
    def __init__(self, text: str) -> None:
        self.text = text

    def eval(self) -> str:
        return self.text


class GroundTruthUpdateTest(unittest.TestCase):
    def _make_case(
        self, *, expected_text: str, actual_lines: list[str]
    ) -> GroundTruthCase:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        path = Path(tmpdir.name) / "sample.txt"
        path.write_text(expected_text, encoding="utf-8")
        expressions = [FakeExpression(line) for line in actual_lines]
        return GroundTruthCase(
            name="sample",
            ground_truth_path=path,
            expressions=expressions,
            kind="historic",
        )

    def test_compare_case_lines_collects_extra_lines_after_matching_prefix(
        self,
    ) -> None:
        case = self._make_case(
            expected_text="line one\n",
            actual_lines=["line one", "line two", "line three"],
        )
        comparison = compare_case_lines(case)
        self.assertFalse(comparison.has_mismatch)
        self.assertEqual(comparison.extra_lines, ["line two", "line three"])

    def test_review_case_updates_only_appends_confirmed_prefix(self) -> None:
        case = self._make_case(
            expected_text="line one\n",
            actual_lines=["line one", "line two", "line three"],
        )
        comparison = compare_case_lines(case)
        responses = iter(["y", "n"])
        with redirect_stderr(io.StringIO()):
            status = _review_case_updates(
                comparison,
                input_fn=lambda _: next(responses),
            )
        self.assertEqual(status, "updated")
        self.assertEqual(
            case.ground_truth_path.read_text(encoding="utf-8"),
            "line one\nline two\n",
        )

    def test_review_case_updates_prints_recent_context_before_new_line(self) -> None:
        expected_lines = [f"line {index}" for index in range(1, 13)]
        case = self._make_case(
            expected_text="\n".join(expected_lines) + "\n",
            actual_lines=expected_lines + ["line 13"],
        )
        comparison = compare_case_lines(case)
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            status = _review_case_updates(
                comparison,
                input_fn=lambda _: "n",
            )
        output = stderr.getvalue()
        self.assertEqual(status, "stopped")
        self.assertIn("[sample] context", output)
        self.assertIn("   3 | line 3", output)
        self.assertIn("  12 | line 12", output)
        self.assertNotIn("   1 | line 1", output)
        self.assertNotIn("   2 | line 2", output)
        self.assertIn("[sample] line 13", output)
        self.assertIn("line 13", output)

    def test_review_case_updates_blocks_on_existing_mismatch(self) -> None:
        case = self._make_case(
            expected_text="line one\n",
            actual_lines=["different line", "line two"],
        )
        comparison = compare_case_lines(case)
        with redirect_stderr(io.StringIO()):
            status = _review_case_updates(
                comparison,
                input_fn=lambda _: self.fail("input should not be called"),
            )
        self.assertEqual(status, "blocked")
        self.assertEqual(
            case.ground_truth_path.read_text(encoding="utf-8"),
            "line one\n",
        )

    def test_compare_case_lines_raises_render_error_for_non_expression_items(
        self,
    ) -> None:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        path = Path(tmpdir.name) / "sample.txt"
        path.write_text("", encoding="utf-8")
        case = GroundTruthCase(
            name="sample",
            ground_truth_path=path,
            expressions=[("bad", "tuple")],
            kind="historic",
        )
        with self.assertRaises(GroundTruthRenderError) as ctx:
            compare_case_lines(case)
        self.assertEqual(ctx.exception.line_no, 1)
        self.assertEqual(type(ctx.exception.expr).__name__, "tuple")

    def test_review_case_by_name_blocks_render_errors_without_prompting(self) -> None:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        path = Path(tmpdir.name) / "sample.txt"
        path.write_text("", encoding="utf-8")
        case = GroundTruthCase(
            name="sample",
            ground_truth_path=path,
            expressions=[("bad", "tuple")],
            kind="historic",
        )
        with redirect_stderr(io.StringIO()):
            status = _review_case_by_name(
                case,
                input_fn=lambda _: self.fail("input should not be called"),
            )
        self.assertEqual(status, "blocked")

    def test_compare_case_lines_raises_source_load_error(self) -> None:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        path = Path(tmpdir.name) / "sample.txt"
        path.write_text("", encoding="utf-8")
        case = GroundTruthCase(
            name="sample",
            ground_truth_path=path,
            expressions=(),
            kind="historic",
            load_error=NameError("missing_name"),
        )
        with self.assertRaises(GroundTruthSourceLoadError) as ctx:
            compare_case_lines(case)
        self.assertEqual(type(ctx.exception.cause).__name__, "NameError")


if __name__ == "__main__":
    unittest.main()
