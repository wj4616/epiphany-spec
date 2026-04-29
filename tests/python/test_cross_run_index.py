import json
import yaml  # PyYAML available via miniconda
from pathlib import Path
from scripts.cross_run_index import load_or_rebuild, update, rebuild_from_scratch


def _make_session(base: Path, sid: str, *, state: str, slug: str, conv_count: int):
    sd = base / sid
    sd.mkdir(parents=True)
    session_md = {
        "session_id": sid,
        "state": state,
        "topic_slug": slug,
        "convergent_nodes": [{"concept": f"c{i}"} for i in range(conv_count)],
        "final_version": 1 if state == "FINALIZED" else None,
    }
    (sd / "session.md").write_text(yaml.safe_dump(session_md))


def test_load_or_rebuild_missing_index_rebuilds(tmp_path):
    base = tmp_path
    _make_session(base, "sess-A", state="FINALIZED", slug="alpha-beta", conv_count=3)
    _make_session(base, "sess-B", state="RUNNING",   slug="gamma",      conv_count=0)
    _make_session(base, "sess-C", state="ABORTED",   slug="delta",      conv_count=0)

    idx = load_or_rebuild(base)
    assert "sess-A" in idx
    assert "sess-B" not in idx  # not finalized
    assert "sess-C" not in idx
    assert idx["sess-A"]["topic_slug"] == "alpha-beta"
    assert idx["sess-A"]["convergent_nodes_count"] == 3
    # The index file was written.
    assert (base / "cross_run_index.json").exists()


def test_update_atomic(tmp_path):
    base = tmp_path
    _make_session(base, "sess-A", state="FINALIZED", slug="alpha", conv_count=2)
    update(base, "sess-A", {
        "topic_slug": "alpha",
        "convergent_nodes_count": 2,
        "finalized_ts": "2026-04-29T00:00:00Z",
        "file_path": str(base / "sess-A" / "session.md"),
    })
    with open(base / "cross_run_index.json") as f:
        idx = json.load(f)
    assert idx["sess-A"]["convergent_nodes_count"] == 2
    # No tmp leftover.
    assert not (base / "cross_run_index.json.tmp").exists()


def test_rebuild_from_scratch_skips_corrupted_session_md(tmp_path):
    base = tmp_path
    _make_session(base, "sess-A", state="FINALIZED", slug="alpha", conv_count=1)
    bad = base / "sess-bad"
    bad.mkdir()
    (bad / "session.md").write_text("::: not yaml :::")

    idx = rebuild_from_scratch(base)
    assert "sess-A" in idx
    assert "sess-bad" not in idx


def test_load_corrupted_index_triggers_rebuild(tmp_path):
    base = tmp_path
    _make_session(base, "sess-A", state="FINALIZED", slug="alpha", conv_count=1)
    (base / "cross_run_index.json").write_text("{ broken json")
    idx = load_or_rebuild(base)
    assert "sess-A" in idx


import multiprocessing


def _writer(base_str, sid, payload):
    from pathlib import Path
    from scripts.cross_run_index import update
    update(Path(base_str), sid, payload)


def test_concurrent_updates_no_partial_json(tmp_path):
    base = tmp_path
    _make_session(base, "sess-A", state="FINALIZED", slug="a", conv_count=1)
    payload_a = {"topic_slug": "a", "convergent_nodes_count": 1,
                 "finalized_ts": "2026-04-29T00:00:00Z",
                 "file_path": str(base / "sess-A" / "session.md")}
    payload_b = {"topic_slug": "b", "convergent_nodes_count": 99,
                 "finalized_ts": "2026-04-29T00:00:01Z",
                 "file_path": str(base / "sess-A" / "session.md")}

    procs = [
        multiprocessing.Process(target=_writer, args=(str(base), "sess-A", payload_a)),
        multiprocessing.Process(target=_writer, args=(str(base), "sess-A", payload_b)),
    ]
    for p in procs: p.start()
    for p in procs: p.join(timeout=10)

    with open(base / "cross_run_index.json") as f:
        idx = json.load(f)
    assert idx["sess-A"]["convergent_nodes_count"] in (1, 99)
