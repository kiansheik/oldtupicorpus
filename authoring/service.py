from __future__ import annotations

import ast
import importlib.util
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

from authoring.records import GroundTruthRecord, normalize_surface, write_records
from authoring.source_annotations import source_entries
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
            "record_path": str(case.record_path),
        }
        for case in load_ground_truth_cases(include_synthetic=include_synthetic)
    ]


def reload_engine() -> dict[str, Any]:
    """Evict cached `pydicate`/`tupi` engine modules so the next render re-imports them.

    This authoring MCP server is a long-lived process, and Python caches every
    imported module in `sys.modules` for that process's lifetime. Editing
    `../nhe-enga/{pydicate,tupi}` source on disk does nothing to an already
    running server until those cached modules are evicted — `historic/lexicon.tu.py`
    is reloaded fresh on every call, but its `from pydicate...import *` statement
    is a no-op against an already-cached package. Call this immediately after any
    engine edit, before the next render_candidate, verify_ground_truth, or
    line_status call, or you will silently re-test the OLD engine code.
    """
    prefixes = ("pydicate", "tupi")
    removed = sorted(
        name for name in list(sys.modules) if name.split(".", 1)[0] in prefixes
    )
    for name in removed:
        del sys.modules[name]
    return {"reloaded_modules": removed}


def get_source_context(
    source: str, record_id: str | int, *, radius: int = 3
) -> dict[str, Any]:
    case = get_case(source)
    records = get_case_records(case)
    record = get_record(records, record_id)
    rendered = render_lines(case.expressions)
    index = record.ordinal - 1
    start = max(0, index - max(0, radius))
    end = min(max(len(records), len(rendered)), index + max(0, radius) + 1)
    context = []
    for ordinal in range(start + 1, end + 1):
        expected = records[ordinal - 1] if ordinal <= len(records) else None
        actual = rendered[ordinal - 1] if ordinal <= len(rendered) else None
        context.append(
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
        "context": context,
    }


def render_candidate(
    source: str, expression: str, *, record_id: str | int | None = None
) -> dict[str, Any]:
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
    result: dict[str, Any] = {
        "source": source,
        "expression": expression,
        "rendered": rendered,
        "annotated": render_annotated(value),
        "value_type": type(value).__name__,
    }
    if record_id is not None:
        record = get_record(get_case_records(get_case(source)), record_id)
        result.update(
            {
                "record": serialize_record(record),
                "matches_target": rendered == record.expected_surface,
                "target": record.expected_surface,
            }
        )
    return result


def search_rendered_expressions(query: str, *, limit: int = 30) -> list[dict[str, Any]]:
    needle = normalize_query(query)
    if not needle:
        return []
    matches: list[dict[str, Any]] = []
    for case in load_ground_truth_cases(include_synthetic=False):
        records = get_case_records(case)
        for ordinal, rendered in enumerate(render_lines(case.expressions), start=1):
            record = records[ordinal - 1] if ordinal <= len(records) else None
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
                    "ordinal": ordinal,
                    "id": record.id if record else f"{case.name}:{ordinal:04d}",
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
    needle = normalize_query(query)
    if not needle:
        return []
    results: list[dict[str, Any]] = []
    for name, value in sorted(load_lexicon_namespace().items()):
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
        if needle not in normalize_query(f"{name} {surface} {definition or ''}"):
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


def line_status(source: str) -> dict[str, Any]:
    """Per-source-line ground-truth status for one historic source.

    Every source-list entry gets its own status, independent of whether an
    earlier entry mismatches, so one bad line never hides the status of the
    rest of the file:

    - "verified": an approved record exists at this ordinal and the current
      rendering matches it.
    - "mismatch": an approved record exists at this ordinal but the current
      rendering does not match it (or fails to render at all).
    - "unaccounted": no ground-truth record exists yet at this ordinal.
    """
    case = get_case(source)
    records_by_ordinal = {record.ordinal: record for record in get_case_records(case)}
    entries = source_entries(source_file_path(source), source_name=source)
    expressions = list(
        case.expressions() if callable(case.expressions) else case.expressions
    )
    return {
        "source": source,
        "lines": lines_from_entries(entries, expressions, records_by_ordinal),
    }


