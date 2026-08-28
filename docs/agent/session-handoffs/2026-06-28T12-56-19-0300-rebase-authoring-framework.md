# Authoring Framework Rebase Handoff

## Goal

Resolve the local `agent-authoring-mcp-framework` branch after `git pull`
reported divergence from `origin/agent-authoring-mcp-framework`.

## Files Inspected

- `docs/agent/index.md`
- `docs/agent/current-state.md`
- `docs/agent/repo-map.md`
- `docs/agent/open-questions.md`
- `authoring/records.py`
- `authoring/source_annotations.py`
- `tests/ground_truth_records_test.py`
- `tests/source_annotations_test.py`
- `authoring/ground_truth_cli.py`
- `authoring/regenerate.py`
- `tests/ground_truth_cases.py`
- `ground_truth/records/historic/araujo_catecismo_1686.jsonl`

## Files Changed

- `authoring/records.py`
- `authoring/source_annotations.py`
- `tests/ground_truth_records_test.py`
- `ground_truth/records/historic/araujo_catecismo_1686.jsonl`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-06-28T12-56-19-0300-rebase-authoring-framework.md`

## Commands Run

- `git rebase origin/agent-authoring-mcp-framework`
- `python3 -m py_compile authoring/records.py authoring/source_annotations.py tests/ground_truth_records_test.py`
- `git diff --check`
- `python3 -m unittest tests.ground_truth_records_test tests.source_annotations_test tests.mcp_server_test tests.nominal_pro_drop_test tests.moro_incorporation_test`
- `python3 tests/run_tests.py --skip-tokenizer --ground-truth-source araujo_catecismo_1686`
- `python3 tests/run_tests.py --skip-tokenizer`
- `python3 -m authoring.ground_truth_cli verify --source araujo_catecismo_1686`
- `make regenerate-ground-truth ARGS="--source araujo_catecismo_1686"`
- `python3 tests/run_tests.py --accept-new-ground-truth --ground-truth-source araujo_catecismo_1686`
- `make verify-ground-truth`

## What Worked

- The branch now rebases cleanly on remote commit `2464d79`.
- `authoring/records.py` keeps subsection serialization plus the structured
  ground-truth append/replace helpers used by the review/update path.
- `authoring/source_annotations.py` keeps the remote page/section/subsection
  waterfall behavior.
- `tests/ground_truth_records_test.py` now round-trips section and subsection
  locations.
- Araujo JSONL records were regenerated from `.tu.py` annotations, so
  `make verify-ground-truth` sees generated records and saved artifacts as
  current.

## What Failed

- The first `git rebase --continue` launched `vi` in a non-interactive session.
  The rebase was completed with `GIT_EDITOR=true git rebase --continue`, then
  the stale editor process was terminated.
- Before regeneration, `python3 -m authoring.ground_truth_cli verify --source
  araujo_catecismo_1686` failed at record 1 because the generated record had
  source-derived locations while the saved JSONL did not.

## Remaining Questions

- The sibling `../nhe-enga` checkout still has the nominal pro-drop morphology
  edit and a local `docs/.DS_Store` modification. They are outside this rebase.

## Suggested Next Prompt

Push the rebased `agent-authoring-mcp-framework` branch after reviewing the
single local commit on top of origin.
