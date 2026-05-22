# Repo Map

## Root

- `README.md`: detailed project overview, workflows, source conventions, and
  tokenizer/dictionary command documentation.
- `CLAUDE.md`: compact agent-oriented overview that predates this wiki.
- `docs/xmlpage-stylization-guide.md`: Portuguese user guide for PAGE XML
  shorthand, inline formatting, footnotes, response marks, rendered examples,
  and the Transkribus export workflow for `scripts/xmlpage_to_html.py`.
- `docs/tokenizer-theory.md`: teaching document for the tokenizer/canonicalizer
  passes, ML assumptions, baselines, metrics, and current goals.
- `Makefile`: primary command surface for tests, REPL, dictionary builds,
  frontend build, and local dictionary serving.
- `primary_sources.py`: compatibility aggregator for historic and synthetic
  sources.
- `playground.py`: interactive REPL bootstrap.

## Historic Source System

- `historic/*.tu.py`: preferred source modules. Each source exports a list named
  after the filename stem.
- `historic/primary_sources.py`: central discovery registry for historic source
  modules.
- `historic/lexicon.tu.py`: shared lexicon and `load_lexicon()`.
- `historic/lexicon.py`: compatibility loader for the `.tu.py` lexicon.

Current checked-in historic sources include:

- `historic/araujo_catecismo_1686.tu.py`
- `historic/bettendorff_compendio.tu.py`

## Synthetic Sources

- `synthetic/primary_sources.py`: explicit export registry for synthetic data.
- `synthetic/verb_generator.py`: synthetic verb generation.
- `synthetic/verb_helpers.py`: helper logic for generated verb material.

## Ground Truth And Tests

- `ground_truth/historic/*.txt`: rendered historic reference lines.
- `ground_truth/synthetic/*.txt`: rendered synthetic reference lines.
- `tests/run_tests.py`: main runner and interactive ground-truth updater.
- `tests/ground_truth_cases.py`: source loading and ground-truth comparison.
- `tests/rendered_corpus_test.py`: rendered corpus, morpheme metadata, and
  syntax-span coverage.
- `tests/tooltip_overrides_test.py`: tooltip override store and request parsing.
- `tests/*_test.py`: standard unittest files discovered by the main runner.

## Tokenizer And DSL Pipeline

- `tokenizer/build_corpus_json.py`: emits corpus rows from source expressions.
- `tokenizer/rawgrammarpair.py`: builds stable token/tag/subtag registries and
  canonical input/output pairs.
- `tokenizer/compile_to_dsl.py`: compiles canonical streams into a DSL-like
  reconstruction format.
- `tokenizer/dsl_runtime.py`: runtime helpers for generated DSL output.
- `tokenizer/viterbi.py`: experimental canonicalizer baseline.
- `tokenizer/output/`: checked-in tokenizer artifacts. Treat as generated unless
  a task explicitly asks to update them.
- `tokenizer/notebooks/`: exploratory notebook material and notes.

## Dictionary Pipeline

- `dictionary/build_dict.py`: full dictionary data build entry point.
- `dictionary/build_rendered_corpus.py`: builds structured rendered corpus data.
- `dictionary/build_entries.py`: builds dictionary entries and attestations.
- `dictionary/utils.py`: shared artifact helpers, normalization, source iteration,
  morpheme metadata, and `syntax_spans`.
- `dictionary/navarro_import.py`: optional Navarro-derived supplemental entries.
- `dictionary/tooltip_overrides.py`: SQLite store for editable tooltip notes.
- `dictionary/serve_dict.py`: local static server plus tooltip API.

Generated dictionary artifacts are written to:

- `site/data/rendered_corpus.json`
- `site/data/rendered_corpus.json.gz`
- `site/data/dictionary_entries.json`
- `site/data/dictionary_entries.json.gz`

## Frontend

- `frontend/src/App.jsx`: main React UI for search, entry cards, attestations,
  annotation display, syntax spans, and tooltip editing.
- `frontend/src/lib.js`: data loading, search, URL settings, tooltip scope and
  override helpers, Navarro root lookup, and tooltip positioning.
- `frontend/src/styles.css`: dictionary site styling.
- `frontend/package.json`: Vite/React build scripts.
- `frontend/vite.config.js`: frontend build config.

Built frontend assets land in `site/` and `site/assets/`.

## Local State

- `var/tooltip_overrides.sqlite3`: default local tooltip note database. Treat as
  runtime local state, not source code.
