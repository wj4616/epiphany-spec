#!/usr/bin/env python3
"""d2_trigger_eval.py — pure D2 trigger evaluation, callable + testable."""
from __future__ import annotations

MAX_REPLACEMENTS_PER_CYCLE = 2
_THRESHOLD = {"MINIMAL": 1, "STANDARD": 3, "DEEP": 5}


def evaluate(convergent_node_count: int, mode: str, state: dict) -> dict:
    threshold = _THRESHOLD.get(mode, _THRESHOLD["STANDARD"])
    if convergent_node_count >= threshold:
        return {"fire": False, "action": None, "warning": None}
    if state.get("d2_replacements_this_cycle", 0) >= MAX_REPLACEMENTS_PER_CYCLE:
        cycle = state.get("cycle", "?")
        return {
            "fire": False, "action": None,
            "warning": (
                f"[D2-REPLACEMENT-LIMIT cycle={cycle} "
                f"convergent_node_count={convergent_node_count}]"
            ),
        }
    return {
        "fire": True,
        "action": "refire-spreading-and-random-entry",
        "warning": None,
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="D2 trigger evaluator — checks N-SPREADING convergent node count against mode threshold.")
    p.add_argument("--count", type=int, required=True)
    p.add_argument("--mode",  default="STANDARD")
    p.add_argument("--cycle", type=int, default=1)
    p.add_argument("--prior", type=int, default=0)
    args = p.parse_args()
    state = {"cycle": args.cycle, "d2_replacements_this_cycle": args.prior}
    print(evaluate(args.count, args.mode, state))
