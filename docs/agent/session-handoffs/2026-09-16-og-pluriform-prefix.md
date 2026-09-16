# Referential `og` before a pluriform noun

## Goal

Fix the grammar engine so the unchanged expression for Araujo record 74
renders the human-approved form without an absolute `t-` between `og` and
`apixara`.

## Files inspected

`historic/araujo_catecismo_1686.tu.py`, `historic/lexicon.tu.py`,
`ground_truth/records/historic/araujo_catecismo_1686.jsonl`,
`../nhe-enga/{AGENTS.md,AGENT_NOTES.md,docs/agent/grammar-navigation.md}`,
`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/noun.py`,
`../nhe-enga/tupi/tupi/noun.py`, and authoring service and CLI code.

## Files changed

`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/noun.py`,
`../nhe-enga/docs/agent/grammar-navigation.md`,
`../nhe-enga/AGENT_NOTES.md`, `tests/og_pluriform_prefix_test.py`,
`docs/agent/current-state.md`, `docs/agent/log.md`, and this handoff.
The historic source expression and generated ground truth were not changed.

## Commands run

`python3 -B -m unittest tests.og_pluriform_prefix_test`,
`make test ARGS="--skip-tokenizer"`, `make verify-ground-truth`,
`git diff --check`, and fresh-process `render_candidate`,
`verify_ground_truth`, and `line_status` calls through
`authoring.mcp_server.handle_request`.

## What worked

The exact expression `((îabé * (+asé * aûsub * îe)) + n((asé * aûsub) *
(og * apixara)) + no)` now renders
`oîeaûsuba îabé asé oapixararaûsuba no`.
The annotated output has `o[PRONOUN:MAIN_CLAUSE_SUBJECT:3p]apixar` with
no absolute `t-`. All saved targets still match: Araujo 73/73 and
Bettendorff 40/40. Across both historic sources, only Araujo record 74
changed. The focused regression and the corpus test suite pass.

## What failed

The long-running authoring MCP process retained the old grammar module;
a fresh MCP server process supplied the current rendering. The CLI
`make verify-ground-truth` fails because Araujo source records 74–77 exist
after the last generated JSONL record, 73. This predates the engine edit.
Regenerating would also accept three unrelated unreviewed lines, so the
generated artifact was left untouched.

## Remaining questions

The human editor must review Araujo records 75–77 before extending the
generated JSONL. A matching render for record 74 is engine validation,
not independent confirmation of its historical analysis.

## Suggested next prompt

Review the remaining unaccounted Araujo records 75–77 one at a time,
approve their analyses and targets, then regenerate and verify ground truth.
