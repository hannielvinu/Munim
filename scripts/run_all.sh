#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-python}"
"$PYTHON" -m arena.tune
"$PYTHON" -m pytest -q
(cd web && npm ci && npm run build)
"$PYTHON" scripts/build_submission.py
echo "Run python -m uvicorn api.main:app --host 127.0.0.1 --port 8000, then scripts/make_video.sh"

