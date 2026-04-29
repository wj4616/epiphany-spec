#!/usr/bin/env bash
# tests/shell/test_session_init.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SCRIPT="$REPO/scripts/session-init.sh"

TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT

UUID="00000000-0000-4000-8000-000000000001"
INPUT="$TMP/input.md"
echo "Design a really small spec for a thing." > "$INPUT"

# Pre-condition: directory absence is asserted by orchestrator BEFORE calling
# this script. We pre-create the parent.
SESSION_BASE="$TMP/spec"
SOLUTION_BASE="$TMP/solution"
mkdir -p "$SESSION_BASE" "$SOLUTION_BASE"

bash "$SCRIPT" \
  --session-id "$UUID" \
  --input-file "$INPUT" \
  --session-base "$SESSION_BASE" \
  --solution-base "$SOLUTION_BASE" \
  --mode STANDARD \
  --flags "" \
  --date "29-04" \
  > "$TMP/init.out"

SD="$SESSION_BASE/$UUID"
[ -d "$SD/stages" ] || { echo "FAIL: stages dir missing"; exit 1; }
[ -f "$SD/input.md" ] || { echo "FAIL: input.md missing"; exit 1; }
[ -f "$SD/session.md" ] || { echo "FAIL: session.md missing"; exit 1; }
[ -f "$SD/grs-ledger.md" ] || { echo "FAIL: grs-ledger.md missing"; exit 1; }
[ -f "$SD/topology-trace.md" ] || { echo "FAIL: topology-trace.md missing"; exit 1; }
[ ! -s "$SD/grs-ledger.md" ] || { echo "FAIL: grs-ledger.md not empty"; exit 1; }
[ ! -s "$SD/topology-trace.md" ] || { echo "FAIL: topology-trace.md not empty"; exit 1; }
[ -L "$SD/spec-export" ] || { echo "FAIL: spec-export not a symlink"; exit 1; }

# input.md must be byte-identical to original
diff -q "$INPUT" "$SD/input.md" >/dev/null

# session.md must contain session_id, state: RUNNING, topic_slug
grep -q "session_id: $UUID" "$SD/session.md"
grep -q "state: RUNNING"      "$SD/session.md"
grep -q "topic_slug:"         "$SD/session.md"
grep -q "scale: STANDARD"     "$SD/session.md"

# F116 — verify F010 active_branches deterministic init AND F014 spawn_count: 0
grep -qE "active_branches: \[?SPREADING,? *LATERAL\]?" "$SD/session.md" \
  || { echo "FAIL: active_branches"; cat "$SD/session.md"; exit 1; }
grep -q "spawn_count: 0" "$SD/session.md" \
  || { echo "FAIL: spawn_count init"; exit 1; }

# Parametric variant: MINIMAL must yield [SPREADING] only.
UUID2="00000000-0000-4000-8000-000000000002"
bash "$SCRIPT" --session-id "$UUID2" --input-file "$INPUT" \
  --session-base "$SESSION_BASE" --solution-base "$SOLUTION_BASE" \
  --mode MINIMAL --flags "" --date "29-04" >/dev/null
SD2="$SESSION_BASE/$UUID2"
grep -qE "active_branches: \[SPREADING\]" "$SD2/session.md" \
  || { echo "FAIL: MINIMAL active_branches"; exit 1; }

# DEEP must yield all 4 branches.
UUID3="00000000-0000-4000-8000-000000000003"
bash "$SCRIPT" --session-id "$UUID3" --input-file "$INPUT" \
  --session-base "$SESSION_BASE" --solution-base "$SOLUTION_BASE" \
  --mode DEEP --flags "" --date "29-04" >/dev/null
SD3="$SESSION_BASE/$UUID3"
grep -qE "active_branches: \[SPREADING,? *LATERAL,? *SIMULATION,? *ADVERSARIAL\]" "$SD3/session.md" \
  || { echo "FAIL: DEEP active_branches"; cat "$SD3/session.md"; exit 1; }

# Idempotency: re-running with same UUID MUST fail (collision detection in orchestrator,
# but session-init asserts the dir is empty/absent itself as defense-in-depth).
set +e
bash "$SCRIPT" \
  --session-id "$UUID" \
  --input-file "$INPUT" \
  --session-base "$SESSION_BASE" \
  --solution-base "$SOLUTION_BASE" \
  --mode STANDARD \
  --flags "" \
  --date "29-04"
RC=$?
set -e
[ $RC -ne 0 ] || { echo "FAIL: re-run did not error"; exit 1; }

echo "PASS: test_session_init.sh"
