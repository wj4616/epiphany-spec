import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_graph_schema_is_valid_json():
    with open(REPO / "graph.schema.json") as f:
        schema = json.load(f)
    assert schema["$schema"].startswith("http")
    assert "properties" in schema
    for required in ("version", "nodes", "edges", "dynamic_templates", "branch_labels"):
        assert required in schema["required"], f"{required} missing from required list"


def test_graph_schema_node_shape():
    with open(REPO / "graph.schema.json") as f:
        schema = json.load(f)
    node = schema["properties"]["nodes"]["items"]
    for required in ("id", "module_file", "phase", "exec_type", "tier", "required_output_sections"):
        assert required in node["required"]
    assert set(node["properties"]["exec_type"]["enum"]) == {"inline", "spawn"}
    assert set(node["properties"]["tier"]["enum"]) == {"large", "medium", "small", "no-llm"}


def test_graph_schema_edge_kinds():
    with open(REPO / "graph.schema.json") as f:
        schema = json.load(f)
    edge = schema["properties"]["edges"]["items"]
    assert set(edge["properties"]["kind"]["enum"]) == {"forward", "back", "conditional", "dynamic"}


REQUIRED_NODE_IDS = {
    "N-INTAKE", "N-CROSS-RUN-SEED", "N-RESTATE", "N-DECOMPOSE-APU",
    "N-INTENT-LAYER", "N-CONSTRAINT-INVENTORY", "N-AMBIGUITY-SCAN", "N-CLARIFY-LOOP",
    "N-LATERAL", "N-SPREADING", "N-SIMULATION", "N-ADVERSARIAL",
    "N-AGGREGATION", "N-IDEA-STRUCTURE", "N-PRUNE", "N-ADVERSARIAL-REVIEW",
    "N-FALSIFY", "N-FORWARD-CHAIN-BATCH", "N-DEPENDENCY-MAP", "N-SPEC-CONSTRUCT",
    "N-SPEC-AUDIT-MECHANICAL", "N-SPEC-AUDIT-SEMANTIC", "N-GRS-EXPORT",
    "N-SCORE", "N-DEFIXATION", "N-REWRITE-EVALUATOR", "N-REFINE-QUERY",
}
NO_LLM_NODES = {"N-CROSS-RUN-SEED", "N-GRS-EXPORT", "N-DEFIXATION", "N-REWRITE-EVALUATOR"}
PHASE_6_BRANCHES = {"N-LATERAL", "N-SPREADING", "N-SIMULATION", "N-ADVERSARIAL"}


def _load_graph():
    with open(REPO / "graph.json") as f:
        return json.load(f)


def test_graph_json_has_all_nodes():
    g = _load_graph()
    ids = {n["id"] for n in g["nodes"]}
    missing = REQUIRED_NODE_IDS - ids
    assert not missing, f"missing nodes: {sorted(missing)}"


def test_graph_no_llm_tier_assignment():
    g = _load_graph()
    for n in g["nodes"]:
        if n["id"] in NO_LLM_NODES:
            assert n["tier"] == "no-llm", f"{n['id']} expected no-llm"


def test_graph_phase_6_branch_labels():
    g = _load_graph()
    by_id = {n["id"]: n for n in g["nodes"]}
    expected = {"N-LATERAL": "A", "N-SPREADING": "B", "N-SIMULATION": "C", "N-ADVERSARIAL": "D"}
    for node, label in expected.items():
        assert by_id[node]["branch_label"] == label


def test_graph_aggregation_join_is_AND():
    g = _load_graph()
    by_id = {n["id"]: n for n in g["nodes"]}
    assert by_id["N-AGGREGATION"]["join"] == "AND"


def test_graph_dynamic_templates_present():
    g = _load_graph()
    assert set(g["dynamic_templates"].keys()) == {"DOMAIN-TARGETED", "RANDOM-ENTRY", "REFRAME"}


