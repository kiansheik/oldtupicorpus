# Explicit `mbo-` variation of `mo-`

## Goal

Make the unchanged Araujo record 82 expression render the editor's
`i karaíba pupé îemboîasuka` while preserving approved `mo-` forms.

## Files inspected

`historic/araujo_catecismo_1686.tu.py`, `historic/lexicon.tu.py`,
saved Araujo and Bettendorff targets,
`../nhe-enga/docs/agent/grammar-navigation.md`,
`../nhe-enga/pydicate/pydicate/predicate.py` (`Predicate.var`), and
`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`.

## Files changed

`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`,
`../nhe-enga/docs/agent/grammar-navigation.md`,
`../nhe-enga/AGENT_NOTES.md`, `historic/lexicon.tu.py`,
`tests/mo_mbo_variation_test.py`, `docs/agent/current-state.md`,
`docs/agent/log.md`, and this handoff. The historic source expression
and generated ground truth were not edited.

## Commands run

MCP `get_source_context`, `search_lexicon`,
`search_rendered_expressions`, `render_candidate`, `reload_engine`,
`verify_ground_truth`, and `line_status`; targeted `rg` and source
reads; `python3 -B -m unittest tests.mo_mbo_variation_test`;
`make test ARGS="--skip-tokenizer"`; `git diff --check`.

## What worked

`mbo = mo.var(1)` selects `mbo-` on the bare augmentor and when
composed with a verb. The shared `moîasuk` helper uses `mbo`; the
unchanged full record renders the editor's target. Approved `mo-`
constructions with nonnasal roots remain unchanged. The focused test
and 95-test corpus suite pass. MCP reports all 80 saved Araujo and
40 Bettendorff targets matched.

## What failed

A blanket nonnasal-root rule conflicts with approved `mo * îaok` and
`mo * (ar / ukar)` forms, so the editor chose explicit variation.

## Remaining questions

Araujo records 81 and 82 are unaccounted. The human editor must review
and commit their ground truth if accepted. The matching render does not
independently establish the historical analysis.

## Suggested next prompt

Review Araujo record 82 in the editor and use Commit ground truth if its
analysis and surface are accepted.
