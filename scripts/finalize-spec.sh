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
