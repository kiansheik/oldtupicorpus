# Agent Log

## 2026-06-28

- Reverted the broad shared `gen` inflection leak by keeping the shared generic
  person prefix as `moro` for nominal/deverbal forms, while hardcoding `poro`
  only in the conjugated generic-object verb branch. This restores Araujo line
  52 as `arobîar moropysyrõanamo sekó`.
- Updated `tests/moro_incorporation_test.py` to cover
  `sara.var(1) * (moro * pysyro)` as `moropysyrõana` and the possessed
  deverbal case as `nde moroapitîaba`.
- Ran `python3 tests/run_tests.py --accept-new-ground-truth --ground-truth-source araujo_catecismo_1686`;
  it appended the three new trailing commandment lines and a second run reported
  no new lines.
- Added session handoff:
  `docs/agent/session-handoffs/2026-06-28T09-30-12-0300-moro-absolute-restore.md`.
- Fixed generic `moro` object imperatives in sibling `../nhe-enga`: explicit
  non-3p `gen` object conjugations now keep the subject/imperative prefix, so
  `(+nde * apiti * moro).imp()` renders `eporoapiti`.
- Marked the final Araujo commandment expression as a negative imperative, so it
  renders `eporoapiti umẽ`.
- Updated `tests/moro_incorporation_test.py` to cover both positive
  `eporoapiti` and prohibitive `eporoapiti umẽ`.
- Verified with `python3 -m unittest tests.moro_incorporation_test`, direct
  expression probes, and `PYTHONPATH=. python3 historic/araujo_catecismo_1686.tu.py | tail -n 8`.
- Added session handoff:
  `docs/agent/session-handoffs/2026-06-28T09-24-48-0300-moro-imperative-prefix.md`.

## 2026-06-13

- Changed generic `moro` in the sibling `../nhe-enga` Tupi inflection table so
  the absolute form stays `moro` while the dependent/prefix form is `poro`.
  This makes incorporated-object verb forms render as `poro...`, e.g.
  `(+nde * apiti * moro).imp()` -> `poroapiti`.
- Added `tests/moro_incorporation_test.py` covering absolute `moro`,
  conjugated incorporation, and possessed/deverbal `poro...` forms.
- Verified with `python3 -m unittest tests.moro_incorporation_test` and
  `python3 -m unittest tests.rendered_corpus_test`. A targeted
  `python3 tests/run_tests.py --skip-tokenizer --ground-truth-source araujo_catecismo_1686`
  shows the expected Araujo line 52 mismatch:
  `poropysyrõanamo` vs old `moropysyrõanamo`.
- Added session handoff:
  `docs/agent/session-handoffs/2026-06-13T10-57-46-0300-moro-incorporation.md`.
- Extended `make review-ground-truth` mismatch handling: when an existing line
  differs, the prompt can keep `[e]xpected`, accept `[a]ctual` into the
  ground-truth file, or `[q]uit`; accepting actual replaces only the selected
  logical line and then re-runs comparison.
- Added `replace_ground_truth_line()` and regression coverage for accepting an
  actual mismatch and preserving blank lines during replacement.
- Verified with `python3 -m unittest tests.ground_truth_cases_test`.
- Added session handoff:
  `docs/agent/session-handoffs/2026-06-13T10-40-22-0300-review-ground-truth-mismatches.md`.
- Changed `make update-ground-truth` into the fast append workflow: it now runs
  `make test ARGS="..."` first and then runs
  `python3 tests/run_tests.py --accept-new-ground-truth $(ARGS)` to append all
  trailing rendered lines only after tests pass.
- Added `make review-ground-truth` for the previous interactive line-by-line
  updater.
- Added non-interactive append helpers and regression tests in
  `tests/ground_truth_cases_test.py`.
- Verified with `python3 -m unittest tests.ground_truth_cases_test` and dry-run
  `make -n` checks for both updater targets. Broader
  `python3 tests/run_tests.py --skip-tokenizer` is blocked by an existing line
  18 `îeerobîasaba`/`îerobîasaba` mismatch in both historic cases.
- Added session handoff:
  `docs/agent/session-handoffs/2026-06-13T10-37-25-0300-fast-ground-truth-update.md`.
- Fixed `saba` deverbal negation in the sibling `../nhe-enga` checkout:
  `-(saba * v(marãtekó))` and `saba * -v(marãtekó)` now render with
  `e'ym` as `marãtekoabe'yma`.
- Added `tests/deverbal_negation_test.py` to pin both negation propagation
  paths from this repo's `historic.lexicon` import path.
- Verified with `python3 -m unittest tests.deverbal_negation_test` and
  `python3 -m unittest tests.rendered_corpus_test`.
- Added session handoff:
  `docs/agent/session-handoffs/2026-06-13T10-34-02-0300-saba-negation.md`.

## 2026-05-22

- Added PAGE XML faded-text markup: `%XX text%` now renders `text` with the
  requested visible opacity percentage, keeps the underlying text searchable,
  and excludes the `%XX`/closing `%` markers from line-width estimation. The
  Portuguese stylization guide and focused XML page tests cover the new syntax.
- Added Transkribus export directory mode to `scripts/xmlpage_to_html.py`.
  Directory input now discovers `mets.xml` documents, validates all declared
  `PAGEXML` page files before writing, and emits one continuous scrollable HTML
  book. Added `--output` for explicit destination files.
- Generated `scripts/export_job_26821620/output.html` from the 248-page
  Transkribus export as a live check of the new directory mode.
- Added PAGE XML ligature shorthands: `a=e`/`o=e` now render as `æ`/`œ`, with
  capitalized variants for `Æ`/`Œ`, so Latin ligatures can be typed from a US
  keyboard without broad automatic `ae`/`oe` replacement.
