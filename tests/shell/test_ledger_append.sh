#!/usr/bin/env bash
# tests/shell/test_ledger_append.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SCRIPT="$REPO/scripts/ledger_append.py"

TMP=$(mktemp -d); trap "rm -rf $TMP" EXIT
SD="$TMP/sess"; mkdir -p "$SD/stages"
LEDGER="$SD/grs-ledger.md"; : > "$LEDGER"

# Build a fragment with annotations.
FRAG="$SD/stages/N2-DECOMPOSE-APU.md"
cat > "$FRAG" <<EOF
## output
apus:
  - APU-001: "stated"
  - APU-002: "inferred"

## annotations:
- [ann-001] correction: "Wrong wording corrected"
- [ann-002] observation: "Two distinct functional clusters"
EOF

python3 "$SCRIPT" \
  --session-dir "$SD" \
  --node-id N-DECOMPOSE-APU \
  --phase 2 \
  --cycle 1 \
  --fragment stages/N2-DECOMPOSE-APU.md \
  --hat decomposer \
  --tier medium \
  --exec-type inline \
  --score 0.82 \
  --signals '{ "apus_extracted": 14, "types_observed": 5, "source_quote_coverage_pct": 100 }' \
  --provenance-tags '[user-stated, inferred]' \
  --headline 'Extracted 14 APUs across 5 type tags'

grep -q "## ledger-entry: N-DECOMPOSE-APU \[cycle=1\]" "$LEDGER" || { echo FAIL header; exit 1; }
grep -q "node_id: N-DECOMPOSE-APU" "$LEDGER" || { echo FAIL node_id; exit 1; }
grep -q "tier: medium" "$LEDGER" || { echo FAIL tier; exit 1; }
grep -q "annotations_picked_up: \[ann-N2-DECOMPOSE-APU-001, ann-N2-DECOMPOSE-APU-002\]" "$LEDGER" \
  || { echo FAIL annotation pickup; cat "$LEDGER"; exit 1; }

# Re-running with no NEW annotations should produce a second entry with empty pickup.
python3 "$SCRIPT" \
  --session-dir "$SD" \
  --node-id N-DECOMPOSE-APU \
  --phase 2 \
  --cycle 2 \
  --fragment stages/N2-DECOMPOSE-APU.md \
  --hat decomposer \
  --tier medium \
  --exec-type inline \
  --score 0.84 \
  --signals '{}' \
  --provenance-tags '[]' \
  --headline 're-run'

# Two entries now.
COUNT=$(grep -c "^## ledger-entry: " "$LEDGER")
[ "$COUNT" -eq 2 ] || { echo "FAIL count=$COUNT"; exit 1; }

# F103 regression: backticks and $(...) in --headline must be treated as
# literal text, NOT executed. If the script ran `whoami`, the ledger would
# contain the username. We instead expect the literal characters to appear.
INJECT='headline with `whoami` and $(uname) literal'
python3 "$SCRIPT" \
  --session-dir "$SD" --node-id N-INJECT-TEST --phase 0 --cycle 99 \
  --fragment stages/N2-DECOMPOSE-APU.md --hat decomposer --tier medium \
  --exec-type inline --score 0.0 --signals '{}' --provenance-tags '[]' \
  --headline "$INJECT"

# Whoami output (e.g. "myuser") MUST NOT appear in the ledger:
WHOAMI=$(whoami)
if grep -q "headline: \".*${WHOAMI}.*\"" "$LEDGER"; then
  echo "FAIL: F103 regression — \`whoami\` was executed and substituted"; exit 1
fi
# The literal backtick text MUST appear (escaped to YAML-safe form):
grep -q 'whoami' "$LEDGER" || { echo "FAIL: F103 — literal text missing"; exit 1; }

echo "PASS: test_ledger_append.sh"
