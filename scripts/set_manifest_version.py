# ruff: noqa: INP001  # standalone CLI helper for CI
"""Write a version string into a manifest.json file."""

import json
import re
import sys
from pathlib import Path

_VERSION_KEY = re.compile(r'("version"\s*:\s*")[^"]*(")')


def main() -> None:
    manifest_path = sys.argv[1]
    version = sys.argv[2]
    path = Path(manifest_path)
    text = path.read_text(encoding="utf-8")

    new_text, count = _VERSION_KEY.subn(rf"\g<1>{version}\g<2>", text, count=1)
    if count != 1:
        sys.exit(f"No version key found in {manifest_path}")
    if json.loads(new_text)["version"] != version:
        sys.exit(f"Failed to set version in {manifest_path}")

    path.write_text(new_text, encoding="utf-8")


if __name__ == "__main__":
    main()
