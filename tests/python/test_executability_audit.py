"""I104 — automated instruction-clarity lint for SKILL.md.

Catches the F106/F107/F108 class of findings: ambiguous verbs without
algorithm references, undocumented halt codes, missing state-machine resume
clauses, etc.
"""
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "SKILL.md"

if not SKILL.exists():
    pytest.skip("SKILL.md not yet created", allow_module_level=True)

TEXT = SKILL.read_text()


def test_no_ambiguous_digest_without_algorithm_reference():
    """F106-class — `digest` and `summarize` must be paired with a script
    reference (build_prompt.py, ledger_digest.py) so the operation is
    deterministic."""
    matches = []
    for m in re.finditer(r"\b(digest|summarize)\b", TEXT, re.IGNORECASE):
        window = TEXT[m.start():m.start() + 400]
        if "ledger_digest.py" in window or "build_prompt.py" in window or "scripts/" in window:
            continue
        if re.search(r"\b" + re.escape(m.group()) + r"\.(?:sh|py)\b", window, re.IGNORECASE):
            continue
        matches.append((m.start(), m.group(), window[:80]))
    assert not matches, (
        f"Ambiguous '{matches[0][1]}' at offset {matches[0][0]}: "
        f"{matches[0][2]!r}\nMust be paired with a script reference."
    )


def test_every_halt_code_in_inventory():
    """F108-class — every [halt-…] code mentioned in SKILL.md must appear in
    the ## HALT STATE INVENTORY section's table."""
    inventory_match = re.search(
        r"## HALT STATE INVENTORY(.*?)(?=\n## |\Z)", TEXT, re.DOTALL
    )
    assert inventory_match, "## HALT STATE INVENTORY section missing"
    inventory = inventory_match.group(1)

    mentioned = set(re.findall(r"`(halt-[a-z0-9-]+)`", TEXT))
    in_inventory = set(re.findall(r"`(halt-[a-z0-9-]+)`", inventory))

    missing = mentioned - in_inventory
    assert not missing, f"Halt codes mentioned but not in inventory: {missing}"


def test_resume_sequence_covers_every_state():
    """F107-class — every state in the state-machine table must appear in
    the resume-sequence step 3 parsing rules."""
    states = re.findall(r"^\| `(RUNNING|AWAITING_\w+|FINALIZED|ABORTED)` \|",
                        TEXT, re.MULTILINE)
    states = set(states) - {"RUNNING"}
    resume_match = re.search(
        r"### Resume sequence(.*?)(?=\n### |\n## )", TEXT, re.DOTALL
    )
    assert resume_match, "### Resume sequence section missing"
    resume = resume_match.group(1)
    missing = [s for s in states if s not in resume]
    assert not missing, f"States in machine table but not in resume parsing: {missing}"


def test_no_in_memory_without_persistence_pair():
    """Finds 'in memory' claims without matching 'persisted to' / 'session.md.<X>'
    nearby — catches F014-class regressions."""
    matches = []
    for m in re.finditer(r"in memory", TEXT, re.IGNORECASE):
        window = TEXT[m.start():m.start() + 600]
        if "session.md" in window or "persisted" in window or "scripts/" in window:
            continue
        matches.append((m.start(), window[:80]))
    assert not matches, (
        f"'in memory' at offset {matches[0][0]} lacks persistence pairing: "
        f"{matches[0][1]!r}"
    )
