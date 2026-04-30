#!/usr/bin/env python3
"""V3 — Constraint completeness (§10, §15)."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

from ._common import parse_constraints, word_count


def run(spec_path: Path, session_md_path: Path) -> dict:
    text = Path(spec_path).read_text()
    sm = yaml.safe_load(Path(session_md_path).read_text()) or {}
    constraints = parse_constraints(text)

    missing: list[dict] = []
    for c in constraints:
        if "statedness" not in c["tags"] or "severity" not in c["tags"]:
            missing.append({"id": c["id"], "tags": c["tags"]})
    enum_complete = bool((sm.get("constraint_inventory") or {}).get("enumeration_complete"))

    warnings: list[str] = []
    conflicts = sm.get("conflict_ledger") or []
    vague = sm.get("vague_items") or []
    input_path_raw = sm.get("input_md_path") or ""
    if conflicts == [] and vague == [] and input_path_raw:
        wc = word_count(Path(input_path_raw))
        if wc >= 50:
            warnings.append("[CONFLICT-DETECTION-SUSPECT — ambiguity scan produced no output]")

    if missing or not enum_complete:
        return {
            "status": "fail",
            "details": {
                "constraints_missing_axis": missing,
                "enumeration_complete": enum_complete,
                "warnings": warnings,
            },
        }
    return {"status": "pass", "details": {"warnings": warnings}}


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
