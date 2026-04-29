#!/usr/bin/env bash
# tests/shell/test_session_md_update.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SCRIPT="$REPO/scripts/session_md_update.py"

TMP=$(mktemp -d); trap "rm -rf $TMP" EXIT
SD="$TMP/sess"; mkdir -p "$SD/stages"
cat > "$SD/session.md" <<EOF
session_id: abc
state: RUNNING
spawn_count: 0
phase_actuals: {}
EOF

python3 "$SCRIPT" --session-dir "$SD" --field state --value AWAITING_GATE
grep -q "state: AWAITING_GATE" "$SD/session.md" || { echo FAIL state; exit 1; }
[ -f "$SD/stages/session.md.bak" ] || { echo FAIL bak; exit 1; }

python3 "$SCRIPT" --session-dir "$SD" --increment spawn_count
grep -q "spawn_count: 1" "$SD/session.md" || { echo FAIL increment; exit 1; }

[ ! -f "$SD/stages/session.md.tmp" ] || { echo FAIL leftover tmp; exit 1; }
echo "PASS: test_session_md_update.sh"