- Added PAGE XML escaping for literal brackets: `\[` and `\]` now render as
  literal brackets instead of triggering footnotes, including inside footnote
  text.
- Updated the Portuguese stylization guide's `Notas` section and help-output
  tests with escaped bracket examples.
- Rewrote `docs/xmlpage-stylization-guide.md` in Portuguese for Brazilian
  users, moved user syntax plus rendered examples to the top, and moved
  converter usage to the bottom.
- Added Transkribus workflow guidance to the PAGE XML guide: choose `Export`
  from the menu to obtain the XML/PAGE XML representation used to generate the
  book HTML.
- Updated help-output tests to assert the Portuguese guide structure and
  Transkribus export instruction.
- Added `docs/xmlpage-stylization-guide.md` as the maintained human reference
  for PAGE XML shorthand, inline syntax, footnotes, response marks, and future
  sugar additions.
- Added `scripts/xmlpage_to_html.py --help` and missing-argument output that
  read the stylization guide from disk and render it in terminal-friendly text.
- Added tests for the help output and for preserving literal syntax markers in
  the terminal-rendered guide.
- Added PAGE XML shorthand normalization for `-p-` to the per glyph `ꝑ`, with
  regression coverage for both rendered HTML text and visible line text.

## 2026-05-21

- Removed the remaining PAGE XML `& ` to `R. ` shorthand conversion; paragraph
  or response marks now require literal `R.` input to receive the styled span.
- Stopped rewriting PAGE XML `R.` response markers to `¶`; `R.` now remains
  visible text and renders through a dedicated stylized manuscript-like span.
- Updated tests so `R. & aba` leaves `&` literal, styles only the literal `R.`,
  and avoids the paragraph symbol path.
- Added PAGE XML inline `|...|` formatting for manuscript deletions: marked
  text now renders with a slightly slanted vertical strike while width
  estimation ignores the pipe markers.
- Added regression coverage for `ocäu|m|baeráma? oporomonhang|m|bae-` and for
  the generated vertical-strike CSS.
- Generalized PAGE text normalization for prefix diacritics: markers such as
  `˜`, `ˆ`, `^`, `´`, grave, diaeresis, and cedilla now combine with the
  following letter and are NFC-normalized when possible.
- Added regression coverage for `˜q` becoming `q̃` in generated line text.
- Changed inline PAGE footnote markers so superscript numbers are CSS generated
  content from `data-footnote-number`, keeping the visible marker out of the
  line's searchable DOM text for browser Ctrl+F.
- Replaced regex footnote extraction with a bracket scanner that treats
  `[g[eral]]` as one top-level footnote whose note text is `g[eral]`; unclosed
  brackets remain literal inline text.
- Tuned the PAGE HTML browser fitter so it uses font-size and word/letter
  spacing adjustments before capped horizontal scaling, reducing the visibly
  smooshed letterforms on dense baseline-fitted lines.
- Reordered the manuscript font stack to try `Apple Chancery` before the more
  ornamental `Snell Roundhand` fallback.
- Reworked PAGE XML HTML line fitting so baseline polyline length becomes the
  target width, rendered text keeps a fixed manuscript-style font size, and the
  browser measures actual text width before applying horizontal-only `scaleX`.
- Changed generated PAGE HTML styling toward manuscript facsimile: parchment
  paper color, sepia ink tone, and local cursive font stack before generic
  cursive fallback.
- Extended `tests/xmlpage_to_html_test.py` for emitted fitting hooks, baseline
  target widths, fixed manuscript font sizing, and reversed/polyline baseline
  normalization.
- Added session handoff:
  `docs/agent/session-handoffs/2026-05-21T15-44-15-0300-xmlpage-line-fitting.md`.
- Updated `scripts/xmlpage_to_html.py` so bracketed line text such as
  `[note]` becomes a numbered superscript reference in the rendered page and a
  numbered footnote below the page box.
- Fixed a follow-up layout regression where scaling from `top center` pushed the
  generated page above the viewport and made the browser view appear blank.
- Restyled generated footnotes with a muted editorial color, serif typography,
  larger readable footnote text, and a transparent academic-paper-style footnote
  area instead of a small detached white box.
- Adjusted positioned OCR text so each `.line` is a zero-height baseline anchor
  and each `.text` sits on `bottom: 0`, making vertical spacing follow PAGE XML
  baselines more faithfully than normal browser line boxes.
- Wrapped `scripts/xmlpage_to_html.py` in import-safe helper functions and
  `main()` so the behavior can be tested directly.
- Added `tests/xmlpage_to_html_test.py` for footnote extraction, empty-bracket
  handling, rendered HTML placement, and PAGE XML line collection.
- Added session handoff:
  `docs/agent/session-handoffs/2026-05-21T15-07-40-0300-xmlpage-footnotes.md`.

## 2026-05-11

- Added `docs/tokenizer-theory.md`, a teaching document for the current tokenizer
  and morphology-aware ML pipeline. It covers source data, corpus construction,
  canonical ID registries, DSL reconstruction, notebook factorization, Navarro
  lexical priors, baselines, neural seq2seq assumptions, metrics, and failure
  debugging.
- Added session handoff:
  `docs/agent/session-handoffs/2026-05-11T12-10-18-0300-tokenizer-theory-doc.md`.
- Created the initial `docs/agent/` wiki structure.
- Read repo-local context from `README.md`, `CLAUDE.md`, `Makefile`, selected
  dictionary/frontend/test files, and prior oldtupicorpus workflow memory.
- Documented the current dictionary pipeline, tokenizer pipeline, verification
  ladder, and known open questions.
- Added session handoff:
  `docs/agent/session-handoffs/2026-05-11T11-53-26-0300-agent-wiki-bootstrap.md`.
