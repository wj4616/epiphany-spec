#!/usr/bin/env python3
"""V9 — Verbatim preservation check (BUG-13 fix).

Consumes N-VERBATIM-GUARD output and verifies every locked verbatim block
appears in the spec output unchanged in meaning and structure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def run(spec_path: Path, session_md_path: Path) -> dict:
    sd = Path(session_md_path).parent
    guard = sd / "stages" / "N0-VERBATIM-GUARD.md"
    if not guard.exists():
        return {"status": "pass", "details": {"reason": "no N-VERBATIM-GUARD fragment found"}}

    spec_text = Path(spec_path).read_text()
    guard_text = guard.read_text()

    # Extract locked blocks from guard fragment
    # Format: - lock_id: VB-001\n  block_type: ...\n  fingerprint: ...
    block_re = re.compile(
        r"-\s+lock_id:\s*(\S+)\s*\n"
        r"(?:\s+\w+:\s*.*?\n)*?"
        r"\s+fingerprint:\s*'(.*?)'",
        re.MULTILINE | re.DOTALL,
    )

    missing = []
    altered = []

    for match in block_re.finditer(guard_text):
        lock_id = match.group(1)
        fingerprint = match.group(2)
        parts = fingerprint.split("...")
        if len(parts) == 2:
            prefix, suffix = parts
            # Check if both prefix and suffix appear in spec
            prefix_found = prefix.strip() in spec_text
            suffix_found = suffix.strip() in spec_text
            if not prefix_found and not suffix_found:
                missing.append(lock_id)
            elif not prefix_found or not suffix_found:
                altered.append(lock_id)
        else:
            # Simple containment check
            if fingerprint.strip() not in spec_text:
                missing.append(lock_id)

    if missing or altered:
        return {
            "status": "fail",
            "details": {
                "missing_blocks": missing,
                "altered_blocks": altered,
            },
        }
    return {"status": "pass", "details": {}}


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(
        description="V9 — Verbatim preservation: checks locked verbatim blocks survive to spec."
    )
    p.add_argument("--spec", required=True, type=Path)
    p.add_argument("--session-md", required=True, type=Path)
    args = p.parse_args(argv)
    r = run(args.spec, args.session_md)
    print(r)
    return 0 if r["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
