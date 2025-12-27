from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import primary_sources as sources


@dataclass(frozen=True)
class PrimarySourceCase:
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


GROUND_TRUTH_DIR = ROOT / "ground_truth"


def _load_primary_sources() -> list[PrimarySourceCase]:
    cases: list[PrimarySourceCase] = []
    for path in sorted(GROUND_TRUTH_DIR.glob("*.txt")):
        name = path.stem
        expressions = getattr(sources, name, None)
        if expressions is None:
            raise AttributeError(
                f"Missing primary source for '{name}'. "
                f"Define a list named '{name}' in a source module and import it "
                f"in primary_sources.py."
            )
        cases.append(
            PrimarySourceCase(
                name=name,
                ground_truth_path=path,
                expressions=expressions,
            )
        )
    return cases


class TestPrimarySourceGroundTruth(unittest.TestCase):
    def test_ground_truth_alignment(self) -> None:
        cases = _load_primary_sources()
        self.assertTrue(
            cases,
            msg=f"No ground truth files found in {GROUND_TRUTH_DIR}.",
        )
        for case in cases:
            with self.subTest(case=case.name):
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
                    with self.subTest(case=case.name, line=line_no):
                        self.assertEqual(
                            actual,
                            expected,
                            msg=(
                                f"{case.name} line {line_no} mismatch:\n"
                                f"expected: {expected}\n"
                                f"actual:   {actual}"
                            ),
                        )


if __name__ == "__main__":
    unittest.main()
