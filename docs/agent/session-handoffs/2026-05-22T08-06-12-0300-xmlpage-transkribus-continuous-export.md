# Session Handoff: PAGE XML Transkribus Continuous Export

## Goal

Add a repeatable mode to `scripts/xmlpage_to_html.py` that accepts a
Transkribus export directory like `scripts/export_job_26821620` and writes one
continuous HTML file containing every PAGE XML page in METS order.

## Files Inspected

- `docs/agent/index.md`
- `docs/agent/current-state.md`
- `docs/agent/repo-map.md`
- `docs/agent/open-questions.md`
- `/Users/kian/.codex/memories/MEMORY.md`
- `scripts/export_job_26821620/log.txt`
- `scripts/export_job_26821620/9202537/ms_1089_vulgar_bettendorf/metadata.xml`
- `scripts/export_job_26821620/9202537/ms_1089_vulgar_bettendorf/mets.xml`
- `scripts/export_job_26821620/9202537/ms_1089_vulgar_bettendorf/page/0001_p002.xml`
- `scripts/export_job_26821620/9202537/ms_1089_vulgar_bettendorf/page/0002_p003.xml`
- `scripts/xmlpage_to_html.py`
- `tests/xmlpage_to_html_test.py`
- `docs/xmlpage-stylization-guide.md`
- `docs/agent/log.md`

## Files Changed

- `scripts/xmlpage_to_html.py`
- `tests/xmlpage_to_html_test.py`
- `docs/xmlpage-stylization-guide.md`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-05-22T08-06-12-0300-xmlpage-transkribus-continuous-export.md`

## Generated Files

- `scripts/export_job_26821620/output.html`

## Commands Run

- `sed -n '1,220p' docs/agent/index.md`
- `sed -n '1,260p' docs/agent/current-state.md`
- `sed -n '1,220p' docs/agent/repo-map.md`
- `sed -n '1,160p' docs/agent/open-questions.md`
- `rg -n "xmlpage_to_html|Transkribus|export_job|PAGE XML|continuous|output.html|render_html" /Users/kian/.codex/memories/MEMORY.md`
- `find . -maxdepth 4 -type d -name 'export_job_26821620' -o -type f -path '*export_job_26821620*'`
- `find scripts/export_job_26821620 -maxdepth 3 -type d | sort | sed -n '1,120p'`
- `find scripts/export_job_26821620 -maxdepth 4 -type f | sort | sed -n '1,200p'`
- `sed -n '1,200p' scripts/export_job_26821620/log.txt`
- `sed -n '1,220p' scripts/export_job_26821620/9202537/ms_1089_vulgar_bettendorf/metadata.xml`
- `sed -n '1,260p' scripts/export_job_26821620/9202537/ms_1089_vulgar_bettendorf/mets.xml`
- `sed -n '1,220p' scripts/export_job_26821620/9202537/ms_1089_vulgar_bettendorf/page/0001_p002.xml`
- `sed -n '1,220p' scripts/export_job_26821620/9202537/ms_1089_vulgar_bettendorf/page/0002_p003.xml`
- `find scripts/export_job_26821620 -maxdepth 5 -type f | wc -l`
- `find scripts/export_job_26821620 -maxdepth 5 -type f \( -name '*.jpg' -o -name '*.jpeg' -o -name '*.png' -o -name '*.tif' -o -name '*.tiff' \) | sed -n '1,40p'`
- `sed -n '180,340p' scripts/xmlpage_to_html.py`
- `sed -n '340,720p' scripts/xmlpage_to_html.py`
- `rg -n "render_html\(|main\(|output.html|Usage|wrapper|scale-container|footnote-ref" scripts/xmlpage_to_html.py tests/xmlpage_to_html_test.py docs/xmlpage-stylization-guide.md`
- `python3 -m py_compile scripts/xmlpage_to_html.py`
- `python3 -m unittest tests.xmlpage_to_html_test`
- `python3 scripts/xmlpage_to_html.py --help`
- `python3 scripts/xmlpage_to_html.py --output scripts/export_job_26821620/output.html scripts/export_job_26821620`
- `rg -n "data-page-count|Page 1:|Page 248:|resizeContinuousPages|p1-fn|p248|DOUTRINA|nhen" scripts/export_job_26821620/output.html`
- `wc -c scripts/export_job_26821620/output.html`
- `find scripts/export_job_26821620/9202537/ms_1089_vulgar_bettendorf/page -maxdepth 1 -type f -name '*.xml' | wc -l`
- `git status --short --untracked-files=all | sed -n '1,80p'`
- `date +%Y-%m-%dT%H-%M-%S%z`

## What Worked

- The script now treats file input as the existing one-page mode and directory
  input as Transkribus export mode.
- Export mode discovers document directories under the supplied directory by
  finding `mets.xml` files with a sibling `page/` directory.
- The METS `PAGEXML` file group is the page-order source of truth. The script
  sorts by `SEQ`, validates all declared hrefs exist, and only writes output
  after validation and parsing finish.
- Continuous HTML renders each page in a scrollable stack, scales each page to
  viewport width, keeps the existing browser line-fitting behavior, and prefixes
  footnote IDs per page to avoid duplicate anchors.
- `--output` chooses the output path.
- Focused checks passed: `python3 -m py_compile scripts/xmlpage_to_html.py` and
  `python3 -m unittest tests.xmlpage_to_html_test`.
- Live export check passed: 248 PAGE XML files generated one 3,288,954-byte
  `scripts/export_job_26821620/output.html` with `data-page-count="248"`.

## What Failed

- No failures in the focused checks or the live export generation.

## Remaining Questions

- `scripts/export_job_26821620` is user-added untracked input data. Do not
  assume it should be committed.
- The generated `scripts/export_job_26821620/output.html` is also untracked
  generated output.

## Suggested Next Prompt

Open `scripts/export_job_26821620/output.html` in a browser and visually inspect
the continuous scroll behavior, especially page scaling, line fitting, and
footnote anchors across pages.
