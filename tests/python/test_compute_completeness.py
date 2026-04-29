import yaml
from pathlib import Path
from scripts.compute_completeness import compute, run


def _spec_with(tmp_path, body):
    p = tmp_path / "spec.md"
    p.write_text(body)
    return p


def _session(tmp_path, **fields):
    sm = tmp_path / "session.md"
    base = {
        "apus": [{"id": "APU-001", "type": "functional"},
                 {"id": "APU-002", "type": "invariant"}],
        "conflict_ledger": [],
    }
    base.update(fields)
    sm.write_text(yaml.safe_dump(base))
    return sm


def test_compute_all_ones_when_all_cited(tmp_path):
    spec = _spec_with(tmp_path,
        "## 3. Invariants\n[APU-001] [APU-002]\n"
        "## 10. Falsifiability\n### R-001 (APU-001)\n"
        "  - test: x\n  - break_attempt: y\n"
        "## 15. Dependency Summary\n- R-001 → constrains [R-002]\n"
    )
    sm = _session(tmp_path)
    falsify_path = tmp_path / "stages" / "N11-FALSIFY.md"
    falsify_path.parent.mkdir(parents=True, exist_ok=True)
    falsify_path.write_text(yaml.safe_dump({
        "requirements": [{"id": "R-001", "apu_id": "APU-001"}],
    }))
    out = compute(spec, sm)
    assert out["coverage_apus"] == 1.0
    assert out["coverage_falsifiability"] == 1.0
    assert out["coverage_dependency_map"] == 1.0
    assert out["coverage_conflict_resolution"] == 1.0
    assert out["overall_min"] == 1.0


def test_compute_partial_coverage(tmp_path):
    spec = _spec_with(tmp_path,
        "## 3. Invariants\n[APU-001]\n"
        "## 10. Falsifiability\n(none)\n"
        "## 15. Dependency Summary\n(none)\n"
    )
    sm = _session(tmp_path,
        apus=[{"id": "APU-001", "type": "functional"},
              {"id": "APU-002", "type": "functional"}])
    falsify_path = tmp_path / "stages" / "N11-FALSIFY.md"
    falsify_path.parent.mkdir(parents=True, exist_ok=True)
    falsify_path.write_text(yaml.safe_dump({"requirements": [{"id": "R-001"}]}))
    out = compute(spec, sm)
    assert out["coverage_apus"] == 0.5
    assert out["coverage_falsifiability"] == 0.0
    assert out["coverage_dependency_map"] == 0.0
    assert out["overall_min"] == 0.0
