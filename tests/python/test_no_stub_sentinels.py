"""I006 — fail if SKILL.md still has STUB sentinels at final-review time."""
import re
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[2] / "SKILL.md"
SENTINEL = re.compile(r"<!-- STUB: Task \d+[^>]*-->")


def test_no_stub_sentinels():
    if not SKILL.exists():
        pytest.skip("SKILL.md not yet created")
    matches = SENTINEL.findall(SKILL.read_text())
    assert not matches, f"SKILL.md still has stub sentinels: {matches}"
