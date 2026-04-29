# tests/python/test_v5_topology_audit.py
from pathlib import Path
from scripts.verifications.v5_topology_audit import run


def _session(tmp_path, trace_text, ledger_nodes):
    (tmp_path / "topology-trace.md").write_text(trace_text)
    ledger_text = "\n".join(f"## ledger-entry: {n} [cycle=1]\n" for n in ledger_nodes)
    (tmp_path / "grs-ledger.md").write_text(ledger_text)
    sm = tmp_path / "session.md"
    sm.write_text("apus: []\n")
    return sm


def test_v5_passes_on_valid_trace(tmp_path):
    trace = (
        "## insertion\n"
        "node: DOMAIN-TARGETED-1\nreason: D1 coverage gap\ntriggered_by_node: N-AGGREGATION\n"
    )
    sm = _session(tmp_path, trace, ["N-AGGREGATION", "DOMAIN-TARGETED-1"])
    r = run(tmp_path / "x.md", sm)
    assert r["status"] == "pass"


def test_v5_fails_missing_reason(tmp_path):
    trace = "## insertion\nnode: REFRAME-1\ntriggered_by_node: N-IDEA-STRUCTURE\n"
    sm = _session(tmp_path, trace, ["N-IDEA-STRUCTURE", "REFRAME-1"])
    r = run(tmp_path / "x.md", sm)
    assert r["status"] == "fail"
    assert any("reason" in b.get("missing_fields", []) for b in r["details"]["bad_entries"])


def test_v5_fails_orphan_node(tmp_path):
    trace = "## insertion\nnode: GHOST-NODE\nreason: nope\ntriggered_by_node: NOT-IN-LEDGER\n"
    sm = _session(tmp_path, trace, ["N-INTAKE"])
    r = run(tmp_path / "x.md", sm)
    assert r["status"] == "fail"


def test_v5_passes_on_empty_trace(tmp_path):
    sm = _session(tmp_path, "", [])
    r = run(tmp_path / "x.md", sm)
    assert r["status"] == "pass"
