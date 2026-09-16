# Raw number nominalization and adjuncts

## Goal

Fix the grammar engine so the unchanged Araujo record 80 expression
renders the human editor's `opakombó îabi'õ Tupã supé oîepé asé mba'e
moîa'oka`, ignoring whitespace differences.

## Files inspected

`historic/araujo_catecismo_1686.tu.py`, `historic/lexicon.tu.py`,
`ground_truth/records/historic/araujo_catecismo_1686.jsonl`,
`../nhe-enga/docs/agent/grammar-navigation.md`,
`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/{number,noun,adverb,postposition}.py`,
`../nhe-enga/pydicate/pydicate/predicate.py`, and relevant tests and
agent context pages.

## Files changed

`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/number.py`,
`../nhe-enga/docs/agent/grammar-navigation.md`,
`../nhe-enga/AGENT_NOTES.md`, `tests/number_nominalization_test.py`,
`docs/agent/current-state.md`, `docs/agent/log.md`, and this handoff.
The historic expression and generated JSONL were not edited.

## Commands run

MCP `get_source_context`, `search_lexicon`, `search_rendered_expressions`,
`render_candidate`, `reload_engine`, `verify_ground_truth`, and
`line_status`; targeted `rg` and code reads; in-memory rule simulation;
`python3 -B -m unittest tests.number_nominalization_test`;
`make test ARGS="--skip-tokenizer"`; `git diff --check`.

## What worked

`Number.base_nominal` allows a raw number to serve as a noun without
changing its surface. `Number.preval` now includes pre- and
post-adjuncts; the pre-adjuncts appear in reverse attachment order.
Record 80 renders `opakombó îabi'õ Tupã supé oîepé asé
mba'emoîa'oka`, matching the editor's form after removing whitespace.
The MCP all-source check reports 79 verified Araujo and 40 verified
Bettendorff targets, with only record 80 unaccounted.

## What failed

Before the engine change, the Araujo source could not load because
`Number` had no `base_nominal` method. Nominalization alone in an
in-memory simulation still lost the preceding phrases because
`Number.preval` ignored attached adjuncts.

## Remaining questions

Record 80 needs human editorial review and the editor's Commit ground
truth action. The matching render does not independently establish the
historical analysis.

## Suggested next prompt

After reviewing record 80 in the editor, use Commit ground truth for
that line and rerun all-source verification.
