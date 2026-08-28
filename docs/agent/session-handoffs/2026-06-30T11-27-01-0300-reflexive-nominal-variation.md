# Reflexive Nominal Variation

## Goal

Support the Araujo page 6 source line:

```python
l += (iabiõ * seîxu) + (îe * mombeu).base_nominal()
```

with an opt-in variation that renders:

```text
seîxu îabi'õ îemombe'u
```

## Files Inspected

- `historic/AGENTS.md`
- `historic/araujo_catecismo_1686.tu.py`
- `historic/lexicon.tu.py`
- `../nhe-enga/AGENTS.md`
- `../nhe-enga/tupi/AGENTS.md`
- `../nhe-enga/tupi/tupi/verb.py`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/postposition.py`

## Files Changed

- `../nhe-enga/tupi/tupi/verb.py`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`
- `historic/araujo_catecismo_1686.tu.py`
- `tests/reflexive_nominal_variation_test.py`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-06-30T11-27-01-0300-reflexive-nominal-variation.md`

## Commands Run

- `python3 - <<'PY' ... (iabiõ * seîxu) + (îe * mombeu).var(1).base_nominal() ... PY`
- `python3 -m unittest tests.reflexive_nominal_variation_test`
- `python3 -m unittest tests.reflexive_nominal_variation_test tests.proper_noun_phonetics_test tests.base_nominal_object_pro_drop_test tests.paben_adverb_test tests.nominal_pro_drop_test tests.moro_incorporation_test`
- `python3 - <<'PY' ... from historic.primary_sources import araujo_catecismo_1686 ... PY`
- `make verify-ground-truth`

## What Worked

- `iabiõ * seîxu` already rendered `seîxu îabi'õ`; the needed change was only
  the nominalized reflexive verb.
- `(îe * mombeu).base_nominal()` still renders the default `oîo mombe'u`.
- `(îe * mombeu).var(1).base_nominal()` now renders `îemombe'u`.
- `(îo * mombeu).var(1).base_nominal()` renders the reciprocal contrast
  `îomombe'u`.
- The Araujo source tail now includes record 77 as
  `seîxu îabi'õ îemombe'u`.

## What Failed

- Running `python3 historic/araujo_catecismo_1686.tu.py` directly failed because
  direct file execution does not put the repo root on `sys.path`. Importing via
  `historic.primary_sources` worked.
- `make verify-ground-truth` still fails at the existing active Araujo record 74
  source/JSONL drift. Ground truth was not regenerated.

## Remaining Questions

- The active Araujo records from 74 onward still need ground-truth acceptance
  once the page 6 source sequence is ready.

## Suggested Next Prompt

Continue adding/reviewing the page 6 Araujo lines, then regenerate Araujo
structured ground truth when the active source sequence should become approved.
