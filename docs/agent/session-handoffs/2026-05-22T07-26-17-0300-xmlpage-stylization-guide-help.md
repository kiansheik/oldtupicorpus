# Session Handoff: PAGE XML Stylization Guide Help

## Goal

Create a maintained human-facing guide for PAGE XML shorthand, inline syntax,
and stylization sugar, then have `scripts/xmlpage_to_html.py --help` read and
print that guide in terminal-friendly form.

## Files Inspected

- `docs/agent/index.md`
- `docs/agent/current-state.md`
- `docs/agent/repo-map.md`
- `docs/agent/open-questions.md`
- `scripts/xmlpage_to_html.py`
- `tests/xmlpage_to_html_test.py`
- `docs/agent/log.md`

## Files Changed

- `docs/xmlpage-stylization-guide.md`
- `scripts/xmlpage_to_html.py`
- `tests/xmlpage_to_html_test.py`
- `docs/agent/current-state.md`
- `docs/agent/repo-map.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-05-22T07-26-17-0300-xmlpage-stylization-guide-help.md`

## Commands Run

- `sed -n '1,220p' docs/agent/index.md`
- `sed -n '1,240p' docs/agent/current-state.md`
- `sed -n '1,220p' docs/agent/repo-map.md`
- `sed -n '1,180p' docs/agent/open-questions.md`
- `rg -n "xmlpage_to_html|PAGE XML|stylization|style guide|REPLACES|help" /Users/kian/.codex/memories/MEMORY.md`
- `sed -n '1,220p' scripts/xmlpage_to_html.py`
- `sed -n '220,580p' scripts/xmlpage_to_html.py`
- `sed -n '560,660p' scripts/xmlpage_to_html.py`
- `sed -n '1,260p' tests/xmlpage_to_html_test.py`
- `find docs -maxdepth 2 -type f -print | sort`
- `python3 -m py_compile scripts/xmlpage_to_html.py`
- `python3 -m unittest tests.xmlpage_to_html_test`
- `python3 scripts/xmlpage_to_html.py --help`
- `date +%Y-%m-%dT%H-%M-%S%z`

## What Worked

- Added `docs/xmlpage-stylization-guide.md` with the current character
  shorthands, prefix diacritics, inline formatting, footnotes, response marks,
  and a maintenance checklist.
- Added `STYLIZATION_GUIDE_PATH`, `markdown_to_terminal()`, and
  `build_help_text()` to `scripts/xmlpage_to_html.py`.
- `--help` now exits 0 and prints the guide. Missing arguments print the same
  guide and exit 1.
- Help rendering removes code fences and heading markers while preserving
  literal syntax such as `**text**`, `|text|`, and `-p-`.
- `tests/xmlpage_to_html_test.py` now covers `--help` output and the missing
  argument help path.
- The focused PAGE XML checks pass.

## What Failed

- The first help-output test exposed an over-aggressive Markdown stripper that
  removed literal markers such as `**text**`. The formatter was tightened to
  unwrap inline code without stripping the syntax being documented.
- The first guide wording for the grave-accent shorthand used Markdown backtick
  syntax awkwardly. It was rewritten as `grave-e` so terminal output is clear.

## Remaining Questions

- None for this pass.

## Suggested Next Prompt

When adding the next PAGE XML shorthand or formatting marker, update
`docs/xmlpage-stylization-guide.md` and `tests/xmlpage_to_html_test.py` in the
same patch.
