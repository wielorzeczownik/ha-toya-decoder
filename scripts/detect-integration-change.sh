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

base_for_diff="$raw_tag"
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

integration_changed="false"
if git diff --name-only "${base_commit}"..HEAD -- custom_components/toya_decoder | grep -q .; then
  integration_changed="true"
elif [[ "$last_tag" == "0.0.0" && -d "custom_components/toya_decoder" ]]; then
  integration_changed="true"
fi

{
  echo "version=${current_version}"
  echo "changed=${integration_changed}"
} >> "${GITHUB_OUTPUT:-/dev/null}"
