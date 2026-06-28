from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path

from authoring.records import (
    PhilologicalLocation,
    add_record_location,
    record_path,
    write_records,
)
from tests.ground_truth_cases import (
    GroundTruthRenderError,
    GroundTruthSourceLoadError,
    append_case_ground_truth_lines,
    compare_case_lines,
    get_case_records,
    load_ground_truth_cases,
    migrate_case_to_records,
)


ROOT = Path(__file__).resolve().parents[1]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect, migrate, annotate, and human-approve Old Tupi ground truth."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser("verify", help="Compare rendered historic sources with approved targets.")
    verify.add_argument("--source", action="append", default=[], help="Historic source name; repeatable.")
    verify.add_argument("--json", action="store_true", help="Emit machine-readable output.")

    migrate = subparsers.add_parser("migrate", help="Create canonical JSONL records from legacy text.")
    migrate.add_argument("--source", action="append", default=[], help="Historic source name; repeatable.")
    migrate.add_argument("--overwrite", action="store_true", help="Replace an existing JSONL record file.")

    review = subparsers.add_parser(
        "review",
        help="Interactively approve only new trailing rendered lines. Existing targets are immutable here.",
    )
    review.add_argument("--source", action="append", default=[], help="Historic source name; repeatable.")

    locate = subparsers.add_parser(
        "locate",
        help="Append one witness, edition, page or folio, and line locator to a source record.",
    )
    locate.add_argument("--source", required=True, help="Historic source name.")
    locate.add_argument("--record", required=True, help="Ground-truth record id or ordinal.")
    locate.add_argument("--witness", help="Witness, manuscript, or source siglum.")
    locate.add_argument("--edition", help="Edition or bibliographic reference.")
    locate.add_argument("--page-start", help="First printed page, including Roman or bracketed forms.")
    locate.add_argument("--page-end", help="Last printed page when the attestation crosses pages.")
    locate.add_argument("--folio-start", help="First folio, for example 10r or 23v.")
    locate.add_argument("--folio-end", help="Last folio when the attestation crosses folios.")
    locate.add_argument("--line-start", help="First source line number or label.")
    locate.add_argument("--line-end", help="Last source line number or label.")
    locate.add_argument("--section", help="Section, chapter, prayer, or other internal locator.")
    locate.add_argument("--url", help="Stable catalogue, facsimile, or edition URL.")
    locate.add_argument("--note", help="Short transcription or locator note.")
    return parser.parse_args(argv)


def selected_cases(names: list[str]):
    cases = load_ground_truth_cases(include_synthetic=False)
    if not names:
        return cases
    wanted = set(names)
    selected = [case for case in cases if case.name in wanted]
    missing = sorted(wanted - {case.name for case in selected})
    if missing:
        raise KeyError(f"Unknown historic source(s): {', '.join(missing)}")
    return selected


def verify(cases) -> tuple[int, list[dict[str, object]]]:
    results: list[dict[str, object]] = []
    failures = 0
    for case in cases:
        try:
            comparison = compare_case_lines(case)
        except (GroundTruthRenderError, GroundTruthSourceLoadError, ValueError) as exc:
            failures += 1
            results.append({"source": case.name, "ok": False, "error": str(exc)})
            continue
        if comparison.has_mismatch:
            failures += 1
            results.append(
                {
                    "source": case.name,
                    "ok": False,
                    "mismatch": {
                        "ordinal": comparison.mismatch_line_no,
                        "expected": comparison.mismatch_expected,
                        "actual": comparison.mismatch_actual,
                    },
                }
            )
            continue
        results.append(
            {
                "source": case.name,
                "ok": True,
                "approved_records": len(comparison.expected_lines),
                "rendered_lines": len(comparison.actual_lines),
                "new_unapproved_lines": comparison.extra_lines,
            }
        )
    return failures, results


