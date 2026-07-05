# ruff: noqa: INP001, T201  # standalone CLI helper for CI; prints to stdout
"""Print the version field from a manifest.json file."""

import json
import sys
from pathlib import Path


def main() -> None:
    manifest_path = sys.argv[1]
    with Path(manifest_path).open(encoding="utf-8") as f:
        data = json.load(f)
    version = str(data.get("version", "")).strip()
    if not version:
        print("Missing version in manifest.json", file=sys.stderr)
        sys.exit(1)
    print(version)


if __name__ == "__main__":
    main()
