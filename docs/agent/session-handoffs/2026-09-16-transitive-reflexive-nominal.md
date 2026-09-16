# Transitive reflexive nominal variation

## Goal

Make the human editor's revised Araujo record 79 expression render
`Santa Madre Igreja îekuakupûaîa îabi'õ îekuakuba` by fixing the
one-argument transitive reflexive nominal path.

## Files inspected

`historic/araujo_catecismo_1686.tu.py`,
`ground_truth/records/historic/araujo_catecismo_1686.jsonl`,
`docs/agent/{index,current-state,repo-map,open-questions,source-authoring}.md`,
`../nhe-enga/{AGENTS.md,AGENT_NOTES.md,docs/agent/grammar-navigation.md}`,
`../nhe-enga/pydicate/pydicate/{predicate.py,lang/tupilang/pos/verb.py}`,
and `../nhe-enga/tupi/tupi/verb.py`.

## Files changed

`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`,
`../nhe-enga/docs/agent/grammar-navigation.md`,
`../nhe-enga/AGENT_NOTES.md`,
`tests/reflexive_nominal_variation_test.py`,
`docs/agent/current-state.md`, `docs/agent/log.md`, and this handoff.
The source expression was already revised by the human editor before
the engine edit; this task did not change it or generated JSONL.

## Commands run

MCP `get_source_context`, `search_lexicon`, `search_rendered_expressions`,
`render_candidate`, `reload_engine`, `verify_ground_truth`, and
`line_status`; targeted `rg` and source reads; read-only in-memory corpus
comparison; `python3 -B -m unittest tests.reflexive_nominal_variation_test`;
`make test ARGS="--skip-tokenizer"`; `git diff --check`.

## What worked

The editor's first-clause rewrite removed the spurious `oîo` without an
engine change. The narrow engine rule lets a transitive verb with one
`îe` or `îo` argument use intransitive-style nominal variation 1. The
exact record-79 expression now renders the agreed target. The MCP
all-source check finds no mismatch among 78 saved Araujo and 40 saved
Bettendorff targets. Record 79 remains unaccounted, ready for the
human editor's Commit ground truth action.

## What failed

Applying intransitive treatment to every one-argument transitive
reflexive in a read-only simulation changed approved record 23 in both
historic sources. The implemented rule is limited to variation 1.

## Remaining questions

Whether other nominal variations of one-argument transitive reflexives
should share the intransitive behavior requires separate linguistic
review. A matching render does not prove the historical analysis.

## Suggested next prompt

After human review, use the editor's Commit ground truth action for
Araujo record 79 and verify the saved target.
