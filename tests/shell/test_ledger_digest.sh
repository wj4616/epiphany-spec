#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"

TMP=$(mktemp -d); trap "rm -rf $TMP" EXIT
SD="$TMP/sess"; mkdir -p "$SD"

cat > "$SD/grs-ledger.md" <<'EOF'
preamble (ignored)

## ledger-entry: N-A [cycle=1]
body A
## ledger-entry: N-B [cycle=1]
body B
## ledger-entry: N-C [cycle=1]
body C
EOF

OUT=$(bash "$REPO/scripts/ledger-digest.sh" --session-dir "$SD" --max-entries 2 --max-bytes 1024)
echo "$OUT" | grep -q "^## ledger-entry: N-B" || { echo FAIL B; exit 1; }
echo "$OUT" | grep -q "^## ledger-entry: N-C" || { echo FAIL C; exit 1; }
echo "$OUT" | grep -q "ledger-entry: N-A"     && { echo FAIL A should be dropped; exit 1; }

# byte-cap test: tiny budget drops more entries
SHORT=$(bash "$REPO/scripts/ledger-digest.sh" --session-dir "$SD" --max-entries 8 --max-bytes 30)
COUNT=$(echo "$SHORT" | grep -c "^## ledger-entry:" || true)
[ "$COUNT" -le 1 ] || { echo "FAIL byte-cap kept too many: $COUNT"; exit 1; }

echo "PASS: test_ledger_digest.sh"
