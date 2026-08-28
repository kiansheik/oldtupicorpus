DOCKER="docker"
IMAGE_NAME="kiansheik/nhe-enga"
TAG_NAME="production"

REPOSITORY=""
FULL_IMAGE_NAME=${IMAGE_NAME}:${TAG_NAME}
HOST ?= 0.0.0.0
PORT ?= 8000
TOOLTIP_DB ?= var/tooltip_overrides.sqlite3
FRONTEND_DIR ?= frontend
FRONTEND_STAMP := $(FRONTEND_DIR)/node_modules/.installed
SITE_DIR ?= site
GH_PAGES_REMOTE ?= origin
GH_PAGES_BRANCH ?= gh-pages
GH_PAGES_WORKTREE ?= .gh-pages-worktree
GH_PAGES_COMMIT_MESSAGE ?=

.PHONY: help lint push test review-ground-truth verify-ground-truth regenerate-ground-truth play dict frontend-install frontend-build serve-dict deploy-gh-pages

help: ## Show available targets
	@printf "Available targets:\n"
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-30s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf "\nVariables:\n"
	@printf "  %-20s %s\n" 'ARGS="..."' "Extra arguments passed through to test or ground-truth commands"
	@printf "  %-20s %s\n" 'HOST=0.0.0.0' "Host interface used by serve-dict"
	@printf "  %-20s %s\n" 'PORT=8000' "Port used by serve-dict"
	@printf "  %-20s %s\n" 'TOOLTIP_DB=...' "SQLite file used for editable tooltip notes"
	@printf "  %-20s %s\n" 'FRONTEND_DIR=frontend' "Directory containing the React/Vite frontend"
	@printf "  %-20s %s\n" 'SITE_DIR=site' "Built static site directory"
	@printf "  %-20s %s\n" 'GH_PAGES_REMOTE=origin' "Git remote used by deploy-gh-pages"
	@printf "  %-20s %s\n" 'GH_PAGES_BRANCH=gh-pages' "GitHub Pages branch"
	@printf "  %-20s %s\n" 'GH_PAGES_WORKTREE=.gh-pages-worktree' "Temporary worktree for gh-pages"
	@printf "  %-20s %s\n" 'GH_PAGES_COMMIT_MESSAGE=...' "Commit message for deploy-gh-pages"

lint: ## Format Python code with black
	black .

push: ## Lint, test, commit, and push the current branch
	make lint
	make test
	git add .
	git commit
	git push origin HEAD

test: ## Run the test suite; pass extra args with ARGS="..."
	python3 tests/run_tests.py $(ARGS)

verify-ground-truth: ## Verify source renderings and source-derived JSONL ground truth
	python3 -m authoring.ground_truth_cli verify $(ARGS)

regenerate-ground-truth: ## Rebuild JSONL ground truth from `.tu.py` source annotations
	python3 -m authoring.ground_truth_cli regenerate $(ARGS)

review-ground-truth: ## Check whether generated JSONL is current with its source annotations
	python3 -m authoring.ground_truth_cli review $(ARGS)

play: ## Open the interactive playground
	python3 -i playground.py

dict: ## Build the dictionary data artifacts into SITE_DIR/data
	python3 -m dictionary.build_dict --out-dir "$(SITE_DIR)/data"

$(FRONTEND_STAMP): $(FRONTEND_DIR)/package.json
	npm install --prefix $(FRONTEND_DIR)
	@mkdir -p $(FRONTEND_DIR)/node_modules
	@touch $(FRONTEND_STAMP)

frontend-install: $(FRONTEND_STAMP) ## Install React/Vite frontend dependencies

frontend-build: $(FRONTEND_STAMP) ## Build the React/Vite frontend into SITE_DIR
	rm -rf "$(SITE_DIR)/assets"
	SITE_DIR="$(SITE_DIR)" npm run build --prefix $(FRONTEND_DIR)

serve-dict: dict frontend-build ## Build data, build the frontend, and serve with SQLite-backed tooltip editing
	python3 -m dictionary.serve_dict --host $(HOST) --port $(PORT) --site-dir "$(SITE_DIR)" --db-path $(TOOLTIP_DB)

deploy-gh-pages: dict frontend-build ## Build and publish site/ to the gh-pages branch
	SITE_DIR="$(SITE_DIR)" GH_PAGES_REMOTE="$(GH_PAGES_REMOTE)" GH_PAGES_BRANCH="$(GH_PAGES_BRANCH)" GH_PAGES_WORKTREE="$(GH_PAGES_WORKTREE)" GH_PAGES_COMMIT_MESSAGE="$(GH_PAGES_COMMIT_MESSAGE)" scripts/deploy_gh_pages.sh
