# tests/python/test_v2_vocab_lock.py
import yaml
from pathlib import Path
from scripts.verifications.v2_vocab_lock import run

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "specs"


def _session(tmp_path, vocab):
    sm = tmp_path / "session.md"
    sm.write_text(yaml.safe_dump({"locked_vocabulary": vocab}))
    return sm


def test_v2_passes_when_canonical_used(tmp_path):
    vocab = [{"term": "spec doc", "synonyms": ["specification document", "spec file"]}]
    spec = tmp_path / "ok.md"
    spec.write_text("## 5. Behavior\n- The spec doc must include all APUs.\n")
    sm = _session(tmp_path, vocab)
    assert run(spec, sm)["status"] == "pass"


def test_v2_fails_on_synonym_leakage(tmp_path):
    vocab = [{"term": "spec doc", "synonyms": ["specification document"]}]
    sm = _session(tmp_path, vocab)
    r = run(FIX / "vocab_leak.md", sm)
    assert r["status"] == "fail"
    sites = r["details"]["leakage_sites"]
    assert any("specification document" in s["synonym"] for s in sites)


def test_v2_passes_when_no_locked_vocab(tmp_path):
    sm = _session(tmp_path, [])
    spec = tmp_path / "x.md"
    spec.write_text("## 5. Behavior\n- whatever\n")
    assert run(spec, sm)["status"] == "pass"
