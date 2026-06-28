from __future__ import annotations

import ast
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable

from authoring.records import GroundTruthRecord, PhilologicalLocation, normalize_surface


DIRECTIVE_RE = re.compile(r"^\s*#\s*@(?P<key>[a-z][a-z0-9_-]*)\s*(?P<value>.*?)\s*$", re.IGNORECASE)
LOCATION_KEYS = frozenset({"witness", "edition", "page", "folio", "line", "section", "url", "note"})
RECORD_KEYS = frozenset({"diplomatic", "target", "translation", "analysis", "status"})


@dataclass(frozen=True)
class SourceAnnotation:
    """Metadata parsed from `# @...` comments attached to one source expression."""

    source_line: int
    locations: tuple[PhilologicalLocation, ...] = ()
    diplomatic: str | None = None
    normalized_target: str | None = None
    translation: str | None = None
    analysis: str | None = None
    status: str = "approved"
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SourceEntry:
    """One expression position in source order, including its physical source line."""

    source_line: int


def source_records_from_file(
    source_path: Path,
    expressions: Iterable[object],
    *,
    source: str,
    kind: str,
) -> list[GroundTruthRecord]:
    """Generate records from `.tu.py` expressions and attached comment directives.

    The source expression is authoritative. A comment block immediately above a
    list item or `l += expression` statement attaches to that next entry:

        # @page 25-26
        # @line 25-34
        l += (...)

    Pages waterfall in source order. When an entry has no `@page`, it inherits
    the ending page of the prior page-bearing entry. Lines never waterfall.
    The directive comments do not alter the Pydicate expression, its rendering,
    or the ordinary Python source syntax.
    """
    entries = source_entries(source_path, source_name=source)
    rendered_expressions = list(expressions)
    if len(entries) != len(rendered_expressions):
        raise ValueError(
            f"{source_path}: found {len(entries)} source expressions but loaded "
            f"{len(rendered_expressions)} runtime expressions. Keep the declared source "
            "list and its additions in positional correspondence."
        )
    annotations = waterfall_page_annotations(
        entries, annotations_by_source_line(source_path, entries)
    )
    return [
        record_from_expression(
            expression,
            source=source,
            kind=kind,
            ordinal=ordinal,
            annotation=annotations.get(entry.source_line),
        )
        for ordinal, (entry, expression) in enumerate(
            zip(entries, rendered_expressions, strict=True), start=1
        )
    ]


def source_entries(source_path: Path, *, source_name: str | None = None) -> list[SourceEntry]:
    """Find source expressions in either `l = [...]` or `<source> = [...]` style.

    Older files use a convenience list named `l` and add entries with `l +=`.
    Others declare their canonical source list directly, for example
    `bettendorff_compendio = [...]`. Both styles are deliberate and supported.
    """
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    collection_name, initial = _initial_collection(tree, source_path, source_name)
    entries = [SourceEntry(element.lineno) for element in initial.elts]

    for statement in tree.body:
        if _is_append_to(statement, collection_name):
            entries.extend(SourceEntry(statement.lineno) for _ in _append_values(statement.value))

    return entries


def annotations_by_source_line(
    source_path: Path, entries: Iterable[SourceEntry]
) -> dict[int, SourceAnnotation]:
    lines = source_path.read_text(encoding="utf-8").splitlines()
    return {
        entry.source_line: annotation
        for entry in entries
        if (annotation := _annotation_before(lines, entry.source_line)) is not None
    }


def waterfall_page_annotations(
    entries: Iterable[SourceEntry],
    annotations: dict[int, SourceAnnotation],
) -> dict[int, SourceAnnotation]:
    """Fill an omitted page from the nearest preceding page-bearing source entry.

    `@page 25-26` establishes page 26 as the active page for later entries.
    An inherited page is written as a single page, never a copied range. Line
    locators are intentionally not inherited.
    """
    effective: dict[int, SourceAnnotation] = {}
    active_page: str | None = None

    for entry in entries:
        annotation = _with_inherited_page(
            annotations.get(entry.source_line),
            active_page,
            source_line=entry.source_line,
        )
        if annotation is not None:
            effective[entry.source_line] = annotation

        ending_page = _ending_page(annotation)
        if ending_page is not None:
            active_page = ending_page

    return effective


def record_from_expression(
    expression: object,
    *,
    source: str,
    kind: str,
    ordinal: int,
    annotation: SourceAnnotation | None = None,
) -> GroundTruthRecord:
    rendered = expression.eval()
    if not isinstance(rendered, str):
        raise TypeError(
            f"Source {source} record {ordinal} rendered {type(rendered).__name__}, expected str."
        )
    return GroundTruthRecord(
        id=f"{source}:{ordinal:04d}",
        source=source,
        kind=kind,
        ordinal=ordinal,
        surface=normalize_surface(rendered),
        status=annotation.status if annotation else "approved",
        diplomatic=annotation.diplomatic if annotation else None,
        normalized_target=annotation.normalized_target if annotation else None,
        translation=annotation.translation if annotation else None,
        analysis=annotation.analysis if annotation else None,
        locations=annotation.locations if annotation else (),
        notes=annotation.notes if annotation else (),
    )