def line_status_for_text(source: str, text: str) -> dict[str, Any]:
    """Like `line_status`, but rendered from an in-memory buffer, not disk.

    Lets an editor show status for unsaved edits without writing them to the
    real source file. The buffer is written to a throwaway temp file only so
    it can be parsed and imported as `historic.<name>`; that temp file is
    always removed before returning.
    """
    case = get_case(source)
    records_by_ordinal = {record.ordinal: record for record in get_case_records(case)}

    with tempfile.NamedTemporaryFile(
        suffix=".tu.py", mode="w", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(text)
        temp_path = Path(handle.name)

    try:
        entries = source_entries(temp_path, source_name=source)
        module = _load_module_from_path(f"historic._authoring_live_{source}", temp_path)
    except Exception as exc:
        return {
            "source": source,
            "lines": [],
            "error": f"{exc.__class__.__name__}: {exc}",
        }
    finally:
        temp_path.unlink(missing_ok=True)

    expressions = getattr(module, source, None)
    if expressions is None:
        return {
            "source": source,
            "lines": [],
            "error": f"Missing '{source}' list in the edited buffer.",
        }

    return {
        "source": source,
        "lines": lines_from_entries(entries, list(expressions), records_by_ordinal),
    }


def commit_ground_truth(source: str, ordinal: int) -> dict[str, Any]:
    """Approve exactly one source line's current rendering as ground truth.

    This only ever writes the JSONL record at `ordinal` — it never re-renders
    or re-approves any other line, even ones whose live rendering has since
    drifted from what is persisted for them. That is what makes this safe to
    call on a partially-reviewed source without silently blessing neighboring
    lines nobody has looked at yet (unlike a full `regenerate`, which rebuilds
    every record in the source from its current rendering).

    Ordinals must be approved in order: this refuses an ordinal more than one
    past the last persisted record, since JSONL ground-truth records must be
    contiguous starting at 1.

    Refuses when the existing record at `ordinal` already declares a
    `normalized_target` (a human-specified correct surface — from `@target`
    or a prior "Correct ground truth" pass) that the current rendering does
    not match: silently overwriting that declared target with whatever
    currently renders would be exactly the automatic target replacement this
    tool must never do.
    """
    case = get_case(source)
    expressions = list(
        case.expressions() if callable(case.expressions) else case.expressions
    )
    if ordinal < 1 or ordinal > len(expressions):
        raise KeyError(f"{source} has no source entry at ordinal {ordinal}.")

    existing = list(get_case_records(case))
    if ordinal > len(existing) + 1:
        raise ValueError(
            f"{source} record {ordinal} cannot be approved yet — records must "
            f"be approved in order. Approve record {len(existing) + 1} first."
        )

    prior = existing[ordinal - 1] if ordinal <= len(existing) else None
    rendered = render_one(expressions[ordinal - 1])
    if rendered is None:
        raise ValueError(f"{source} record {ordinal} failed to render a string.")

    if (
        prior is not None
        and prior.normalized_target is not None
        and rendered != prior.expected_surface
    ):
        raise ValueError(
            f"{source} record {ordinal} already declares a target "
            f"({prior.normalized_target!r}) that the current rendering does not "
            "match. Fix the engine, or use 'Correct ground truth' instead of "
            "committing over a declared target."
        )

    new_record = GroundTruthRecord(
        id=f"{source}:{ordinal:04d}",
        source=source,
        kind=case.kind,
        ordinal=ordinal,
        surface=rendered,
        status="approved",
        diplomatic=prior.diplomatic if prior else None,
        normalized_target=prior.normalized_target if prior else None,
        translation=prior.translation if prior else None,
        analysis=prior.analysis if prior else None,
        locations=prior.locations if prior else (),
        notes=prior.notes if prior else (),
    )
    records = list(existing)
    if prior is None:
        records.append(new_record)
    else:
        records[ordinal - 1] = new_record
    write_records(case.record_path, records)

    return {"source": source, "ordinal": ordinal, "committed_surface": rendered}


def lines_from_entries(
    entries: list[Any],
    expressions: list[Any],
    records_by_ordinal: dict[int, GroundTruthRecord],
) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for ordinal, entry in enumerate(entries, start=1):
        record = records_by_ordinal.get(ordinal)
        expression = expressions[ordinal - 1] if ordinal <= len(expressions) else None
        rendered = render_one(expression) if expression is not None else None
        if record is None:
            status = "unaccounted"
        elif rendered is not None and rendered == record.expected_surface:
            status = "verified"
        else:
            status = "mismatch"
        lines.append(
            {
                "ordinal": ordinal,
                "source_line": entry.source_line,
                "end_line": entry.end_line,
                "status": status,
                "rendered": rendered,
                "target": record.expected_surface if record else None,
                "declared_target": record.normalized_target if record else None,
            }
        )
    return lines


def render_one(expression: object) -> str | None:
    evaluator = getattr(expression, "eval", None)
    if not callable(evaluator):
        return None
    try:
        rendered = evaluator()
    except Exception:
        return None
    if not isinstance(rendered, str):
        return None
    return normalize_surface(rendered)


def get_case(source: str) -> GroundTruthCase:
    for case in load_ground_truth_cases(include_synthetic=False):
        if case.name == source:
            return case
    raise KeyError(f"Unknown historic source: {source}")


def get_record(
    records: Iterable[GroundTruthRecord], record_id: str | int
) -> GroundTruthRecord:
    values = list(records)
    if isinstance(record_id, int) or str(record_id).isdigit():
        ordinal = int(record_id)
        if ordinal < 1 or ordinal > len(values):
            raise KeyError(f"Unknown ground-truth ordinal: {ordinal}")
        return values[ordinal - 1]
    value = str(record_id)
    for record in values:
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
        raise CandidateSafetyError(
            f"Candidate is not a Python expression: {exc.msg}"
        ) from exc
    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.Lambda,
                ast.ListComp,
                ast.SetComp,
                ast.DictComp,
                ast.GeneratorExp,
                ast.NamedExpr,
            ),
        ):
            raise CandidateSafetyError(f"Candidate may not use {type(node).__name__}.")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise CandidateSafetyError("Candidate may not access dunder names.")
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            raise CandidateSafetyError(
                "Candidate may not access private or dunder attributes."
            )
        if isinstance(node, ast.Call) and callable_name(node.func) in BLOCKED_CALLS:
            raise CandidateSafetyError(
                f"Candidate may not call {callable_name(node.func)}()."
            )


def callable_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def load_source_namespace(source: str) -> dict[str, Any]:
    module_name = f"historic._authoring_{source}"
    return dict(vars(_load_module_from_path(module_name, source_file_path(source))))


def _load_module_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)
    return module


def load_lexicon_namespace() -> dict[str, Any]:
    path = HISTORIC_SOURCE_DIR / "lexicon.tu.py"
    spec = importlib.util.spec_from_file_location("historic._authoring_lexicon", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load lexicon module {path}")
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
    for attempt in (lambda: evaluator(True), lambda: evaluator(annotated=True)):
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
