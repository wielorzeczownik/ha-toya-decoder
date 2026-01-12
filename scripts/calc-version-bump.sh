#!/usr/bin/env bash
set -euo pipefail

MAJOR_THRESHOLD=30
MINOR_THRESHOLD=10

BASE_OVERRIDE=${1:-}

current_version=$(python3 - <<'PY'
import json
import sys

with open("custom_components/toya_decoder/manifest.json", "r", encoding="utf-8") as handle:
    data = json.load(handle)

version = str(data.get("version", "")).strip()
if not version:
    print("Missing version in manifest.json", file=sys.stderr)
    sys.exit(1)
print(version)
PY
)

base_for_diff="$BASE_OVERRIDE"
if [[ -z "$base_for_diff" ]]; then
  base_for_diff="$current_version"
fi
if [[ -z "$base_for_diff" || "$base_for_diff" == "0.0.0" ]]; then
  base_for_diff=$(git rev-parse HEAD^ 2>/dev/null || true)
fi
if [[ -z "$base_for_diff" ]]; then
  base_for_diff="HEAD"
fi

base_commit=$(git rev-list -n1 "$base_for_diff" 2>/dev/null || true)
if [[ -z "$base_commit" ]]; then
  base_commit="HEAD"
fi

diff_lines=$(git diff --numstat "${base_commit}"..HEAD -- custom_components/toya_decoder || true)
if [[ -z "$diff_lines" ]]; then
  diff_lines=0
fi

if [[ "$diff_lines" -ge "$MAJOR_THRESHOLD" ]]; then
  bump="major"
elif [[ "$diff_lines" -ge "$MINOR_THRESHOLD" ]]; then
  bump="minor"
else
  bump="patch"
fi

IFS=. read -r major minor patch <<<"$current_version"
major=${major:-0}
minor=${minor:-0}
patch=${patch:-0}

case "$bump" in
  major) major=$((major + 1)); minor=0; patch=0 ;;
  minor) minor=$((minor + 1)); patch=0 ;;
  *) patch=$((patch + 1)) ;;
esac

next_version="${major}.${minor}.${patch}"

{
  echo "bump=${bump}"
  echo "diff_lines=${diff_lines}"
  echo "last_tag=${current_version}"
  echo "version=${next_version}"
} >> "${GITHUB_OUTPUT:-/dev/null}"
