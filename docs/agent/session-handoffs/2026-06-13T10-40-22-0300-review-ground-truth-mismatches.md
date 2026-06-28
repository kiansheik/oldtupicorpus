# Session Handoff: Review Ground-Truth Mismatches

## Goal

Improve `make review-ground-truth` so an existing ground-truth mismatch can be
resolved interactively by choosing either the checked-in expected line or the
newly rendered actual line.

## Files Inspected

- `tests/ground_truth_cases.py`
- `tests/run_tests.py`
- `tests/ground_truth_cases_test.py`
- `README.md`
- `docs/agent/current-state.md`
- `docs/agent/log.md`

## Files Changed

- `tests/ground_truth_cases.py`
- `tests/run_tests.py`
- `tests/ground_truth_cases_test.py`
- `README.md`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-06-13T10-40-22-0300-review-ground-truth-mismatches.md`

## Commands Run

- `python3 -m unittest tests.ground_truth_cases_test`
- `make -n review-ground-truth ARGS="--ground-truth-source araujo_catecismo_1686"`
- `date +%Y-%m-%dT%H-%M-%S%z`

## What Worked

- Added `replace_ground_truth_line()` to replace one logical nonblank
  ground-truth line while preserving blank lines in the file.
- Changed `_review_case_updates()` so mismatches prompt for `[e]xpected`,
  `[a]ctual`, or `[q]uit`.
- Choosing actual writes the rendered line, re-runs the comparison, and then
  continues to append-review if the source has only trailing new lines left.
- Choosing expected keeps the file unchanged and stops that source.
- Added tests for accepting actual mismatches and preserving blank lines.

## What Failed

- No focused test failures in this turn.

## Remaining Questions

- If hand editing arbitrary text is needed in the future, add a separate choice
  that opens an editor or accepts a typed replacement. Current behavior only
  chooses between expected and actual.

## Suggested Next Prompt

Run `make review-ground-truth ARGS="--ground-truth-source araujo_catecismo_1686"`
and choose `[a]ctual` for the line 18 mismatch if the rendered form should
become the new ground truth.
