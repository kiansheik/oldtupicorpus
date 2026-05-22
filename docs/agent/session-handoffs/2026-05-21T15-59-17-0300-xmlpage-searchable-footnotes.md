# Session Handoff: XML Page Searchable Footnotes

## Goal

Keep inline footnote superscript numbers visible at their PAGE XML line
positions without making those numbers part of the browser-searchable line text.
Also allow annotation authors to include nested bracket text such as
`[g[eral]]` inside a single footnote.

## Files Inspected

- `scripts/xmlpage_to_html.py`
- `tests/xmlpage_to_html_test.py`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `/private/tmp/output.html`

## Files Changed

- `scripts/xmlpage_to_html.py`
- `tests/xmlpage_to_html_test.py`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-05-21T15-59-17-0300-xmlpage-searchable-footnotes.md`

## Commands Run

- `python3 -m py_compile scripts/xmlpage_to_html.py`
- `python3 -m unittest tests.xmlpage_to_html_test`
- `python3 /Users/kian/code/oldtupicorpus/scripts/xmlpage_to_html.py /Users/kian/Downloads/YJUDZXHLPYXPHCIGGIWCUBTU.xml` from `/private/tmp`
- `rg -n "footnote-ref|data-footnote-number|content: attr|lingoa g|quæ in mundo" /private/tmp/output.html`

## What Worked

- Inline footnote anchors now have `data-footnote-number` and an `aria-label`,
  but no literal number text between the tags.
- CSS renders the visible superscript number with
  `content: attr(data-footnote-number)`, so the marker stays visible/clickable
  but is not part of the line's text content for Ctrl+F.
- `visible_text` no longer counts footnote marker numbers when estimating the
  no-JS fallback fit.
- Replaced the previous non-nested regex with `find_closing_bracket()`, which
  balances bracket depth and treats nested brackets as literal note content
  inside the top-level footnote.
- Added tests for marker data attributes, absence of literal marker text,
  nested `[g[eral]]` parsing, and unclosed bracket fallback.
- Targeted checks pass: `python3 -m py_compile scripts/xmlpage_to_html.py` and
  `python3 -m unittest tests.xmlpage_to_html_test`.

## What Failed

- No failures in the final pass.

## Remaining Questions

- Browser Ctrl+F behavior was reasoned from DOM/text-content behavior and the
  generated HTML structure; no automated browser find test was added.

## Suggested Next Prompt

Open `/private/tmp/output.html`, use Ctrl+F on text surrounding a footnote
marker, and confirm the visible superscript no longer interrupts browser search.
