from scripts.dry_run_pipeline import predict


def test_minimal_dispatch_skips_lateral_simulation_adversarial():
    seq = predict(mode="MINIMAL", apu_count=10)
    branch_nodes = {"N-LATERAL", "N-SIMULATION", "N-ADVERSARIAL"}
    dispatched = {step["node"] for step in seq if step["dispatched"]}
    assert "N-SPREADING" in dispatched
    assert dispatched.isdisjoint(branch_nodes), \
        f"MINIMAL should skip non-SPREADING branches, got {dispatched & branch_nodes}"


def test_deep_dispatches_all_branches():
    seq = predict(mode="DEEP", apu_count=10)
    dispatched = {step["node"] for step in seq if step["dispatched"]}
    for b in ("N-LATERAL", "N-SPREADING", "N-SIMULATION", "N-ADVERSARIAL"):
        assert b in dispatched


def test_forward_chain_batch_inline_when_small_apu_count():
    seq = predict(mode="STANDARD", apu_count=20)
    fcb = next(s for s in seq if s["node"] == "N-FORWARD-CHAIN-BATCH")
    assert fcb["exec_type"] == "inline"


def test_forward_chain_batch_spawn_when_large_apu_count():
    seq = predict(mode="STANDARD", apu_count=50)
    fcb = next(s for s in seq if s["node"] == "N-FORWARD-CHAIN-BATCH")
    assert fcb["exec_type"] == "spawn"


def test_total_spawn_count_within_mode_cap():
    for mode, hard in (("MINIMAL", 3), ("STANDARD", 7), ("DEEP", 10)):
        seq = predict(mode=mode, apu_count=10)
        spawns = sum(1 for s in seq if s["dispatched"] and s["exec_type"] == "spawn")
        assert spawns <= hard, f"{mode} predicted spawns {spawns} > hard cap {hard}"
