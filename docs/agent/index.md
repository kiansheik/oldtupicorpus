# Agent Wiki

This directory is the repo-local operating context for future coding agents.
Code, tests, checked-in configs, and schemas remain the source of truth. These
notes are compiled memory: trust the code first, then update these docs when
the docs drift.

## Start Here

Read these files before editing:

1. `docs/agent/index.md`
2. `docs/agent/current-state.md`
3. `docs/agent/repo-map.md`
4. `docs/agent/open-questions.md`

For substantial work, finish by updating:

1. `docs/agent/current-state.md`
2. `docs/agent/log.md`
3. A new file under `docs/agent/session-handoffs/`

## Project Shape

`oldtupicorpus` encodes Old Tupi source material as compositional Python/Pydicate
expressions, validates rendered text against ground truth, and derives tokenizer,
DSL, and dictionary-site artifacts from those sources.

The main current user-facing surface is the static dictionary site:

- Python build steps write structured artifacts into `site/data/`.
- The React/Vite frontend consumes those artifacts from `frontend/src/`.
- `make serve-dict` builds data, builds the frontend, and serves `site/` with a
  local SQLite-backed tooltip API.

## Working Rules

- Prefer small, reviewable diffs.
- Do not edit generated artifacts unless the user explicitly asks for it.
- Do not run destructive commands without explicit approval.
- Use `rg`, `git grep`, `find`, and targeted reads before opening large files.
- Reuse the structured artifact flow before adding new raw-string parsing.
- Run the narrowest useful checks for the touched area.

## Common Commands

```bash
make test
make test ARGS="--skip-tokenizer"
make dict
make frontend-build
make serve-dict
python3 -m unittest tests.rendered_corpus_test
python3 -m unittest tests.tooltip_overrides_test tests.rendered_corpus_test
python3 tests/run_tests.py
```

`make serve-dict` defaults to `HOST=0.0.0.0`, `PORT=8000`, and
`TOOLTIP_DB=var/tooltip_overrides.sqlite3`. Use `HOST=127.0.0.1` for local-only
serving.

