#!/usr/bin/env bash
# finalize-spec.sh — atomic copy spec-v<N>.md → spec-final.md (F008).
set -euo pipefail

SD=""; VERSION=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --solution-dir) SD="$2"; shift 2;;
    --version)      VERSION="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

[ -d "$SD" ]      || { echo "solution dir missing" >&2; exit 2; }
[ -n "$VERSION" ] || { echo "missing --version" >&2; exit 2; }

SRC="$SD/spec-v${VERSION}.md"
DST="$SD/spec-final.md"
[ -f "$SRC" ] || { echo "source missing: $SRC" >&2; exit 3; }

TMP="$DST.tmp"
cp "$SRC" "$TMP"
sync "$TMP" 2>/dev/null || true
mv "$TMP" "$DST"
echo "wrote $DST"

# Langfuse tracing — non-blocking.
REPO="$(cd "$(dirname "$0")/.." && pwd)"
# Find the session dir whose spec-export symlink points at this solution dir.
SESSION_DIR=$(find ~/docs/epiphany/spec -maxdepth 1 -mindepth 1 -type d \
  -exec sh -c '[ "$(readlink "$1/spec-export" 2>/dev/null)" = "'"$SD"'" ] && echo "$1"' _ {} \; 2>/dev/null | head -1)
if [ -n "$SESSION_DIR" ] && [ -f "$SESSION_DIR/.langfuse_state.json" ]; then
  python3 "$REPO/scripts/langfuse_tracer.py" finalize \
    --session-dir "$SESSION_DIR" \
    --spec-path "$DST" \
    --state FINALIZED 2>/dev/null || true
fi
