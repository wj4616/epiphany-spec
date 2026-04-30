#!/usr/bin/env python3
"""V7b — Intent-alignment threshold (§10). Consumes N-SPEC-AUDIT-SEMANTIC output."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


def run(spec_path: Path, session_md_path: Path, threshold: float = 0.7) -> dict:
    sd = Path(session_md_path).parent
    audit = sd / "stages" / "N-SPEC-AUDIT-SEMANTIC.md"
    if not audit.exists():
        return {"status": "fail", "details": {"audit_fragment_missing": str(audit)}}
    data = yaml.safe_load(audit.read_text()) or {}
    try:
        score = float(data.get("intent_alignment_score", 0.0))
    except (ValueError, TypeError):
        return {"status": "fail", "details": {"reason": "non-numeric intent_alignment_score", "raw_value": data.get("intent_alignment_score")}}
    divergence = data.get("divergence_list") or []
    if score < threshold:
        return {"status": "fail", "details": {"score": score, "threshold": threshold, "divergence_list": divergence}}
    return {"status": "pass", "details": {"score": score, "threshold": threshold}}


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="V7b — Intent alignment: checks spec content against intent-layer declarations.")
    p.add_argument("--spec",       required=True, type=Path)
    p.add_argument("--session-md", required=True, type=Path)
    p.add_argument("--threshold",  type=float, default=0.7)
    args = p.parse_args(argv)
    r = run(args.spec, args.session_md, threshold=args.threshold)
    print(r)
    return 0 if r["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
