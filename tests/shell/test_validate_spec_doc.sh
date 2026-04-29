#!/usr/bin/env bash
# tests/shell/test_validate_spec_doc.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SCRIPT="$REPO/scripts/validate-spec-doc.sh"

TMP=$(mktemp -d); trap "rm -rf $TMP" EXIT
SD="$TMP/sess"; mkdir -p "$SD/stages"
cp "$REPO/tests/fixtures/specs/valid_v1.md" "$SD/stages/spec-v1-section-test.md"

# Build a minimal session.md the V-checks can read
cat > "$SD/session.md" <<EOF
scale: STANDARD
current_version: 1
write_progress:
  spec_v1: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
apus: []
locked_vocabulary: []
constraint_inventory:
  enumeration_complete: true
conflict_ledger: []
vague_items: []
input_md_path: $SD/input.md
convergent_nodes:
  - {concept: x, signal_strength: 2}
active_branches: [SPREADING]
EOF
echo "word " > "$SD/input.md"; for i in $(seq 1 200); do echo "word " >> "$SD/input.md"; done

# Create N-SPEC-AUDIT-SEMANTIC.md so V7b passes.
cat > "$SD/stages/N-SPEC-AUDIT-SEMANTIC.md" <<'EOF'
intent_alignment_score: 0.85
divergence_list: []
EOF

cp "$REPO/tests/fixtures/specs/valid_v1.md" "$TMP/spec-v1.md"
# Pad to 12 KB+ for STANDARD threshold (2000 lines of ~10 bytes each ≈ 20 KB)
for _ in $(seq 1 2000); do echo "padding " >> "$TMP/spec-v1.md"; done
echo "<!-- end:spec-v1 -->" >> "$TMP/spec-v1.md"

# Pre-GRS-export phase: V4 + V5 only.
bash "$SCRIPT" --phase pre-grs-export --session-dir "$SD" > "$TMP/pre.out"
grep -q "V4: pass" "$TMP/pre.out" || { echo FAIL V4; cat "$TMP/pre.out"; exit 1; }
grep -q "V5: pass" "$TMP/pre.out" || { echo FAIL V5; cat "$TMP/pre.out"; exit 1; }
grep -q "V1: "      "$TMP/pre.out" && { echo "FAIL: V1 should not run pre-GRS-export"; exit 1; }

# Post-GRS-export: spec-file-dependent battery.
bash "$SCRIPT" --phase post-grs-export --session-dir "$SD" --spec "$TMP/spec-v1.md" > "$TMP/post.out"
for chk in V1 V2 V3 V6 V7a V7b V8; do
  grep -q "$chk: " "$TMP/post.out" || { echo "FAIL: $chk missing"; cat "$TMP/post.out"; exit 1; }
done
echo "PASS: test_validate_spec_doc.sh"
