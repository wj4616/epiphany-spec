#!/usr/bin/env python3
"""V4 — Convergent node detection (§10)."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


def run(spec_path: Path, session_md_path: Path) -> dict:
    sm = yaml.safe_load(Path(session_md_path).read_text()) or {}
    cn = sm.get("convergent_nodes") or []
    active = sm.get("active_branches") or []
    if not cn:
        if active:
            return {"status": "fail", "details": {"reason": "no convergent_nodes despite active branches", "active_branches": active}}
        return {"status": "pass", "details": {"reason": "no branches active"}}
    bad = [c for c in cn if int(c.get("signal_strength", 0)) < 2]
    if bad:
        return {"status": "fail", "details": {"signal_strength_below_two": bad}}
    return {"status": "pass", "details": {"count": len(cn)}}


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--spec",       required=True, type=Path)
    p.add_argument("--session-md", required=True, type=Path)
    args = p.parse_args(argv)
    r = run(args.spec, args.session_md)
    print(r)
    return 0 if r["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
