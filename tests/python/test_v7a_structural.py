# tests/python/test_v7a_structural.py
from pathlib import Path
from scripts.verifications.v7a_structural import run, count_verbs

VERB_FIXTURES = [
    ("Compute and emit X", 2),
    ("Compute X", 1),
    ("Validate the input", 1),
    ("Read APU then write spec", 2),
]


def test_count_verbs():
    for txt, expected in VERB_FIXTURES:
        assert count_verbs(txt) == expected, txt


def test_v7a_passes_on_atomic_steps(tmp_path):
    spec = tmp_path / "x.md"
    spec.write_text(
        "## 5. Behavior\n"
        "- Step 1: Compute X\n  - input: APU-007\n  - output: X-result\n"
        "- Step 2: Validate X-result\n  - input: X-result\n  - output: validated\n"
        "## 11. Risk\n- consumes validated\n"
    )
    sm = tmp_path / "session.md"
    sm.write_text("apus:\n  - id: APU-007\n")
    r = run(spec, sm)
    assert r["status"] == "pass"


def test_v7a_fails_two_verbs(tmp_path):
    spec = tmp_path / "x.md"
    spec.write_text(
        "## 5. Behavior\n"
        "- Compute and emit X\n  - input: APU-007\n  - output: X\n"
        "## 11. Risk\n- consumes X\n"
    )
    sm = tmp_path / "session.md"
    sm.write_text("apus:\n  - id: APU-007\n")
    r = run(spec, sm)
    assert r["status"] == "fail"
    assert "non_atomic_steps" in r["details"]


def test_v7a_fails_on_dead_end(tmp_path):
    spec = tmp_path / "x.md"
    spec.write_text(
        "## 5. Behavior\n"
        "- Step 1: Compute X\n  - input: APU-007\n  - output: orphan-X\n"
        "## 11. Risk\n- nothing references it\n"
    )
    sm = tmp_path / "session.md"
    sm.write_text("apus:\n  - id: APU-007\n")
    r = run(spec, sm)
    assert r["status"] == "fail"
    assert "dead_end_outputs" in r["details"]


def test_v7a_output_referenced_in_later_block_body_passes(tmp_path):
    """F115 — output mentioned as free narrative in next step's body (not
    as `input:` field) is still considered consumed."""
    spec = tmp_path / "x.md"
    spec.write_text(
        "## 5. Behavior\n"
        "- Step 1: Compute X\n  - input: APU-007\n  - output: alpha\n"
        "- Step 2: Validate alpha after computation\n  - input: APU-008\n  - output: beta\n"
        "## 11. Risk\n- consumes beta\n"
    )
    sm = tmp_path / "session.md"
    sm.write_text("apus:\n  - id: APU-007\n  - id: APU-008\n")
    r = run(spec, sm)
    assert r["status"] == "pass", r


def test_v7a_output_used_as_input_in_later_block_passes(tmp_path):
    """F115 — explicit input chain."""
    spec = tmp_path / "x.md"
    spec.write_text(
        "## 5. Behavior\n"
        "- Step 1: Compute X\n  - input: APU-007\n  - output: alpha\n"
        "- Step 2: Validate alpha\n  - input: alpha\n  - output: beta\n"
        "## 11. Risk\n- consumes beta\n"
    )
    sm = tmp_path / "session.md"
    sm.write_text("apus:\n  - id: APU-007\n")
    assert run(spec, sm)["status"] == "pass"


def test_v7a_output_only_in_own_block_is_dead_end(tmp_path):
    """F115 — output appears only in producer block; nowhere else; flagged."""
    spec = tmp_path / "x.md"
    spec.write_text(
        "## 5. Behavior\n"
        "- Step 1: Compute orphan-X\n  - input: APU-007\n  - output: orphan-X\n"
        "## 11. Risk\n- nothing references it\n"
    )
    sm = tmp_path / "session.md"
    sm.write_text("apus:\n  - id: APU-007\n")
    r = run(spec, sm)
    assert r["status"] == "fail"
    assert "orphan-X" in r["details"]["dead_end_outputs"]


def test_v7a_fails_on_missing_precondition(tmp_path):
    spec = tmp_path / "x.md"
    spec.write_text(
        "## 5. Behavior\n"
        "- Step 1: Validate Y\n  - input: missing-Y\n  - output: ok\n"
        "## 11. Risk\n- consumes ok\n"
    )
    sm = tmp_path / "session.md"
    sm.write_text("apus: []\n")
    r = run(spec, sm)
    assert r["status"] == "fail"
    assert "missing_preconditions" in r["details"]
