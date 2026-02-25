#!/usr/bin/env bash
# Bump version, commit, tag, push, and build.
# Usage: ./bump.sh [major|minor|patch]   (default: patch)

set -euo pipefail

INIT_FILE="src/flatdir/__init__.py"

# Read current version
current=$(sed -n 's/^__version__ = "\(.*\)"/\1/p' "$INIT_FILE")
IFS='.' read -r major minor patch <<< "$current"

# Bump
part="${1:-patch}"
case "$part" in
    major) major=$((major + 1)); minor=0; patch=0 ;;
    minor) minor=$((minor + 1)); patch=0 ;;
    patch) patch=$((patch + 1)) ;;
    *) echo "Usage: $0 [major|minor|patch]"; exit 1 ;;
esac

new_version="$major.$minor.$patch"
echo "Bumping $current → $new_version"

# Update __init__.py
sed -i '' "s/__version__ = \"$current\"/__version__ = \"$new_version\"/" "$INIT_FILE"

# Commit, tag, push
# git add -A
# git commit -m "v$new_version"
git tag "v$new_version"
git push
git push --tags

# Build
python -m build

echo "✅ v$new_version released"
run 