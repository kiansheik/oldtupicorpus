from __future__ import annotations

import sys
import time
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from synthetic import primary_sources as sources


@dataclass(frozen=True)
class SyntheticCase:
    name: str
    ground_truth_path: Path
    expressions: Sequence[object]
    allow_extra_lines: bool = True


def _normalize_expected_lines(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped[-1] in ".;:!?":
            stripped = stripped[:-1]
        lines.append(stripped)
    return lines


def _render_lines(expressions: Iterable[object]) -> list[str]:
    return [expr.eval().strip() for expr in expressions]


GROUND_TRUTH_DIR = ROOT / "ground_truth" / "synthetic"


def _load_synthetic_sources() -> list[SyntheticCase]:
    cases: list[SyntheticCase] = []
    for path in sorted(GROUND_TRUTH_DIR.glob("*.txt")):
        name = path.stem
        expressions = getattr(sources, name, None)
        if expressions is None:
            raise AttributeError(
                f"Missing synthetic source for '{name}'. "
                f"Define a list named '{name}' in synthetic/primary_sources.py."
            )
        if callable(expressions):
            expressions = expressions()
        cases.append(
            SyntheticCase(
                name=name,
                ground_truth_path=path,
                expressions=expressions,
            )
        )
    return cases


class SyntheticCaseTest(unittest.TestCase):
    def __init__(self, case: SyntheticCase) -> None:
        super().__init__("run_case")
        self.case = case

    def run_case(self) -> None:
        case = self.case
        expected_lines = _normalize_expected_lines(
            case.ground_truth_path.read_text(encoding="utf-8")
        )
        actual_lines = _render_lines(case.expressions)
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
    cases = _load_synthetic_sources()
    if not cases:

        def _no_ground_truth() -> None:
            raise AssertionError(
                f"No synthetic ground truth files found in {GROUND_TRUTH_DIR}."
            )

        suite.addTest(unittest.FunctionTestCase(_no_ground_truth))
        return suite
    for case in cases:
        suite.addTest(SyntheticCaseTest(case))
    return suite


if __name__ == "__main__":
    unittest.main()
