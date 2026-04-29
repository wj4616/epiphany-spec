#!/usr/bin/env bash
# spec-chunk-write.sh -- concatenate 17 section partials into spec-v<N>.md.
# STUB -- full implementation in Task 10.
set -euo pipefail

SESSION_DIR=""
VERSION="1"
SOLUTION_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --session-dir)  SESSION_DIR="$2";  shift 2 ;;
    --version)      VERSION="$2";      shift 2 ;;
    --solution-dir) SOLUTION_DIR="$2"; shift 2 ;;
    *) echo "spec-chunk-write.sh: unknown flag: $1" >&2; exit 1 ;;
  esac
done

STAGES="$SESSION_DIR/stages"
SPEC_FILE="$SOLUTION_DIR/spec-v${VERSION}.md"

# Concatenate all v<V>-section-*.md files in numeric order.
{
  for secfile in "$STAGES"/spec-v${VERSION}-section-*.md; do
    [[ -f "$secfile" ]] && cat "$secfile" && echo ""
  done
  echo "_epiphany-spec-end-marker_"
} > "$SPEC_FILE"

echo "spec-v${VERSION}.md written to $SPEC_FILE"
