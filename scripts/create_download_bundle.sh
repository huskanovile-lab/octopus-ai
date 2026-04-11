#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$ROOT_DIR/dist"
mkdir -p "$OUT_DIR"

STAMP="$(date +%Y%m%d-%H%M%S)"
ZIP_FILE="$OUT_DIR/trading-ai-$STAMP.zip"
TAR_FILE="$OUT_DIR/trading-ai-$STAMP.tar.gz"

cd "$ROOT_DIR"
zip -r "$ZIP_FILE" . \
  -x ".git/*" \
  -x "dist/*" \
  -x "**/__pycache__/*" \
  -x "*.pyc" >/dev/null

tar --exclude='.git' --exclude='dist' --exclude='__pycache__' --exclude='*.pyc' -czf "$TAR_FILE" .

echo "Created:"
echo "$ZIP_FILE"
echo "$TAR_FILE"
