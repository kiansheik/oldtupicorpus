# Session Handoff: GitHub Pages Dictionary Deploy

## Goal

Set up a GitHub Pages deployment workflow for the generated dictionary/corpus
viewer and expose it as `make deploy-gh-pages`.

## Files Inspected

- `docs/agent/index.md`
- `docs/agent/current-state.md`
- `docs/agent/repo-map.md`
- `docs/agent/open-questions.md`
- `README.md`
- `Makefile`
- `frontend/src/lib.js`
- `frontend/vite.config.js`
- `dictionary/build_dict.py`
- `site/index.html`
- `site/assets/`

## Files Changed

- `.gitignore`
- `Makefile`
- `README.md`
- `frontend/src/lib.js`
- `frontend/vite.config.js`
- `dictionary/build_dict.py`
- `scripts/deploy_gh_pages.sh`
- `docs/agent/current-state.md`
- `docs/agent/log.md`
- `docs/agent/session-handoffs/2026-08-28T06-58-08-0300-gh-pages-dictionary-deploy.md`

## Commands Run

- `git status --short --branch`
- `bash -n scripts/deploy_gh_pages.sh`
- `make help`
- `make dict`
- `make frontend-build`
- `rg -o "data/(dictionary_entries|rendered_corpus|navarro_dict)\\.json\\.gz" site/assets site/index.html`
- `rg -o "\\\"/data/[A-Za-z0-9_./-]+|'\\/data\\/[A-Za-z0-9_./-]+" site/assets site/index.html`
- `find site/assets -maxdepth 1 -type f`
- `find site/data -maxdepth 1 -type f`
- `sed -n '1,60p' site/index.html`
- `git diff --check -- .gitignore Makefile README.md dictionary/build_dict.py frontend/src/lib.js frontend/vite.config.js scripts/deploy_gh_pages.sh docs/agent/current-state.md docs/agent/log.md docs/agent/session-handoffs/2026-08-28T06-58-08-0300-gh-pages-dictionary-deploy.md`

## What Worked

- `make deploy-gh-pages` now builds dictionary data and the Vite frontend, then
  publishes `SITE_DIR` via `scripts/deploy_gh_pages.sh`.
- `SITE_DIR` is honored by `make dict`, `make frontend-build`,
  `make serve-dict`, and `make deploy-gh-pages`, with Vite reading it from the
  environment for `build.outDir`.
- The deploy script creates or reuses a local Pages worktree, commits changes
  on the configured Pages branch, writes `.nojekyll`, and pushes to the
  configured remote.
- Existing Pages worktrees are checked before file replacement. The script
  refuses a dirty Pages worktree, a wrong-branch Pages worktree, and the repo
  root as the target worktree.
- The frontend now uses Vite base-relative data artifact paths instead of
  absolute `/data/...` URLs, so GitHub Pages project paths work.
- `make frontend-build` now removes stale generated `SITE_DIR/assets/` before
  building, which prevents old hashed bundles from being copied to Pages.
- `make dict` removes stale optional `navarro_dict.json(.gz)` files from
  `SITE_DIR/data/`, preventing old supplemental data from leaking into static
  deploys.
- The rebuilt `site/index.html` references current assets with `./assets/...`.
- The current built assets contain the expected relative data file names and no
  absolute `/data/...` path literals.

## What Failed

- One exploratory `rg` command for `./assets/...` had a shell quoting typo and
  failed with `zsh:1: unmatched "`. The same check was completed by reading
  `site/index.html` directly.
- `make deploy-gh-pages` was not run because it commits and pushes the
  configured Pages branch.

## Remaining Questions

- GitHub repository settings still need to point Pages at the `gh-pages` branch
  and `/` directory if that is not already configured.
- The static Pages deployment cannot provide the local SQLite tooltip editing
  API. The app already treats that endpoint as optional.

## Suggested Next Prompt

Run `make deploy-gh-pages` and verify the published GitHub Pages URL after
Pages finishes building.
