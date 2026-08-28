#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
SITE_DIR="${SITE_DIR:-site}"
GH_PAGES_REMOTE="${GH_PAGES_REMOTE:-origin}"
GH_PAGES_BRANCH="${GH_PAGES_BRANCH:-gh-pages}"
GH_PAGES_WORKTREE="${GH_PAGES_WORKTREE:-.gh-pages-worktree}"

case "$SITE_DIR" in
  /*) SITE_PATH="$SITE_DIR" ;;
  *) SITE_PATH="$ROOT_DIR/$SITE_DIR" ;;
esac

case "$GH_PAGES_WORKTREE" in
  /*) WORKTREE_PATH="$GH_PAGES_WORKTREE" ;;
  *) WORKTREE_PATH="$ROOT_DIR/$GH_PAGES_WORKTREE" ;;
esac

if [ "$WORKTREE_PATH" = "$ROOT_DIR" ]; then
  echo "Refusing to use the repository root as the gh-pages worktree." >&2
  exit 1
fi

if [ ! -d "$SITE_PATH" ]; then
  echo "Static site directory does not exist: $SITE_PATH" >&2
  exit 1
fi

if [ ! -f "$SITE_PATH/index.html" ]; then
  echo "Static site directory is missing index.html: $SITE_PATH" >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required to deploy the static site." >&2
  exit 1
fi

if [ ! -d "$WORKTREE_PATH/.git" ] && [ ! -f "$WORKTREE_PATH/.git" ]; then
  mkdir -p "$(dirname "$WORKTREE_PATH")"
  if git show-ref --verify --quiet "refs/heads/$GH_PAGES_BRANCH"; then
    git worktree add "$WORKTREE_PATH" "$GH_PAGES_BRANCH"
  elif git ls-remote --exit-code --heads "$GH_PAGES_REMOTE" "$GH_PAGES_BRANCH" >/dev/null 2>&1; then
    git fetch "$GH_PAGES_REMOTE" "$GH_PAGES_BRANCH:$GH_PAGES_BRANCH"
    git worktree add "$WORKTREE_PATH" "$GH_PAGES_BRANCH"
  else
    git worktree add --detach "$WORKTREE_PATH"
    git -C "$WORKTREE_PATH" checkout --orphan "$GH_PAGES_BRANCH"
  fi
fi

CURRENT_BRANCH="$(git -C "$WORKTREE_PATH" branch --show-current)"
if [ "$CURRENT_BRANCH" != "$GH_PAGES_BRANCH" ]; then
  echo "Existing worktree is on '$CURRENT_BRANCH', expected '$GH_PAGES_BRANCH'." >&2
  exit 1
fi

if ! git -C "$WORKTREE_PATH" diff --quiet || ! git -C "$WORKTREE_PATH" diff --cached --quiet; then
  echo "Existing gh-pages worktree has uncommitted changes: $WORKTREE_PATH" >&2
  exit 1
fi

find "$WORKTREE_PATH" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
rsync -a --exclude ".DS_Store" "$SITE_PATH"/ "$WORKTREE_PATH"/
printf "" > "$WORKTREE_PATH/.nojekyll"

SOURCE_REV="$(git -C "$ROOT_DIR" rev-parse --short HEAD)"
if ! git -C "$ROOT_DIR" diff --quiet || ! git -C "$ROOT_DIR" diff --cached --quiet; then
  SOURCE_REV="$SOURCE_REV-dirty"
fi

git -C "$WORKTREE_PATH" add -A
if git -C "$WORKTREE_PATH" diff --cached --quiet; then
  echo "No gh-pages changes to commit."
else
  git -C "$WORKTREE_PATH" commit -m "${GH_PAGES_COMMIT_MESSAGE:-Deploy dictionary site from $SOURCE_REV}"
fi

git -C "$WORKTREE_PATH" push "$GH_PAGES_REMOTE" "$GH_PAGES_BRANCH"
