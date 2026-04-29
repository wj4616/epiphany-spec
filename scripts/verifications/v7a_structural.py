#!/usr/bin/env python3
"""V7a — Structural checks (§10): atomic-step, dead-end, missing-precondition."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from ._common import NEXT_SEC, load_apus

# Compact common-verb list. Heuristic: a step is "non-atomic" iff it contains
# more than one of these verbs in the title fragment.
_VERBS = {
    "compute", "emit", "validate", "read", "write", "verify", "check",
    "produce", "consume", "transform", "parse", "render", "append", "load",
    "save", "send", "receive", "execute", "fire", "trigger", "evaluate",
    "score", "rank", "select", "reject", "approve",
}


def count_verbs(s: str) -> int:
    tokens = re.findall(r"\b[A-Za-z]+\b", s.lower())
    return sum(1 for t in tokens if t in _VERBS)


_BEHAVIOR = re.compile(r"^##\s+5\.\s+Behavior", re.MULTILINE)
_STEP_BLOCK_INPUT = re.compile(r"^\s*[-*]\s*input:\s*(.+?)$", re.MULTILINE)
_STEP_BLOCK_OUTPUT = re.compile(r"^\s*[-*]\s*output:\s*(.+?)$", re.MULTILINE)


def _section_body(text: str, start: re.Match) -> str:
    nxt = NEXT_SEC.search(text, pos=start.end())
    end = nxt.start() if nxt else len(text)
    return text[start.end():end]


def run(spec_path: Path, session_md_path: Path) -> dict:
    text = Path(spec_path).read_text()
    m = _BEHAVIOR.search(text)
    if not m:
        return {"status": "pass", "details": {"reason": "Section 5 absent"}}
    behavior = _section_body(text, m)

    apu_ids = set(load_apus(Path(session_md_path)))

    # Split behavior into per-step blocks: a block starts at a top-level "- " line
    # and continues until the next top-level "- " or end.
    raw_lines = behavior.splitlines()
    blocks: list[list[str]] = []
    cur: list[str] = []
    for line in raw_lines:
        if re.match(r"^[-*]\s+\S", line):
            if cur:
                blocks.append(cur)
            cur = [line]
        else:
            if cur:
                cur.append(line)
    if cur:
        blocks.append(cur)

    non_atomic: list[str] = []
    inputs: list[tuple[int, str]] = []
    outputs: list[tuple[int, str]] = []
    for idx, blk in enumerate(blocks):
        title = re.sub(r"^[-*]\s+", "", blk[0]).split(":", 1)[-1] if ":" in blk[0] else blk[0][2:]
        if count_verbs(title) > 1:
            non_atomic.append(title.strip())
        body = "\n".join(blk[1:])
        for mi in _STEP_BLOCK_INPUT.finditer(body):
            inputs.append((idx, mi.group(1).strip()))
        for mo in _STEP_BLOCK_OUTPUT.finditer(body):
            outputs.append((idx, mo.group(1).strip()))

    output_names = {o for _, o in outputs}

    # Build search corpus = (text after Section 5) + (per-block bodies AFTER the
    # producing block, within Section 5). Excludes the producing block's own
    # body so the output line itself doesn't count as downstream reference.
    next_sec_after_5 = NEXT_SEC.search(text, pos=m.end())
    text_after_section_5 = text[next_sec_after_5.start():] if next_sec_after_5 else ""

    block_bodies: list[str] = ["\n".join(b) for b in blocks]

    dead_end: list[str] = []
    for idx, oname in outputs:
        # 1) Consumed by another step's `input:` (different block from producer).
        if any(name == oname and i_idx != idx for i_idx, name in inputs):
            continue
        # 2) Mentioned in any later step's body (Section 5, blocks AFTER the producer).
        later_block_text = "\n".join(block_bodies[idx + 1:])
        if oname in later_block_text:
            continue
        # 3) Mentioned anywhere in sections 6+ (consumer in another section).
        if oname in text_after_section_5:
            continue
        dead_end.append(oname)

    missing_pre: list[str] = []
    available: set[str] = set()
    for idx, blk in enumerate(blocks):
        body = "\n".join(blk[1:])
        for mi in _STEP_BLOCK_INPUT.finditer(body):
            inp = mi.group(1).strip()
            if re.match(r"^APU-\d{3,}$", inp):
                if inp not in apu_ids:
                    missing_pre.append(inp)
                continue
            if inp not in available:
                missing_pre.append(inp)
        for mo in _STEP_BLOCK_OUTPUT.finditer(body):
            available.add(mo.group(1).strip())

    fails: dict = {}
    if non_atomic:
        fails["non_atomic_steps"] = non_atomic
    if dead_end:
        fails["dead_end_outputs"] = dead_end
    if missing_pre:
        fails["missing_preconditions"] = missing_pre
    if fails:
        return {"status": "fail", "details": fails}
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
