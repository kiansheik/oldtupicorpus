from __future__ import annotations

from pathlib import Path

from authoring.records import GroundTruthRecord, record_path, write_records
from authoring.source_annotations import source_records_from_file
from tests.ground_truth_cases import GroundTruthCase, get_case_records


ROOT = Path(__file__).resolve().parents[1]


def source_path(case: GroundTruthCase) -> Path:
    return ROOT / case.kind / f"{case.name}.tu.py"


def generated_records(case: GroundTruthCase) -> list[GroundTruthRecord]:
    """Build structured records from executable source and adjacent directives."""
    if case.load_error is not None:
        raise RuntimeError(f"Cannot regenerate {case.name}: {case.load_error}")
    expressions = case.expressions() if callable(case.expressions) else case.expressions
    return source_records_from_file(
        source_path(case), expressions, source=case.name, kind=case.kind
    )


def regenerate_case(case: GroundTruthCase) -> tuple[Path, list[GroundTruthRecord]]:
    """Rebuild one JSONL ground-truth artifact from its annotated source file."""
    records = generated_records(case)
    structured = record_path(ROOT, kind=case.kind, source=case.name)
    write_records(structured, records)
    return structured, records


def generated_records_match_disk(case: GroundTruthCase) -> bool:
    """Whether checked-in JSONL exactly matches the current annotated source code."""
    return generated_records(case) == get_case_records(case)
