#!/usr/bin/env bash
# Runs all shell + pytest tests for epiphany-spec.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"

echo "=== pytest ==="
cd "$REPO"
python3 -m pytest tests/python -v

echo "=== shell tests ==="
for t in "$HERE"/test_*.sh; do
  echo "--- $(basename "$t") ---"
  bash "$t"
done
echo "=== ALL PASS ==="
