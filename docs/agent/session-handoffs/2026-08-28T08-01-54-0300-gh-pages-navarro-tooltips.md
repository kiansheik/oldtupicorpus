# Session Handoff: GitHub Pages Navarro And Tooltips

## Goal

Fix the remaining GitHub Pages console 404s after the required dictionary and
corpus data files started loading.

## Files Inspected

- `/Users/kian/.codex/attachments/62a02796-27f9-4936-aafc-57c81a6a6051/pasted-text.txt`
- `dictionary/build_dict.py`
- `dictionary/navarro_import.py`
- `frontend/src/lib.js`
- `scripts/deploy_gh_pages.sh`
- `docs/agent/current-state.md`
- `docs/agent/log.md`

## Files Changed

- `dictionary/build_dict.py`
- `dictionary/navarro_import.py`
- `frontend/src/lib.js`
- `scripts/deploy_gh_pages.sh`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-08-28T07-57-36-0300-gh-pages-data-files.md`
- `docs/agent/session-handoffs/2026-08-28T08-01-54-0300-gh-pages-navarro-tooltips.md`

## Commands Run

- `sed -n '1,220p' /Users/kian/.codex/attachments/62a02796-27f9-4936-aafc-57c81a6a6051/pasted-text.txt`
- `black dictionary/build_dict.py dictionary/navarro_import.py`
- `bash -n scripts/deploy_gh_pages.sh`
- `make dict`
- `make frontend-build`
- `make deploy-gh-pages`
- `sleep 10`
- `curl -I https://kiansheik.io/oldtupicorpus/assets/index-fXoTmJbf.js`
- `curl -I https://kiansheik.io/oldtupicorpus/data/navarro_dict.json`
- `curl -I https://kiansheik.io/oldtupicorpus/data/navarro_dict.json.gz`
- `curl -I https://kiansheik.io/oldtupicorpus/`

## What Worked

- The remaining app-owned console 404s were
  `data/navarro_dict.json(.gz)` and `/api/tooltip-overrides`.
- `dictionary/navarro_import.py` now exposes `load_raw_navarro_entries()`, and
  `dictionary/build_dict.py` writes raw `navarro_dict.json(.gz)` sidecars for
  the frontend.
- `scripts/deploy_gh_pages.sh` now requires the Navarro sidecars before
  publishing, alongside the dictionary and rendered-corpus artifacts.
- `frontend/src/lib.js` skips tooltip override fetching on HTTPS/static hosts,
  while keeping the local/private HTTP fetch path for `make serve-dict`.
- `make deploy-gh-pages` pushed `gh-pages` commit `1dff408`, adding the
  Navarro sidecars and updated frontend bundle.
- After propagation, the Pages root, updated JS bundle, and Navarro JSON/gzip
  URLs all returned HTTP 200.

## What Failed

- The first live checks immediately after deploy still saw stale Pages content
  until propagation completed.
- `python3 -m black dictionary/build_dict.py dictionary/navarro_import.py`
  failed because the `black` Python module is not installed for that interpreter;
  the `black` executable succeeded.

## Remaining Questions

- The `contentscript.js` MaxListeners/ObjectMultiplex warnings in the browser
  log appear to come from a browser extension or injected content script, not
  from this static app bundle.
- The source branch remains dirty with unrelated Araujo/morphology work.

## Suggested Next Prompt

Reload `https://kiansheik.io/oldtupicorpus/` with the browser cache disabled and
confirm the console no longer has app-owned 404s.
