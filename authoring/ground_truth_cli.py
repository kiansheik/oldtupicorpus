from __future__ import annotations

import argparse
import json
import sys

from authoring.regenerate import generated_records, regenerate_case
from tests.ground_truth_cases import (
    GroundTruthRenderError,
    GroundTruthSourceLoadError,
    compare_case_lines,
    get_case_records,
    load_ground_truth_cases,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify and regenerate Old Tupi JSONL ground truth from annotated source code."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (
        ("verify", "Verify renderings and ensure JSONL artifacts match source annotations."),
        ("regenerate", "Rebuild JSONL records from `.tu.py` source entries."),
        ("review", "Inspect whether JSONL artifacts are current."),
    ):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument(
            "--source", action="append", default=[], help="Historic source name; repeatable."
        )
        if name == "verify":
            command.add_argument("--json", action="store_true", help="Emit machine-readable output.")
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


def _first_record_difference(expected, actual):
    for ordinal, (left, right) in enumerate(zip(expected, actual), start=1):
        if left != right:
            return ordinal
    if len(expected) != len(actual):
        return min(len(expected), len(actual)) + 1
    return None


def verify(cases) -> tuple[int, list[dict[str, object]]]:
    results: list[dict[str, object]] = []
    failures = 0
    for case in cases:
        try:
            generated = generated_records(case)
            saved = get_case_records(case)
            stale_ordinal = _first_record_difference(generated, saved)
            comparison = compare_case_lines(case)
        except (GroundTruthRenderError, GroundTruthSourceLoadError, ValueError, RuntimeError) as exc:
            failures += 1
            results.append({"source": case.name, "ok": False, "error": str(exc)})
            continue
        if stale_ordinal is not None:
            failures += 1
            results.append({"source": case.name, "ok": False, "stale": {"ordinal": stale_ordinal}})
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
        if comparison.extra_lines:
            failures += 1
            results.append(
                {"source": case.name, "ok": False, "new_unapproved_lines": comparison.extra_lines}
            )
            continue
        results.append(
            {
                "source": case.name,
                "ok": True,
                "approved_records": len(comparison.expected_lines),
                "rendered_lines": len(comparison.actual_lines),
            }
        )
    return failures, results


def regenerate(cases) -> int:
    for case in cases:
        try:
            structured, records = regenerate_case(case)
        except (GroundTruthRenderError, GroundTruthSourceLoadError, ValueError, RuntimeError) as exc:
            print(f"[ground-truth] {case.name}: blocked: {exc}", file=sys.stderr)
            return 1
        print(f"[ground-truth] {case.name}: regenerated {len(records)} record(s)\n  JSONL: {structured}")
    return 0


def review(cases) -> int:
    failures, results = verify(cases)
    for result in results:
        if result["ok"]:
            print(f"[ground-truth] {result['source']}: source annotations and JSONL are current")
            continue
        print(f"[ground-truth] {result['source']}: requires source-driven regeneration")
        if "stale" in result:
            print(f"  first changed record: {result['stale']['ordinal']}")
        elif "mismatch" in result:
            mismatch = result["mismatch"]
            print(f"  record {mismatch['ordinal']}: expected {mismatch['expected']}")
            print(f"  rendered: {mismatch['actual']}")
        elif "error" in result:
            print(f"  {result['error']}")
        else:
            print("  Edit the source entry and its `# @...` comments, then run regenerate.")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        cases = selected_cases(args.source)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.command == "regenerate":
        return regenerate(cases)
    if args.command == "review":
        return review(cases)

    failures, results = verify(cases)
    if args.json:
        print(json.dumps({"ok": failures == 0, "sources": results}, ensure_ascii=False, indent=2))
    else:
        for result in results:
            if result["ok"]:
                print(
                    f"[ground-truth] {result['source']}: OK "
                    f"({result['approved_records']} generated, {result['rendered_lines']} rendered)"
                )
                continue
            print(f"[ground-truth] {result['source']}: FAILED")
            if "stale" in result:
                print(f"  source annotations differ from generated JSONL at record {result['stale']['ordinal']}.")
                print("  Run: make regenerate-ground-truth")
            elif "mismatch" in result:
                mismatch = result["mismatch"]
                print(f"  record {mismatch['ordinal']}: expected {mismatch['expected']}")
                print(f"  rendered: {mismatch['actual']}")
            elif "new_unapproved_lines" in result:
                print("  source has rendered lines absent from generated JSONL.")
                print("  Run: make regenerate-ground-truth")
            else:
                print(f"  {result['error']}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
