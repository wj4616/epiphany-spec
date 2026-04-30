#!/usr/bin/env python3
"""d1_trigger_eval.py — pure D1 trigger evaluation, callable + testable."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def evaluate(aggregation_fragment_path: Path) -> dict:
    """Read N-AGGREGATION fragment, extract coverage_gaps, decide if D1 fires."""
    if not aggregation_fragment_path.exists():
        return {"fire": False, "action": None, "warning": "D1: N-AGGREGATION fragment not found"}

    text = aggregation_fragment_path.read_text()
    gaps = _extract_coverage_gaps(text)

    if not gaps:
        return {"fire": False, "action": None, "warning": None}

    return {
        "fire": True,
        "action": "instantiate-domain-targeted-per-gap",
        "gaps": gaps,
        "warning": None,
    }


def _extract_coverage_gaps(text: str) -> list[dict]:
    """Extract coverage_gaps from N-AGGREGATION output YAML block."""
    in_block = False
    lines = []
    for line in text.split("\n"):
        if line.strip() == "```yaml":
            in_block = True
            continue
        if in_block and line.strip() == "```":
            break
        if in_block:
            lines.append(line)

    if not lines:
        return []

    try:
        data = yaml_safe_load("\n".join(lines))
    except Exception:
        return []

    if not isinstance(data, dict):
        return []

    gaps = data.get("coverage_gaps", [])
    if not isinstance(gaps, list):
        return []
    return [g for g in gaps if isinstance(g, dict) and g.get("domain_class")]


def yaml_safe_load(text: str) -> dict:
    """Minimal YAML loader for N-AGGREGATION output (no pyyaml dependency)."""
    import yaml
    return yaml.safe_load(text) or {}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(
        description="D1 trigger evaluator — checks N-AGGREGATION coverage_gaps."
    )
    p.add_argument("--aggregation-fragment", required=True, type=Path,
                   help="Path to N-AGGREGATION fragment YAML")
    args = p.parse_args()
    result = evaluate(args.aggregation_fragment)
    json.dump(result, sys.stdout, indent=2)
    sys.exit(0 if not result["fire"] else 0)
