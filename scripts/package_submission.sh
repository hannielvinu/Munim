#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
"${PYTHON:-python}" scripts/build_submission.py
"${PYTHON:-python}" scripts/package_submission.py
"${PYTHON:-python}" submission/check.py
