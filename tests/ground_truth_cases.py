from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from authoring.records import (
    GroundTruthRecord,
    append_records,
    legacy_path,
    load_preferred_records,
    record_path,
    records_from_legacy_text,
    replace_record_surface,
    write_records,
)

ExpressionSource = Iterable[object] | Callable[[], Iterable[object]]

HISTORIC_GROUND_TRUTH_DIR = ROOT / "ground_truth" / "historic"
SYNTHETIC_GROUND_TRUTH_DIR = ROOT / "ground_truth" / "synthetic"
HISTORIC_SOURCE_DIR = ROOT / "historic"


@dataclass(frozen=True)
class GroundTruthCase:
    name: str
    ground_truth_path: Path
    expressions: ExpressionSource
    kind: str
    allow_extra_lines: bool = True
    load_error: Exception | None = None
    record_path: Path | None = None


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
        expr_type = type(expr).__name__
        detail = f"line {line_no}: {expr_type} does not render via .eval()"
        if cause is not None:
            detail = f"{detail} ({cause})"
        super().__init__(detail)


class GroundTruthSourceLoadError(Exception):
    def __init__(self, cause: Exception) -> None:
        self.cause = cause
        super().__init__(
            f"source could not be loaded ({cause.__class__.__name__}: {cause})"
        )


def normalize_expected_lines(text: str) -> list[str]:
    """Legacy compatibility helper for callers and old text fixtures."""
    return [record.expected_surface for record in records_from_legacy_text(
        text, source="legacy", kind="legacy"
    )]


def get_case_records(case: GroundTruthCase) -> list[GroundTruthRecord]:
    """Load structured JSONL records when present, otherwise adapt legacy text."""
    if case.record_path is not None and case.record_path.exists():
        records, _ = load_preferred_records(ROOT, source=case.name, kind=case.kind)
        return records
    if case.ground_truth_path.exists():
        return records_from_legacy_text(
            case.ground_truth_path.read_text(encoding="utf-8"),
            source=case.name,
            kind=case.kind,
        )
    return []


def render_lines(expressions: ExpressionSource) -> list[str]:
    if callable(expressions):
        expressions = expressions()
    rendered_lines = []
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
        rendered_lines.append(rendered.strip())
    return rendered_lines


def compare_case_lines(case: GroundTruthCase) -> GroundTruthComparison:
    if case.load_error is not None:
        raise GroundTruthSourceLoadError(case.load_error)
    expected_lines = [record.expected_surface for record in get_case_records(case)]
    actual_lines = render_lines(case.expressions)
    for index, expected in enumerate(expected_lines):
        line_no = index + 1
        if index >= len(actual_lines):
            return GroundTruthComparison(
                case=case,
                expected_lines=expected_lines,
                actual_lines=actual_lines,
                mismatch_line_no=line_no,
                mismatch_expected=expected,
                mismatch_actual=None,
            )
        actual = actual_lines[index]
        if actual != expected:
            return GroundTruthComparison(
                case=case,
                expected_lines=expected_lines,
                actual_lines=actual_lines,
                mismatch_line_no=line_no,
                mismatch_expected=expected,
                mismatch_actual=actual,
            )
    return GroundTruthComparison(
        case=case,
        expected_lines=expected_lines,
        actual_lines=actual_lines,
    )


def append_ground_truth_lines(path: Path, lines: list[str]) -> None:
    """Append legacy text for compatibility with existing corpus consumers."""
    if not lines:
        return
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    updated = existing
    if updated and not updated.endswith("\n"):
        updated += "\n"
    updated += "\n".join(lines)
    if not updated.endswith("\n"):
        updated += "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(updated, encoding="utf-8")


def replace_ground_truth_line(path: Path, line_no: int, line: str) -> None:
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    normalized_line_no = 0
    target_index = None
    for index, raw_line in enumerate(raw_lines):
        if not raw_line.strip():
            continue
        normalized_line_no += 1
        if normalized_line_no == line_no:
            target_index = index
            break
    if target_index is None:
        raise IndexError(f"Ground-truth line {line_no} not found in {path}")
    raw_lines[target_index] = line
    path.write_text("\n".join(raw_lines) + "\n", encoding="utf-8")


