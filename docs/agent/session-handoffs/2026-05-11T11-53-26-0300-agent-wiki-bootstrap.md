# Handoff: Agent Wiki Bootstrap

## Goal

Create the repo-local agent documentation structure under `docs/agent/` after
the user asked to fill out `docs/` for future agents.

## Files Inspected

- `README.md`
- `CLAUDE.md`
- `Makefile`
- `tests/run_tests.py`
- `tests/rendered_corpus_test.py`
- `tests/tooltip_overrides_test.py`
- `dictionary/build_dict.py`
- `dictionary/build_rendered_corpus.py`
- `dictionary/build_entries.py`
- `dictionary/utils.py`
- `dictionary/serve_dict.py`
- `dictionary/tooltip_overrides.py`
- `historic/primary_sources.py`
- `frontend/package.json`
- `frontend/src/App.jsx`
- `frontend/src/lib.js`
- Prior oldtupicorpus workflow memory

## Files Changed

- `docs/agent/index.md`
- `docs/agent/current-state.md`
- `docs/agent/repo-map.md`
- `docs/agent/open-questions.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-05-11T11-53-26-0300-agent-wiki-bootstrap.md`

## Commands Run

```bash
mkdir -p docs
ls -ld docs
pwd
find docs -maxdepth 3 -type f -print
rg --files -g '!*__pycache__*' -g '!site/output/**' -g '!node_modules/**'
git status --short
rg -n "oldtupicorpus|Dictionary pipeline|tooltip|syntax_spans|serve-dict" /Users/kian/.codex/memories/MEMORY.md
nl -ba /Users/kian/.codex/memories/MEMORY.md | sed -n '1434,1492p'
sed -n '1,220p' /Users/kian/.codex/memories/skills/oldtupicorpus-dictionary-workflow/SKILL.md
sed -n '1,220p' README.md
sed -n '1,220p' Makefile
sed -n '1,220p' CLAUDE.md
find . -maxdepth 2 -type d -not -path './.git*' -not -path './frontend/node_modules*' -not -path './site/output*' -print
sed -n '1,240p' tests/run_tests.py
sed -n '1,220p' dictionary/build_dict.py
sed -n '1,220p' dictionary/serve_dict.py
sed -n '1,220p' dictionary/tooltip_overrides.py
cat frontend/package.json
sed -n '1,260p' frontend/src/lib.js
sed -n '1,260p' frontend/src/App.jsx
sed -n '1,260p' dictionary/utils.py
sed -n '1,220p' dictionary/build_rendered_corpus.py
sed -n '1,220p' dictionary/build_entries.py
sed -n '1,220p' historic/primary_sources.py
rg -n "def main|def run|subprocess|rawgrammarpair|build_corpus_json|compile_to_dsl|load_ground_truth_cases|discover" tests/run_tests.py
rg -n "function App|function AnnotatedDisplay|function assignSyntaxRows|syntax_spans|tooltip|searchEntries|topEntries" frontend/src/App.jsx frontend/src/lib.js
rg -n "def build_annotated|syntax_spans|source_sort_key|DEEPEST_NODE|write_json_artifact|iter_historic_sources|load_lexicon|load_navarro" dictionary tokenizer historic synthetic tests | head -n 80
sed -n '340,560p' tests/run_tests.py
sed -n '260,920p' frontend/src/lib.js
sed -n '300,470p' dictionary/utils.py
sed -n '1,160p' tests/rendered_corpus_test.py
sed -n '1,180p' tests/tooltip_overrides_test.py
date +%Y-%m-%dT%H-%M-%S%z
mkdir -p docs/agent/session-handoffs
find docs/agent -maxdepth 3 -type f -print
git diff -- docs/agent
git status --short
rg -n "^#|^##|Goal|Files Inspected|Files Changed|Commands Run|What Worked|What Failed|Remaining Questions|Suggested Next Prompt" docs/agent
sed -n '1,220p' docs/agent/index.md
sed -n '1,260p' docs/agent/session-handoffs/2026-05-11T11-53-26-0300-agent-wiki-bootstrap.md
```

## What Worked

- `docs/` already existed after the first setup step.
- The repo had enough local documentation and source structure to build a useful
  agent wiki without guessing.
- Prior workflow memory aligned with the current code shape around dictionary
  artifacts, tooltip overrides, syntax spans, and `make serve-dict`.

## What Failed

- No command failures.
- Tests were not run because this was a documentation-only bootstrap.

## Remaining Questions

- Decide whether future agents should update `CLAUDE.md` alongside
  `docs/agent/`, or treat this wiki as the primary handoff surface.
- Clarify when generated tokenizer and dictionary artifacts should be committed.
- Clarify whether UI-only work requires the full tokenizer-regenerating test
  gate or a narrower frontend/Python check.

## Suggested Next Prompt

Use the new `docs/agent/` wiki as the startup context, then inspect the exact
files for the next code or corpus change before editing.
