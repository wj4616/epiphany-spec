# tests/python/test_v1_apu_coverage.py — F207 merged
import yaml
from pathlib import Path
from scripts.verifications.v1_apu_coverage import run

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "specs"


def _session(tmp_path, apu_ids):
    sm = tmp_path / "session.md"
    sm.write_text(yaml.safe_dump({"apus": [{"id": a} for a in apu_ids]}))
    return sm


def test_v1_passes_on_valid_spec_with_all_apus_cited(tmp_path):
    sm = _session(tmp_path, ["APU-001", "APU-002", "APU-003"])
    assert run(FIX / "valid_v1.md", sm)["status"] == "pass"


def test_v1_fails_when_section_3_to_11_missing_citation(tmp_path):
    sm = _session(tmp_path, [])  # no APUs declared = no orphan check
    r = run(FIX / "missing_apu_citation.md", sm)
    assert r["status"] == "fail"
    assert 7 in r["details"]["sections_without_citation"]
    assert r["details"]["uncited_apus"] == []


def test_v1_fails_on_orphan_apu(tmp_path):
    # APU-099 declared but not in spec body → orphan.
    sm = _session(tmp_path, ["APU-001", "APU-099"])
    r = run(FIX / "valid_v1.md", sm)
    assert r["status"] == "fail"
    assert "APU-099" in r["details"]["uncited_apus"]
    assert r["details"]["sections_without_citation"] == []


def test_v1_handles_bare_references(tmp_path):
    spec = tmp_path / "bare.md"
    spec.write_text(
        "## 14. Decision Log\n"
        "dependencies: [APU-007, APU-008]\n"
        "<!-- end -->\n"
    )
    sm = _session(tmp_path, ["APU-007", "APU-008"])
    # No section-3-11 citations exist; per-section will fail. Orphan part
    # passes (broad regex finds the bare refs in Section 14).
    r = run(spec, sm)
    assert r["status"] == "fail"
    assert r["details"]["uncited_apus"] == []  # orphan side passes


def test_v1_exempt_sections_dont_need_citation(tmp_path):
    # Section 1 has no [APU-NNN] but it's exempt → not flagged.
    sm = _session(tmp_path, ["APU-001", "APU-002", "APU-003"])
    assert run(FIX / "valid_v1.md", sm)["status"] == "pass"