def test_graph_forward_edges_form_chain():
    g = _load_graph()
    forward = [(e["from"], e["to"]) for e in g["edges"] if e["kind"] == "forward"]
    # spot checks against §4 phase chain
    expected_pairs = [
        ("N-INTAKE", "N-CROSS-RUN-SEED"),
        ("N-CROSS-RUN-SEED", "N-RESTATE"),
        ("N-RESTATE", "N-DECOMPOSE-APU"),
        ("N-DECOMPOSE-APU", "N-INTENT-LAYER"),
        ("N-INTENT-LAYER", "N-CONSTRAINT-INVENTORY"),
        ("N-CONSTRAINT-INVENTORY", "N-AMBIGUITY-SCAN"),
        ("N-AMBIGUITY-SCAN", "N-CLARIFY-LOOP"),
        ("N-AGGREGATION", "N-IDEA-STRUCTURE"),
        ("N-IDEA-STRUCTURE", "N-PRUNE"),
        ("N-PRUNE", "N-ADVERSARIAL-REVIEW"),
        ("N-ADVERSARIAL-REVIEW", "N-FALSIFY"),
        ("N-SPEC-CONSTRUCT", "N-SPEC-AUDIT-MECHANICAL"),
        ("N-SPEC-AUDIT-MECHANICAL", "N-SPEC-AUDIT-SEMANTIC"),
        ("N-SPEC-AUDIT-SEMANTIC", "N-GRS-EXPORT"),
    ]
    for pair in expected_pairs:
        assert pair in forward, f"missing forward edge {pair}"
    # Phase 6 branches all feed N-AGGREGATION
    for branch in PHASE_6_BRANCHES:
        assert (branch, "N-AGGREGATION") in forward


def test_graph_back_edges_declared():
    g = _load_graph()
    back = [(e["from"], e["to"], e.get("label", "")) for e in g["edges"] if e["kind"] == "back"]
    labels = [lbl for _, _, lbl in back]
    assert "DEFIXATION" in labels  # 9→6 N-SPREADING re-fire
    assert "REJECT-items" in labels  # 12→11 N-REFINE-QUERY
    assert "CLARIFY-LOOP" in labels  # Phase 5 pause-resume (logical, not graph self-loop)
    assert "REWORK" in labels  # 12 → phase N


import subprocess
import pytest as _pytest

SCRIPT = REPO / "scripts" / "validate-graph.py"


def test_validate_graph_runs_clean_on_static_config(tmp_path):
    # No --session-dir → skip check 5
    result = subprocess.run(
        ["python3", str(SCRIPT), "--skip-modules"],
        capture_output=True, text=True, cwd=str(REPO),
    )
    assert result.returncode == 0, result.stderr


def test_validate_graph_session_check_pass(tmp_path):
    sd = tmp_path / "abc-uuid"
    (sd / "stages").mkdir(parents=True)
    (sd / "input.md").write_text("hello\n")
    (sd / "session.md").write_text("session_id: abc-uuid\nstate: RUNNING\ntopic_slug: hello\nscale: STANDARD\nactive_branches: [SPREADING, LATERAL]\nspawn_count: 0\ncurrent_version: 0\n")
    (sd / "grs-ledger.md").touch()
    (sd / "topology-trace.md").touch()
    solution_target = tmp_path / "solution-target"
    solution_target.mkdir()
    (sd / "spec-export").symlink_to(solution_target)
    result = subprocess.run(
        ["python3", str(SCRIPT), "--skip-modules",
         "--session-dir", str(sd),
         "--allowed-solution-root", str(tmp_path)],
        capture_output=True, text=True, cwd=str(REPO),
    )
    assert result.returncode == 0, result.stderr


def test_validate_graph_passes_with_all_modules_present(tmp_path):
    # Run WITHOUT --skip-modules: all modules exist → must pass all checks.
    result = subprocess.run(
        ["python3", str(SCRIPT)],
        capture_output=True, text=True, cwd=str(REPO),
    )
    assert result.returncode == 0, result.stderr


def test_validate_graph_session_check_fail_dirty_dir(tmp_path):
    sd = tmp_path / "dirty-uuid"
    (sd / "stages").mkdir(parents=True)
    (sd / "input.md").write_text("x\n")
    (sd / "session.md").write_text("session_id: dirty-uuid\nstate: RUNNING\n")
    (sd / "grs-ledger.md").write_text("## ledger-entry: pre-existing\n")  # dirty!
    (sd / "topology-trace.md").touch()
    result = subprocess.run(
        ["python3", str(SCRIPT), "--skip-modules", "--session-dir", str(sd)],
        capture_output=True, text=True, cwd=str(REPO),
    )
    assert result.returncode != 0
    assert "non-empty" in (result.stdout + result.stderr).lower()
