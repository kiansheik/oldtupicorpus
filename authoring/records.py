from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


VALID_RECORD_STATUSES = frozenset({"draft", "human_review", "approved", "implemented", "unresolved"})


def normalize_surface(value: str) -> str:
    """Match the legacy text comparator's treatment of blank lines and terminal punctuation."""
    normalized = value.strip()
    if normalized and normalized[-1] in ".;:!?":
        normalized = normalized[:-1]
    return normalized.strip()


@dataclass(frozen=True)
class GroundTruthRecord:
    """One human-owned editorial target for one executable source expression.

    ``surface`` is the canonical comparison target. ``diplomatic`` may preserve a
    source transcription, while ``normalized_target`` records an explicitly
    editorial modern-orthography form when it differs from the diplomatic text.
    Unknown JSON fields are retained under ``metadata`` so the format can grow
    without forcing migrations.
    """

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
    notes: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def expected_surface(self) -> str:
        return normalize_surface(self.normalized_target or self.surface)

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "id": self.id,
            "source": self.source,
            "kind": self.kind,
            "ordinal": self.ordinal,
            "surface": self.surface,
            "status": self.status,
        }
        optional = {
            "diplomatic": self.diplomatic,
            "normalized_target": self.normalized_target,
            "translation": self.translation,
            "analysis": self.analysis,
        }
        value.update({key: item for key, item in optional.items() if item is not None})
        if self.notes:
            value["notes"] = list(self.notes)
        value.update(self.metadata)
        return value

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

        record_id = str(value.get("id") or f"{record_source}:{record_ordinal:04d}").strip()
        status = str(value.get("status") or "approved").strip()
        if status not in VALID_RECORD_STATUSES:
            raise ValueError(
                f"Ground-truth record {record_id!r} has unsupported status {status!r}."
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
            "notes",
        }
        notes = value.get("notes") or []
        if not isinstance(notes, list) or not all(isinstance(note, str) for note in notes):
            raise ValueError(f"Ground-truth record {record_id!r} has invalid 'notes'.")

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
            notes=tuple(notes),
            metadata={key: item for key, item in value.items() if key not in known},
        )


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def record_path(root: Path, *, kind: str, source: str) -> Path:
    return root / "ground_truth" / "records" / kind / f"{source}.jsonl"


def legacy_path(root: Path, *, kind: str, source: str) -> Path:
    return root / "ground_truth" / kind / f"{source}.txt"


def records_from_legacy_text(text: str, *, source: str, kind: str) -> list[GroundTruthRecord]:
    records: list[GroundTruthRecord] = []
    for raw in text.splitlines():
        surface = normalize_surface(raw)
        if not surface:
            continue
        ordinal = len(records) + 1
        records.append(
            GroundTruthRecord(
                id=f"{source}:{ordinal:04d}",
                source=source,
                kind=kind,
                ordinal=ordinal,
                surface=surface,
            )
        )
    return records


def load_records(path: Path, *, source: str, kind: str) -> list[GroundTruthRecord]:
    records: list[GroundTruthRecord] = []
    seen_ids: set[str] = set()
    seen_ordinals: set[int] = set()
    for physical_line, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path}:{physical_line}: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"Ground-truth record {path}:{physical_line} must be a JSON object.")
        record = GroundTruthRecord.from_dict(
            payload,
            source=source,
            kind=kind,
            ordinal=len(records) + 1,
        )
        if record.id in seen_ids:
            raise ValueError(f"Duplicate ground-truth record id {record.id!r} in {path}.")
        if record.ordinal in seen_ordinals:
            raise ValueError(f"Duplicate ground-truth ordinal {record.ordinal} in {path}.")
        seen_ids.add(record.id)
        seen_ordinals.add(record.ordinal)
        records.append(record)

    expected_ordinals = list(range(1, len(records) + 1))
    actual_ordinals = [record.ordinal for record in records]
    if actual_ordinals != expected_ordinals:
        raise ValueError(
            f"Ground-truth records in {path} must use contiguous ordinals 1..{len(records)}."
        )
    return records


def load_preferred_records(
    root: Path,
    *,
    source: str,
    kind: str,
) -> tuple[list[GroundTruthRecord], Path | None]:
    structured_path = record_path(root, kind=kind, source=source)
    if structured_path.exists():
        return load_records(structured_path, source=source, kind=kind), structured_path

    legacy = legacy_path(root, kind=kind, source=source)
    if not legacy.exists():
        raise FileNotFoundError(
            f"No structured or legacy ground truth found for {kind}/{source}."
        )
    return records_from_legacy_text(legacy.read_text(encoding="utf-8"), source=source, kind=kind), None


def write_records(path: Path, records: Iterable[GroundTruthRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = [json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) for record in records]
    path.write_text("\n".join(serialized) + ("\n" if serialized else ""), encoding="utf-8")


def append_records(
    records: Iterable[GroundTruthRecord],
    surfaces: Iterable[str],
    *,
    source: str,
    kind: str,
) -> list[GroundTruthRecord]:
    updated = list(records)
    for surface in surfaces:
        normalized = normalize_surface(surface)
        if not normalized:
            continue
        ordinal = len(updated) + 1
        updated.append(
            GroundTruthRecord(
                id=f"{source}:{ordinal:04d}",
                source=source,
                kind=kind,
                ordinal=ordinal,
                surface=normalized,
                status="approved",
            )
        )
    return updated


def replace_record_surface(
    records: Iterable[GroundTruthRecord], line_no: int, surface: str) -> list[GroundTruthRecord]:
    updated = list(records)
    if line_no < 1 or line_no > len(updated):
        raise IndexError(f"Ground-truth record {line_no} not found.")
    record = updated[line_no - 1]
    normalized = normalize_surface(surface)
    if record.normalized_target is not None:
        updated[line_no - 1] = GroundTruthRecord(
            **{**record.__dict__, "normalized_target": normalized}
        )
    else:
        updated[line_no - 1] = GroundTruthRecord(**{**record.__dict__, "surface": normalized})
    return updated
