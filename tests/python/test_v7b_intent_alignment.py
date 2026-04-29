# tests/python/test_v7b_intent_alignment.py
import yaml
from pathlib import Path
from scripts.verifications.v7b_intent_alignment import run


def _audit_fragment(tmp_path, score, divergence=None):
    sd = tmp_path
    (sd / "stages").mkdir(parents=True, exist_ok=True)
    p = sd / "stages" / "N-SPEC-AUDIT-SEMANTIC.md"
    p.write_text(yaml.safe_dump({
        "intent_alignment_score": score,
        "divergence_list": divergence or [],
    }))
    sm = sd / "session.md"
    sm.write_text("apus: []\n")
    return sm


def test_v7b_passes_above_threshold(tmp_path):
    sm = _audit_fragment(tmp_path, 0.85)
    r = run(tmp_path / "x.md", sm, threshold=0.7)
    assert r["status"] == "pass"


def test_v7b_fails_below_threshold(tmp_path):
    sm = _audit_fragment(tmp_path, 0.65, divergence=[{"item": "X drifted"}])
    r = run(tmp_path / "x.md", sm, threshold=0.7)
    assert r["status"] == "fail"
    assert r["details"]["score"] == 0.65


def test_v7b_fails_when_audit_fragment_missing(tmp_path):
    sm = tmp_path / "session.md"
    sm.write_text("apus: []\n")
    r = run(tmp_path / "x.md", sm, threshold=0.7)
    assert r["status"] == "fail"
    assert "audit_fragment_missing" in r["details"]
