# Proper Noun Phonetics

## Goal

Fix the current Araujo source expression:

```python
l += ((esé * domingo) + ((esebé * noworkday)) + (missa * endub))
```

The broad `is -> ix` phonetic cleanup should not rewrite proper nouns, so the
target ending is `missarendubi`, not `mixsarendubi`.

## Files Inspected

- `historic/AGENTS.md`
- `historic/araujo_catecismo_1686.tu.py`
- `historic/lexicon.tu.py`
- `ground_truth/records/historic/araujo_catecismo_1686.jsonl`
- `../nhe-enga/AGENTS.md`
- `../nhe-enga/tupi/AGENTS.md`
- `../nhe-enga/tupi/tupi/tupi.py`
- `../nhe-enga/tupi/tupi/verb.py`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/noun.py`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`

## Files Changed

- `../nhe-enga/tupi/tupi/tupi.py`
- `../nhe-enga/tupi/tupi/verb.py`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`
- `tests/proper_noun_phonetics_test.py`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-06-30T01-55-13-0300-proper-noun-phonetics.md`

## Commands Run

- `python3 - <<'PY' ... ((esé * domingo) + ((esebé * noworkday)) + (missa * endub)).eval() ... PY`
- `python3 -m unittest tests.proper_noun_phonetics_test`
- `python3 -m unittest tests.proper_noun_phonetics_test tests.base_nominal_object_pro_drop_test tests.paben_adverb_test tests.nominal_pro_drop_test tests.moro_incorporation_test`
- `make verify-ground-truth`

## What Worked

- `ProperNoun("missa") * Verb("endub")` now renders `missa osendub`.
- `Noun("missa") * Verb("endub")` still renders `mixsa osendub`, preserving the
  regular phonetic cleanup contrast.
- The full current Araujo expression renders
  `domingo resé 'ara marãtekoabe'yma resebé missarendubi`.
- Multiword proper nouns keep internal `is`: `Luis Felipe` renders
  `Luis Felipe osendub`.

## What Failed

- The first engine-only patch did not work because Pydicate passed unannotated
  proper-noun strings into the Tupi verb engine during unannotated final renders.
  The fix needed both the engine preservation helper and a Pydicate handoff
  change for proper-noun subject/object strings.
- `make verify-ground-truth` failed before regeneration with:
  `source annotations differ from generated JSONL at record 74`. This reflects
  the active Araujo authoring drift already present in the source/JSONL pair,
  so ground truth was not regenerated as part of this fix.

## Remaining Questions

- Decide when the currently active Araujo record 74 and later source lines
  should be accepted into structured ground truth.
- The sibling `../nhe-enga` working tree still has unrelated `.DS_Store`
  modifications; they were not touched.

## Suggested Next Prompt

Review/accept the active Araujo source lines starting at record 74, then run
`make regenerate-ground-truth ARGS="--source araujo_catecismo_1686"` when those
lines are ready to enter structured ground truth.
