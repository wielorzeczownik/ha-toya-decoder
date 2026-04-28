# Contributing to ha-toya-decoder

Thank you for considering a contribution. This document describes how to get started.

## Prerequisites

- Python 3.11+
- [ruff](https://docs.astral.sh/ruff/) for linting and formatting
- [shfmt](https://github.com/mvdan/sh) for shell script formatting
- [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2) for Markdown linting
- A Home Assistant development environment (or devcontainer)

## Project structure

- `custom_components/toya_decoder/` – Home Assistant integration source
- `scripts/bump-version.sh` – determines the next release version and updates the manifest
- `scripts/get_manifest_version.py` – reads the current version from `manifest.json`
- `scripts/set_manifest_version.py` – writes a new version to `manifest.json`

## Development setup

```bash
git clone https://github.com/wielorzeczownik/ha-toya-decoder.git
cd ha-toya-decoder
pip install -r requirements_dev.txt -r requirements_lint.txt
```

Alternatively, open the repository in VSCode – the included devcontainer provides a ready-to-use environment.

## Before submitting a PR

Run all checks locally before opening a pull request.

### With tools installed locally

```bash
ruff check .
ruff format --check .
shfmt --diff scripts/
markdownlint-cli2 "**/*.md"
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

Common prefixes:

| Prefix      | When to use                         |
| ----------- | ----------------------------------- |
| `feat:`     | New feature or entity               |
| `fix:`      | Bug fix                             |
| `chore:`    | Maintenance, dependency updates     |
| `refactor:` | Code change without behavior change |
| `docs:`     | Documentation only                  |
| `ci:`       | CI/CD changes                       |

Breaking changes must include `BREAKING CHANGE:` in the commit footer.

## Pull requests

- Keep PRs focused on a single concern.
- Reference any related issue in the PR description.
- All CI checks must pass: hassfest, HACS, Python linting, shell linting, and Markdown linting.

## Reporting bugs

Open an [issue](https://github.com/wielorzeczownik/ha-toya-decoder/issues) and include:

- What you did
- What you expected
- What actually happened
- Home Assistant version
- Integration version
- Relevant logs from Home Assistant (`Settings > System > Logs`)

> For security issues, please read [SECURITY.md](SECURITY.md) before opening a public issue.

## License

By contributing you agree that your changes will be licensed under the [MIT License](LICENSE).
