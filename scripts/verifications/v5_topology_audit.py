#!/usr/bin/env python3
"""V5 — Topology-trace audit (§10).

V5 is audit-only: emits FAIL but the orchestrator does NOT re-route
(emits [V5-AUDIT-FAIL] warning at gate per §10).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

INSERTION_BLOCK = re.compile(
    r"##\s*insertion\s*$(.*?)(?=^##\s|\Z)", re.MULTILINE | re.DOTALL
)
LEDGER_NODE = re.compile(r"^##\s+ledger-entry:\s+(\S+)\s+\[", re.MULTILINE)


def run(spec_path: Path, session_md_path: Path) -> dict:
    sd = Path(session_md_path).parent
    trace_path = sd / "topology-trace.md"
    ledger_path = sd / "grs-ledger.md"
    if not trace_path.exists() or trace_path.stat().st_size == 0:
        return {"status": "pass", "details": {"reason": "empty trace"}}

    trace_text = trace_path.read_text()
    ledger_text = ledger_path.read_text() if ledger_path.exists() else ""
    ledger_nodes = set(LEDGER_NODE.findall(ledger_text))

    bad: list[dict] = []
    for m in INSERTION_BLOCK.finditer(trace_text):
        block = m.group(1)
        attrs = {}
        for line in block.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                attrs[k.strip()] = v.strip()
        missing = [k for k in ("node", "reason", "triggered_by_node") if k not in attrs]
        if missing:
            bad.append({"missing_fields": missing, "block": block.strip()[:80]})
            continue
        if attrs["triggered_by_node"] not in ledger_nodes:
            bad.append({"orphan_triggered_by": attrs["triggered_by_node"], "node": attrs["node"]})

    if bad:
        return {"status": "fail", "details": {"bad_entries": bad}}
    return {"status": "pass", "details": {}}


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
