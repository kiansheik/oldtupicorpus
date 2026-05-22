# Session Handoff: XML Page Line Fitting

## Goal

Explain and fix why PAGE XML baselines could span nearly the whole manuscript
line while the generated HTML text stayed smaller and left too much right-side
whitespace. Also make the generated paper color and font feel closer to the
manuscript.

## Files Inspected

- `docs/agent/index.md`
- `docs/agent/current-state.md`
- `docs/agent/repo-map.md`
- `docs/agent/open-questions.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-05-21T15-07-40-0300-xmlpage-footnotes.md`
- `scripts/xmlpage_to_html.py`
- `tests/xmlpage_to_html_test.py`
- `/Users/kian/Downloads/YJUDZXHLPYXPHCIGGIWCUBTU.xml`
- `/Users/kian/Downloads/output.html`
- `/Users/kian/.codex/memories/MEMORY.md`

## Files Changed

- `scripts/xmlpage_to_html.py`
- `tests/xmlpage_to_html_test.py`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-05-21T15-44-15-0300-xmlpage-line-fitting.md`

## Commands Run

- `rg -n "dictionary|manuscript|canvas|baseline|page|font|layout|Doutrina|Bettendorff|serve-dict" /Users/kian/.codex/memories/MEMORY.md`
- `sed -n '1,220p' docs/agent/index.md`
- `sed -n '1,260p' docs/agent/current-state.md`
- `sed -n '1,260p' docs/agent/repo-map.md`
- `sed -n '1,220p' docs/agent/open-questions.md`
- `git status --short`
- `rg -n "xmlpage_to_html|TextLine|Baseline|baseline|font|canvas|page|word|spacing|bbox|coords|DOUTRINA|Bettendorff|background" -S .`
- `sed -n '1,280p' scripts/xmlpage_to_html.py`
- `sed -n '1,260p' tests/xmlpage_to_html_test.py`
- `find . -maxdepth 4 -iname '*page*.xml' -o -iname '*.xml' -o -iname '*output*.html' -o -iname '*.html'`
- `sed -n '1,220p' /Users/kian/Downloads/YJUDZXHLPYXPHCIGGIWCUBTU.xml`
- `sed -n '1,180p' /Users/kian/Downloads/output.html`
- `python3 -m py_compile scripts/xmlpage_to_html.py`
- `python3 -m unittest tests.xmlpage_to_html_test`
- `python3 /Users/kian/code/oldtupicorpus/scripts/xmlpage_to_html.py /Users/kian/Downloads/YJUDZXHLPYXPHCIGGIWCUBTU.xml` from `/private/tmp`
- `rg -n "font-family|background: #eadbbd|data-target-width|Sobre o fim|quæ in mundo|function fitLines|scaleX" /private/tmp/output.html`

## What Worked

- Root cause: the old renderer estimated line width as
  `font_size * 0.6 * character_count`, then used that estimate in
  `transform: scale(x, x)`. A bad horizontal width estimate therefore also
  changed vertical font size, making long lines look smaller.
- `baseline_geometry()` now normalizes reversed baselines and computes the
  target width from the full baseline polyline, not just rough character count.
- Generated line spans now include `data-target-width`, start with a no-JS
  fallback `scaleX(...)`, and then browser JS measures `text.offsetWidth` after
  fonts load to fit the actual rendered text horizontally.
- Vertical size is now independent from text length via a fixed
  `MANUSCRIPT_FONT_SIZE`.
- The generated page background is parchment-toned and source lines use a local
  cursive manuscript font stack with sepia ink coloring.
- Targeted checks pass: `python3 -m py_compile scripts/xmlpage_to_html.py` and
  `python3 -m unittest tests.xmlpage_to_html_test`.
- A representative sample was regenerated to `/private/tmp/output.html`; the
  emitted HTML contains the expected `data-target-width`, `scaleX`, parchment
  background, and manuscript font hooks.

## What Failed

- No live browser screenshot/pixel verification was run. The browser-side fit
  code was checked by unit assertions and generated HTML inspection.

## Remaining Questions

- The chosen manuscript font stack depends on locally installed fonts; browsers
  will fall through to the next available cursive font.
- Exact visual taste may still need tuning after looking at the generated page
  in the browser next to the scanned manuscript.

## Suggested Next Prompt

Run `python3 scripts/xmlpage_to_html.py /Users/kian/Downloads/YJUDZXHLPYXPHCIGGIWCUBTU.xml`,
open the generated `output.html`, and compare the text reach, paper tone, and
font against the manuscript scan.
