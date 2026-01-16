#!/usr/bin/env bash
set -euo pipefail

BASE_OVERRIDE=${1:-}
INTEGRATION_PATH="custom_components/toya_decoder"
MANIFEST_PATH="${INTEGRATION_PATH}/manifest.json"
HACS_PATH="hacs.json"
DIFF_PATHS=("$INTEGRATION_PATH" "$HACS_PATH")

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

raw_tag="${BASE_OVERRIDE:-}"
if [[ -z "$raw_tag" ]]; then
  raw_tag=$(git describe --tags --abbrev=0 2>/dev/null || true)
fi

last_tag=$(printf '%s' "${raw_tag:-}" | sed 's/^[vV]//; s/^\([0-9]\+\.[0-9]\+\.[0-9]\+\).*/\1/')
last_tag="${last_tag:-0.0.0}"

base_ref="$raw_tag"
if [[ -z "$base_ref" || "$base_ref" == "0.0.0" ]]; then
  base_ref=$(git rev-parse HEAD^ 2>/dev/null || true)
fi
base_ref="${base_ref:-HEAD}"

# Resolve the base ref to a commit (tags/branches allowed), fallback to HEAD.
base_commit=$(git rev-parse -q --verify "${base_ref}^{commit}" 2>/dev/null || true)
base_commit="${base_commit:-HEAD}"

integration_changed="false"
if git diff --name-only "${base_commit}"..HEAD -- "${DIFF_PATHS[@]}" | grep -q .; then
  integration_changed="true"
elif [[ "$last_tag" == "0.0.0" && -d "$INTEGRATION_PATH" ]]; then
  integration_changed="true"
fi

{
  echo "version=${current_version}"
  echo "changed=${integration_changed}"
} >> "${GITHUB_OUTPUT:-/dev/null}"