def review(cases, *, input_fn: Callable[[str], str] = input) -> int:
    """Append only human-confirmed new lines. Existing targets must be edited as records."""
    exit_code = 0
    for case in cases:
        try:
            comparison = compare_case_lines(case)
        except (GroundTruthRenderError, GroundTruthSourceLoadError, ValueError) as exc:
            print(f"[ground-truth] {case.name}: blocked: {exc}", file=sys.stderr)
            exit_code = 1
            continue
        if comparison.has_mismatch:
            print(f"[ground-truth] {case.name}: mismatch at record {comparison.mismatch_line_no}", file=sys.stderr)
            print(f"  approved target: {comparison.mismatch_expected}", file=sys.stderr)
            print(f"  rendered output: {comparison.mismatch_actual}", file=sys.stderr)
            print("  No automatic replacement is available. Resolve the analysis or edit the record deliberately.", file=sys.stderr)
            exit_code = 1
            continue
        if not comparison.extra_lines:
            print(f"[ground-truth] {case.name}: no new rendered lines", file=sys.stderr)
            continue

        approved: list[str] = []
        existing = comparison.expected_lines
        for offset, rendered in enumerate(comparison.extra_lines, start=1):
            ordinal = len(existing) + offset
            context = (existing + approved)[-5:]
            print(f"\n[{case.name}] record {ordinal}", file=sys.stderr)
            for prior_offset, line in enumerate(context, start=max(1, ordinal - len(context))):
                print(f"  {prior_offset:>4} | {line}", file=sys.stderr)
            print(f"  proposed | {rendered}", file=sys.stderr)
            choice = input_fn("Approve this as a new editorial target? [y]es/[n]o/[q]uit: ").strip().lower()
            if choice == "q":
                break
            if choice != "y":
                print(f"[ground-truth] {case.name}: stopped before record {ordinal}", file=sys.stderr)
                break
            approved.append(rendered)

        if approved:
            append_case_ground_truth_lines(case, approved)
            print(f"[ground-truth] {case.name}: appended {len(approved)} approved record(s)", file=sys.stderr)
    return exit_code


def add_location(args: argparse.Namespace) -> int:
    try:
        case = selected_cases([args.source])[0]
        location = PhilologicalLocation.from_dict(
            {
                key: value
                for key, value in {
                    "witness": args.witness,
                    "edition": args.edition,
                    "page_start": args.page_start,
                    "page_end": args.page_end,
                    "folio_start": args.folio_start,
                    "folio_end": args.folio_end,
                    "line_start": args.line_start,
                    "line_end": args.line_end,
                    "section": args.section,
                    "url": args.url,
                    "note": args.note,
                }.items()
                if value is not None
            }
        )
        records = get_case_records(case)
        updated = add_record_location(records, args.record, location)
    except (KeyError, ValueError) as exc:
        print(f"[ground-truth] {args.source}: {exc}", file=sys.stderr)
        return 2

    path = case.record_path or record_path(ROOT, kind=case.kind, source=case.name)
    write_records(path, updated)
    print(
        f"[ground-truth] {case.name}: added locator to {args.record}: {location.display or location.to_dict()}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "locate":
        return add_location(args)

    try:
        cases = selected_cases(args.source)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.command == "verify":
        failures, results = verify(cases)
        if args.json:
            print(json.dumps({"ok": failures == 0, "sources": results}, ensure_ascii=False, indent=2))
        else:
            for result in results:
                if result["ok"]:
                    print(
                        f"[ground-truth] {result['source']}: OK "
                        f"({result['approved_records']} approved, {result['rendered_lines']} rendered)"
                    )
                    if result["new_unapproved_lines"]:
                        print(
                            f"  {len(result['new_unapproved_lines'])} new trailing line(s) need review."
                        )
                else:
                    print(f"[ground-truth] {result['source']}: FAILED")
                    if "mismatch" in result:
                        mismatch = result["mismatch"]
                        print(f"  record {mismatch['ordinal']}: expected {mismatch['expected']}")
                        print(f"  rendered: {mismatch['actual']}")
                    else:
                        print(f"  {result['error']}")
        return 1 if failures else 0

    if args.command == "migrate":
        for case in cases:
            path = migrate_case_to_records(case, overwrite=args.overwrite)
            print(f"[ground-truth] {case.name}: {path}")
        return 0

    return review(cases)


if __name__ == "__main__":
    raise SystemExit(main())
