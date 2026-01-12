#!/usr/bin/env bash
set -euo pipefail

RAW_LAST_TAG=${1:-}
RAW_NEW_VERSION=${2:-}

if [[ -z "$RAW_NEW_VERSION" ]]; then
  echo "Usage: $0 <last-tag> <new-version>" >&2
  exit 1
fi

NEW_VERSION=$(printf '%s' "${RAW_NEW_VERSION}" | sed 's/^[vV]//; s/^\([0-9]\+\.[0-9]\+\.[0-9]\+\).*/\1/')
if [[ -z "$NEW_VERSION" ]]; then
  echo "Invalid new version: ${RAW_NEW_VERSION}" >&2
  exit 1
fi

TAG_NAME="v${NEW_VERSION}"
RELEASE_DATE=$(date -u +%Y-%m-%d)

LAST_TAG=""
if [[ -n "$RAW_LAST_TAG" && "$RAW_LAST_TAG" != "0.0.0" ]]; then
  LAST_TAG=$(printf '%s' "${RAW_LAST_TAG}" | sed 's/^[vV]//; s/^\([0-9]\+\.[0-9]\+\.[0-9]\+\).*/\1/')
  if [[ -n "$LAST_TAG" ]]; then
    LAST_TAG="v${LAST_TAG}"
  fi
fi

if [[ -n "$LAST_TAG" ]]; then
  CHANGELOG=$(git log --pretty=format:"- %s (%h)" "${LAST_TAG}..HEAD" \
    | grep -vE '^- (Merge pull request|chore\(release\): bump version to v)' || true)
else
  CHANGELOG=$(git log --pretty=format:"- %s (%h)" \
    | grep -vE '^- (Merge pull request|chore\(release\): bump version to v)' || true)
fi
if [[ -z "$CHANGELOG" ]]; then
  CHANGELOG="- No commits found"
fi

PREV_TAG_NAME="${LAST_TAG:-}"
if [[ -z "$PREV_TAG_NAME" ]]; then
  PREV_TAG_NAME="initial"
fi

if [[ -n "${GITHUB_REPOSITORY:-}" && "$PREV_TAG_NAME" != "initial" ]]; then
  FULL_CHANGELOG="https://github.com/${GITHUB_REPOSITORY}/compare/${PREV_TAG_NAME}...${TAG_NAME}"
elif [[ -n "${GITHUB_REPOSITORY:-}" ]]; then
  FULL_CHANGELOG="https://github.com/${GITHUB_REPOSITORY}/commits/${TAG_NAME}"
else
  FULL_CHANGELOG=""
fi

if [[ -n "$FULL_CHANGELOG" ]]; then
  FULL_CHANGELOG_LINE="#### Full Changelog: [${PREV_TAG_NAME}...${TAG_NAME}](${FULL_CHANGELOG})"
else
  FULL_CHANGELOG_LINE="#### Full Changelog: ${PREV_TAG_NAME}...${TAG_NAME}"
fi

cat <<EOF > release_notes.md
# Release Notes for Version ${TAG_NAME}
**Release Date: ${RELEASE_DATE}**

### What's Changed
${CHANGELOG}

${FULL_CHANGELOG_LINE}
EOF

{
  echo "notes<<EOF"
  cat release_notes.md
  echo "EOF"
  echo "body_path=release_notes.md"
} >> "${GITHUB_OUTPUT:-/dev/null}"
