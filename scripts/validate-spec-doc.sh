#!/usr/bin/env bash
# validate-spec-doc.sh — V-check dispatcher (§10, §22 item 5).
# I302 — reads checks from scripts/verifications/manifest.json instead of
# hardcoding. Adding/removing a V-check now only requires editing JSON.
set -euo pipefail

PHASE=""; SD=""; SPEC=""; INTENT_THRESHOLD="0.7"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --phase)         PHASE="$2"; shift 2;;
    --session-dir)   SD="$2"; shift 2;;
    --spec)          SPEC="$2"; shift 2;;
    --intent-threshold) INTENT_THRESHOLD="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

[ -d "$SD" ] || { echo "session dir missing" >&2; exit 2; }
SM="$SD/session.md"

REPO="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$REPO/scripts/verifications/manifest.json"

FAIL_COUNT=0

run_check() {
  local name="$1"; local script="$2"; shift 2
  local module="scripts.verifications.${script%.py}"
  local out rc
  if out=$(PYTHONPATH="$REPO" python3 -m "$module" "$@" 2>&1); then
    echo "$name: pass"
  else
    rc=$?
    echo "$name: fail (exit $rc)"
    FAIL_COUNT=$((FAIL_COUNT+1))
    echo "$out" | sed 's/^/    /'
  fi
}

# I302 — dispatch from manifest instead of hardcoded case block.
# Use process substitution (< <(...)) so the while loop runs in the
# parent shell; FAIL_COUNT mutations persist.  PHASE and MANIFEST are
# passed as argv to the inline Python so single-quote / shell-meta
# characters in user-supplied --phase cannot escape the Python string.
while read name script; do
    if [ "$name" = "V7b" ]; then
        run_check "$name" "$script" --spec "$SPEC" --session-md "$SM" --threshold "$INTENT_THRESHOLD"
    else
        run_check "$name" "$script" --spec "${SPEC:-/dev/null}" --session-md "$SM"
    fi
done < <(python3 -c "
import json, sys
m = json.load(open(sys.argv[1]))
for c in m['checks']:
    if c['phase'] == sys.argv[2]:
        print(c['name'], c['script'])
" "$MANIFEST" "$PHASE")

[ "$FAIL_COUNT" -eq 0 ] || exit 1
exit 0
