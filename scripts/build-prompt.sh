#!/usr/bin/env bash
# build-prompt.sh — F111+I105 script-side substitution.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
PYTHONPATH="$REPO" exec python3 "$REPO/scripts/_build_prompt.py" "$@"
