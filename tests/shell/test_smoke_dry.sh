#!/usr/bin/env bash
# tests/shell/test_smoke_dry.sh — wires together init → ledger → chunk-write → validate
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"

TMP=$(mktemp -d); trap "rm -rf $TMP" EXIT
mkdir -p "$TMP/spec" "$TMP/solution"

UUID="00000000-0000-4000-8000-000000000001"
INPUT="$REPO/tests/fixtures/inputs/raw_simple.md"
DATE="29-04"

# 1. session-init.sh
bash "$REPO/scripts/session-init.sh" \
  --session-id "$UUID" \
  --input-file "$INPUT" \
  --session-base "$TMP/spec" \
  --solution-base "$TMP/solution" \
  --mode STANDARD --flags "" --date "$DATE" >/dev/null

SD="$TMP/spec/$UUID"
# session-init.sh writes the resolved solution_dir into session.md — read it
# directly rather than reconstructing from topic_slug (which is the un-truncated
# form; the dir uses the truncated form per §11).
SOL=$(grep '^solution_dir:' "$SD/session.md" | cut -d: -f2- | tr -d ' ')
[ -d "$SOL" ] || { echo FAIL: solution dir missing; exit 1; }

# 2. PRC1 (skip module checks since modules exist already; full check)
python3 "$REPO/scripts/validate-graph.py" --session-dir "$SD" --allowed-solution-root "$TMP" || { echo FAIL: PRC1; exit 1; }

# 3. Synthesize one ledger entry to prove ledger-append works
mkdir -p "$SD/stages"
cat > "$SD/stages/N0-INTAKE.md" <<EOF
## output
input_kind: raw
processed_input_path: stages/00-processed-input.md
headline: smoke test

## annotations:
- [ann-001] observation: "Smoke test annotation"
EOF
python3 "$REPO/scripts/ledger_append.py" \
  --session-dir "$SD" --node-id N-INTAKE --phase 0 --cycle 1 \
  --fragment stages/N0-INTAKE.md --hat intake --tier medium --exec-type inline \
  --score 1.0 --signals '{}' --provenance-tags '[]' --headline 'smoke'
grep -q "ledger-entry: N-INTAKE" "$SD/grs-ledger.md" || { echo FAIL ledger; exit 1; }
grep -q "ann-N0-INTAKE-001" "$SD/grs-ledger.md" || { echo FAIL annotation pickup; exit 1; }

# 4. Synthesize 17 spec section partials and chunk-write
for i in $(seq -w 01 17); do
  cat > "$SD/stages/spec-v1-section-$i.md" <<EOF
## section-$i
- placeholder body for section $i
- [APU-001] placeholder citation
EOF
done
# Pad section 5 so post-concat size > STANDARD threshold (12 KB) — V8 needs this.
set +o pipefail  # yes|head produces expected SIGPIPE
yes "padding line " | head -n 2000 >> "$SD/stages/spec-v1-section-05.md"
set -o pipefail

bash "$REPO/scripts/spec-chunk-write.sh" \
  --session-dir "$SD" --version 1 --solution-dir "$SOL" >/dev/null
[ -f "$SD/stages/N-GRS-EXPORT-v1.md" ] || { echo FAIL canonical; exit 1; }
[ -f "$SOL/spec-v1.md" ]               || { echo FAIL user-editable; exit 1; }

# 5. Pre-grs-export V-checks: V4, V5
# V4 needs convergent_nodes; V5 needs trace contents — pre-populate session.md.
python3 -c "
import yaml; from pathlib import Path
sd = Path('$SD')
sm = yaml.safe_load((sd/'session.md').read_text()) or {}
sm['convergent_nodes'] = [{'concept': 'x', 'signal_strength': 2}]
sm['active_branches'] = ['SPREADING']
sm['scale'] = 'STANDARD'
sm['current_version'] = 1
sm['write_progress'] = {'spec_v1': list(range(1, 18))}
sm['apus'] = [{'id': 'APU-001'}]
sm['locked_vocabulary'] = []
sm['constraint_inventory'] = {'enumeration_complete': True}
sm['conflict_ledger'] = []
sm['vague_items'] = []
sm['input_md_path'] = str(sd / 'input.md')
(sd/'session.md').write_text(yaml.safe_dump(sm))
"
# Re-quote created_ts since yaml.safe_dump strips quotes (YAML auto-parses timestamps)
sed -i 's/^created_ts: \(.*\)$/created_ts: "\1"/' "$SD/session.md"
bash "$REPO/scripts/validate-spec-doc.sh" --phase pre-grs-export --session-dir "$SD" > "$TMP/pre.out"
grep -q "V4: pass" "$TMP/pre.out" || { echo FAIL V4; cat "$TMP/pre.out"; exit 1; }
grep -q "V5: pass" "$TMP/pre.out" || { echo FAIL V5; cat "$TMP/pre.out"; exit 1; }

# 6. Mock the N-SPEC-AUDIT-SEMANTIC fragment for V7b
cat > "$SD/stages/N-SPEC-AUDIT-SEMANTIC.md" <<EOF
intent_alignment_score: 0.85
divergence_list: []
EOF

# 7. Post-grs-export V-checks (allow failures on synthetic content)
set +e
bash "$REPO/scripts/validate-spec-doc.sh" --phase post-grs-export \
  --session-dir "$SD" --spec "$SOL/spec-v1.md" > "$TMP/post.out" 2>&1
_POST_EC=$?
set -e
for chk in V1 V2 V3 V6 V7a V7b V8; do
  grep -q "$chk: " "$TMP/post.out" || { echo "FAIL: $chk missing"; cat "$TMP/post.out"; exit 1; }
done

echo "PASS: test_smoke_dry.sh"
