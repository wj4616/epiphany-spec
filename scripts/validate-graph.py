#!/usr/bin/env python3
"""validate-graph.py — PRC1 mechanized for epiphany-spec.

Five checks (§3):
  1) Module completeness — every node has modules/N*.md (skippable with --skip-modules)
  2) Ledger placeholder — every LLM-backed module's prompt template contains
     {{ledger_at_dispatch}} (no-llm tier exempt; resolved via hats.json)
  3) No MCP references — no module references mcp__dify-* tools
  4) Script presence — every script in §3 exists and is executable
  5) Session isolation — post-init directory contents match expected state
     (only runs when --session-dir is passed)

Exit 0 = all checks pass, 1 = ≥1 failure.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GRAPH_PATH = REPO / "graph.json"
HATS_PATH  = REPO / "hats.json"
SCHEMA_PATH = REPO / "graph.schema.json"

REQUIRED_SCRIPTS = [
    "scripts/session-init.sh",
    "scripts/ledger-append.sh",
    "scripts/spec-chunk-write.sh",
    "scripts/seed-similarity.py",
    "scripts/cross_run_index.py",
    "scripts/validate-graph.py",
    "scripts/validate-spec-doc.sh",
]

LEDGER_PLACEHOLDER = "{{ledger_at_dispatch}}"
MCP_REGEX = re.compile(r"mcp__[A-Za-z0-9_\-]+")


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def check_module_completeness(graph: dict) -> list[str]:
    errors: list[str] = []
    for n in graph["nodes"]:
        mod = REPO / n["module_file"]
        if not mod.exists():
            errors.append(f"PRC1.1: missing module file {mod}")
    for tname, tmpl in graph["dynamic_templates"].items():
        mod = REPO / tmpl["module_file"]
        if not mod.exists():
            errors.append(f"PRC1.1: missing dynamic-template module {mod}")
    return errors


def check_ledger_placeholder(graph: dict, hats: dict) -> list[str]:
    errors: list[str] = []
    no_llm_hats: set[str] = set(hats["tiers"]["no-llm"])
    for n in graph["nodes"]:
        if n["tier"] == "no-llm":
            continue
        mod = REPO / n["module_file"]
        if not mod.exists():
            continue  # caught by check 1
        body = mod.read_text()
        if LEDGER_PLACEHOLDER not in body:
            errors.append(f"PRC1.2: {n['id']} prompt missing {LEDGER_PLACEHOLDER}")
    return errors


def check_no_mcp(graph: dict) -> list[str]:
    errors: list[str] = []
    for n in graph["nodes"]:
        mod = REPO / n["module_file"]
        if not mod.exists():
            continue
        body = mod.read_text()
        m = MCP_REGEX.search(body)
        if m:
            errors.append(f"PRC1.3: {n['id']} references {m.group()}")
    return errors


def check_script_presence() -> list[str]:
    errors: list[str] = []
    for s in REQUIRED_SCRIPTS:
        p = REPO / s
        if not p.exists():
            errors.append(f"PRC1.4: missing script {s}")
        elif s.endswith(".sh") and not os.access(p, os.X_OK):
            errors.append(f"PRC1.4: script not executable {s}")
    return errors


def check_session_isolation(session_dir: Path,
                            allowed_solution_roots: list[Path] | None = None) -> list[str]:
    errors: list[str] = []
    expected_files = {"input.md", "session.md", "grs-ledger.md", "topology-trace.md"}
    expected_dirs = {"stages"}
    optional = {"spec-export"}  # symlink

    # All expected entries must exist.
    for f in expected_files:
        p = session_dir / f
        if not p.exists():
            errors.append(f"PRC1.5: missing {f}")
    for d in expected_dirs:
        p = session_dir / d
        if not p.is_dir():
            errors.append(f"PRC1.5: missing dir {d}")

    # Append-only files must be empty.
    for f in ("grs-ledger.md", "topology-trace.md"):
        p = session_dir / f
        if p.exists() and p.stat().st_size > 0:
            errors.append(f"PRC1.5: {f} is non-empty (must be empty post-init)")

    # stages/ MUST be empty post-init.
    stages = session_dir / "stages"
    if stages.is_dir():
        for child in stages.iterdir():
            if child.name == "session.md.bak":
                continue
            errors.append(f"PRC1.5: unexpected pre-existing fragment {child.name}")

    # No unexpected siblings.
    allowed = expected_files | expected_dirs | optional | {"session.md.bak"}
    for child in session_dir.iterdir():
        if child.name not in allowed:
            errors.append(f"PRC1.5: unexpected entry {child.name}")

    # Validate spec-export symlink (F015 + F109).
    sx = session_dir / "spec-export"
    if sx.exists() or sx.is_symlink():
        if not sx.is_symlink():
            errors.append("PRC1.5: spec-export is not a symlink")
        else:
            try:
                target = sx.resolve(strict=True)
            except (FileNotFoundError, OSError) as e:
                errors.append(f"PRC1.5: spec-export resolves to missing target ({e})")
            else:
                if not target.is_dir():
                    errors.append("PRC1.5: spec-export resolves to non-directory")
                roots = allowed_solution_roots or [
                    Path("~/docs/solution").expanduser().resolve()
                ]
                if not any(_is_under(target, r) for r in roots):
                    errors.append(
                        f"PRC1.5: spec-export resolves outside allowed roots "
                        f"({target}; allowed={[str(r) for r in roots]})"
                    )
    return errors


def _is_under(path: Path, root: Path) -> bool:
    """Return True if `path` is inside `root` (after resolution)."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--session-dir", type=Path, default=None)
    p.add_argument("--skip-modules", action="store_true",
                   help="Skip checks 1, 2, 3 (module-dependent) — useful before modules exist.")
    p.add_argument("--allowed-solution-root", action="append", type=Path, default=None,
                   help="Allowed root for spec-export symlink target (F109). May be repeated. "
                        "Default: ~/docs/solution.")
    args = p.parse_args(argv)

    graph = load_json(GRAPH_PATH)
    hats  = load_json(HATS_PATH)

    errors: list[str] = []
    if not args.skip_modules:
        errors += check_module_completeness(graph)
        errors += check_ledger_placeholder(graph, hats)
        errors += check_no_mcp(graph)
    errors += check_script_presence()
    if args.session_dir is not None:
        errors += check_session_isolation(args.session_dir, args.allowed_solution_root)

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("PRC1: all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
