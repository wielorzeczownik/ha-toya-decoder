import json
import sys


def main() -> None:
    manifest_path = sys.argv[1]
    version = sys.argv[2]
    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)
    data["version"] = version
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
