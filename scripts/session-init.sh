#!/usr/bin/env bash
# session-init.sh — epiphany-spec §3 step 5 (7-step responsibility list).
#
# The orchestrator (SKILL.md):
#   - generates UUID v4 in memory
#   - asserts session dir absent
#   - then invokes this script with --session-id and other flags
# This script implements steps 2..7. Step 1's UUID generation + presence assertion
# is done by the orchestrator (the spec is explicit on this — see §3 step 1 note
# about "hold in memory; do not yet write").
#
# Usage:
#   session-init.sh \
#     --session-id <UUID-v4> \
#     --input-file <path/to/input.md> \
#     --session-base <dir e.g. ~/docs/epiphany/spec> \
#     --solution-base <dir e.g. ~/docs/solution> \
#     --mode {MINIMAL|STANDARD|DEEP} \
#     --flags "<space-separated raw flags>" \
#     --date "<DD-MM>"
set -euo pipefail

SESSION_ID=""; INPUT_FILE=""; SESSION_BASE=""; SOLUTION_BASE=""
MODE="STANDARD"; FLAGS=""; DATE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --session-id)    SESSION_ID="$2"; shift 2;;
    --input-file)    INPUT_FILE="$2"; shift 2;;
    --session-base)  SESSION_BASE="$2"; shift 2;;
    --solution-base) SOLUTION_BASE="$2"; shift 2;;
    --mode)          MODE="$2"; shift 2;;
    --flags)         FLAGS="$2"; shift 2;;
    --date)          DATE="$2"; shift 2;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

[ -n "$SESSION_ID" ]    || { echo "missing --session-id" >&2; exit 2; }
[ -f "$INPUT_FILE" ]    || { echo "input file missing: $INPUT_FILE" >&2; exit 2; }
[ -d "$SESSION_BASE" ]  || { echo "session-base missing: $SESSION_BASE" >&2; exit 2; }
[ -d "$SOLUTION_BASE" ] || { echo "solution-base missing: $SOLUTION_BASE" >&2; exit 2; }

SD="$SESSION_BASE/$SESSION_ID"

# Step 1 (defense-in-depth): assert dir absent.
if [ -e "$SD" ]; then
  echo "[SESSION-ISOLATION-FAIL — $SD already exists]" >&2
  exit 3
fi

# Step 2: create session dir + stages/ subdir ONLY.
mkdir -p "$SD/stages"

# Step 3: write verbatim input.md (HG2).
cp "$INPUT_FILE" "$SD/input.md"

# Step 5 (compute topic_slug + spec-output dir BEFORE writing session.md so we
# can persist the slug; algorithm authority = scripts/seed_similarity.py).
REPO="$(cd "$(dirname "$0")/.." && pwd)"
# Read input.md via file path to avoid ARG_MAX overflow from $(cat ...)
TOPIC_SLUG=$(PYTHONPATH="$REPO" python3 -c "
import sys
from scripts.seed_similarity import slugify
print(slugify(open(sys.argv[1]).read()))
" "$SD/input.md")
# Use PYTHONPATH so `from scripts.seed_similarity import ...` resolves.
TRUNCATED_SLUG=$(PYTHONPATH="$REPO" python3 -c "
import sys
from scripts.seed_similarity import truncate_at_word_boundary
print(truncate_at_word_boundary(sys.argv[1], 40))
" "$TOPIC_SLUG")

OUT_BASE="$SOLUTION_BASE/${DATE}-${TRUNCATED_SLUG}"
SUFFIX=""; N=2
TARGET="$OUT_BASE"
while [ -e "$TARGET" ]; do
  TARGET="${OUT_BASE}-${N}"
  N=$((N+1))
done
mkdir "$TARGET" || { echo "solution dir collision: $TARGET" >&2; exit 3; }
SOLUTION_DIR="$TARGET"

# Step 4: initialize session.md with all default fields + captured session_id.
STOPWORDS_HASH=$(python3 "$REPO/scripts/seed_similarity.py" --hash)
TIMESTAMP=$(date '+%Y-%m-%dT%H:%M:%SZ')

# F010 — compute active_branches deterministically from MODE so there is no
# transient empty-state window between session-init and the first ready-set.
case "$MODE" in
  MINIMAL)  ACTIVE_BRANCHES='[SPREADING]' ;;
  STANDARD) ACTIVE_BRANCHES='[SPREADING, LATERAL]' ;;
  DEEP)     ACTIVE_BRANCHES='[SPREADING, LATERAL, SIMULATION, ADVERSARIAL]' ;;
  *) echo "unknown mode: $MODE" >&2; exit 2 ;;
esac

# Sanitize FLAGS for YAML double-quoted string: escape backslash + double-quote,
# strip newlines and control characters.
SANITIZED_FLAGS=$(echo "$FLAGS" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n\r' | tr -c '[:print:]\t' ' ')
cat > "$SD/session.md" <<EOF
session_id: $SESSION_ID
state: RUNNING
scale: $MODE
flags: "$SANITIZED_FLAGS"
topic_slug: "$TOPIC_SLUG"
input_kind: ""
active_branches: $ACTIVE_BRANCHES
spawn_count: 0
current_version: 0
final_version: null
conflict_ledger: []
gate_history: []
open_questions_queue: []
idea_refinement_history: {}
cross_run_seed:
  injected_nodes: []
  source_sessions: []
  scan_ts: ""
  stopwords_hash: $STOPWORDS_HASH
write_progress: {}
verification_log: []
handoff_bundle: {}
locked_vocabulary: []
apus: []
pre_idea_id_map: {}
convergent_nodes: []
phase_budgets: {}
phase_actuals: {}
section_overrides: {}
abort_metadata: null
created_ts: \"$TIMESTAMP\"
pause_ts: null
solution_dir: "$SOLUTION_DIR"
EOF

# Backup discipline (§3): atomic backup at write time.
cp "$SD/session.md" "$SD/stages/session.md.bak"

# Step 6: spec-export symlink → solution dir.
ln -s "$SOLUTION_DIR" "$SD/spec-export"

# Step 7: empty grs-ledger.md, topology-trace.md.
: > "$SD/grs-ledger.md"
: > "$SD/topology-trace.md"

# Print resolved session dir on stdout line 1 for orchestrator capture.
echo "$SD"
echo "topic_slug: $TOPIC_SLUG"
echo "solution_dir: $SOLUTION_DIR"

# Langfuse tracing — non-blocking, errors are suppressed.
python3 "$REPO/scripts/langfuse_tracer.py" init --session-dir "$SD" 2>/dev/null || true
