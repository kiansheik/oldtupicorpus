# Ase Aûsub Commandment

## Goal

Encode the next Araujo line:
`opakatu mba'e tetiruã asé saûsuba sosé asé Tupã raûsuba`.

## Files Inspected

- `historic/araujo_catecismo_1686.tu.py`
- `historic/lexicon.tu.py`
- `ground_truth/records/historic/araujo_catecismo_1686.jsonl`
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/postposition.py`

## Files Changed

- `historic/lexicon.tu.py`
- `historic/araujo_catecismo_1686.tu.py`
- `ground_truth/records/historic/araujo_catecismo_1686.jsonl`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-06-28T17-31-18-0300-ase-ausub-commandment.md`

## Commands Run

- `python3 -c "... get_source_context('araujo_catecismo_1686', 72, radius=5)"`
- `rg -n "opakatu|tetiruã|a[uû]sub|sa[uû]sub|ra[uû]sub|sosé|Tupã|tupan|mbae|mba'e" historic tests ground_truth/records -S`
- `python3 -c "... render_candidate('araujo_catecismo_1686', ...)"`
- `make regenerate-ground-truth ARGS="--source araujo_catecismo_1686"`
- `make verify-ground-truth`
- `python3 -m unittest tests.paben_adverb_test`
- `make test ARGS="--skip-tokenizer"`

## What Worked

- Added `aûsub = love` as a source-authoring alias for the existing
  `Verb("aûsub")`.
- The user-corrected subexpression `asé * aûsub * +ae`, nominalized as
  `(asé * aûsub * +ae).base_nominal()`, renders `asé saûsuba`.
- `asé * (tupan * aûsub.base_nominal())` renders `asé Tupã raûsuba`.
- The full source expression renders exactly:
  `opakatu mba'e tetiruã asé saûsuba sosé asé Tupã raûsuba`.
- Regenerated Araujo JSONL now includes `araujo_catecismo_1686:0073`.

## What Failed

- No verification failures. One broad `rg` over sibling nhe-enga paths was noisy
  because it included generated/transpiled output; future searches should keep
  tighter path or glob constraints.

## Remaining Questions

- None for this line.

## Suggested Next Prompt

Continue after Araujo record 73 and check whether the existing `# new numbers`
marker is intended as the next subsection/transition marker before adding the
next expression.
