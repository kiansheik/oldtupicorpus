from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Iterable


VALID_RECORD_STATUSES = frozenset(
    {"draft", "human_review", "approved", "implemented", "unresolved"}
)


def normalize_surface(value: str) -> str:
    normalized = value.strip()
    if normalized and normalized[-1] in ".;:!?":
        normalized = normalized[:-1]
    return normalized.strip()


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


@dataclass(frozen=True)
class PhilologicalLocation:
    witness: str | None = None
    edition: str | None = None
    page_start: str | None = None
    page_end: str | None = None
    folio_start: str | None = None
    folio_end: str | None = None
    line_start: str | None = None
    line_end: str | None = None
    section: str | None = None
    subsection: str | None = None
    url: str | None = None
    note: str | None = None

    def to_dict(self) -> dict[str, str]:
        return {key: value for key, value in self.__dict__.items() if value is not None}

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "PhilologicalLocation":
        if not isinstance(value, dict):
            raise ValueError("A philological location must be a JSON object.")
        known = set(cls.__dataclass_fields__)
        unknown = sorted(set(value) - known)
        if unknown:
            raise ValueError(
                "Philological location has unsupported field(s): " + ", ".join(unknown)
            )
        location = cls(**{key: _optional_text(value.get(key)) for key in known})
        if not location.to_dict():
            raise ValueError(
                "A philological location must contain at least one locator field."
            )
        return location

    @property
    def display(self) -> str:
        parts = [
            item
            for item in (self.witness, self.edition, self.section, self.subsection)
            if item
        ]
        if self.folio_start:
            value = f"f. {self.folio_start}"
            if self.folio_end and self.folio_end != self.folio_start:
                value += f"-{self.folio_end}"
            parts.append(value)
        elif self.page_start:
            value = f"p. {self.page_start}"
            if self.page_end and self.page_end != self.page_start:
                value += f"-{self.page_end}"
            parts.append(value)
        if self.line_start:
            value = f"l. {self.line_start}"
            if self.line_end and self.line_end != self.line_start:
                value += f"-{self.line_end}"
            parts.append(value)
        return ", ".join(parts)


@dataclass(frozen=True)
class GroundTruthRecord:
    id: str
    source: str
    kind: str
    ordinal: int
    surface: str
    status: str = "approved"
    diplomatic: str | None = None
    normalized_target: str | None = None
    translation: str | None = None
    analysis: str | None = None
    locations: tuple[PhilologicalLocation, ...] = ()
    notes: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def expected_surface(self) -> str:
        return normalize_surface(self.normalized_target or self.surface)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "source": self.source,
            "kind": self.kind,
            "ordinal": self.ordinal,
            "surface": self.surface,
            "status": self.status,
        }
        for key in ("diplomatic", "normalized_target", "translation", "analysis"):
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        if self.locations:
            result["locations"] = [location.to_dict() for location in self.locations]
        if self.notes:
            result["notes"] = list(self.notes)
        result.update(self.metadata)
        return result

    @classmethod
    def from_dict(
        cls,
        value: dict[str, Any],
        *,
        source: str | None = None,
        kind: str | None = None,
        ordinal: int | None = None,
    ) -> "GroundTruthRecord":
        record_source = str(value.get("source") or source or "").strip()
        record_kind = str(value.get("kind") or kind or "").strip()
        record_ordinal = int(value.get("ordinal") or ordinal or 0)
        surface = str(value.get("surface") or value.get("target") or "").strip()
        if not record_source:
            raise ValueError("Ground-truth record is missing 'source'.")
        if not record_kind:
            raise ValueError("Ground-truth record is missing 'kind'.")
        if record_ordinal < 1:
            raise ValueError("Ground-truth record ordinal must be >= 1.")
        if not surface:
            raise ValueError("Ground-truth record is missing 'surface'.")
        record_id = str(
            value.get("id") or f"{record_source}:{record_ordinal:04d}"
        ).strip()
        status = str(value.get("status") or "approved").strip()
        if status not in VALID_RECORD_STATUSES:
            raise ValueError(
                f"Ground-truth record {record_id!r} has unsupported status {status!r}."
            )
        notes = value.get("notes") or []
        locations = value.get("locations") or []
        if not isinstance(notes, list) or not all(
            isinstance(note, str) for note in notes
        ):
            raise ValueError(f"Ground-truth record {record_id!r} has invalid 'notes'.")
        if not isinstance(locations, list):
            raise ValueError(
                f"Ground-truth record {record_id!r} has invalid 'locations'."
            )
        known = {
            "id",
            "source",
            "kind",
            "ordinal",
            "surface",
            "target",
            "status",
            "diplomatic",
            "normalized_target",
            "translation",
            "analysis",
            "locations",
            "notes",
        }
        return cls(
            id=record_id,
            source=record_source,
            kind=record_kind,
            ordinal=record_ordinal,
            surface=normalize_surface(surface),
            status=status,
            diplomatic=_optional_text(value.get("diplomatic")),
            normalized_target=_optional_text(value.get("normalized_target")),
            translation=_optional_text(value.get("translation")),
            analysis=_optional_text(value.get("analysis")),
            locations=tuple(PhilologicalLocation.from_dict(item) for item in locations),
            notes=tuple(notes),
            metadata={key: item for key, item in value.items() if key not in known},
        )


