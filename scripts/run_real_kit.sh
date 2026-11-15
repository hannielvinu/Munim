#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export MUNIM_KIT=official
"${PYTHON:-python}" scripts/run_real_kit.py

