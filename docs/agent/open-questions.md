# Open Questions

Last updated: 2026-05-11

## Product And Workflow

- Should `docs/agent/` eventually replace overlapping parts of `CLAUDE.md`, or
  should both be kept in sync indefinitely?
- Which generated artifacts are intentionally committed after normal work?
  Current guidance is to avoid editing generated outputs unless the user asks.
- Should dictionary/frontend work always end with the full
  `python3 tests/run_tests.py` gate, or is `--skip-tokenizer` acceptable for
  purely UI-only changes?
- For tokenizer experiments, should dev/test splitting group related
  orthographic variants and synthetic families together to avoid optimistic
  metrics?

## Dictionary Site

- The optional Navarro import depends on the sibling `../nhe-enga` checkout.
  Confirm expected local path behavior before changing it.
- Tooltip form-specific notes currently use the legacy
  `ROOT_MORPHEME:<form>` prefix. Preserve compatibility unless the user asks for
  a migration.
- `dictionary/serve_dict.py` defaults its CLI host to `127.0.0.1`, while
  `make serve-dict` passes `HOST=0.0.0.0`. Keep both contexts clear in docs and
  command output.

## Corpus And Language Data

- Historic source authoring conventions are clear, but individual linguistic
  analyses should come from the user or source files. Do not invent analyses.
- When ground truth and rendered source output differ, use the mismatch output to
  identify whether the source expression or ground truth should change.
- The current notebook snapshot is heavily synthetic. Decide which metrics should
  be tracked specifically on historic rows when evaluating tokenizer progress.
