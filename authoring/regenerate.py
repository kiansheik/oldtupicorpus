from __future__ import annotations

from pathlib import Path
from typing import Iterable

from authoring.records import GroundTruthRecord, record_path, write_records
from authoring.source_annotations import source_records_from_file
from tests.ground_truth_cases import GroundTruthCase, get_case_records


ROOT = Path(__file__).resolve().parents[1]


def source_path(case: GroundTruthCase) -> Path:
    return ROOT / case.kind / f"{case.name}.tu.py"


def generated_records(case: GroundTruthCase) -> list[GroundTruthRecord]:
    """Build records from executable source and directly attached `# @...` comments."""
    if case.load_error is not None:
        raise RuntimeError(f"Cannot regenerate {case.name}: {case.load_error}")
    expressions = case.expressions() if callable(case.expressions) else case.expressions
    return source_records_from_file(
        source_path(case), expressions, source=case.name, kind=case.kind
    )


def regenerate_case(case: GroundTruthCase) -> tuple[Path, Path, list[GroundTruthRecord]]:
    """Rebuild JSONL and legacy text artifacts from one annotated source file."""
    records = generated_records(case)
    structured = record_path(ROOT, kind=case.kind, source=case.name)
    write_records(structured, records)
    write_legacy_mirror(case.ground_truth_path, records)
    return structured, case.ground_truth_path, records


def generated_records_match_disk(case: GroundTruthCase) -> bool:
    """Whether checked-in artifacts exactly match the current annotated source code."""
    return generated_records(case) == get_case_records(case)


def write_legacy_mirror(path: Path, records: Iterable[GroundTruthRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [record.expected_surface for record in records]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
