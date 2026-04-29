"""I106 — mock-LLM end-to-end shake-out.

Drives the dispatch predictor (Task 51) and verifies sequencing constraints
that an actual LLM run would also need to honor. Doesn't run real LLMs;
pre-cans node outputs and confirms the pipeline structure is sane.
"""
from scripts.dry_run_pipeline import predict


def test_minimal_dispatch_sequence_respects_phase_order():
    seq = predict(mode="MINIMAL", apu_count=15)
    dispatched = [s for s in seq if s["dispatched"]]
    last_phase = -1
    back_edge_nodes = {"N-REFINE-QUERY", "N-DEFIXATION", "N-REWRITE-EVALUATOR"}
    for s in dispatched:
        if s["phase"] == "cross-cutting" or s["node"] in back_edge_nodes:
            continue
        p = 0.5 if s["phase"] == "0_5" else float(s["phase"])
        assert p >= last_phase, f"{s['node']}: phase {p} < last {last_phase}"
        last_phase = p


def test_standard_dispatches_aggregation_after_branches():
    seq = predict(mode="STANDARD", apu_count=15)
    by_node = {s["node"]: i for i, s in enumerate(seq)}
    branches = ["N-SPREADING", "N-LATERAL"]
    for b in branches:
        assert by_node[b] < by_node["N-AGGREGATION"], f"{b} after AGG"


def test_deep_dispatches_idea_structure_after_aggregation():
    seq = predict(mode="DEEP", apu_count=15)
    by_node = {s["node"]: i for i, s in enumerate(seq)}
    assert by_node["N-AGGREGATION"] < by_node["N-IDEA-STRUCTURE"]


def test_phase_12_audit_then_export_then_v_checks_order():
    """Sequence intent: AUDIT-MECHANICAL -> AUDIT-SEMANTIC -> GRS-EXPORT in
    graph order. (V-checks run via validate-spec-doc.sh, outside graph
    dispatch.)"""
    seq = predict(mode="STANDARD", apu_count=15)
    by_node = {s["node"]: i for i, s in enumerate(seq)}
    assert by_node["N-SPEC-AUDIT-MECHANICAL"] < by_node["N-SPEC-AUDIT-SEMANTIC"]
    assert by_node["N-SPEC-AUDIT-SEMANTIC"]   < by_node["N-GRS-EXPORT"]
