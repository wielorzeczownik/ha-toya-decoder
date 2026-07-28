#!/usr/bin/env bash
set -euo pipefail

manifest_path="custom_components/toya_decoder/manifest.json"

emit() {
  {
    echo "released=$1"
    echo "version=$2"
    echo "tag=$3"
    echo "commit_changes=$4"
  } >>"$GITHUB_OUTPUT"
}

current_version=$(python3 scripts/get_manifest_version.py "$manifest_path")

next_tag=$(echo "${CLIFF_BUMPED_VERSION:-}" | tr -d '[:space:]')
if [[ -z "$next_tag" ]]; then
  echo "Unable to determine next version from git-cliff"
  exit 1
fi
if [[ "$next_tag" != v* ]]; then
  next_tag="v$next_tag"
fi

next_version="${next_tag#v}"
current_tag="v${current_version}"
has_current_tag="false"
if git rev-parse -q --verify "refs/tags/${current_tag}" >/dev/null; then
  has_current_tag="true"
fi
latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || true)

if [[ "$has_current_tag" == "false" && -z "$latest_tag" ]]; then
  echo "No existing tags found. Creating initial release for ${current_tag}."
  emit true "$current_version" "$current_tag" false
  exit 0
fi

if [[ "$next_version" == "$current_version" ]]; then
  if [[ "$has_current_tag" == "false" ]]; then
    echo "No bump from git-cliff, but no current tag exists. Creating release for ${current_tag}."
    emit true "$current_version" "$current_tag" false
    exit 0
  fi

  echo "No user-facing commits since ${current_tag}. Nothing to release."
  emit false "$current_version" "$current_tag" false
  exit 0
fi

if [[ "$(printf '%s\n' "$current_version" "$next_version" | sort -V | tail -1)" != "$next_version" ]]; then
  echo "git-cliff returned $next_version which is lower than current $current_version. Nothing to release."
  emit false "$current_version" "$current_tag" false
  exit 0
fi

python3 scripts/set_manifest_version.py "$manifest_path" "$next_version"

emit true "$next_version" "$next_tag" true
