#!/usr/bin/env bash
# session-md-update.sh — atomic session.md mutation (F009).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$REPO/scripts/_session_md_update.py" "$@"
