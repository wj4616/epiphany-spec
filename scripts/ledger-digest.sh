#!/usr/bin/env bash
# ledger-digest.sh — F106 deterministic digest. Thin wrapper.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
PYTHONPATH="$REPO" exec python3 "$REPO/scripts/_ledger_digest.py" "$@"
