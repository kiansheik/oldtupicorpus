# `emi` with nasal `tym` and referential `og`

## Goal

Make `og * (emi * tym)` render `oemityma` through the grammar engine.
No historic source expression was edited.

## Files inspected

`../nhe-enga/docs/agent/grammar-navigation.md`,
`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/{deverbal,noun}.py`,
`../nhe-enga/tupi/tupi/{noun,tupi}.py`,
`historic/lexicon.tu.py`, related historic `emi` uses, and corpus tests.

## Files changed

`../nhe-enga/tupi/tupi/noun.py`,
`../nhe-enga/pydicate/pydicate/lang/tupilang/pos/deverbal.py`,
`../nhe-enga/docs/agent/grammar-navigation.md`,
`../nhe-enga/AGENT_NOTES.md`, `tests/emi_referential_test.py`,
`docs/agent/current-state.md`, `docs/agent/log.md`, and this handoff.

## Commands run

MCP `reload_engine`, `render_candidate`, `verify_ground_truth`, and
`line_status`; targeted `rg` and source reads;
`python3 -B -m unittest tests.emi_referential_test`;
`make test ARGS="--skip-tokenizer"`; `git diff --check`.

## What worked

`TupiNoun.emi()` now retains `emi-` when an initial `t` stem already
contains a nasal. `emi_morphology()` uses the attached referential
pronoun in place of the derived noun's absolute `t-`. The requested
expression renders `oemityma`; `emi * tym` renders `temityma`, and
`nde * (emi * tym)` renders `nde remityma`. MCP verification found all
79 saved Araujo and 40 Bettendorff targets unchanged. The focused
test and 89-test corpus suite pass.

## What failed

The first draft of the referential possessor branch fell through to a
`None` possessor and raised an exception. The conditional was corrected
before final verification.

## Remaining questions

The editor added Araujo record 81, using `og * (emi * tym)`, during this
work. It renders `oemityma pupé Tupã rotabame'engi no` and remains
unaccounted; a matching render does not establish the historical analysis.
The same referential behavior for other kinds of deverbal noun may need
separate investigation. Araujo records 80 and 81 await the human editor's
Commit ground truth action.

## Suggested next prompt

Review other deverbal classes with `og` and an absolute pluriform
prefix, using annotated renderings and approved historic contrasts.
