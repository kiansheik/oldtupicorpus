# Current State

Last updated: 2026-08-28

## Repo State

- GitHub Pages deployment for the dictionary/corpus viewer is now wired through
  `make deploy-gh-pages`. The target rebuilds dictionary artifacts and the
  Vite frontend into `SITE_DIR`, then `scripts/deploy_gh_pages.sh` syncs that
  static bundle into a local `.gh-pages-worktree`, commits on `gh-pages`,
  writes `.nojekyll`, and pushes to the configured remote. `SITE_DIR`,
  `GH_PAGES_REMOTE`, `GH_PAGES_BRANCH`, `GH_PAGES_WORKTREE`, and
  `GH_PAGES_COMMIT_MESSAGE` are configurable from `make`.
- `frontend/src/lib.js` now builds static data URLs from
  `import.meta.env.BASE_URL`, so the default Vite `base: "./"` produces paths
  that work under a GitHub Pages project subpath. The tooltip override endpoint
  remains `/api/tooltip-overrides`; it is only available from
  `make serve-dict` and is treated as optional by the static app.
- `make dict`, `make frontend-build`, `make serve-dict`, and
  `make deploy-gh-pages` all honor `SITE_DIR`. `frontend/vite.config.js` reads
  that environment variable for its `outDir`, and `make frontend-build` removes
  stale generated `SITE_DIR/assets/` files before invoking Vite. This preserves
  `SITE_DIR/data/` while preventing old hashed bundles from being copied into
  the GitHub Pages branch.
- `dictionary/build_dict.py` removes stale `navarro_dict.json(.gz)` sidecar
  files from its output directory, because the current builder does not
  regenerate that sidecar and the frontend treats it as optional if present.
- `../nhe-enga/tupi/tupi/tupi.py`, `../nhe-enga/tupi/tupi/verb.py`, and
  `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py` now preserve
  `[PROPER_NOUN]` spans through final verb phonetic cleanup. This keeps the
  broad `is -> ix` rule active for regular lexical material while preventing
  proper-noun objects such as `missa` and `Luis Felipe` from becoming
  `mixsa`/`Luix`. The current Araujo source expression
  `(esé * domingo) + (esebé * noworkday) + (missa * endub)` renders
  `domingo resé 'ara marãtekoabe'yma resebé missarendubi`, and the nominalized
  variant with `(missa * endub).base_nominal()` renders
  `domingo resé 'ara marãtekoabe'yma resebé missarenduba`.
  `tests/proper_noun_phonetics_test.py` covers finite and nominal direct
  objects, the regular noun contrasts, and both Araujo phrase shapes.
- `../nhe-enga/tupi/tupi/verb.py` now accepts an opt-in nominal variation for
  intransitive reflexive/reciprocal subjects. `Verb.base_nominal()` passes
  `variation_id` through from the Pydicate predicate, so
  `(îe * mombeu).var(1).base_nominal()` renders `îemombe'u` while the default
  `(îe * mombeu).base_nominal()` remains `oîo mombe'u`. Araujo record 77 uses
  this in `l += (iabiõ * seîxu) + (îe * mombeu).var(1).base_nominal()`,
  rendering `seîxu îabi'õ îemombe'u`. The regression is
  `tests/reflexive_nominal_variation_test.py`.
- `historic/lexicon.tu.py` now shadows imported `paben` with an
  `Adverb("pabẽ", tag="[ADVERB:ALL]")`, matching the attested particle/adverb
  use of `pabẽ` as "all/completely". Because preposed adverbs already trigger
  circumstantial mood in the verb wrapper, `paben + (aîpo * îub)` renders
  `pabẽ aîpoba'e ruî` without an explicit `.circ()`. The same file also defines
  `aîpo` as the unaccented Araujo demonstrative variant, while existing
  postposed `... + paben` surfaces such as `oîkobeba'e omanõba'epûera pabẽ`
  remain unchanged. `tests/paben_adverb_test.py` covers both paths.
- `historic/araujo_catecismo_1686.tu.py` now includes record
  `araujo_catecismo_1686:0072`, rendered from
  `nã + ((bae * ei) * pupé) + (paben + (aîpo * îub))` as
  `nã e'iba'e pupé pabẽ aîpoba'e ruî`.
- `historic/lexicon.tu.py` also aliases `aûsub = love` for source expressions
  that should use the Tupi verb name directly. `historic/araujo_catecismo_1686.tu.py`
  now includes record `araujo_catecismo_1686:0073`, rendered from
  `opkmbt + (((asé * aûsub * +opkmbt).base_nominal()) * sosé) + (asé * (tupan * aûsub.base_nominal()))`
  as `opakatu mba'e tetiruã asé saûsuba sosé asé Tupã raûsuba`.
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py` now makes
  `Verb.base_nominal()` respect non-pronoun object pro-drop. This lets Araujo
  record 73 keep `opkmbt` both as the overt fronted object and as the dropped
  object of `asé * aûsub` without repeating it in the rendered nominal:
  `(asé * aûsub * +opkmbt).base_nominal()` renders `asé saûsuba`, while the
  dropped object remains present in the nominal arguments for syntax metadata.
  `tests/base_nominal_object_pro_drop_test.py` covers this behavior plus the
  unchanged `+ae` pronoun contrast.
- `../nhe-enga/tupi/tupi/verb.py` now renders 3p nominal reflexive/reciprocal
  objects with the correlational `o-` prefix when there is no overt subject
  string. This makes `(+asé * aûsub * îe).base_nominal()` render `oîeaûsuba`
  and the reciprocal contrast render `oîoaûsuba`, instead of the older
  `i îe...` split. Regenerated historic JSONL now carries the same correction
  into earlier Araujo and Bettendorff reflexive nominal records.
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/deverbal.py` now applies
  `e'ym` negation to `saba` deverbals when either the `saba` wrapper itself is
  negated or the input verb is negated. This fixes expressions such as
  `-(saba * v(marãtekó))` and `saba * -v(marãtekó)`, which now render
  `marãtekoabe'yma` instead of the positive `marãtekoaba`.
