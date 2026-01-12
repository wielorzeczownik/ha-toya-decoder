#!/usr/bin/env bash
set -euo pipefail

MANIFEST_PATH="custom_components/toya_decoder/manifest.json"
INPUT=${1:-}

if [[ -z "$INPUT" ]]; then
  echo "Usage: $0 <major|minor|patch|x.y.z>" >&2
  exit 1
fi

if [[ ! -f "$MANIFEST_PATH" ]]; then
  echo "Missing manifest: ${MANIFEST_PATH}" >&2
  exit 1
fi

new_version=$(python3 - "$INPUT" <<'PY'
import json
import re
import sys

path = "custom_components/toya_decoder/manifest.json"
bump = sys.argv[1].strip()

with open(path, "r", encoding="utf-8") as handle:
    data = json.load(handle)

current = str(data.get("version", "")).strip()
if not current:
    print("Missing version in manifest.json", file=sys.stderr)
    sys.exit(1)

def parse_version(value: str):
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", value)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())

explicit = parse_version(bump)
if explicit:
    new_version = bump
else:
    current_parts = parse_version(current)
    if current_parts is None:
        print(f"Invalid current version: {current}", file=sys.stderr)
        sys.exit(1)
    if bump not in {"major", "minor", "patch"}:
        print(f"Invalid bump: {bump}", file=sys.stderr)
        sys.exit(1)
    major, minor, patch = current_parts
    if bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    new_version = f"{major}.{minor}.{patch}"

data["version"] = new_version
with open(path, "w", encoding="utf-8") as handle:
    json.dump(data, handle, indent=2)
    handle.write("\n")

print(new_version)
PY
)

echo "Updated ${MANIFEST_PATH} to ${new_version}"
if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  echo "version=${new_version}" >> "${GITHUB_OUTPUT}"
fi
