# `(m)` pluriform possession in Araujo record 81

## Goal

Make the unchanged Araujo record 81 expression render the editor's
`oemitymbûerypy pupé Tupã potabame'engi no` by fixing the `(m)` noun
rule in the engine.

## Files inspected

`historic/araujo_catecismo_1686.tu.py`, `historic/lexicon.tu.py`,
`../nhe-enga/docs/agent/grammar-navigation.md`,
`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/noun.py`,
`../nhe-enga/tupi/tupi/noun.py`, and related corpus tests.

## Files changed

`../nhe-enga/tupi/tupi/noun.py`,
`../nhe-enga/docs/agent/grammar-navigation.md`,
`../nhe-enga/AGENT_NOTES.md`, `tests/m_pluriform_possession_test.py`,
`docs/agent/current-state.md`, `docs/agent/log.md`, and this handoff.
The historic expression and generated ground truth were not edited.

## Commands run

MCP `get_source_context`, `search_lexicon`,
`search_rendered_expressions`, `render_candidate`, `reload_engine`,
`verify_ground_truth`, and `line_status`; targeted `rg` and source
reads; `python3 -B -m unittest tests.m_pluriform_possession_test`;
`make test ARGS="--skip-tokenizer"`; `git diff --check`.

## What worked

`Noun.pluriform_prefix` now chooses `m-` for absolute and `p-` for
possessed `(m)` nouns before other pluriform branches. `Noun.possessive`
does not force `r-` on `(m)` nouns with an explicit possessor. The
unchanged full expression renders the editor's target, with annotated
`p[PLURIFORM_PREFIX:P]` on the direct object. The focused test and
92-test corpus suite pass. MCP verification reports 80 saved Araujo and
40 Bettendorff targets matched. Record 81 alone is unaccounted.

## What failed

The first full-suite run hit a `RecursionError` in the new test because
it combined a module-level imported pronoun with a source file loaded
after the suite's engine reload test. Loading both from the same source
context fixed the test; the suite then passed.

## Remaining questions

The editor must review record 81 and use Commit ground truth to account
for it. A matching render does not independently establish the historical
analysis.

## Suggested next prompt

Review Araujo record 81's historical analysis and commit its ground
truth in the editor if accepted.
