"""I007 — every module's hat must resolve to the same tier as the node's
declared tier in graph.json."""
import json
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def _module_frontmatter(name: str) -> dict:
    p = REPO / "modules" / f"{name}.md"
    if not p.exists():
        return {}
    m = FRONTMATTER.match(p.read_text())
    return yaml.safe_load(m.group(1)) if m else {}


def test_node_hat_resolves_to_declared_tier():
    graph = json.loads((REPO / "graph.json").read_text())
    hats = json.loads((REPO / "hats.json").read_text())
    hat_to_tier = {h: tier for tier, hat_list in hats["tiers"].items() for h in hat_list}

    failures: list[str] = []
    for node in graph["nodes"]:
        nid = node["id"]
        declared_tier = node["tier"]
        fm = _module_frontmatter(nid)
        if not fm:
            continue
        hat = fm.get("hat")
        if hat is None:
            if declared_tier != "no-llm":
                failures.append(f"{nid}: hat=null but graph tier={declared_tier!r}")
            continue
        resolved = hat_to_tier.get(hat)
        if resolved is None:
            failures.append(f"{nid}: hat {hat!r} not in hats.json")
        elif resolved != declared_tier:
            failures.append(f"{nid}: hat {hat!r} → tier {resolved!r}, but graph declares {declared_tier!r}")
    assert not failures, "\n".join(failures)
