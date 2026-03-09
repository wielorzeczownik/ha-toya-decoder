# Contributing to ha-toya-decoder

Thank you for considering a contribution. This document describes how to get started.

## Prerequisites

- Python 3.11+
- [ruff](https://docs.astral.sh/ruff/) for linting and formatting
- A Home Assistant development environment (or devcontainer)

## Development setup

```bash
git clone https://github.com/wielorzeczownik/ha-toya-decoder.git
cd ha-toya-decoder
pip install -r requirements_dev.txt -r requirements_lint.txt
```

Alternatively, open the repository in VSCode - the included devcontainer provides a ready-to-use environment.

## Before submitting a PR

Make sure these pass locally:

```bash
ruff check .
ruff format --check .
```

## Commit style

This project uses [Conventional Commits](https://www.conventionalcommits.org/). Commit messages drive automatic changelog generation and version bumping.

Common prefixes:

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature or entity |
| `fix:` | Bug fix |
| `chore:` | Maintenance, dependency updates |
| `refactor:` | Code change without behavior change |
| `docs:` | Documentation only |
| `style:` | Formatting, no logic change |
| `ci:` | CI/CD changes |

Breaking changes must include `BREAKING CHANGE:` in the commit footer.

## Pull requests

- Keep PRs focused on a single concern.
- Reference any related issue in the PR description.
- The CI `validators` workflow must pass (hassfest, HACS, ruff).

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
