#!/usr/bin/env python3
"""_ledger_digest.py — deterministic ledger digest emission (F106).

Algorithm: emit the last K complete ledger-entry blocks (where K =
min(--max-entries, total_entries)) in their raw markdown form,
header-to-header. Total output capped at --max-bytes; if the K-block window
exceeds the cap, drop the OLDEST blocks until under cap. No summarization;
no LLM call.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ENTRY_HEADER = re.compile(r"^##\s+ledger-entry:\s+", re.MULTILINE)


def split_entries(text: str) -> list[str]:
    """Return list of `## ledger-entry:` blocks. The pre-first-entry preamble
    (if any) is discarded."""
    starts = [m.start() for m in ENTRY_HEADER.finditer(text)]
    if not starts:
        return []
    blocks: list[str] = []
    for i, s in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        blocks.append(text[s:end])
    return blocks


def emit(text: str, max_entries: int, max_bytes: int) -> str:
    blocks = split_entries(text)
    window = blocks[-max_entries:] if max_entries > 0 else []
    out = "".join(window)
    while window and len(out.encode("utf-8")) > max_bytes:
        window.pop(0)  # drop oldest
        out = "".join(window)
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--session-dir", required=True, type=Path)
    p.add_argument("--max-entries", type=int, default=8)
    p.add_argument("--max-bytes",   type=int, default=8192)
    args = p.parse_args(argv)

    ledger = args.session_dir / "grs-ledger.md"
    if not ledger.exists():
        return 0  # empty digest, exit clean
    sys.stdout.write(emit(ledger.read_text(), args.max_entries, args.max_bytes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
