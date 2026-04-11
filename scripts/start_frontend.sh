#!/usr/bin/env bash
set -euo pipefail
cd apps/web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
