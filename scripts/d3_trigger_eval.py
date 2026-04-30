#!/usr/bin/env python3
"""d3_trigger_eval.py — pure D3 trigger evaluation, callable + testable."""
from __future__ import annotations

MAX_REFRAMES_PER_IDEA = 2


def evaluate(scores: list[float], idea_id: str, prior_reframe_count: int) -> dict:
    """Check D3 score-stagnation condition.

    Args:
        scores: Last N scores for the same idea_id in the same reframe_seq group.
                Must have at least 2 values to check stagnation.
        idea_id: The idea being scored.
        prior_reframe_count: How many times REFRAME has already fired for this idea.
    """
    if len(scores) < 2:
        return {"fire": False, "action": None, "warning": None}

    # Check last two consecutive score deltas
    recent = scores[-2:]
    delta = abs(recent[1] - recent[0])

    if delta > 0.05:
        return {"fire": False, "action": None, "warning": None}

    if prior_reframe_count >= MAX_REFRAMES_PER_IDEA:
        return {
            "fire": True,
            "action": "skip-reframe-and-queue",
            "idea_id": idea_id,
            "warning": (
                f"[D3-REFRAME-LIMIT idea_id={idea_id} "
                f"prior_reframes={prior_reframe_count}]"
            ),
        }

    return {
        "fire": True,
        "action": "instantiate-reframe",
        "idea_id": idea_id,
        "warning": None,
    }


if __name__ == "__main__":
    import argparse, json, sys
    p = argparse.ArgumentParser(
        description="D3 trigger evaluator — checks score stagnation across refinement passes."
    )
    p.add_argument("--scores", required=True,
                   help="Comma-separated scores for the same idea_id (e.g. '0.82,0.84,0.86')")
    p.add_argument("--idea-id", required=True)
    p.add_argument("--prior-reframes", type=int, default=0)
    args = p.parse_args()

    try:
        score_list = [float(s.strip()) for s in args.scores.split(",")]
    except ValueError:
        print("D3: invalid score format", file=sys.stderr)
        sys.exit(2)

    result = evaluate(score_list, args.idea_id, args.prior_reframes)
    json.dump(result, sys.stdout, indent=2)