def _initial_collection(
    tree: ast.Module, source_path: Path, source_name: str | None
) -> tuple[str, ast.List | ast.Tuple]:
    candidates: list[tuple[str, ast.List | ast.Tuple]] = []
    for statement in tree.body:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        if not isinstance(target, ast.Name) or not isinstance(statement.value, (ast.List, ast.Tuple)):
            continue
        candidates.append((target.id, statement.value))

    if source_name:
        for name, values in candidates:
            if name == source_name:
                return name, values
    for name, values in candidates:
        if name == "l":
            return name, values
    if len(candidates) == 1:
        return candidates[0]

    wanted = f"`{source_name} = [...]` or " if source_name else ""
    raise ValueError(
        f"{source_path}: no initial {wanted}`l = [...]` source list was found."
    )


def _annotation_before(lines: list[str], expression_line: int) -> SourceAnnotation | None:
    directives: list[tuple[str, str]] = []
    line_index = expression_line - 2
    while line_index >= 0:
        raw = lines[line_index]
        if not raw.strip():
            if directives:
                line_index -= 1
                continue
            return None
        match = DIRECTIVE_RE.match(raw)
        if match is None:
            break
        directives.append((match.group("key").lower(), match.group("value").strip()))
        line_index -= 1

    if not directives:
        return None
    directives.reverse()
    return _parse_directives(directives, source_line=expression_line)


def _parse_directives(
    directives: Iterable[tuple[str, str]], *, source_line: int
) -> SourceAnnotation:
    location_values: dict[str, str] = {}
    record_values: dict[str, str] = {}
    notes: list[str] = []

    for key, value in directives:
        if key == "lines":
            key = "line"
        elif key == "pages":
            key = "page"
        elif key == "folios":
            key = "folio"
        if key in LOCATION_KEYS:
            if key == "note":
                notes.append(value)
            else:
                location_values[key] = value
            continue
        if key in RECORD_KEYS:
            record_values[key] = value
            continue
        raise ValueError(
            f"Source annotation at line {source_line} uses unsupported directive @{key}."
        )

    locations = ()
    if location_values:
        locations = (_location_from_values(location_values),)
    status = record_values.get("status", "approved") or "approved"
    return SourceAnnotation(
        source_line=source_line,
        locations=locations,
        diplomatic=_optional(record_values.get("diplomatic")),
        normalized_target=_optional(record_values.get("target")),
        translation=_optional(record_values.get("translation")),
        analysis=_optional(record_values.get("analysis")),
        status=status,
        notes=tuple(note for note in notes if note),
    )


def _with_inherited_page(
    annotation: SourceAnnotation | None,
    active_page: str | None,
    *,
    source_line: int,
) -> SourceAnnotation | None:
    if active_page is None or _ending_page(annotation) is not None:
        return annotation

    inherited_location = PhilologicalLocation(page_start=active_page)
    if annotation is None:
        return SourceAnnotation(source_line=source_line, locations=(inherited_location,))
    if not annotation.locations:
        return replace(annotation, locations=(inherited_location,))

    locations = list(annotation.locations)
    locations[-1] = replace(locations[-1], page_start=active_page)
    return replace(annotation, locations=tuple(locations))


def _ending_page(annotation: SourceAnnotation | None) -> str | None:
    if annotation is None:
        return None
    for location in reversed(annotation.locations):
        if location.page_end is not None:
            return location.page_end
        if location.page_start is not None:
            return location.page_start
    return None


def _location_from_values(values: dict[str, str]) -> PhilologicalLocation:
    page_start, page_end = _span(values.get("page"))
    folio_start, folio_end = _span(values.get("folio"))
    line_start, line_end = _span(values.get("line"))
    return PhilologicalLocation.from_dict(
        {
            key: value
            for key, value in {
                "witness": _optional(values.get("witness")),
                "edition": _optional(values.get("edition")),
                "page_start": page_start,
                "page_end": page_end,
                "folio_start": folio_start,
                "folio_end": folio_end,
                "line_start": line_start,
                "line_end": line_end,
                "section": _optional(values.get("section")),
                "url": _optional(values.get("url")),
            }.items()
            if value is not None
        }
    )


def _span(value: str | None) -> tuple[str | None, str | None]:
    normalized = _optional(value)
    if normalized is None:
        return None, None
    for separator in ("–", "—", "-", " to "):
        if separator in normalized:
            start, end = normalized.split(separator, 1)
            return _optional(start), _optional(end)
    return normalized, None


def _is_append_to(statement: ast.stmt, collection_name: str) -> bool:
    return (
        isinstance(statement, ast.AugAssign)
        and isinstance(statement.target, ast.Name)
        and statement.target.id == collection_name
        and isinstance(statement.op, ast.Add)
    )


def _append_values(value: ast.expr) -> list[ast.expr]:
    if isinstance(value, (ast.List, ast.Tuple)):
        return list(value.elts)
    return [value]


def _optional(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
