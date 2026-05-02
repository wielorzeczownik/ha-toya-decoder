# Contributing to ha-toya-decoder

Thank you for considering a contribution. This document covers everything you need to get started.

## Overview

A Home Assistant custom integration that exposes your TOYA cable TV decoder as a `media_player` entity, enabling remote control, channel switching, and home automation directly from Home Assistant.

## Project structure

```text
.
├── custom_components/toya_decoder/   Home Assistant integration source
└── scripts/
    ├── bump-version.sh               determines the next release version and updates the manifest
    ├── get_manifest_version.py       reads the current version from manifest.json
    └── set_manifest_version.py       writes a new version to manifest.json
```

## Development setup

```bash
git clone https://github.com/wielorzeczownik/ha-toya-decoder.git
cd ha-toya-decoder
pip install -r requirements_dev.txt -r requirements_lint.txt
```

Alternatively, open the repository in VSCode – the included devcontainer provides a ready-to-use environment.

## Running checks locally

### With tools installed

```bash
# Python
ruff check .
ruff format --check .

# Shell
shfmt --diff scripts/

# Markdown
markdownlint-cli2 "**/*.md"

# Tests
pytest
```

### With Docker (no local installs required)

```bash
docker run --rm -v "$(pwd):/src" -w /src ghcr.io/astral-sh/ruff check .
docker run --rm -v "$(pwd):/src" -w /src ghcr.io/astral-sh/ruff format --check .

docker run --rm -v "$(pwd):/src" -w /src mvdan/shfmt --diff scripts/

docker run --rm -v "$(pwd):/workdir" davidanson/markdownlint-cli2 "**/*.md"
```

The CI runs all of the above plus hassfest and HACS validation.

## Commit style

This project uses [Conventional Commits](https://www.conventionalcommits.org/). Commit messages drive automatic changelog generation and version bumping.

| Prefix      | When to use                         |
| ----------- | ----------------------------------- |
| `feat:`     | New feature or entity               |
| `fix:`      | Bug fix                             |
| `test:`     | Adding or updating tests            |
| `chore:`    | Maintenance, dependency updates     |
| `refactor:` | Code change without behavior change |
| `docs:`     | Documentation only                  |
| `ci:`       | CI/CD changes                       |

Breaking changes must include `BREAKING CHANGE:` in the commit footer.

Keep commits focused on a single concern. If a change touches both logic and tests, a single commit is fine – if it touches unrelated areas, split it.

## Pull requests

- Keep PRs focused on a single concern.
- Reference any related issue in the PR description.
- All CI checks must pass before merging: hassfest, HACS, Python linting, shell linting, and Markdown linting.

## Reporting bugs

Open an [issue](https://github.com/wielorzeczownik/ha-toya-decoder/issues) and include:

- What you did
- What you expected
- What actually happened
- Home Assistant version
- Integration version
- Relevant logs from Home Assistant (`Settings > System > Logs`)

> For security issues, read [SECURITY.md](SECURITY.md) before opening a public issue.

## License

By contributing you agree that your changes will be licensed under the [MIT License](LICENSE).
