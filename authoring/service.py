from __future__ import annotations

import ast
import importlib.util
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

from authoring.records import GroundTruthRecord
from tests.ground_truth_cases import (
    GroundTruthCase,
    compare_case_lines,
    get_case_records,
    load_ground_truth_cases,
    render_lines,
)


ROOT = Path(__file__).resolve().parents[1]
HISTORIC_SOURCE_DIR = ROOT / "historic"
BLOCKED_CALLS = frozenset(
    {
        "__import__",
        "breakpoint",
        "compile",
        "delattr",
        "eval",
        "exec",
        "exit",
        "getattr",
        "globals",
        "help",
        "input",
        "locals",
        "open",
        "quit",
        "setattr",
        "vars",
    }
)


class CandidateSafetyError(ValueError):
    """Raised when a candidate contains constructs outside the authoring evaluator."""


def list_sources(*, include_synthetic: bool = False) -> list[dict[str, Any]]:
    return [
        {
            "source": case.name,
            "kind": case.kind,
            "record_count": len(get_case_records(case)),
            "record_path": str(case.record_path) if case.record_path else None,
            "legacy_path": str(case.ground_truth_path),
        }
        for case in load_ground_truth_cases(include_synthetic=include_synthetic)
    ]


def get_source_context(
    source: str,
    record_id: str | int,
    *,
    radius: int = 3,
) -> dict[str, Any]:
    case = get_case(source)
    records = get_case_records(case)
    record = get_record(records, record_id)
    rendered = render_lines(case.expressions)
    index = record.ordinal - 1
    start = max(0, index - max(0, radius))
    end = min(max(len(records), len(rendered)), index + max(0, radius) + 1)

    window = []
    for ordinal in range(start + 1, end + 1):
        expected = records[ordinal - 1] if ordinal <= len(records) else None
        actual = rendered[ordinal - 1] if ordinal <= len(rendered) else None
        window.append(
            {
                "ordinal": ordinal,
                "id": expected.id if expected else f"{source}:{ordinal:04d}",
                "target": expected.expected_surface if expected else None,
                "rendered": actual,
                "matches": expected is not None and actual == expected.expected_surface,
            }
        )

    return {
        "source": source,
        "kind": case.kind,
        "record": serialize_record(record),
        "rendered": rendered[index] if index < len(rendered) else None,
        "matches": index < len(rendered) and rendered[index] == record.expected_surface,
        "context": window,
    }


def render_candidate(source: str, expression: str, *, record_id: str | int | None = None) -> dict[str, Any]:
    validate_candidate_expression(expression)
    namespace = load_source_namespace(source)
    try:
        value = eval(compile(expression, f"<candidate:{source}>", "eval"), namespace)
    except Exception as exc:
        return {
            "source": source,
            "expression": expression,
            "error": f"{exc.__class__.__name__}: {exc}",
        }

    rendered = render_value(value)
    annotated = render_annotated(value)
    result: dict[str, Any] = {
        "source": source,
        "expression": expression,
        "rendered": rendered,
        "annotated": annotated,
        "value_type": type(value).__name__,
    }
    if record_id is not None:
        record = get_record(get_case_records(get_case(source)), record_id)
        result["record"] = serialize_record(record)
        result["matches_target"] = rendered == record.expected_surface
        result["target"] = record.expected_surface
    return result


def search_rendered_expressions(query: str, *, limit: int = 30) -> list[dict[str, Any]]:
    needle = normalize_query(query)
    if not needle:
        return []
    matches: list[dict[str, Any]] = []
    for case in load_ground_truth_cases(include_synthetic=False):
        records = get_case_records(case)
        for index, rendered in enumerate(render_lines(case.expressions), start=1):
            record = records[index - 1] if index <= len(records) else None
            haystack = " ".join(
                item
                for item in (
                    rendered,
                    record.expected_surface if record else "",
                    record.translation if record else "",
                    record.analysis if record else "",
                )
                if item
            )
            if needle not in normalize_query(haystack):
                continue
            matches.append(
                {
                    "source": case.name,
                    "kind": case.kind,
                    "ordinal": index,
                    "id": record.id if record else f"{case.name}:{index:04d}",
                    "rendered": rendered,
                    "target": record.expected_surface if record else None,
                    "translation": record.translation if record else None,
                    "analysis": record.analysis if record else None,
                }
            )
            if len(matches) >= limit:
                return matches
    return matches


def search_lexicon(query: str, *, limit: int = 50) -> list[dict[str, Any]]:
    """Search runtime lexicon values without requiring editor-specific indexes."""
    needle = normalize_query(query)
    if not needle:
        return []
    namespace = load_lexicon_namespace()
    results: list[dict[str, Any]] = []
    for name, value in sorted(namespace.items()):
        if name.startswith("_"):
            continue
        evaluator = getattr(value, "eval", None)
        if not callable(evaluator):
            continue
        try:
            surface = str(evaluator()).strip()
        except Exception:
            continue
        definition = getattr(value, "definition", None)
        haystack = normalize_query(f"{name} {surface} {definition or ''}")
        if needle not in haystack:
            continue
        results.append(
            {
                "name": name,
                "surface": surface,
                "definition": str(definition) if definition else None,
                "type": type(value).__name__,
            }
        )
        if len(results) >= limit:
            break
    return results


