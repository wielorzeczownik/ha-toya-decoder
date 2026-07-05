# ruff: noqa: INP001  # standalone CLI helper for CI
"""Write a version string into a manifest.json file."""

import json
import sys
from pathlib import Path


def main() -> None:
    manifest_path = sys.argv[1]
    version = sys.argv[2]
    path = Path(manifest_path)
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    data["version"] = version
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
