import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXPECTED_TIERS = {"large", "medium", "small", "no-llm"}
LARGE_HATS = {
    "constraint-enumerator", "lateral-creative", "spreading-activation",
    "simulator", "janusian-adversary", "aggregator", "reframer"
}
MEDIUM_HATS = {
    "paraphraser", "decomposer", "intent-layerer", "clarifier",
    "random-injector", "domain-surveyor", "falsifier", "query-refiner",
    "intake", "semantic-auditor", "adversarial-reviewer", "pruner",
    "idea-structurer"
}
SMALL_HATS = {"scorer", "dep-mapper", "mechanical-auditor"}


def test_hats_json_structure():
    with open(REPO / "hats.json") as f:
        hats = json.load(f)
    assert set(hats.keys()) == {"tiers", "default_models"}
    assert set(hats["tiers"].keys()) == EXPECTED_TIERS


def test_hats_each_hat_unique_to_one_tier():
    with open(REPO / "hats.json") as f:
        hats = json.load(f)
    seen = {}
    for tier, hat_list in hats["tiers"].items():
        for h in hat_list:
            assert h not in seen, f"hat {h!r} appears in {seen[h]} and {tier}"
            seen[h] = tier


def test_hats_membership_matches_spec_section_17():
    with open(REPO / "hats.json") as f:
        hats = json.load(f)
    assert set(hats["tiers"]["large"]) == LARGE_HATS
    assert set(hats["tiers"]["medium"]) == MEDIUM_HATS
    assert set(hats["tiers"]["small"]) == SMALL_HATS
    assert hats["tiers"]["no-llm"] == []


def test_hats_default_models_populated():
    with open(REPO / "hats.json") as f:
        hats = json.load(f)
    dm = hats["default_models"]
    assert dm["large"] == "claude-opus-4-7"
    assert dm["medium"] == "claude-sonnet-4-6"
    assert dm["small"] == "claude-haiku-4-5-20251001"
    assert dm["no-llm"] is None
