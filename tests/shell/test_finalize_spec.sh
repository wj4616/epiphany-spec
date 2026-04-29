#!/usr/bin/env bash
# tests/shell/test_finalize_spec.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SCRIPT="$REPO/scripts/finalize-spec.sh"

TMP=$(mktemp -d); trap "rm -rf $TMP" EXIT
SOL="$TMP/29-04-foo"; mkdir -p "$SOL"
echo "spec body" > "$SOL/spec-v3.md"

bash "$SCRIPT" --solution-dir "$SOL" --version 3
[ -f "$SOL/spec-final.md" ] || { echo FAIL final missing; exit 1; }
diff -q "$SOL/spec-v3.md" "$SOL/spec-final.md" >/dev/null

set +e
bash "$SCRIPT" --solution-dir "$SOL" --version 99
RC=$?
set -e
[ $RC -ne 0 ] || { echo FAIL must error on missing source; exit 1; }

echo "PASS: test_finalize_spec.sh"
