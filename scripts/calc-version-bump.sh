#!/usr/bin/env bash
set -euo pipefail

BASE_OVERRIDE=${1:-}
MANIFEST_PATH="custom_components/toya_decoder/manifest.json"

if [[ ! -f "$MANIFEST_PATH" ]]; then
  echo "Missing manifest: ${MANIFEST_PATH}" >&2
  exit 1
fi

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

raw_tag="$BASE_OVERRIDE"
if [[ -z "$raw_tag" ]]; then
  raw_tag=$(git describe --tags --abbrev=0 2>/dev/null || true)
fi
last_tag=$(printf '%s' "${raw_tag:-}" | sed 's/^[vV]//; s/^\([0-9]\+\.[0-9]\+\.[0-9]\+\).*/\1/')
if [[ -z "$last_tag" ]]; then
  last_tag="0.0.0"
fi

bump="none"
if [[ "$current_version" != "$last_tag" ]]; then
  IFS=. read -r cur_major cur_minor cur_patch <<<"$current_version"
  IFS=. read -r last_major last_minor last_patch <<<"$last_tag"
  cur_major=${cur_major:-0}
  cur_minor=${cur_minor:-0}
  cur_patch=${cur_patch:-0}
  last_major=${last_major:-0}
  last_minor=${last_minor:-0}
  last_patch=${last_patch:-0}

  if (( cur_major > last_major )); then
    bump="major"
  elif (( cur_minor > last_minor )); then
    bump="minor"
  elif (( cur_patch > last_patch )); then
    bump="patch"
  fi
fi

{
  echo "bump=${bump}"
  echo "last_tag=${last_tag}"
  echo "version=${current_version}"
} >> "${GITHUB_OUTPUT:-/dev/null}"
