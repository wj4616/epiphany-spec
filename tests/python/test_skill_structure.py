import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2] / "SKILL.md"

# Required H2 section titles in order.
REQUIRED_SECTIONS = [
    "## ARCHITECTURE",
    "## TRIGGERS",
    "## HARD GATES",
    "## MODE + FLAGS",
    "## HALT STATE INVENTORY",
    "## PRC1 — PRE-RUN CHECK",
    "## SESSION INIT",
    "## PHASE CHAIN — READY-SET DISPATCH",
    "## PHASE 6 — AND-JOIN + ACTIVE BRANCHES",
    "## DYNAMIC REWRITE (D1 / D2 / D3)",
    "## PAUSE / RESUME PROTOCOL",
    "## PHASE 12 — REVIEW GATE + STATE MACHINE",
    "## EDIT-PROPAGATION ROUTING",
    "## V-CHECK BATTERY + RE-ROUTE POLICY",
    "## ANNOUNCE STRINGS",
]


def test_skill_md_exists():
    assert SKILL.exists()


def test_skill_md_has_frontmatter():
    text = SKILL.read_text()
    assert text.startswith("---\n"), "missing YAML frontmatter"
    fm_end = text.index("\n---\n", 4)
    fm = text[4:fm_end]
    for k in ("name:", "description:", "trigger:", "skill_path:"):
        assert k in fm, f"frontmatter missing {k}"


def test_skill_md_has_all_required_sections():
    text = SKILL.read_text()
    last_pos = -1
    for sec in REQUIRED_SECTIONS:
        idx = text.find("\n" + sec)
        assert idx != -1, f"missing section: {sec}"
        assert idx > last_pos, f"section {sec} out of order"
        last_pos = idx
