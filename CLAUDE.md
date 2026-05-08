# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Computational linguistics research project implementing Old Tupi language encoding and analysis (doctoral research, University of Sao Paulo / FFLCH). It encodes historic Old Tupi texts as compositional Pydicate expressions, validates them against ground truth, and generates corpus data for NLP/tokenizer experiments.

## Common Commands

```bash
make test                          # Run full test suite
make play                          # Open interactive REPL (playground.py)
make dict                          # Build dictionary artifacts
make serve-dict                    # Serve dictionary at localhost:8000 (PORT= to override)
make update-ground-truth           # Interactively update ground truth files
make lint                          # Format code with Black
make push                          # lint + test + git push
```

Run a subset of tests directly:
```bash
python3 tests/run_tests.py --skip-tokenizer        # skip slow tokenizer tests
python3 tests/run_tests.py --include-synthetic      # include synthetic sources
python3 tests/run_tests.py --tokenizer-verbose      # verbose tokenizer output
python3 tests/run_tests.py --timings                # show timing info
```

## Dependencies

There is no `requirements.txt`. The project depends on two **local sibling checkouts** that are injected into `sys.path` at runtime:
- `../nhe-enga/pydicate` — composable expression language (Pydicate DSL)
- `../nhe-enga/tupi` — Old Tupi language support library

Both must be present at those paths for anything to run.

## Architecture

### Data Flow

```
historic/*.tu.py sources
  → auto-discovered by historic/primary_sources.py
  → expressions rendered to strings
  → validated against ground_truth/historic/*.txt
  → tokenizer/build_corpus_json.py extracts corpus rows (tokenizer/output/corpus.jsonl)
  → tokenizer/rawgrammarpair.py builds stable morpheme/tag registries + training pairs
  → tokenizer/compile_to_dsl.py generates Pydicate DSL for reconstruction
  → dictionary/build_dict.py builds interactive static site (site/data/)
```

### Key Modules

- **`historic/`** — Historic source texts as `.tu.py` files. Each file exports a list named after its stem (e.g. `bettendorff_compendio.tu.py` exports `bettendorff_compendio`). `lexicon.tu.py` holds all POS-tagged lexicon entries. `primary_sources.py` auto-discovers and loads all `.tu.py` modules.

- **`synthetic/`** — Synthetic verb conjugation generators for training data. `verb_generator.py` generates indicativo/permissivo/imperativo forms; `primary_sources.py` exports the `verb()` generator.

- **`tests/`** — `run_tests.py` is the main runner. `ground_truth_cases.py` loads ground truth files and compares against rendered expressions. Ground truth text files live in `ground_truth/historic/` and `ground_truth/synthetic/`.

- **`tokenizer/`** — Corpus building pipeline. `build_corpus_json.py` → `rawgrammarpair.py` (stable M#/T#/S# registries) → `compile_to_dsl.py` (annotated string → morpheme AST → DSL). `viterbi.py` is an experimental Viterbi-based canonicalization baseline. Artifacts written to `tokenizer/output/`.

- **`dictionary/`** — Static dictionary site builder. `build_dict.py` is the entry point; `build_entries.py` generates lexicon entries with corpus attestations.

- **`site/`** — Single-page static dictionary app. `site/data/` holds generated JSON artifacts; gzipped versions are served in production.

- **`playground.py`** — Interactive REPL bootstrap; loads pydicate, tupi, lexicon, all sources, and helper functions.

### Source File Conventions

- Historic source files are `.tu.py` (preferred over `.py` for the same stem name).
- Each source file exports a list of expressions; `.tu.py` files that use the Pydicate DSL are auto-evaluated.
- All expressions must have an `.eval()` method returning a rendered string.
- Ground truth files are plain text, one rendered expression per line, named `<source_stem>.txt`.
