# tests/python/test_v4_convergent_node_detection.py
import yaml
from pathlib import Path
from scripts.verifications.v4_convergent_node_detection import run


def _session(tmp_path, conv_nodes, active_branches=None):
    sm = tmp_path / "session.md"
    sm.write_text(yaml.safe_dump({
        "convergent_nodes": conv_nodes,
        "active_branches": active_branches or ["SPREADING"],
    }))
    return sm


def test_v4_passes_with_convergent_nodes(tmp_path):
    sm = _session(tmp_path, [
        {"concept": "x", "branches_activated_by": ["LATERAL", "ADVERSARIAL"], "signal_strength": 2},
    ])
    r = run(tmp_path / "irrelevant.md", sm)
    assert r["status"] == "pass"


def test_v4_fails_on_empty_convergent_with_active_branch(tmp_path):
    sm = _session(tmp_path, [], active_branches=["SPREADING"])
    r = run(tmp_path / "x.md", sm)
    assert r["status"] == "fail"


def test_v4_fails_when_signal_strength_below_two(tmp_path):
    sm = _session(tmp_path, [{"concept": "y", "signal_strength": 1}])
    r = run(tmp_path / "x.md", sm)
    assert r["status"] == "fail"
