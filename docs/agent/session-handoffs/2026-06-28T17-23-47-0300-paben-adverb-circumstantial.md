# Pabẽ Adverb Circumstantial

## Goal

Encode the next Araujo line `nã e'iba'e pupé pabẽ aîpoba'e ruî` so `pabẽ`
acts as an all/completely particle-adverb, and so `ruî` comes from the
circumstantial form of `îub` rather than a bare string.

## Files Inspected

- `docs/agent/index.md`
- `docs/agent/current-state.md`
- `docs/agent/repo-map.md`
- `docs/agent/open-questions.md`
- `docs/agent/source-authoring.md`
- `historic/AGENTS.md`
- `historic/lexicon.tu.py`
- `historic/araujo_catecismo_1686.tu.py`
- `ground_truth/records/historic/araujo_catecismo_1686.jsonl`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/adverb.py`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/noun.py`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`
- `../nhe-enga/tupi/tupi/verb.py`

## Files Changed

- `historic/lexicon.tu.py`
- `historic/araujo_catecismo_1686.tu.py`
- `tests/paben_adverb_test.py`
- `ground_truth/records/historic/araujo_catecismo_1686.jsonl`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-06-28T17-23-47-0300-paben-adverb-circumstantial.md`

## Commands Run

- `rg -n "paben|pabẽ|pab˜e|îub|aîpó|aîpo" historic tests ground_truth/records -S`
- `python3 -c "... render_candidate('araujo_catecismo_1686', ...)"` for
  `nã + ((bae * ei) * pupé) + (paben + (aîpo * îub))`
- `python3 -m unittest tests.paben_adverb_test`
- `make regenerate-ground-truth ARGS="--source araujo_catecismo_1686"`
- `make verify-ground-truth`
- `make test ARGS="--skip-tokenizer"`

## What Worked

- `historic/lexicon.tu.py` now shadows the imported `paben` with
  `Adverb("pabẽ", tag="[ADVERB:ALL]")`.
- Preposed `paben` now naturally triggers circumstantial mood through the
  existing `Verb.indicative()` adverb check:
  `paben + (aîpo * îub)` renders `pabẽ aîpoba'e ruî`.
- Existing postposed all-quantifier surfaces are preserved:
  `(bae * ikobé) + (pûera * (bae * manõ)) + paben` still renders
  `oîkobeba'e omanõba'epûera pabẽ`.
- Araujo record `araujo_catecismo_1686:0072` was regenerated as
  `nã e'iba'e pupé pabẽ aîpoba'e ruî`.

## What Failed

- A direct import probe using `historic.araujo_catecismo_1686` failed because
  `.tu.py` sources are loaded by the repo source loader, not as normal Python
  modules under that name. The candidate was rendered through
  `authoring.service.render_candidate` instead.

## Remaining Questions

- `paben` remains modeled locally in `oldtupicorpus` rather than changing the
  sibling `nhe-enga` POS definition. A shared-library change would need its own
  historic contrast and focused regression in that repository.

## Suggested Next Prompt

Continue Araujo from record 72, using `paben` for adverbial all-quantifier
contexts and checking whether each new `pabẽ` is the particle/adverb or the
postposition "with".
