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

.PHONY: help lint push test update-ground-truth review-ground-truth verify-ground-truth migrate-ground-truth-records play dict frontend-install frontend-build serve-dict

help: ## Show available targets
	@printf "Available targets:\n"
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-30s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf "\nVariables:\n"
	@printf "  %-20s %s\n" 'ARGS="..."' "Extra arguments passed through to test or ground-truth commands"
	@printf "  %-20s %s\n" 'HOST=0.0.0.0' "Host interface used by serve-dict"
	@printf "  %-20s %s\n" 'PORT=8000' "Port used by serve-dict"
	@printf "  %-20s %s\n" 'TOOLTIP_DB=...' "SQLite file used for editable tooltip notes"
	@printf "  %-20s %s\n" 'FRONTEND_DIR=frontend' "Directory containing the React/Vite frontend"

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

verify-ground-truth: ## Compare rendered historic sources to approved records without writing
	python3 -m authoring.ground_truth_cli verify $(ARGS)

migrate-ground-truth-records: ## Create structured JSONL records from legacy ground-truth text
	python3 -m authoring.ground_truth_cli migrate $(ARGS)

update-ground-truth: ## Backward-compatible alias for human-approved structured review
	$(MAKE) review-ground-truth ARGS="$(ARGS)"

review-ground-truth: ## Interactively approve new trailing targets into structured JSONL and legacy mirrors
	python3 -m authoring.ground_truth_cli review $(ARGS)

play: ## Open the interactive playground
	python3 -i playground.py

dict: ## Build the dictionary site data artifacts
	python3 -m dictionary.build_dict

$(FRONTEND_STAMP): $(FRONTEND_DIR)/package.json
	npm install --prefix $(FRONTEND_DIR)
	@mkdir -p $(FRONTEND_DIR)/node_modules
	@touch $(FRONTEND_STAMP)

frontend-install: $(FRONTEND_STAMP) ## Install React/Vite frontend dependencies

frontend-build: $(FRONTEND_STAMP) ## Build the React/Vite frontend into site/
	npm run build --prefix $(FRONTEND_DIR)

serve-dict: dict frontend-build ## Build data, build the frontend, and serve with SQLite-backed tooltip editing
	python3 -m dictionary.serve_dict --host $(HOST) --port $(PORT) --db-path $(TOOLTIP_DB)
