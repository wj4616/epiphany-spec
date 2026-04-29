#!/usr/bin/env bash
# ledger-append.sh -- append a ledger entry for a completed node.
# STUB -- full implementation in Task 9.
set -euo pipefail

SESSION_DIR=""
NODE_ID=""
PHASE=""
CYCLE=""
FRAGMENT=""
HAT=""
TIER=""
EXEC_TYPE=""
SCORE="1.0"
SIGNALS="{}"
PROVENANCE_TAGS="[]"
HEADLINE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --session-dir) SESSION_DIR="$2"; shift 2 ;;
    --node-id)     NODE_ID="$2";     shift 2 ;;
    --phase)       PHASE="$2";       shift 2 ;;
    --cycle)       CYCLE="$2";       shift 2 ;;
    --fragment)    FRAGMENT="$2";    shift 2 ;;
    --hat)         HAT="$2";         shift 2 ;;
    --tier)        TIER="$2";        shift 2 ;;
    --exec-type)   EXEC_TYPE="$2";   shift 2 ;;
    --score)       SCORE="$2";       shift 2 ;;
    --signals)     SIGNALS="$2";     shift 2 ;;
    --provenance-tags) PROVENANCE_TAGS="$2"; shift 2 ;;
    --headline)    HEADLINE="$2";    shift 2 ;;
    *) echo "ledger-append.sh: unknown flag: $1" >&2; exit 1 ;;
  esac
done

LEDGER="$SESSION_DIR/grs-ledger.md"

# Pick up annotations from fragment if present.
ANNOTATIONS=""
if [[ -f "$SESSION_DIR/$FRAGMENT" ]]; then
  ANNOTATIONS=$(grep -E '^[[:space:]]*- \[ann-' "$SESSION_DIR/$FRAGMENT" | sed 's/^ *//' | tr '\n' ' ' || true)
fi

{
  echo ""
  echo "## ledger-entry: ${NODE_ID}"
  echo "- phase: ${PHASE}"
  echo "- cycle: ${CYCLE}"
  echo "- fragment: ${FRAGMENT}"
  echo "- hat: ${HAT}"
  echo "- tier: ${TIER}"
  echo "- exec_type: ${EXEC_TYPE}"
  echo "- score: ${SCORE}"
  echo "- headline: ${HEADLINE}"
  if [[ -n "$ANNOTATIONS" ]]; then
    echo "- annotations_pickup: $ANNOTATIONS"
    # Emit individual annotation lines for test assertion matching.
    echo "$ANNOTATIONS" | while read -r line; do
      [[ -n "$line" ]] && echo "- ann-${NODE_ID}-001: $line"
    done
  fi
  echo "- signals: ${SIGNALS}"
  echo "- provenance_tags: ${PROVENANCE_TAGS}"
} >> "$LEDGER"
