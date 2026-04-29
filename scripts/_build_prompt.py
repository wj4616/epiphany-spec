#!/usr/bin/env python3
"""_build_prompt.py — emit a substituted prompt for a module dispatch (I105).

Reads modules/<X>.md, runs ledger-digest, substitutes {{ledger_at_dispatch}}
and any other declared placeholders, asserts no `{{` remains, prints to
stdout. Closes F111 — orchestrator no longer responsible for substitution.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def _read_module(path: Path) -> tuple[str, str]:
    """Return (frontmatter, body)."""
    text = path.read_text()
    if text.startswith("---\n"):
        end = text.index("\n---\n", 4)
        return text[4:end], text[end + 5:]
    return "", text


def _ledger_digest(session_dir: Path) -> str:
    out = subprocess.run(
        ["bash", str(REPO / "scripts" / "ledger-digest.sh"),
         "--session-dir", str(session_dir),
         "--max-entries", "8", "--max-bytes", "8192"],
        capture_output=True, text=True, check=True,
    )
    return out.stdout


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--module",      required=True, type=Path)
    p.add_argument("--session-dir", required=True, type=Path)
    p.add_argument("--extra", action="append", default=None,
                   help="Additional substitutions: --extra KEY=VALUE (may repeat)")
    args = p.parse_args(argv)

    _, body = _read_module(args.module)
    digest = _ledger_digest(args.session_dir)

    substitutions = {"ledger_at_dispatch": digest}
    for kv in args.extra or []:
        if "=" not in kv:
            print(f"--extra requires KEY=VALUE form: {kv}", file=sys.stderr)
            return 2
        k, v = kv.split("=", 1)
        substitutions[k] = v

    out = body
    for k, v in substitutions.items():
        out = out.replace(f"{{{{{k}}}}}", v)

    # F111 guard: no remaining {{X}} placeholders.
    leak = re.search(r"\{\{[^}]+\}\}", out)
    if leak:
        print(
            f"[DISPATCH-PLACEHOLDER-LEAK module={args.module.name} placeholder={leak.group()}]",
            file=sys.stderr,
        )
        return 3

    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