def record_path(root: Path, *, kind: str, source: str) -> Path:
    return root / "ground_truth" / "records" / kind / f"{source}.jsonl"


def load_records(path: Path, *, source: str, kind: str) -> list[GroundTruthRecord]:
    records: list[GroundTruthRecord] = []
    seen_ids: set[str] = set()
    seen_ordinals: set[int] = set()
    for physical_line, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw.strip():
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in {path}:{physical_line}: {exc.msg}"
            ) from exc
        if not isinstance(payload, dict):
            raise ValueError(
                f"Ground-truth record {path}:{physical_line} must be a JSON object."
            )
        record = GroundTruthRecord.from_dict(
            payload, source=source, kind=kind, ordinal=len(records) + 1
        )
        if record.id in seen_ids or record.ordinal in seen_ordinals:
            raise ValueError(f"Duplicate ground-truth record identity in {path}.")
        seen_ids.add(record.id)
        seen_ordinals.add(record.ordinal)
        records.append(record)
    if [record.ordinal for record in records] != list(range(1, len(records) + 1)):
        raise ValueError(
            f"Ground-truth records in {path} must use contiguous ordinals."
        )
    return records


def write_records(path: Path, records: Iterable[GroundTruthRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True)
        for record in records
    ]
    path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


def append_records(
    records: Iterable[GroundTruthRecord],
    surfaces: Iterable[str],
    *,
    source: str,
    kind: str,
) -> list[GroundTruthRecord]:
    result = list(records)
    for raw_surface in surfaces:
        surface = normalize_surface(raw_surface)
        if not surface:
            continue
        ordinal = len(result) + 1
        result.append(
            GroundTruthRecord(
                id=f"{source}:{ordinal:04d}",
                source=source,
                kind=kind,
                ordinal=ordinal,
                surface=surface,
            )
        )
    return result


def append_record(path: Path, record: GroundTruthRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + "\n"
        )


def replace_record_surface(
    records: Iterable[GroundTruthRecord], ordinal: int, surface: str
) -> list[GroundTruthRecord]:
    normalized = normalize_surface(surface)
    if not normalized:
        raise ValueError("Replacement ground-truth surface must not be blank.")
    updated = list(records)
    for index, record in enumerate(updated):
        if record.ordinal != ordinal:
            continue
        updated[index] = replace(
            record,
            normalized_target=(
                normalized if record.normalized_target is not None else None
            ),
            surface=(
                record.surface if record.normalized_target is not None else normalized
            ),
        )
        return updated
    raise KeyError(f"No ground-truth record has ordinal {ordinal}.")


def add_record_location(
    record: GroundTruthRecord, location: PhilologicalLocation
) -> GroundTruthRecord:
    return replace(record, locations=(*record.locations, location))
