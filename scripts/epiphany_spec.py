#!/usr/bin/env python3
"""epiphany_spec.py — single CLI entry, git-style subcommand pattern (I301).

Dispatches to the existing helper modules; no business logic here. The
helpers stay as importable Python modules; this is just the front door.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO))


def _dispatch(name: str) -> int:
    if name == "ledger-append":
        from scripts.ledger_append import main; return main()
    if name == "session-md-update":
        from scripts.session_md_update import main; return main()
    if name == "ledger-digest":
        from scripts.ledger_digest import main; return main()
    if name == "build-prompt":
        from scripts.build_prompt import main; return main()
    if name == "compute-completeness":
        from scripts.compute_completeness import main; return main()
    if name == "seed":
        from scripts.seed_similarity import main; return main()
    if name == "cross-run-index":
        from scripts.cross_run_index import main; return main()
    if name == "dry-run":
        from scripts.dry_run_pipeline import main; return main()
    return 2


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(
            "Usage: epiphany_spec.py <subcommand> [args]\n\n"
            "Subcommands:\n"
            "  ledger-append          append a ledger entry\n"
            "  session-md-update      atomic mutation of session.md\n"
            "  ledger-digest          deterministic ledger digest emission\n"
            "  build-prompt           build a substituted prompt for a module\n"
            "  compute-completeness   §15 sub-dimension scores\n"
            "  seed                   slugify / Jaccard\n"
            "  cross-run-index        read/rebuild cross-run index\n"
            "  dry-run                predict dispatch sequence\n"
        )
        return 0
    sub, *rest = argv
    sys.argv = [sub] + rest
    rc = _dispatch(sub)
    if rc == 2:
        print(f"unknown subcommand: {sub}", file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
