# Noun-object incorporation in Araujo record 81

## Goal

Represent the editor's `potame'enga` analysis as an incorporated-object verb,
with Tupã as possessor of `(m)` `potaba`, while preserving the existing `/`
sound changes and other historic renderings.

## Files inspected

- `historic/araujo_catecismo_1686.tu.py`, `historic/lexicon.tu.py`,
  `tests/m_pluriform_possession_test.py`, and corpus authoring docs.
- Sibling `pydicate/pydicate/predicate.py`, `pos/noun.py`, `pos/verb.py`,
  `tupi/tupi/noun.py`, grammar-navigation map, and engine rules.
- Navarro-derived `me'eng` entry in `../nhe-enga/tests/cases.csv`; the
  historical fifth-commandment witness and Portuguese translation.

## Files changed

- Araujo record 81 expression and its corpus regressions.
- Sibling `pos/noun.py`, `pos/verb.py`, engine regression,
  `docs/agent/grammar-navigation.md`, and `AGENT_NOTES.md`.
- Corpus `docs/agent/current-state.md`, `log.md`, and this handoff.

## Commands run

- Focused `python3 -m unittest` suites in both repositories.
- `make test ARGS='--skip-tokenizer'` (102 tests).
- MCP `reload_engine`, `render_candidate`, `verify_ground_truth`, and
  `line_status` for both historic sources.

## What worked

- `(potaba / meeng).base_nominal()` gives `motame'enga`; the possessed
  `.var(1)` with Tupã gives `Tupã potame'enga`. The complete edited line
  gives `oemitymbûerypy pupé Tupã potame'enga no`.
- The annotation identifies the incorporated noun boundary, its `p-`
  pluriform prefix, and Tupã's possessor/object role. A second argument
  remains the object when a subject is also supplied.
- All 80 saved Araujo and 40 saved Bettendorff targets still verify.

## What failed

- Before the engine edit, `potaba / meeng` was a noun, so `.var(1)` did
  not encode argument roles. An initial nominal implementation placed Tupã
  before the preceding postpositional phrase; `IncorporatedVerbNominal`
  corrected adjunct order.
- `make regenerate-ground-truth` was not run: it would also record the
  unreviewed Araujo record 82. The generated JSONL still ends at record 80.

## Remaining questions

- The historical witness spells `Tupã potâ meengano`; the match to the
  editor's normalized nominal form does not prove incorporation.
- The editor's per-line Commit ground truth action is needed to approve
  record 81 without also approving record 82.

## Suggested next prompt

Review record 81's annotated `Tupã potame'enga`, then commit only that
record's ground truth in the editor. Investigate record 82 separately.
