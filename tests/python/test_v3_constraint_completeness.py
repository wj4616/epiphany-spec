# tests/python/test_v3_constraint_completeness.py
import yaml
from pathlib import Path
from scripts.verifications.v3_constraint_completeness import run

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "specs"


def _session(tmp_path, *, enumeration_complete=True, conflicts=None, vague=None,
             input_word_count=200):
    sm = tmp_path / "session.md"
    inp = tmp_path / "input.md"
    inp.write_text("word " * input_word_count)
    sm.write_text(yaml.safe_dump({
        "constraint_inventory": {"enumeration_complete": enumeration_complete},
        "conflict_ledger": conflicts or [],
        "vague_items": vague or [],
        "input_md_path": str(inp),
    }))
    return sm


def test_v3_passes_with_both_axes_and_enumeration_complete(tmp_path):
    spec = tmp_path / "ok.md"
    spec.write_text(
        "## 7. Constraints\n"
        "### C-001 [statedness:Hard, severity:must, APU-007]\n- text\n"
    )
    sm = _session(tmp_path)
    r = run(spec, sm)
    assert r["status"] == "pass"


def test_v3_fails_when_severity_missing(tmp_path):
    sm = _session(tmp_path)
    r = run(FIX / "missing_constraint_axis.md", sm)
    assert r["status"] == "fail"
    bad = r["details"]["constraints_missing_axis"]
    assert any(c["id"] == "C-002" for c in bad)


def test_v3_fails_when_enumeration_not_complete(tmp_path):
    spec = tmp_path / "ok.md"
    spec.write_text("## 7. Constraints\n### C-001 [statedness:Hard, severity:must, APU-001]\n")
    sm = _session(tmp_path, enumeration_complete=False)
    r = run(spec, sm)
    assert r["status"] == "fail"
    assert r["details"]["enumeration_complete"] is False


def test_v3_emits_conflict_detection_suspect_warning(tmp_path):
    spec = tmp_path / "ok.md"
    spec.write_text("## 7. Constraints\n### C-001 [statedness:Hard, severity:must, APU-001]\n")
    sm = _session(tmp_path, conflicts=[], vague=[], input_word_count=80)
    r = run(spec, sm)
    assert r["status"] == "pass"
    assert any("CONFLICT-DETECTION-SUSPECT" in w for w in r["details"].get("warnings", []))


def test_v3_no_warning_below_50_words(tmp_path):
    spec = tmp_path / "ok.md"
    spec.write_text("## 7. Constraints\n### C-001 [statedness:Hard, severity:must, APU-001]\n")
    sm = _session(tmp_path, conflicts=[], vague=[], input_word_count=10)
    r = run(spec, sm)
    assert r["status"] == "pass"
    assert not r["details"].get("warnings")
