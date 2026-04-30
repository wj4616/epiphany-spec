#!/usr/bin/env python3
"""V8 — File save (§10, §11)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

MODE_MIN_BYTES = {"MINIMAL": 4 * 1024, "STANDARD": 12 * 1024, "DEEP": 24 * 1024}
MARKER_RE = re.compile(r"<!--\s*end:spec-v(\d+)\s*-->\s*\Z")


def run(spec_path: Path, session_md_path: Path) -> dict:
    sm = yaml.safe_load(Path(session_md_path).read_text()) or {}
    scale = sm.get("scale", "STANDARD")
    version = int(sm.get("current_version", 1))
    minimum = MODE_MIN_BYTES.get(scale, MODE_MIN_BYTES["STANDARD"])

    p = Path(spec_path)
    if not p.exists():
        return {"status": "fail", "details": {"reason": "spec missing", "path": str(p)}}
    text = p.read_text()
    size = p.stat().st_size

    m = MARKER_RE.search(text)
    if not m:
        return {"status": "fail", "details": {"reason": "missing final-line marker"}}
    if int(m.group(1)) != version:
        return {"status": "fail", "details": {"reason": f"marker version mismatch (file says {m.group(1)}, expected {version})"}}

    progress = (sm.get("write_progress") or {}).get(f"spec_v{version}", [])
    all_sections_present = sorted(int(x) for x in progress) == list(range(1, 18))

    if size >= minimum:
        return {"status": "pass", "details": {"size": size, "minimum": minimum}}

    # Legitimate-small-spec path
    if all_sections_present:
        return {
            "status": "pass",
            "details": {
                "size": size, "minimum": minimum,
                "warnings": [f"[V8-SIZE-WARNING — spec is below mode minimum ({size} B < {minimum} B) but all sections present and well-formed; passing with warning]"],
            },
        }
    return {"status": "fail", "details": {"reason": "below mode minimum and write_progress incomplete", "size": size, "minimum": minimum}}


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="V8 — File save check: validates stage file sizes against mode-specific minimums.")
    p.add_argument("--spec",       required=True, type=Path)
    p.add_argument("--session-md", required=True, type=Path)
    args = p.parse_args(argv)
    r = run(args.spec, args.session_md)
    print(r)
    return 0 if r["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
