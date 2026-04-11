#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$ROOT_DIR/dist"
mkdir -p "$OUT_DIR"

NAME="${1:-Gbg-codex-trading-ready}"
TARGET="$OUT_DIR/${NAME}.zip"

rm -f "$TARGET"
cd "$ROOT_DIR"
zip -r "$TARGET" . \
  -x ".git/*" \
  -x "dist/*" \
  -x "**/__pycache__/*" \
  -x "*.pyc" >/dev/null

echo "Created named bundle: $TARGET"
