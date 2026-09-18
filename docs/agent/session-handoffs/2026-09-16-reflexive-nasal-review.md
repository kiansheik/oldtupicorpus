# Explicit nasal reflexive and reciprocal variants

## Goal

Define `nhe = îe.var(1)` and `nho = îo.var(1)`, then inventory existing
historic lines so the human editor can review their nasal choices.

## Files inspected

`historic/araujo_catecismo_1686.tu.py`,
`historic/bettendorff_compendio.tu.py`, `historic/lexicon.tu.py`,
`../nhe-enga/docs/agent/grammar-navigation.md`,
`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/{noun,verb}.py`,
`../nhe-enga/tupi/tupi/{tupi,verb}.py`, and related corpus tests.

## Files changed

`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/noun.py`,
`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py`,
`../nhe-enga/tupi/tupi/verb.py`,
`../nhe-enga/docs/agent/grammar-navigation.md`,
`../nhe-enga/AGENT_NOTES.md`,
`tests/reflexive_nasal_variation_test.py`,
`docs/agent/reflexive-nasal-review.md`, `docs/agent/current-state.md`,
`docs/agent/log.md`, and this handoff. No historic source expression or
ground-truth record was edited.

## Commands run

Targeted `rg` and source reads; MCP `render_candidate`,
`reload_engine`, `verify_ground_truth`, and `line_status`;
read-only AST candidate renders; focused unittest;
`make test ARGS="--skip-tokenizer"`; `git diff --check`.

## What worked

The standalone variants and direct finite and short nominal
compositions render `nhe`/`nho`. Default variants stay unchanged.
The review inventory maps 20 direct `îe` occurrences to records and
shows one-occurrence candidate surfaces, plus two indirect lexicon
uses. The focused test and 98-test suite pass; all 80 saved Araujo and
40 Bettendorff targets verify.

## What failed

In record 29 of both sources, an in-memory nasal substitution renders
`nhe` as a detached word and changes the remaining verb to
`oîmonhangyba'epûera`. A direct two-argument object adjustment did not
reach the nested construction and was reverted. A Python `py_compile`
attempt could not write bytecode into the sibling checkout under the
sandbox; the focused test imports the edited modules successfully.

## Remaining questions

The editor must decide which historic lines actually take the nasal
form. The record-29 composition needs a separate engine fix if selected.
Araujo records 81 and 82 remain unaccounted for separate editorial
reasons. Matching variants do not establish historical correctness.

## Suggested next prompt

Review one row of `docs/agent/reflexive-nasal-review.md` against its
witness and specify whether it should keep `îe` or use `nhe`.
