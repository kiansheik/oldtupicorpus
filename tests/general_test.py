from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from ground_truth_cases import (
    GroundTruthRenderError,
    GroundTruthSourceLoadError,
    HISTORIC_GROUND_TRUTH_DIR,
    compare_case_lines,
    load_historic_cases,
)


class PrimarySourceCaseTest(unittest.TestCase):
    def __init__(self, case) -> None:
        super().__init__("run_case")
        self.case = case

    def run_case(self) -> None:
        try:
            comparison = compare_case_lines(self.case)
        except (GroundTruthRenderError, GroundTruthSourceLoadError) as exc:
            self.fail(f"{self.case.name} could not be rendered: {exc}")
        case = comparison.case
        expected_lines = comparison.expected_lines
        actual_lines = comparison.actual_lines
        if case.allow_extra_lines:
            self.assertGreaterEqual(
                len(actual_lines),
                len(expected_lines),
                msg=(
                    f"{case.name} line count mismatch: "
                    f"expected at least {len(expected_lines)} got {len(actual_lines)}"
                ),
            )
        else:
            self.assertEqual(
                len(actual_lines),
                len(expected_lines),
                msg=(
                    f"{case.name} line count mismatch: "
                    f"expected {len(expected_lines)} got {len(actual_lines)}"
                ),
            )
        for line_no, (actual, expected) in enumerate(
            zip(actual_lines, expected_lines), start=1
        ):
            with self.subTest(line=line_no):
                self.assertEqual(
                    actual,
                    expected,
                    msg=(
                        f"{case.name} line {line_no} mismatch:\n"
                        f"expected: {expected}\n"
                        f"actual:   {actual}"
                    ),
                )

    def run(self, result: unittest.TestResult | None = None) -> unittest.TestResult:
        if result is None:
            result = self.defaultTestResult()
        failures_before = len(result.failures)
        errors_before = len(result.errors)
        skips_before = len(result.skipped)
        start = time.perf_counter()
        super().run(result)
        duration = time.perf_counter() - start
        status = "ok"
        if len(result.errors) > errors_before:
            status = "ERROR"
        elif len(result.failures) > failures_before:
            status = "FAIL"
        elif len(result.skipped) > skips_before:
            status = "SKIP"
        stream = getattr(result, "stream", None) or sys.stdout
        prefix = "\n" if getattr(result, "dots", False) else ""
        stream.write(f"{prefix}{self.case.name}: {status} ({duration:.3f}s)\n")
        stream.flush()
        return result


def load_tests(
    loader: unittest.TestLoader, tests: unittest.TestSuite, pattern: str | None
) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    suite.addTests(tests)
    cases = load_historic_cases()
    if not cases:

        def _no_ground_truth() -> None:
            raise AssertionError(
                f"No ground truth files found in {HISTORIC_GROUND_TRUTH_DIR}."
            )

        suite.addTest(unittest.FunctionTestCase(_no_ground_truth))
        return suite
    for case in cases:
        suite.addTest(PrimarySourceCaseTest(case))
    return suite


if __name__ == "__main__":
    unittest.main()