def append_case_ground_truth_lines(case: GroundTruthCase, lines: list[str]) -> None:
    """Append approved targets to canonical JSONL and mirror legacy text when present."""
    if not lines:
        return
    records = get_case_records(case)
    updated = append_records(records, lines, source=case.name, kind=case.kind)
    structured = case.record_path or record_path(ROOT, kind=case.kind, source=case.name)
    write_records(structured, updated)
    append_ground_truth_lines(case.ground_truth_path, lines)


def replace_case_ground_truth_line(case: GroundTruthCase, line_no: int, line: str) -> None:
    """Replace an approved target in canonical JSONL and the legacy text mirror."""
    records = get_case_records(case)
    updated = replace_record_surface(records, line_no, line)
    structured = case.record_path or record_path(ROOT, kind=case.kind, source=case.name)
    write_records(structured, updated)
    replace_ground_truth_line(case.ground_truth_path, line_no, line)


def migrate_case_to_records(case: GroundTruthCase, *, overwrite: bool = False) -> Path:
    structured = case.record_path or record_path(ROOT, kind=case.kind, source=case.name)
    if structured.exists() and not overwrite:
        return structured
    records = records_from_legacy_text(
        case.ground_truth_path.read_text(encoding="utf-8"),
        source=case.name,
        kind=case.kind,
    )
    write_records(structured, records)
    return structured


def _load_cases_from_dir(
    *,
    ground_truth_dir: Path,
    kind: str,
    expression_loader: Callable[[str], ExpressionSource],
) -> list[GroundTruthCase]:
    records_dir = ROOT / "ground_truth" / "records" / kind
    names = {path.stem for path in ground_truth_dir.glob("*.txt")}
    names.update(path.stem for path in records_dir.glob("*.jsonl"))
    cases: list[GroundTruthCase] = []
    for name in sorted(names):
        path = ground_truth_dir / f"{name}.txt"
        expressions: ExpressionSource = ()
        load_error = None
        try:
            expressions = expression_loader(name)
        except Exception as exc:
            load_error = exc
        cases.append(
            GroundTruthCase(
                name=name,
                ground_truth_path=path,
                expressions=expressions,
                kind=kind,
                load_error=load_error,
                record_path=records_dir / f"{name}.jsonl",
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
    source_path_tu = HISTORIC_SOURCE_DIR / f"{source_name}.tu.py"
    source_path_py = HISTORIC_SOURCE_DIR / f"{source_name}.py"
    if source_path_tu.exists():
        source_path = source_path_tu
    elif source_path_py.exists():
        source_path = source_path_py
    else:
        raise AttributeError(
            f"Missing primary source for '{source_name}'. "
            f"Define a list named '{source_name}' in a source module under historic/."
        )
    module_name = f"historic._ground_truth_case_{source_name}"
    module = _load_module_from_path(module_name, source_path)
    expressions = getattr(module, source_name, None)
    if expressions is None:
        raise AttributeError(
            f"Missing primary source for '{source_name}'. "
            f"Define a list named '{source_name}' in the source module."
        )
    return expressions


def _load_synthetic_expressions(source_name: str) -> ExpressionSource:
    module = _load_module_from_path(
        "synthetic._ground_truth_primary_sources",
        ROOT / "synthetic" / "primary_sources.py",
    )
    expressions = getattr(module, source_name, None)
    if expressions is None:
        raise AttributeError(
            f"Missing synthetic source for '{source_name}'. "
            f"Define a list named '{source_name}' in synthetic/primary_sources.py."
        )
    return expressions


def load_historic_cases() -> list[GroundTruthCase]:
    return _load_cases_from_dir(
        ground_truth_dir=HISTORIC_GROUND_TRUTH_DIR,
        kind="historic",
        expression_loader=_load_historic_expressions,
    )


def load_synthetic_cases() -> list[GroundTruthCase]:
    return _load_cases_from_dir(
        ground_truth_dir=SYNTHETIC_GROUND_TRUTH_DIR,
        kind="synthetic",
        expression_loader=_load_synthetic_expressions,
    )


def load_ground_truth_cases(
    *, include_synthetic: bool = False
) -> list[GroundTruthCase]:
    cases = load_historic_cases()
    if include_synthetic:
        cases.extend(load_synthetic_cases())
    return cases
