# Proper Noun Base Nominal

## Goal

Extend the proper-noun phonetic preservation fix to nominalized verb forms:

```python
l += ((esé * domingo) + ((esebé * noworkday)) + (missa * endub).base_nominal())
```

The nominal target is `missarenduba`, not `mixsarenduba`.

## Files Inspected

- `historic/araujo_catecismo_1686.tu.py`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`
- `tests/proper_noun_phonetics_test.py`
- `docs/agent/current-state.md`
- `docs/agent/log.md`

## Files Changed

- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`
- `tests/proper_noun_phonetics_test.py`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-06-30T10-56-16-0300-proper-noun-base-nominal.md`

## Commands Run

- `python3 - <<'PY' ... (missa * endub).base_nominal().eval() ... PY`
- `python3 -m unittest tests.proper_noun_phonetics_test`
- `python3 -m unittest tests.proper_noun_phonetics_test tests.base_nominal_object_pro_drop_test tests.paben_adverb_test tests.nominal_pro_drop_test tests.moro_incorporation_test`
- `make verify-ground-truth`

## What Worked

- `(ProperNoun("missa") * Verb("endub")).base_nominal().eval()` now renders
  `missarenduba`.
- `(Noun("missa") * Verb("endub")).base_nominal().eval()` still renders
  `mixsarenduba`, preserving the regular non-proper phonetic rule.
- The selected Araujo expression renders
  `domingo resé 'ara marãtekoabe'yma resebé missarenduba`.
- The combined focused morphology slice passes.

## What Failed

- Before the fix, `Verb.base_nominal()` passed unannotated proper-noun object
  text to the Tupi engine, so the engine could not protect the `[PROPER_NOUN]`
  span and rendered `mixsarenduba`.
- `make verify-ground-truth` still fails at the existing active Araujo record 74
  source/JSONL drift: `source annotations differ from generated JSONL at record
  74`. Ground truth was not regenerated.

## Remaining Questions

- The active Araujo record 74 and later lines still need to be accepted into
  structured ground truth when the source authoring sequence is ready.

## Suggested Next Prompt

Continue reviewing the page 6 Araujo lines and run source-specific ground-truth
regeneration once the active source edits should become approved records.
