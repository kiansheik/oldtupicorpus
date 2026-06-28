from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from authoring.records import GroundTruthRecord, PhilologicalLocation, normalize_surface


@dataclass(frozen=True)
class AttestedExpression:
    """A transparent executable expression with source-local scholarly metadata.

    Instances remain safe in historic expression lists because `.eval()` and all
    unrecognised attributes delegate to the wrapped Pydicate expression. The
    annotation is therefore visible to record generation without changing the
    morphology or corpus APIs that consume the expression.
    """

    expression: object
    locations: tuple[PhilologicalLocation, ...] = ()
    diplomatic: str | None = None
    normalized_target: str | None = None
    translation: str | None = None
    analysis: str | None = None
    status: str = "approved"
    notes: tuple[str, ...] = ()

    def eval(self, *args: Any, **kwargs: Any) -> str:
        return self.expression.eval(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.expression, name)

    def __repr__(self) -> str:
        return f"attest({self.expression!r})"


def loc(
    *,
    witness: str | None = None,
    edition: str | None = None,
    page: str | int | None = None,
    pages: str | int | None = None,
    page_start: str | int | None = None,
    page_end: str | int | None = None,
    folio: str | int | None = None,
    folios: str | int | None = None,
    folio_start: str | int | None = None,
    folio_end: str | int | None = None,
    line: str | int | None = None,
    lines: str | int | None = None,
    line_start: str | int | None = None,
    line_end: str | int | None = None,
    section: str | None = None,
    url: str | None = None,
    note: str | None = None,
) -> PhilologicalLocation:
    """Build a philological locator with compact page and line range shorthand.

    Examples:
        loc(page="157", lines="12-14")
        loc(folio="10r", lines="4-7", witness="BNE MSS/1234")
        loc(pages="xii-xiii", section="Credo")
    """
    page_start, page_end = _resolve_span(page_start, page_end, pages if pages is not None else page)
    folio_start, folio_end = _resolve_span(folio_start, folio_end, folios if folios is not None else folio)
    line_start, line_end = _resolve_span(line_start, line_end, lines if lines is not None else line)
    return PhilologicalLocation.from_dict(
        {
            key: value
            for key, value in {
                "witness": witness,
                "edition": edition,
                "page_start": page_start,
                "page_end": page_end,
                "folio_start": folio_start,
                "folio_end": folio_end,
                "line_start": line_start,
                "line_end": line_end,
                "section": section,
                "url": url,
                "note": note,
            }.items()
            if value is not None
        }
    )


def attest(
    expression: object,
    *locations: PhilologicalLocation,
    witness: str | None = None,
    edition: str | None = None,
    page: str | int | None = None,
    pages: str | int | None = None,
    page_start: str | int | None = None,
    page_end: str | int | None = None,
    folio: str | int | None = None,
    folios: str | int | None = None,
    folio_start: str | int | None = None,
    folio_end: str | int | None = None,
    line: str | int | None = None,
    lines: str | int | None = None,
    line_start: str | int | None = None,
    line_end: str | int | None = None,
    section: str | None = None,
    url: str | None = None,
    note: str | None = None,
    diplomatic: str | None = None,
    normalized_target: str | None = None,
    translation: str | None = None,
    analysis: str | None = None,
    status: str = "approved",
    notes: Iterable[str] = (),
) -> AttestedExpression:
    """Annotate an expression directly where it appears in a historic source.

    The direct shorthand is intended for routine transcription work:

        attest(expr, page="157", lines="12-14")

    Supply multiple `loc(...)` objects when a single corpus line has parallel
    witnesses or spans multiple printed/manuscript locations.
    """
    direct_values = (
        witness,
        edition,
        page,
        pages,
        page_start,
        page_end,
        folio,
        folios,
        folio_start,
        folio_end,
        line,
        lines,
        line_start,
        line_end,
        section,
        url,
        note,
    )
    direct_locations = tuple(locations)
    if any(value is not None for value in direct_values):
        direct_locations += (
            loc(
                witness=witness,
                edition=edition,
                page=page,
                pages=pages,
                page_start=page_start,
                page_end=page_end,
                folio=folio,
                folios=folios,
                folio_start=folio_start,
                folio_end=folio_end,
                line=line,
                lines=lines,
                line_start=line_start,
                line_end=line_end,
                section=section,
                url=url,
                note=note,
            ),
        )
    return AttestedExpression(
        expression=expression,
        locations=direct_locations,
        diplomatic=_clean_optional(diplomatic),
        normalized_target=_clean_optional(normalized_target),
        translation=_clean_optional(translation),
        analysis=_clean_optional(analysis),
        status=status,
        notes=tuple(note for note in notes if str(note).strip()),
    )


def record_from_expression(
    expression: object,
    *,
    source: str,
    kind: str,
    ordinal: int,
) -> GroundTruthRecord:
    """Derive one reproducible target record from the annotated source expression."""
    annotation = expression if isinstance(expression, AttestedExpression) else None
    wrapped = annotation.expression if annotation else expression
    rendered = wrapped.eval()
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


def records_from_expressions(
    expressions: Iterable[object], *, source: str, kind: str
) -> list[GroundTruthRecord]:
    return [
        record_from_expression(expression, source=source, kind=kind, ordinal=ordinal)
        for ordinal, expression in enumerate(expressions, start=1)
    ]


def _resolve_span(
    start: str | int | None,
    end: str | int | None,
    compact: str | int | None,
) -> tuple[str | None, str | None]:
    if start is not None or end is not None:
        return _clean_optional(start), _clean_optional(end)
    value = _clean_optional(compact)
    if value is None:
        return None, None
    for separator in ("–", "—", "-", " to "):
        if separator in value:
            left, right = value.split(separator, 1)
            return _clean_optional(left), _clean_optional(right)
    return value, None


def _clean_optional(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
