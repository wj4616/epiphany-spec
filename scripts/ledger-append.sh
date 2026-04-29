#!/usr/bin/env bash
# ledger-append.sh — F103 fix: thin wrapper around _ledger_append.py.
# All heredoc / Bash-expansion risks eliminated.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
PYTHONPATH="$REPO" exec python3 "$REPO/scripts/_ledger_append.py" "$@"
