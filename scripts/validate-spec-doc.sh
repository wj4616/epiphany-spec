#!/usr/bin/env bash
# validate-spec-doc.sh — V-check dispatcher (§10, §22 item 5).
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

# F104+F206 — track failures; exit non-zero on any non-pass.
# (Pass-3 collapsed the FAIL/ERROR distinction since no v1 caller cares;
#  stdout still labels each check, humans can grep.)
FAIL_COUNT=0

run_check() {
  local name="$1"; local script="$2"; shift 2
  local out rc
  if out=$(python3 "$REPO/scripts/verifications/$script" "$@" 2>&1); then
    echo "$name: pass"
  else
    rc=$?
    echo "$name: fail (exit $rc)"
    FAIL_COUNT=$((FAIL_COUNT+1))
    echo "$out" | sed 's/^/    /'
  fi
}

case "$PHASE" in
  pre-grs-export)
    # V4 and V5 — fragment/trace-only.
    run_check "V4" v4_convergent_node_detection.py --spec "${SPEC:-/dev/null}" --session-md "$SM"
    run_check "V5" v5_topology_audit.py            --spec "${SPEC:-/dev/null}" --session-md "$SM"
    ;;
  post-grs-export)
    [ -f "$SPEC" ] || { echo "spec file missing" >&2; exit 2; }
    run_check "V1"  v1_apu_coverage.py               --spec "$SPEC" --session-md "$SM"
    run_check "V2"  v2_vocab_lock.py                 --spec "$SPEC" --session-md "$SM"
    run_check "V3"  v3_constraint_completeness.py    --spec "$SPEC" --session-md "$SM"
    run_check "V6"  v6_falsifiability.py             --spec "$SPEC" --session-md "$SM"
    run_check "V7a" v7a_structural.py                --spec "$SPEC" --session-md "$SM"
    run_check "V7b" v7b_intent_alignment.py          --spec "$SPEC" --session-md "$SM" --threshold "$INTENT_THRESHOLD"
    run_check "V8"  v8_file_save.py                  --spec "$SPEC" --session-md "$SM"

    echo ""
    echo "completeness:"
    PYTHONPATH="$REPO" python3 "$REPO/scripts/compute_completeness.py" --spec "$SPEC" --session-md "$SM" | sed 's/^/    /'
    ;;
  *)
    echo "unknown phase: $PHASE (use pre-grs-export or post-grs-export)" >&2
    exit 2
    ;;
esac

# F104+F206 — exit codes:
#   0 = all checks passed
#   1 = at least one check did not pass (fail OR script error; humans
#       distinguish via the labelled stdout output)
[ "$FAIL_COUNT" -eq 0 ] || exit 1
exit 0
