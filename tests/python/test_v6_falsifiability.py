# tests/python/test_v6_falsifiability.py
from pathlib import Path
from scripts.verifications.v6_falsifiability import run


def _spec(tmp_path, body):
    p = tmp_path / "x.md"
    p.write_text(body)
    return p


def _session(tmp_path):
    sm = tmp_path / "session.md"
    sm.write_text("apus: []\n")
    return sm


def test_v6_passes(tmp_path):
    spec = _spec(tmp_path,
        "## 10. Falsifiability\n"
        "### R-001 (APU-007)\n"
        "- test: deploy and observe X\n"
        "- break_attempt: feed input Y → result Z\n"
    )
    r = run(spec, _session(tmp_path))
    assert r["status"] == "pass"


def test_v6_fails_missing_test(tmp_path):
    spec = _spec(tmp_path,
        "## 10. Falsifiability\n"
        "### R-001 (APU-007)\n"
        "- break_attempt: only this\n"
    )
    r = run(spec, _session(tmp_path))
    assert r["status"] == "fail"
    assert any(b["id"] == "R-001" and "test" in b["missing"] for b in r["details"]["bad"])


def test_v6_fails_empty_break_attempt(tmp_path):
    spec = _spec(tmp_path,
        "## 10. Falsifiability\n"
        "### R-002 (APU-008)\n"
        "- test: do thing\n"
        "- break_attempt:\n"
    )
    r = run(spec, _session(tmp_path))
    assert r["status"] == "fail"


def test_v6_passes_when_section_empty(tmp_path):
    spec = _spec(tmp_path, "## 10. Falsifiability\n(no requirements yet)\n")
    r = run(spec, _session(tmp_path))
    assert r["status"] == "pass"
