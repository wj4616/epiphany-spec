from scripts.d2_trigger_eval import evaluate, MAX_REPLACEMENTS_PER_CYCLE


def test_d2_fires_below_threshold():
    state = {"cycle": 1, "d2_replacements_this_cycle": 0}
    out = evaluate(convergent_node_count=2, mode="STANDARD", state=state)
    assert out["fire"] is True


def test_d2_skips_above_threshold():
    state = {"cycle": 1, "d2_replacements_this_cycle": 0}
    out = evaluate(convergent_node_count=5, mode="STANDARD", state=state)
    assert out["fire"] is False


def test_d2_loop_guard_max_two_replacements_then_skip():
    state = {"cycle": 1, "d2_replacements_this_cycle": 0}
    o1 = evaluate(convergent_node_count=0, mode="STANDARD", state=state)
    assert o1["fire"] is True
    state["d2_replacements_this_cycle"] += 1
    o2 = evaluate(convergent_node_count=0, mode="STANDARD", state=state)
    assert o2["fire"] is True
    state["d2_replacements_this_cycle"] += 1
    o3 = evaluate(convergent_node_count=0, mode="STANDARD", state=state)
    assert o3["fire"] is False
    assert "[D2-REPLACEMENT-LIMIT" in o3["warning"]


def test_d2_minimal_threshold_is_zero():
    state = {"cycle": 1, "d2_replacements_this_cycle": 0}
    assert evaluate(convergent_node_count=0, mode="MINIMAL", state=state)["fire"] is True
    assert evaluate(convergent_node_count=1, mode="MINIMAL", state=state)["fire"] is False


def test_d2_deep_threshold_is_lt_5():
    state = {"cycle": 1, "d2_replacements_this_cycle": 0}
    assert evaluate(convergent_node_count=4, mode="DEEP", state=state)["fire"] is True
    assert evaluate(convergent_node_count=5, mode="DEEP", state=state)["fire"] is False
