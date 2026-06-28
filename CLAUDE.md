# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository. `AGENTS.md` contains the binding human-approval and write-boundary rules. Read it before editing source, target, or morphology behavior.

## Project overview

Computational linguistics research project implementing Old Tupi language encoding and analysis (doctoral research, University of São Paulo / FFLCH). It encodes historic Old Tupi texts as compositional Pydicate expressions, validates them against human-approved targets, and generates corpus data for NLP/tokenizer experiments.

## Required authoring behavior

- Start source work from a record id and use the `oldtupi-authoring` MCP tools before proposing an expression.
- Use `get_source_context`, `search_lexicon`, `search_rendered_expressions`, and `render_candidate` before editing.
- A rendered match is not proof of a historical analysis.
- Do not replace an approved target with current renderer output merely to pass a check.
- Do not modify `nhe-enga` until the human has approved the analysis and an expression-level solution is impossible.
- Read `historic/AGENTS.md` and `docs/agent/source-authoring.md` for line-authoring details.

## Common commands

```bash
make test                                      # Run full test suite
make test ARGS="--skip-tokenizer"              # Run focused test suite without tokenizer regeneration
make verify-ground-truth                       # Compare renderings to approved targets, no writes
make review-ground-truth                       # Human-approve new trailing targets into JSONL and text mirror
make migrate-ground-truth-records              # Create structured JSONL records from legacy text
make play                                      # Open interactive REPL
make dict                                      # Build dictionary artifacts
make serve-dict                                # Serve dictionary at localhost:8000
make lint                                      # Format code with Black
```

## Dependencies

There is no `requirements.txt`. The project depends on two local sibling checkouts injected into `sys.path` at runtime:

- `../nhe-enga/pydicate` for the composable expression language
- `../nhe-enga/tupi` for Old Tupi language support

Both must be present at those paths for corpus execution.

## Architecture

```text
historic/*.tu.py sources
  -> auto-discovered by historic/primary_sources.py
  -> expressions rendered to strings
  -> validated against ground_truth/records/<kind>/*.jsonl when present
  -> legacy ground_truth/<kind>/*.txt remains a compatibility mirror
  -> tokenizer/build_corpus_json.py extracts corpus rows
  -> tokenizer/rawgrammarpair.py builds canonical registries and training pairs
  -> tokenizer/compile_to_dsl.py generates Pydicate DSL for reconstruction
  -> dictionary/build_dict.py builds the static dictionary site
```

## Key modules

- `historic/` contains historic `.tu.py` source texts and `lexicon.tu.py`.
- `authoring/` owns structured records, safe candidate rendering, source verification, the authoring CLI, and the local MCP server.
- `ground_truth/records/` is the canonical structured target location when a source has been migrated.
- `tests/ground_truth_cases.py` supports both structured JSONL and legacy text targets.
- `tokenizer/` and `dictionary/` consume executable source expressions, not agent-produced prose.

## Source file conventions

- Historic sources export a list named after the file stem.
- Every expression must expose `.eval()` and render to a string.
- Preserve positional correspondence between the expression list and source records.
- Keep source edits narrow, testable, and traceable to an approved record id.
