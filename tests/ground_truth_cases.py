from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from authoring.records import GroundTruthRecord, load_records, record_path

ExpressionSource = Iterable[object] | Callable[[], Iterable[object]]
HISTORIC_SOURCE_DIR = ROOT / "historic"
RECORDS_DIR = ROOT / "ground_truth" / "records"
HISTORIC_GROUND_TRUTH_DIR = RECORDS_DIR / "historic"
SYNTHETIC_GROUND_TRUTH_DIR = RECORDS_DIR / "synthetic"


@dataclass(frozen=True)
class GroundTruthCase:
    name: str
    record_path: Path
    expressions: ExpressionSource
    kind: str
    allow_extra_lines: bool = True
    load_error: Exception | None = None


@dataclass(frozen=True)
class GroundTruthComparison:
    case: GroundTruthCase
    expected_lines: list[str]
    actual_lines: list[str]
    mismatch_line_no: int | None = None
    mismatch_expected: str | None = None
    mismatch_actual: str | None = None

    @property
    def has_mismatch(self) -> bool:
        return self.mismatch_line_no is not None

    @property
    def extra_lines(self) -> list[str]:
        if self.has_mismatch:
            return []
        return self.actual_lines[len(self.expected_lines) :]


class GroundTruthRenderError(Exception):
    def __init__(
        self, line_no: int, expr: object, cause: Exception | None = None
    ) -> None:
        self.line_no = line_no
        self.expr = expr
        self.cause = cause
        detail = f"line {line_no}: {type(expr).__name__} does not render via .eval()"
        if cause is not None:
            detail = f"{detail} ({cause})"
        super().__init__(detail)


class GroundTruthSourceLoadError(Exception):
    def __init__(self, cause: Exception) -> None:
        self.cause = cause
        super().__init__(
            f"source could not be loaded ({cause.__class__.__name__}: {cause})"
        )


def get_case_records(case: GroundTruthCase) -> list[GroundTruthRecord]:
    """Load the sole structured JSONL artifact for a source, if generated."""
    if not case.record_path.exists():
        return []
    return load_records(case.record_path, source=case.name, kind=case.kind)


def render_lines(expressions: ExpressionSource) -> list[str]:
    if callable(expressions):
        expressions = expressions()
    lines: list[str] = []
    for line_no, expr in enumerate(expressions, start=1):
        if not hasattr(expr, "eval"):
            raise GroundTruthRenderError(line_no, expr)
        try:
            rendered = expr.eval()
        except Exception as exc:
            raise GroundTruthRenderError(line_no, expr, exc) from exc
        if not isinstance(rendered, str):
            raise GroundTruthRenderError(
                line_no,
                expr,
                TypeError(f"eval() returned {type(rendered).__name__}, expected str"),
            )
        lines.append(rendered.strip())
    return lines


def compare_case_lines(case: GroundTruthCase) -> GroundTruthComparison:
    if case.load_error is not None:
        raise GroundTruthSourceLoadError(case.load_error)
    expected = [record.expected_surface for record in get_case_records(case)]
    actual = render_lines(case.expressions)
    for index, expected_line in enumerate(expected):
        line_no = index + 1
        if index >= len(actual):
            return GroundTruthComparison(
                case, expected, actual, line_no, expected_line, None
            )
        if actual[index] != expected_line:
            return GroundTruthComparison(
                case, expected, actual, line_no, expected_line, actual[index]
            )
    return GroundTruthComparison(case, expected, actual)


def _load_cases_from_records(
    *, kind: str, expression_loader: Callable[[str], ExpressionSource]
) -> list[GroundTruthCase]:
    records_dir = RECORDS_DIR / kind
    cases: list[GroundTruthCase] = []
    for path in sorted(records_dir.glob("*.jsonl")):
        expressions: ExpressionSource = ()
        load_error = None
        try:
            expressions = expression_loader(path.stem)
        except Exception as exc:
            load_error = exc
        cases.append(
            GroundTruthCase(
                name=path.stem,
                record_path=path,
                expressions=expressions,
                kind=kind,
                load_error=load_error,
            )
        )
    return cases


def _load_module_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        return module
    except Exception:
        sys.modules.pop(module_name, None)
        raise


def _load_historic_expressions(source_name: str) -> ExpressionSource:
    tu_path = HISTORIC_SOURCE_DIR / f"{source_name}.tu.py"
    py_path = HISTORIC_SOURCE_DIR / f"{source_name}.py"
    source_path = tu_path if tu_path.exists() else py_path if py_path.exists() else None
    if source_path is None:
        raise AttributeError(f"Missing primary source for '{source_name}'.")
    module = _load_module_from_path(
        f"historic._ground_truth_case_{source_name}", source_path
    )
    expressions = getattr(module, source_name, None)
    if expressions is None:
        raise AttributeError(
            f"Missing primary source for '{source_name}'. Define a list with that name."
        )
    return expressions


def _load_synthetic_expressions(source_name: str) -> ExpressionSource:
    module = _load_module_from_path(
        "synthetic._ground_truth_primary_sources",
        ROOT / "synthetic" / "primary_sources.py",
    )
    expressions = getattr(module, source_name, None)
    if expressions is None:
        raise AttributeError(f"Missing synthetic source for '{source_name}'.")
    return expressions


def load_historic_cases() -> list[GroundTruthCase]:
    return _load_cases_from_records(
        kind="historic", expression_loader=_load_historic_expressions
    )


def load_synthetic_cases() -> list[GroundTruthCase]:
    return _load_cases_from_records(
        kind="synthetic", expression_loader=_load_synthetic_expressions
    )


def load_ground_truth_cases(
    *, include_synthetic: bool = False
) -> list[GroundTruthCase]:
    cases = load_historic_cases()
    if include_synthetic:
        cases.extend(load_synthetic_cases())
    return cases
