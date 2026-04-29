#!/usr/bin/env bash
# tests/shell/test_spec_chunk_write.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SCRIPT="$REPO/scripts/spec-chunk-write.sh"

TMP=$(mktemp -d); trap "rm -rf $TMP" EXIT
SD="$TMP/sess"; mkdir -p "$SD/stages"
SOL="$TMP/solution/29-04-foo"; mkdir -p "$SOL"
ln -s "$SOL" "$SD/spec-export"

for i in $(seq -w 01 17); do
  echo "## section $i" > "$SD/stages/spec-v1-section-$i.md"
  echo "body $i"      >> "$SD/stages/spec-v1-section-$i.md"
done

bash "$SCRIPT" --session-dir "$SD" --version 1 --solution-dir "$SOL"

# Both files exist
[ -f "$SD/stages/N-GRS-EXPORT-v1.md" ] || { echo FAIL canonical missing; exit 1; }
[ -f "$SOL/spec-v1.md" ]               || { echo FAIL user-editable missing; exit 1; }

# Final-line marker present on both
tail -n 1 "$SD/stages/N-GRS-EXPORT-v1.md" | grep -q "<!-- end:spec-v1 -->" \
  || { echo FAIL canonical marker; exit 1; }
tail -n 1 "$SOL/spec-v1.md" | grep -q "<!-- end:spec-v1 -->" \
  || { echo FAIL user marker; exit 1; }

# All 17 section headings present
COUNT=$(grep -c "^## section " "$SOL/spec-v1.md")
[ "$COUNT" -eq 17 ] || { echo "FAIL count=$COUNT"; exit 1; }

# Refusal when a section file is missing
rm "$SD/stages/spec-v1-section-09.md"
set +e
bash "$SCRIPT" --session-dir "$SD" --version 1 --solution-dir "$SOL"
RC=$?
set -e
[ $RC -ne 0 ] || { echo FAIL must-error-on-missing-section; exit 1; }

# F007 --xml smoke: regenerate partials, run with --xml, expect <spec ...>
# wrapper above first section and </spec> after the marker.
for i in $(seq -w 01 17); do
  echo "## section $i" > "$SD/stages/spec-v1-section-$i.md"
done
bash "$SCRIPT" --session-dir "$SD" --version 1 --solution-dir "$SOL" \
  --xml --session-id "test-uuid" --scale STANDARD
head -1 "$SOL/spec-v1.md" | grep -q '<spec source="epiphany-spec"' \
  || { echo FAIL --xml opening; exit 1; }
tail -1 "$SOL/spec-v1.md" | grep -q '</spec>' \
  || { echo FAIL --xml closing; exit 1; }

echo "PASS: test_spec_chunk_write.sh"
