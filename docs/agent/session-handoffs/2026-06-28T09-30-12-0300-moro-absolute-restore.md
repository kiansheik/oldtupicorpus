# Session Handoff: `moro` Absolute Restore

## Goal

Fix the `make review-ground-truth` mismatch where Araujo line 52 rendered
`arobîar poropysyrõanamo sekó` instead of the absolute/deverbal
`arobîar moropysyrõanamo sekó`, while preserving the new imperative
`eporoapiti umẽ`.

## Files Inspected

- `docs/agent/index.md`
- `docs/agent/current-state.md`
- `docs/agent/repo-map.md`
- `docs/agent/open-questions.md`
- `historic/araujo_catecismo_1686.tu.py`
- `ground_truth/historic/araujo_catecismo_1686.txt`
- `tests/moro_incorporation_test.py`
- `../nhe-enga/tupi/tupi/tupi.py`
- `../nhe-enga/tupi/tupi/verb.py`

## Files Changed

- `../nhe-enga/tupi/tupi/tupi.py`
- `../nhe-enga/tupi/tupi/verb.py`
- `tests/moro_incorporation_test.py`
- `ground_truth/historic/araujo_catecismo_1686.txt`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-06-28T09-30-12-0300-moro-absolute-restore.md`

## Commands Run

- `rg -n "moro|poro|personal_inflections|object_tense == \"gen\"|moro_incorporation" ../nhe-enga/tupi/tupi tests docs/agent historic -g '!__target__'`
- `python3 - <<'PY' ...` probes for `moro * pysyro`, `sara.var(1) * (moro * pysyro)`, possessed deverbals, and imperatives
- `python3 -m unittest tests.moro_incorporation_test`
- `python3 tests/run_tests.py --update-ground-truth --ground-truth-source araujo_catecismo_1686`
- `python3 tests/run_tests.py --accept-new-ground-truth --ground-truth-source araujo_catecismo_1686`
- `tail -n 12 ground_truth/historic/araujo_catecismo_1686.txt`
- `git -C ../nhe-enga diff -- tupi/tupi/tupi.py tupi/tupi/verb.py`

## What Worked

- Restoring the shared `TupiAntigo.personal_inflections["gen"]` dependent form
  to `moro` fixes the line-52 absolute/deverbal output:
  `sara.var(1) * (moro * pysyro)` now renders `moropysyrõana`.
- Keeping `obj = "poro[OBJECT:gen]"` inside the conjugated generic-object branch
  preserves the imperative output:
  `(+nde * apiti * moro).imp()` renders `eporoapiti` and its negative renders
  `eporoapiti umẽ`.
- `python3 -m unittest tests.moro_incorporation_test` passes.
- `python3 tests/run_tests.py --accept-new-ground-truth --ground-truth-source araujo_catecismo_1686`
  appended the three new trailing commandment lines; a second run reported no
  new lines and no blocked sources.

## What Failed

- `python3 tests/run_tests.py --update-ground-truth --ground-truth-source araujo_catecismo_1686`
  failed in the non-interactive agent session because `--update-ground-truth`
  requires an interactive terminal.
- The first test update expected bare `moro * pysyro` to render `moropysyrõ`,
  but that expression is still treated as a conjugated generic-object verb and
  renders `poropysyrõ`. The protected Araujo absolute/deverbal case is the
  wrapped `sara.var(1) * (moro * pysyro)` form.

## Remaining Questions

- The ground-truth file already had unrelated local edits before this session,
  including an existing line-18 change. Do not treat the full file diff as only
  this session's work.

## Suggested Next Prompt

Run the broader historic ground-truth check and review any remaining mismatches
now that Araujo line 52 keeps `moropysyrõanamo`.
