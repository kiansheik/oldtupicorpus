from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Iterable

VALID_RECORD_STATUSES = frozenset({"draft", "human_review", "approved", "implemented", "unresolved"})


def normalize_surface(value: str) -> str:
    value = value.strip()
    if value and value[-1] in ".;:!?":
        value = value[:-1]
    return value.strip()


def _text(value: Any) -> str | None:
    return str(value).strip() or None if value is not None else None


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
            raise ValueError("Philological location has unsupported field(s): " + ", ".join(unknown))
        location = cls(**{key: _text(value.get(key)) for key in known})
        if not location.to_dict():
            raise ValueError("A philological location must contain at least one locator field.")
        return location

    @property
    def display(self) -> str:
        parts = [item for item in (self.witness, self.edition, self.section, self.subsection) if item]
        if self.folio_start:
            parts.append(f"f. {self.folio_start}" + (f"-{self.folio_end}" if self.folio_end and self.folio_end != self.folio_start else ""))
        elif self.page_start:
            parts.append(f"p. {self.page_start}" + (f"-{self.page_end}" if self.page_end and self.page_end != self.page_start else ""))
        if self.line_start:
            parts.append(f"l. {self.line_start}" + (f"-{self.line_end}" if self.line_end and self.line_end != self.line_start else ""))
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
        result: dict[str, Any] = {"id": self.id, "source": self.source, "kind": self.kind, "ordinal": self.ordinal, "surface": self.surface, "status": self.status}
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
    def from_dict(cls, value: dict[str, Any], *, source: str | None = None, kind: str | None = None, ordinal: int | None = None) -> "GroundTruthRecord":
        record_source = str(value.get("source") or source or "").strip()
        record_kind = str(value.get("kind") or kind or "").strip()
        record_ordinal = int(value.get("ordinal") or ordinal or 0)
        surface = str(value.get("surface") or value.get("target") or "").strip()
        if not record_source or not record_kind or record_ordinal < 1 or not surface:
            raise ValueError("Ground-truth record is missing required source, kind, ordinal, or surface.")
        record_id = str(value.get("id") or f"{record_source}:{record_ordinal:04d}").strip()
        status = str(value.get("status") or "approved").strip()
        if status not in VALID_RECORD_STATUSES:
            raise ValueError(f"Ground-truth record {record_id!r} has unsupported status {status!r}.")
        notes = value.get("notes") or []
        locations = value.get("locations") or []
        if not isinstance(notes, list) or not all(isinstance(note, str) for note in notes):
            raise ValueError(f"Ground-truth record {record_id!r} has invalid 'notes'.")
        if not isinstance(locations, list):
            raise ValueError(f"Ground-truth record {record_id!r} has invalid 'locations'.")
        known = {"id", "source", "kind", "ordinal", "surface", "target", "status", "diplomatic", "normalized_target", "translation", "analysis", "locations", "notes"}
        return cls(id=record_id, source=record_source, kind=record_kind, ordinal=record_ordinal, surface=normalize_surface(surface), status=status, diplomatic=_text(value.get("diplomatic")), normalized_target=_text(value.get("normalized_target")), translation=_text(value.get("translation")), analysis=_text(value.get("analysis")), locations=tuple(PhilologicalLocation.from_dict(item) for item in locations), notes=tuple(notes), metadata={key: item for key, item in value.items() if key not in known})


def record_path(root: Path, *, kind: str, source: str) -> Path:
    return root / "ground_truth" / "records" / kind / f"{source}.jsonl"


def legacy_path(root: Path, *, kind: str, source: str) -> Path:
    return root / "ground_truth" / kind / f"{source}.txt"


def records_from_legacy_text(text: str, *, source: str, kind: str) -> list[GroundTruthRecord]:
    return append_records([], text.splitlines(), source=source, kind=kind)


def load_records(path: Path, *, source: str, kind: str) -> list[GroundTruthRecord]:
    records: list[GroundTruthRecord] = []
    seen_ids: set[str] = set()
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path}:{number}: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"Ground-truth record {path}:{number} must be a JSON object.")
        record = GroundTruthRecord.from_dict(payload, source=source, kind=kind, ordinal=len(records) + 1)
        if record.id in seen_ids:
            raise ValueError(f"Duplicate ground-truth record id {record.id!r} in {path}.")
        seen_ids.add(record.id)
        records.append(record)
    if [record.ordinal for record in records] != list(range(1, len(records) + 1)):
        raise ValueError(f"Ground-truth records in {path} must use contiguous ordinals.")
    return records


def load_preferred_records(root: Path, *, source: str, kind: str) -> tuple[list[GroundTruthRecord], Path | None]:
    structured = record_path(root, kind=kind, source=source)
    if structured.exists():
        return load_records(structured, source=source, kind=kind), structured
    legacy = legacy_path(root, kind=kind, source=source)
    if not legacy.exists():
        raise FileNotFoundError(f"No structured or legacy ground truth found for {kind}/{source}.")
    return records_from_legacy_text(legacy.read_text(encoding="utf-8"), source=source, kind=kind), None


def write_records(path: Path, records: Iterable[GroundTruthRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) for record in records]
    path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


def append_records(records: Iterable[GroundTruthRecord], surfaces: Iterable[str], *, source: str, kind: str) -> list[GroundTruthRecord]:
    result = list(records)
    for raw in surfaces:
        surface = normalize_surface(raw)
        if surface:
            ordinal = len(result) + 1
            result.append(GroundTruthRecord(id=f"{source}:{ordinal:04d}", source=source, kind=kind, ordinal=ordinal, surface=surface))
    return result


def append_record(path: Path, record: GroundTruthRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")


def replace_record_surface(records: Iterable[GroundTruthRecord], ordinal: int, surface: str) -> list[GroundTruthRecord]:
    surface = normalize_surface(surface)
    if not surface:
        raise ValueError("Replacement ground-truth surface must not be blank.")
    found = False
    result: list[GroundTruthRecord] = []
    for record in records:
        if record.ordinal == ordinal:
            result.append(replace(record, surface=surface))
            found = True
        else:
            result.append(record)
    if not found:
        raise KeyError(f"No ground-truth record has ordinal {ordinal}.")
    return result


def add_record_location(record: GroundTruthRecord, location: PhilologicalLocation) -> GroundTruthRecord:
    return replace(record, locations=(*record.locations, location))
