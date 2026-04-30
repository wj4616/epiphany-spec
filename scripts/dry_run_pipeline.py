#!/usr/bin/env python3
"""dry_run_pipeline.py — predict node dispatch sequence for a given mode (I103)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ACTIVE_BRANCHES = {
    "MINIMAL":  {"SPREADING"},
    "STANDARD": {"SPREADING", "LATERAL"},
    "DEEP":     {"SPREADING", "LATERAL", "SIMULATION", "ADVERSARIAL"},
}


def predict(mode: str, apu_count: int) -> list[dict]:
    g = json.loads((REPO / "graph.json").read_text())
    active = ACTIVE_BRANCHES.get(mode, ACTIVE_BRANCHES["STANDARD"])
    seq: list[dict] = []
    for n in g["nodes"]:
        nid = n["id"]
        scale_gates = n.get("scale_gates")
        branch_label = n.get("branch_label")
        skipped_for_scale = scale_gates and mode not in scale_gates
        skipped_for_branch = False
        if branch_label:
            skipped_for_branch = g.get("branch_labels", {}).get(branch_label) not in active

        exec_type = n["exec_type"]
        if nid == "N-FORWARD-CHAIN-BATCH":
            exec_type = "inline" if apu_count <= 30 else "spawn"

        seq.append({
            "node": nid,
            "phase": n["phase"],
            "exec_type": exec_type,
            "tier": n["tier"],
            "dispatched": not (skipped_for_scale or skipped_for_branch),
            "skip_reason": (
                "scale_gate" if skipped_for_scale else
                "branch_inactive" if skipped_for_branch else None
            ),
        })
    return seq


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode",      default="STANDARD", choices=["MINIMAL", "STANDARD", "DEEP"])
    p.add_argument("--apu-count", type=int, default=20)
    args = p.parse_args(argv)
    seq = predict(args.mode, args.apu_count)
    spawns = sum(1 for s in seq if s["dispatched"] and s["exec_type"] == "spawn")
    print(f"# Mode={args.mode} apu_count={args.apu_count}  predicted_spawns={spawns}")
    print(f"{'NODE':<28} {'PHASE':<6} {'EXEC':<8} {'TIER':<8} {'STATUS':<22}")
    for s in seq:
        status = "DISPATCH" if s["dispatched"] else f"skip ({s['skip_reason']})"
        print(f"{s['node']:<28} {str(s['phase']):<6} {s['exec_type']:<8} {s['tier']:<8} {status:<22}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
