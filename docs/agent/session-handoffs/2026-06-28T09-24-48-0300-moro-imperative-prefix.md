# Session Handoff: `moro` Imperative Prefix

## Goal

Make `l+= (+nde * apiti * moro).imp()` work for the special generic `moro`
object so the Araujo commandment can render `eporoapiti umẽ`.

## Files Inspected

- `docs/agent/index.md`
- `docs/agent/current-state.md`
- `docs/agent/repo-map.md`
- `docs/agent/open-questions.md`
- `historic/araujo_catecismo_1686.tu.py`
- `historic/lexicon.tu.py`
- `tests/moro_incorporation_test.py`
- `../nhe-enga/tupi/tupi/tupi.py`
- `../nhe-enga/tupi/tupi/verb.py`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`

## Files Changed

- `../nhe-enga/tupi/tupi/verb.py`
- `historic/araujo_catecismo_1686.tu.py`
- `tests/moro_incorporation_test.py`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-06-28T09-24-48-0300-moro-imperative-prefix.md`

## Commands Run

- `rg -n "moro|poro|personal_inflections|apiti|imp\\(" . ../nhe-enga -g '!*.pyc' -g '!__pycache__'`
- `python3 - <<'PY' ...` probes for `(+nde * apiti * moro).imp()`, negation, and `moro * pysyro`
- `python3 -m unittest tests.moro_incorporation_test`
- `PYTHONPATH=. python3 historic/araujo_catecismo_1686.tu.py | tail -n 8`
- `git status --short`
- `git diff -- historic/araujo_catecismo_1686.tu.py tests/moro_incorporation_test.py docs/agent/current-state.md docs/agent/log.md`
- `git -C ../nhe-enga diff -- tupi/tupi/verb.py`

## What Worked

- The issue was in the sibling `../nhe-enga/tupi/tupi/verb.py`
  `object_tense == "gen"` branch: it built `poro + root` without the
  subject/imperative prefix.
- Adding the prefix for explicit non-3p generic-object conjugations makes
  `(+nde * apiti * moro).imp()` render `eporoapiti`.
- Marking the Araujo expression negative makes the source tail render
  `eporoapiti umẽ`.
- `python3 -m unittest tests.moro_incorporation_test` passes.

## What Failed

- A first prefix patch was too broad and made `moro * pysyro` render
  `oporopysyrõ`; narrowing the added prefix away from nominal and pro-dropped
  3p generic-object forms restored the previous `poropysyrõ` test expectation.
- Running `python3 historic/araujo_catecismo_1686.tu.py` directly failed because
  the script needs `PYTHONPATH=.` for the `historic` package import.
- `git -C ../nhe-enga status --short` hung and was interrupted; use targeted
  diffs instead if repo status remains slow.

## Remaining Questions

- The checked-in Araujo ground-truth file was already modified and does not yet
  include the trailing commandment lines shown by the source render. This
  session did not update ground truth.
- Prior memory says absolute/deverbal `moro * pysyro` may need to stay
  `moro...`, but the current local test still expects `poropysyrõ`; resolve that
  separately before changing this path further.

## Suggested Next Prompt

Review and update the Araujo ground-truth tail now that the final commandment
renders `eporoapiti umẽ`, while preserving the existing `moro` regression
expectations.
