# Navarro registry and named passage lexemes

## Goal

Provide a safe corpus-side boundary for the generated Navarro inventory and
make it mechanically enforceable that historic passage trees refer to named
lexicon variables instead of embedding raw Pydicate lexical constructors.

## Files inspected

- `AGENTS.md`
- `docs/agent/{index,current-state,repo-map,open-questions,log}.md`
- `historic/lexicon.tu.py`
- `historic/lexicon.py`
- `historic/araujo_catecismo_1686.tu.py`
- `historic/bettendorff_compendio.tu.py`
- `authoring/source_annotations.py`
- `tests/run_tests.py`
- `Makefile`
- Sibling Pydicate constructor definitions and Studio constructor/publication
  adapters, read only to match the existing 13-constructor contract.

## Files changed

- Added `historic/navarro_lexicon.py`.
- Imported `navarro_lexeme` in `historic/lexicon.tu.py`.
- Added `authoring/lexical_variables.py` and
  `scripts/check_historic_lexical_variables.py`.
- Added `tests/navarro_lexicon_test.py` and
  `tests/lexical_variables_test.py`.
- Added `make check-lexical-variables` in `Makefile`.
- Updated `docs/agent/current-state.md`, `docs/agent/log.md`, and
  `docs/agent/repo-map.md`.

Existing changes in the Araujo source, shared lexicon, ground truth, and
tokenizer outputs predated this task and were preserved. The only intentional
overlap in the already-dirty shared lexicon is the single import of
`navarro_lexeme`.

## Commands run

- `python3 -m unittest tests.navarro_lexicon_test tests.lexical_variables_test`
- `python3 scripts/check_historic_lexical_variables.py`
- `python3 tests/run_tests.py --skip-tokenizer`
- A read-only two-load probe of `historic.lexicon.load_lexicon()`.
- A full temporary-registry probe of `load_navarro_registry()` and
  `navarro_lexeme()` by ID and stable name.
- `PYTHONPYCACHEPREFIX=/tmp/oldtupicorpus-navarro-pycache python3 -m
  py_compile ...` for the five added Python modules/tests.
- `git diff --check`, `git diff --stat`, and targeted `git diff`/`git status`.
- `python3 -m black --check ...` was attempted but Black is not installed in
  this interpreter.

## What worked

- Schema version, source fingerprint, canonical coverage fields and their key
  invariants, constructor distributions, unresolved records, entry identity,
  and shared/dictionary-only status accounting are validated before lookup.
- Registry constructor values accept only JSON scalar/null data and must bind to
  one of the explicit Pydicate constructor signatures. No `eval` or contributor
  source execution is used.
- Top-level entry headwords and definitions must exactly match the keyword
  values used to construct the runtime predicate.
- Lookup works by `registry_id` or stable `name`; duplicate and cross-namespace
  identifiers are rejected. Each call constructs a separate mutable predicate.
- The current historic sources pass the AST-only rule with zero direct lexical
  constructor calls. The regression fixture detects violations in both passage
  expressions and source-local helper assignments while leaving grammatical
  helpers such as `cop()`, `v()`, and `n()` valid. Constructor-class aliases,
  qualified constructor attributes and explicit import aliases are rejected too.
- The final focused suite ran 10 tests and the full no-tokenizer suite ran 112;
  both passed.
- The installed Studio registry passed validation with 7,197 entries, 1,109
  unique unresolved rows, 20 exact shared declarations, and 7,177
  dictionary-only entries. A sampled dictionary-only demonstrative
  resolved by ID and name to distinct objects with the expected headword.

## What failed

- The first focused run exposed that importing the resolver directly did not
  establish the sibling development paths. The resolver now mirrors the shared
  lexicon's local Pydicate/Tupi path setup.
- The first bad-fixture assertion used line numbers one line too high; the
  expected physical source lines were corrected.
- Black was unavailable, so no repository-wide formatting command was run.
- A first `py_compile` attempt could not write a bytecode cache in the sibling
  repository under the managed filesystem. Re-running with its cache under
  `/tmp` passed.

## Remaining questions

- The canonical `historic/navarro_lexicon.json` is installed and reproduced
  byte for byte after installation. It is 10,811,309 bytes with SHA-256
  `3d0a85cf7d496d1fcf665ed0722da2e49c4cadbf401e931abfa2893f24aa9a2e`.
- Three explicitly verbal Navarro rows remain unresolved because their headers
  do not state a safe transitivity/class value; 1,105 other headers remain
  unclassified and one source row remains malformed.
- Tokenizer regeneration was intentionally skipped because neither passage
  expressions nor rendering behavior changed.

## Suggested next prompt

Exercise one dictionary-only Studio publication end to end: add the stable
`navarro_lexeme(...)` declaration, use its variable in a temporary passage, and
verify that no raw constructor remains in the published passage AST.
