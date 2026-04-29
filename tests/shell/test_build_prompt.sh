#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"

TMP=$(mktemp -d); trap "rm -rf $TMP" EXIT
SD="$TMP/sess"; mkdir -p "$SD"
: > "$SD/grs-ledger.md"

# Synthetic module with ledger placeholder.
MOD="$TMP/N-FAKE.md"
cat > "$MOD" <<'EOF'
---
node_id: N-FAKE
phase: 7
hat: aggregator
exec_type: spawn
required_output_sections: [x]
---

# N-FAKE

## PROMPT TEMPLATE

Current ledger digest:
{{ledger_at_dispatch}}

Do something.
EOF

OUT=$(bash "$REPO/scripts/build-prompt.sh" --module "$MOD" --session-dir "$SD")
echo "$OUT" | grep -qF "{{ledger_at_dispatch}}" && { echo FAIL placeholder leaked; exit 1; }
echo "$OUT" | grep -q "Do something." || { echo FAIL body lost; exit 1; }

# Leaked placeholder detection
cat > "$MOD" <<'EOF'
---
node_id: N-FAKE
phase: 7
hat: aggregator
exec_type: spawn
required_output_sections: [x]
---
{{ledger_at_dispatch}}
{{undeclared_placeholder}}
EOF

set +e
bash "$REPO/scripts/build-prompt.sh" --module "$MOD" --session-dir "$SD" >/dev/null 2> "$TMP/err"
RC=$?
set -e
[ $RC -eq 3 ] || { echo "FAIL: must exit 3 on placeholder leak; got $RC"; exit 1; }
grep -q "DISPATCH-PLACEHOLDER-LEAK" "$TMP/err" || { echo FAIL diag; exit 1; }

echo "PASS: test_build_prompt.sh"
