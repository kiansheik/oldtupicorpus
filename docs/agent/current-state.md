# Current State

Last updated: 2026-05-22

## Repo State

- `docs/agent/` now exists as the repo-local agent wiki.
- `docs/tokenizer-theory.md` now exists as a teaching document for the current
  tokenizer/canonicalizer and notebook ML pipeline.
- Existing working tree had unrelated modified files before this documentation
  bootstrap: `.gitignore`, `tokenizer/morph_poc_utils.py`,
  `tokenizer/notebooks/README.md`, and `tokenizer/notebooks/morph_tokenizer_poc.ipynb`.
  Do not revert those unless the user explicitly asks.
- At this update, `git status --short` also showed modified tokenizer output
  files: `tokenizer/output/annotated_token_pairs.json`,
  `tokenizer/output/canonical_io.jsonl`, `tokenizer/output/corpus.jsonl`, and
  `tokenizer/output/morph_dataset_meta.json`. Treat them as user/local generated
  state unless the task explicitly targets them.
- No code behavior was changed by the documentation work.
- `scripts/xmlpage_to_html.py` now converts bracketed text in PAGE XML line
  content into numbered HTML footnotes. Each `[note]` is removed from inline
  text, replaced with a superscript reference, and rendered in a footnote list
  below the generated page box. Inline footnote numbers are drawn through CSS
  generated content from `data-footnote-number`, so browser find does not see
  the marker number as part of the line text. The parser treats a top-level
  bracketed span as one footnote and keeps nested brackets inside that note text
  literal, so `[g[eral]]` is one note rather than an inner-note parse. OCR line
  wrappers are zero-height baseline anchors with the visible text positioned
  from `bottom: 0`, keeping browser line-box spacing from drifting away from the
  PAGE XML baselines. PAGE text normalization also converts `$` to `ſ`,
  `-p-` to `ꝑ`, and `a=e`/`o=e` plus capitalized variants to
  `æ`/`œ`/`Æ`/`Œ`; it also combines prefix diacritic markers such as `˜q`,
  `^y`, `ˆu`, `´a`, `` `e ``, `¨i`, and `¸c` into Unicode normalized letters.
  Inline `|text|` markers now render as a handwritten-style vertical strike
  through the marked text, while line-width estimation treats the marked text as
  visible without the pipes. Escaped brackets `\[` and `\]` render as literal
  brackets instead of starting or ending footnotes; escaped brackets also work
  inside footnote text. `R.` response markers are no longer rewritten to `¶`;
  the text remains `R.` and is wrapped in a stylized manuscript-like inline
  span. `& ` is no longer treated as shorthand for `R. `; it remains literal
  input text.
- `docs/xmlpage-stylization-guide.md` is the Portuguese human-facing source of
  truth for PAGE XML shorthand, inline syntax, and stylization sugar. It should
  keep user syntax plus rendered examples at the top, and usage/workflow notes
  at the bottom. Update it whenever `scripts/xmlpage_to_html.py` gains new
  syntax. The script's `--help` and missing-argument output read this guide and
  render it in a terminal-friendly plain-text form. The usage section mentions
  that users should choose `Export` from the Transkribus menu to obtain the
  XML/PAGE XML representation used to generate the book HTML.
- PAGE XML line fitting now uses the baseline polyline length as the target
  width, renders source text with a fixed manuscript-style font size, and emits
  browser JavaScript that measures each rendered `.text` span before fitting it.
  The browser fitter now adjusts font size and word/letter spacing before using
  a capped horizontal `scaleX(...)`, reducing smooshed glyphs while still
  following the marked baseline. The generated page uses a parchment-toned
  background and a local manuscript font stack, currently trying
  `Apple Chancery` before more ornamental cursive fallbacks.
  `tests/xmlpage_to_html_test.py` covers footnotes, inline formatting markers,
  baseline geometry, and emitted fitting hooks.

## Live Architecture

- Historic sources live under `historic/`. `historic/primary_sources.py`
  auto-discovers source modules and prefers `.tu.py` files over same-stem `.py`
  files.
- The shared historic lexicon lives in `historic/lexicon.tu.py`.
  `historic/lexicon.py` is a compatibility shim.
- Ground-truth text files live under `ground_truth/historic/` and
  `ground_truth/synthetic/`.
- `tests/run_tests.py` is the main test runner. It runs unittest discovery and,
  unless `--skip-tokenizer` is used, regenerates tokenizer artifacts.
- The tokenizer pipeline starts with `tokenizer/build_corpus_json.py`, then
  `tokenizer/rawgrammarpair.py`, then optional DSL work in
  `tokenizer/compile_to_dsl.py`.
- `docs/tokenizer-theory.md` explains the current tokenizer/canonicalizer
  passes, ML assumptions, baselines, and notebook experiment goals.
- The dictionary pipeline starts at `dictionary/build_dict.py`, which writes
  `site/data/rendered_corpus.json(.gz)` and
  `site/data/dictionary_entries.json(.gz)`.
- The static dictionary frontend is in `frontend/src/` and builds into `site/`.
- `dictionary/serve_dict.py` serves `site/` and exposes
  `/api/tooltip-overrides` for SQLite-backed tooltip notes.
- `scripts/xmlpage_to_html.py` is a standalone PAGE XML to positioned HTML
  converter. It reads `pc:TextLine` baselines, writes `output.html` in the
  current working directory, supports lightweight inline formatting markers,
  and numbers bracket-derived footnotes per page.

## Dictionary Workflow Notes

- Keep generated dictionary behavior data-driven. Build structured artifacts in
  Python, then consume them from the frontend.
- `dictionary/utils.py` owns rendered line records, morpheme metadata, and
  `syntax_spans`.
- `dictionary/build_entries.py` owns lexicon entry grouping, attestations, search
  fields, source counts, and optional Navarro supplemental entries.
- `frontend/src/lib.js` owns search ranking, URL query settings, tooltip payload
  assembly, tooltip override resolution, and viewport positioning helpers.
- `frontend/src/App.jsx` owns the React UI, attestation rendering, nested
  `syntax_spans` display, and tooltip note editing.
- Tooltip notes are persistent scoped annotations, not temporary hover text.
  Preserve generic-vs-form-specific note behavior.

## Verification Ladder

Use the smallest relevant check first:

- Rendered corpus or syntax-span work:
  `python3 -m unittest tests.rendered_corpus_test`
- Tooltip API/model work:
  `python3 -m unittest tests.tooltip_overrides_test tests.rendered_corpus_test`
- Dictionary artifact work:
  `python3 -m dictionary.build_dict`
- Frontend work:
  `npm run build --prefix frontend`
- Full repo gate:
  `python3 tests/run_tests.py`
- PAGE XML HTML script work:
  `python3 -m unittest tests.xmlpage_to_html_test`

`python3 tests/run_tests.py --skip-tokenizer` is useful when you only need the
Python tests and want to avoid regenerating tokenizer outputs.
