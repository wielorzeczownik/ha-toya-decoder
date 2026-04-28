import json
import sys


def main() -> None:
    manifest_path = sys.argv[1]
    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)
    version = str(data.get("version", "")).strip()
    if not version:
        print("Missing version in manifest.json", file=sys.stderr)
        sys.exit(1)
    print(version)


if __name__ == "__main__":
    main()
