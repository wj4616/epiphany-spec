#!/usr/bin/env python3
"""V6 — Falsifiability + adversarial break-attempt (§10)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from ._common import R_HEADER, SEC_10, NEXT_SEC


def run(spec_path: Path, session_md_path: Path) -> dict:
    text = Path(spec_path).read_text()
    m = SEC_10.search(text)
    if not m:
        return {"status": "pass", "details": {"reason": "Section 10 absent"}}
    nxt = NEXT_SEC.search(text, pos=m.end())
    end = nxt.start() if nxt else len(text)
    body = text[m.end():end]

    headers = list(R_HEADER.finditer(body))
    bad: list[dict] = []
    for i, h in enumerate(headers):
        sub_end = headers[i + 1].start() if i + 1 < len(headers) else len(body)
        sub = body[h.end():sub_end]
        rid = h.group(1)
        missing: list[str] = []
        for field in ("test", "break_attempt"):
            mat = re.search(rf"^[-*]\s*{field}\s*:\s*(.+?)$", sub, re.MULTILINE)
            if not mat or not mat.group(1).strip():
                missing.append(field)
        if missing:
            bad.append({"id": rid, "missing": missing})

    if bad:
        return {"status": "fail", "details": {"bad": bad}}
    return {"status": "pass", "details": {"requirement_count": len(headers)}}


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="V6 — Falsifiability check: validates requirement falsifiability criteria.")
    p.add_argument("--spec",       required=True, type=Path)
    p.add_argument("--session-md", required=True, type=Path)
    args = p.parse_args(argv)
    r = run(args.spec, args.session_md)
    print(r)
    return 0 if r["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