def verify_ground_truth(source: str | None = None) -> dict[str, Any]:
    cases = load_ground_truth_cases(include_synthetic=False)
    if source:
        cases = [case for case in cases if case.name == source]
        if not cases:
            raise KeyError(f"Unknown historic source: {source}")

    outcomes = []
    blocked = 0
    for case in cases:
        try:
            comparison = compare_case_lines(case)
        except Exception as exc:
            blocked += 1
            outcomes.append(
                {
                    "source": case.name,
                    "ok": False,
                    "error": f"{exc.__class__.__name__}: {exc}",
                }
            )
            continue
        if comparison.has_mismatch:
            blocked += 1
            outcomes.append(
                {
                    "source": case.name,
                    "ok": False,
                    "mismatch": {
                        "ordinal": comparison.mismatch_line_no,
                        "expected": comparison.mismatch_expected,
                        "actual": comparison.mismatch_actual,
                    },
                    "extra_lines": comparison.extra_lines,
                }
            )
        else:
            outcomes.append(
                {
                    "source": case.name,
                    "ok": True,
                    "records": len(comparison.expected_lines),
                    "rendered": len(comparison.actual_lines),
                    "extra_lines": comparison.extra_lines,
                }
            )
    return {"ok": blocked == 0, "blocked": blocked, "sources": outcomes}


def get_case(source: str) -> GroundTruthCase:
    for case in load_ground_truth_cases(include_synthetic=False):
        if case.name == source:
            return case
    raise KeyError(f"Unknown historic source: {source}")


def get_record(records: Iterable[GroundTruthRecord], record_id: str | int) -> GroundTruthRecord:
    records_list = list(records)
    if isinstance(record_id, int) or str(record_id).isdigit():
        ordinal = int(record_id)
        if ordinal < 1 or ordinal > len(records_list):
            raise KeyError(f"Unknown ground-truth ordinal: {ordinal}")
        return records_list[ordinal - 1]
    value = str(record_id)
    for record in records_list:
        if record.id == value:
            return record
    raise KeyError(f"Unknown ground-truth record: {value}")


def serialize_record(record: GroundTruthRecord) -> dict[str, Any]:
    result = record.to_dict()
    result["target"] = record.expected_surface
    return result


def validate_candidate_expression(expression: str) -> None:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise CandidateSafetyError(f"Candidate is not a Python expression: {exc.msg}") from exc

    for node in ast.walk(tree):
        if isinstance(node, (ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.NamedExpr)):
            raise CandidateSafetyError(f"Candidate may not use {type(node).__name__}.")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise CandidateSafetyError("Candidate may not access dunder names.")
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            raise CandidateSafetyError("Candidate may not access private or dunder attributes.")
        if isinstance(node, ast.Call):
            name = callable_name(node.func)
            if name in BLOCKED_CALLS:
                raise CandidateSafetyError(f"Candidate may not call {name}().")


def callable_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def load_source_namespace(source: str) -> dict[str, Any]:
    source_path = source_file_path(source)
    module_name = f"historic._authoring_{source}"
    spec = importlib.util.spec_from_file_location(module_name, source_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load source module {source_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)
    return dict(vars(module))


def load_lexicon_namespace() -> dict[str, Any]:
    lexicon_path = HISTORIC_SOURCE_DIR / "lexicon.tu.py"
    spec = importlib.util.spec_from_file_location("historic._authoring_lexicon", lexicon_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load lexicon module {lexicon_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return dict(vars(module))


def source_file_path(source: str) -> Path:
    tu_path = HISTORIC_SOURCE_DIR / f"{source}.tu.py"
    py_path = HISTORIC_SOURCE_DIR / f"{source}.py"
    if tu_path.exists():
        return tu_path
    if py_path.exists():
        return py_path
    raise KeyError(f"No historic source file found for {source!r}.")


def render_value(value: object) -> str | None:
    evaluator = getattr(value, "eval", None)
    if not callable(evaluator):
        return None
    for attempt in (
        lambda: evaluator(),
        lambda: evaluator(False),
        lambda: evaluator(annotated=False),
    ):
        try:
            rendered = attempt()
        except TypeError:
            continue
        return str(rendered).strip() if rendered is not None else None
    return None


def render_annotated(value: object) -> str | None:
    evaluator = getattr(value, "eval", None)
    if not callable(evaluator):
        return None
    for attempt in (
        lambda: evaluator(True),
        lambda: evaluator(annotated=True),
    ):
        try:
            rendered = attempt()
        except TypeError:
            continue
        return str(rendered).strip() if rendered is not None else None
    return None


def normalize_query(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[áàâãä]", "a", value)
    value = re.sub(r"[éèêẽë]", "e", value)
    value = re.sub(r"[íìîĩï]", "i", value)
    value = re.sub(r"[óòôõö]", "o", value)
    value = re.sub(r"[úùûũü]", "u", value)
    value = value.replace("ŷ", "y").replace("î", "i").replace("û", "u")
    return " ".join(value.split())
