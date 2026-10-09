#!/usr/bin/env bash
set -euo pipefail

curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"

uv python install 3.12

# pyproject.toml does not exist until Day 2 — guard so the first build succeeds
if [ -f pyproject.toml ]; then
  uv sync --all-extras --dev
fi

mkdir -p data/raw
