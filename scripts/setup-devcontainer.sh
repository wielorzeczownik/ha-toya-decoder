#!/usr/bin/env bash

# Script setup
set -e
cd "$(dirname "$0")/.."

export DEVCONTAINER=1

# Install dependencies into the container's system Python environment.
if command -v dpkg >/dev/null 2>&1; then
    if ! dpkg -s libudev-dev >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y libudev-dev
    fi
fi

python3 -m pip install --upgrade uv
uv pip install --system -r requirements_dev.txt

if ! python3 - <<'PY'
try:
    import aiousbwatcher  # noqa: F401
except ImportError:
    raise SystemExit(1)
PY
then
    python3 -m pip install aiousbwatcher==1.1.1
fi
