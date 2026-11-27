#!/usr/bin/env bash

set -euo pipefail

echo "=== Ruff: lint ==="
uv run ruff check .

echo "=== Ruff: format ==="
uv run ruff format --check .

echo "=== Mypy ==="
uv run mypy src/

echo "=== Pytest ==="
uv run pytest

echo "=== Markdown ==="
uv run mdformat --check README.md

echo "=== QA concluído com sucesso ==="
