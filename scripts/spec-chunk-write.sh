#!/usr/bin/env bash
# spec-chunk-write.sh — concatenate 17 spec sections + final-line marker (§11).
set -euo pipefail

SD=""; VERSION=""; SOLUTION_DIR=""; XML_WRAP=0; SESSION_ID=""; SCALE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --session-dir)  SD="$2"; shift 2;;
    --version)      VERSION="$2"; shift 2;;
    --solution-dir) SOLUTION_DIR="$2"; shift 2;;
    --xml)          XML_WRAP=1; shift;;
    --session-id)   SESSION_ID="$2"; shift 2;;   # required when --xml
    --scale)        SCALE="$2"; shift 2;;        # required when --xml
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

[ -d "$SD" ]           || { echo "session dir missing" >&2; exit 2; }
[ -n "$VERSION" ]      || { echo "missing --version" >&2; exit 2; }
[ -d "$SOLUTION_DIR" ] || { echo "solution dir missing" >&2; exit 2; }
if [ "$XML_WRAP" -eq 1 ]; then
  [ -n "$SESSION_ID" ] || { echo "--xml requires --session-id" >&2; exit 2; }
  [ -n "$SCALE" ]      || { echo "--xml requires --scale" >&2; exit 2; }
fi

CANONICAL="$SD/stages/N-GRS-EXPORT-v${VERSION}.md"
USER_FILE="$SOLUTION_DIR/spec-v${VERSION}.md"

# Verify all 17 partials exist.
for i in $(seq -w 01 17); do
  P="$SD/stages/spec-v${VERSION}-section-${i}.md"
  [ -f "$P" ] || { echo "missing partial: $P" >&2; exit 3; }
done

# Concatenate.
TMP_OUT=$(mktemp)
if [ "$XML_WRAP" -eq 1 ]; then
  echo "<spec source=\"epiphany-spec\" session_id=\"$SESSION_ID\" version=\"$VERSION\" scale=\"$SCALE\">" >> "$TMP_OUT"
fi
for i in $(seq -w 01 17); do
  cat "$SD/stages/spec-v${VERSION}-section-${i}.md" >> "$TMP_OUT"
  echo "" >> "$TMP_OUT"
done
echo "<!-- end:spec-v${VERSION} -->" >> "$TMP_OUT"
if [ "$XML_WRAP" -eq 1 ]; then
  echo "</spec>" >> "$TMP_OUT"
fi

# Atomic copy to canonical, then user-editable.
cp "$TMP_OUT" "$CANONICAL"
cp "$TMP_OUT" "$USER_FILE"
rm "$TMP_OUT"

echo "wrote $CANONICAL"
echo "wrote $USER_FILE"
