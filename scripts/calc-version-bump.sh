#!/usr/bin/env bash
set -euo pipefail

MAJOR_THRESHOLD=30
MINOR_THRESHOLD=10

BASE_OVERRIDE=${1:-}
INTEGRATION_PATH="custom_components/toya_decoder"
MANIFEST_PATH="${INTEGRATION_PATH}/manifest.json"

if [[ ! -f "$MANIFEST_PATH" ]]; then
  echo "Missing manifest: ${MANIFEST_PATH}" >&2
  exit 1
fi

current_version=$(python3 - "$MANIFEST_PATH" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as handle:
    data = json.load(handle)

version = str(data.get("version", "")).strip()
if not version:
    print("Missing version in manifest.json", file=sys.stderr)
    sys.exit(1)
print(version)
PY
)

base_ref="${BASE_OVERRIDE:-$current_version}"
if [[ -z "$base_ref" || "$base_ref" == "0.0.0" ]]; then
  base_ref=$(git rev-parse HEAD^ 2>/dev/null || true)
fi
base_ref="${base_ref:-HEAD}"

# Resolve the base ref to a commit (tags/branches allowed), fallback to HEAD.
base_commit=$(git rev-parse -q --verify "${base_ref}^{commit}" 2>/dev/null || true)
base_commit="${base_commit:-HEAD}"

diff_lines=$(git diff --numstat "${base_commit}"..HEAD -- "$INTEGRATION_PATH" || true)
if [[ -z "$diff_lines" ]]; then
  diff_lines=0
else
  diff_lines=$(awk '{
    if ($1 ~ /-/ || $2 ~ /-/) next
    sum += $1 + $2
  } END {print sum + 0}' <<<"$diff_lines")
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
