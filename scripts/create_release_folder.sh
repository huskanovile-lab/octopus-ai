#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$ROOT_DIR/dist/release-package"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

copy_path() {
  local p="$1"
  mkdir -p "$OUT_DIR/$(dirname "$p")"
  cp -R "$ROOT_DIR/$p" "$OUT_DIR/$p"
}

copy_path README.md
copy_path .gitignore
copy_path GITHUB_DEPLOY_AND_DOWNLOAD.md
copy_path scripts/start_backend.sh
copy_path scripts/start_frontend.sh
copy_path scripts/run_demo_session.py
copy_path scripts/create_download_bundle.sh
copy_path apps/web
copy_path services
copy_path packages
copy_path tests
copy_path infrastructure/docker-compose.yml
copy_path infrastructure/postgres/schema.sql

cd "$OUT_DIR"
zip -r ../release-package.zip . >/dev/null

echo "Created release folder: $OUT_DIR"
echo "Created zip: $ROOT_DIR/dist/release-package.zip"
