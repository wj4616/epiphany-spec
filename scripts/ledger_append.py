#!/usr/bin/env python3
"""ledger_append.py — F103 fix.

Replaces the heredoc-based ledger writer (which was vulnerable to Bash
command injection through LLM-supplied --headline values containing backticks
or $(...)). Python's string handling is safe by construction.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import sys
from pathlib import Path

ANN_LINE = re.compile(r"\[ann-(\d+)\]")


def _fragment_prefix(fragment: str) -> str:
    return Path(fragment).stem  # e.g. "stages/N2-DECOMPOSE-APU.md" → "N2-DECOMPOSE-APU"


def _annotations_picked_up(frag_path: Path, frag_prefix: str) -> list[str]:
    if not frag_path.exists():
        return []
    pickup: list[str] = []
    in_block = False
    for line in frag_path.read_text().splitlines():
        if line.lstrip().startswith("## annotations:"):
            in_block = True
            continue
        if in_block and line.startswith("## "):
            break
        if in_block:
            m = ANN_LINE.search(line)
            if m:
                pickup.append(f"ann-{frag_prefix}-{m.group(1)}")
    return pickup


def _digest_lines(frag_path: Path) -> str:
    if not frag_path.exists():
        return "- (no digest content)"
    lines: list[str] = []
    in_output = False
    for line in frag_path.read_text().splitlines():
        if line.startswith("## output"):
            in_output = True
            continue
        if in_output and line.startswith("## "):
            break
        if in_output and line.strip():
            lines.append(f"- {line.strip()}")
        if len(lines) >= 15:
            break
    return "\n".join(lines) if lines else "- (no digest content)"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--session-dir",     required=True, type=Path)
    p.add_argument("--node-id",         required=True)
    p.add_argument("--phase",           required=True)
    p.add_argument("--cycle",           required=True)
    p.add_argument("--fragment",        required=True)
    p.add_argument("--hat",             required=True)
    p.add_argument("--tier",            required=True)
    p.add_argument("--exec-type",       required=True)
    p.add_argument("--score",           required=True)
    p.add_argument("--signals",         default="{}")
    p.add_argument("--provenance-tags", default="[]")
    p.add_argument("--headline",        default="")
    args = p.parse_args()

    ledger = args.session_dir / "grs-ledger.md"
    if not ledger.exists():
        print(f"ledger missing: {ledger}", file=sys.stderr)
        return 2

    frag_path = args.session_dir / args.fragment
    frag_prefix = _fragment_prefix(args.fragment)
    pickup = _annotations_picked_up(frag_path, frag_prefix)
    pickup_rendered = "[" + ", ".join(pickup) + "]" if pickup else "[]"

    ts = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    digest = _digest_lines(frag_path)

    # Escape headline for safe inclusion in YAML double-quoted string:
    # backslash + double-quote, and strip control characters.
    safe_headline = args.headline.replace("\\", "\\\\").replace('"', '\\"')
    safe_headline = "".join(c for c in safe_headline if c == "\t" or 0x20 <= ord(c) < 0x7F or ord(c) >= 0xA0)

    block = (
        "\n"
        f"## ledger-entry: {args.node_id} [cycle={args.cycle}]\n\n"
        "```yaml\n"
        f"node_id: {args.node_id}\n"
        f"phase: {args.phase}\n"
        f"cycle: {args.cycle}\n"
        f"ts: {ts}\n"
        f"fragment: {args.fragment}\n"
        f"hat: {args.hat}\n"
        f"tier: {args.tier}\n"
        f"exec_type: {args.exec_type}\n"
        f"score: {args.score}\n"
        f"signals: {args.signals}\n"
        f"provenance_tags: {args.provenance_tags}\n"
        f"annotations_picked_up: {pickup_rendered}\n"
        f'headline: "{safe_headline}"\n'
        "```\n\n"
        "### Digest (5–15 lines, signal-relevant content)\n"
        f"{digest}\n"
    )

    with open(ledger, "a") as f:
        f.write(block)
    return 0


if __name__ == "__main__":
    sys.exit(main())