- `tests/deverbal_negation_test.py` covers the local `oldtupicorpus` expression
  path against the sibling `../nhe-enga` dev checkout.
- `make update-ground-truth` now runs `make test ARGS="..."` first and only
  then appends all newly rendered trailing ground-truth lines via
  `--accept-new-ground-truth`. The old interactive per-line workflow is
  available as `make review-ground-truth`.
- In `make review-ground-truth`, existing-line mismatches are now reviewable:
  choose `[e]xpected` to keep the checked-in ground-truth line, `[a]ctual` to
  replace that logical line with the rendered output and re-compare, or `[q]uit`.
- `../nhe-enga/tupi/tupi/tupi.py` keeps generic `moro` as `moro` in the shared
  personal inflection table so nominal/deverbal absolute forms such as
  `sara.var(1) * (moro * pysyro)` render `moropysyrõana`. The conjugated
  generic-object branch in `../nhe-enga/tupi/tupi/verb.py` handles its own
  incorporated `poro` prefix and keeps the subject/imperative prefix for
  explicit non-3p conjugations, so `(+nde * apiti * moro).imp()` renders
  `eporoapiti` and the negated Araujo commandment line renders
  `eporoapiti umẽ`. The local regression test is
  `tests/moro_incorporation_test.py`.
- `../nhe-enga/pydicate/pydicate/lang/tupilang/pos/verb.py` now handles
  non-pronoun 3p subjects marked with `+` in nominal contexts by suppressing
  the displaced noun while preserving the 3p nominal prefix slot. This makes
  `saguera(+jesus * ikobé)` render `sekobesagûera`, while explicit
  `saguera(jesus * ikobé)` still renders `Jesus rekobesagûera`. The local
  regression test is `tests/nominal_pro_drop_test.py`. Araujo ground truth now
  includes the resulting approved line `arobîar 'ara mosapyra resé
  sekobesagûera` and the earlier displaced-3p nominal line with `i a'epe`.
- The local `agent-authoring-mcp-framework` branch has been rebased onto remote
  `origin/agent-authoring-mcp-framework` commit `2464d79`. The conflict
  resolution keeps remote source-annotation subsection support and the existing
  ground-truth append/replace helpers. `make verify-ground-truth` passes as of
  2026-06-28.
- `python3 tests/run_tests.py --skip-tokenizer` passes as of 2026-06-28.
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
  visible without the pipes. Inline `%XX text%` markers render `text` with
  `XX` percent visible opacity for erased/faded-but-readable text; the marker is
  stripped from line-width estimation and the underlying text remains searchable.
  Escaped brackets `\[` and `\]` render as literal brackets instead of starting
  or ending footnotes; escaped brackets also work inside footnote text. `R.`
  response markers are no longer rewritten to `¶`; the text remains `R.` and is
  wrapped in a stylized manuscript-like inline span. `& ` is no longer treated
  as shorthand for `R. `; it remains literal input text.
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
- `scripts/deploy_gh_pages.sh` publishes the static `site/` bundle to the
  configured Pages branch using a local worktree. It refuses to use the repo
  root as the worktree, refuses a wrong-branch or dirty existing Pages
  worktree, and requires `site/index.html` before syncing.
- `scripts/xmlpage_to_html.py` is a standalone PAGE XML to positioned HTML
  converter. It reads `pc:TextLine` baselines, writes `output.html` in the
  current working directory, supports lightweight inline formatting markers,
  and numbers bracket-derived footnotes per page. It now also accepts a
  Transkribus export directory as input: it discovers document directories with
  `mets.xml` plus `page/`, reads the METS `PAGEXML` sequence, validates that
  declared PAGE XML files exist before rendering, and emits one scrollable
  continuous HTML book. Use `--output` to choose the destination file.

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
- Static GitHub Pages deploys do not include the local SQLite tooltip editing
  API. The viewer still loads dictionary/corpus data and hides editing when the
  API is unavailable.

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
- GitHub Pages deploy plumbing:
  `bash -n scripts/deploy_gh_pages.sh`, `make dict`, `make frontend-build`,
  and a built-bundle check that no current `site/assets` JS uses absolute
  `/data/...` paths.
- Full repo gate:
  `python3 tests/run_tests.py`
- PAGE XML HTML script work:
  `python3 -m unittest tests.xmlpage_to_html_test`

`python3 tests/run_tests.py --skip-tokenizer` is useful when you only need the
Python tests and want to avoid regenerating tokenizer outputs.
