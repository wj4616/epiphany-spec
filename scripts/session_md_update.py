#!/usr/bin/env python3
"""Atomic mutator for session.md. Invoked by session_md_update.py."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml

from scripts._yaml_io import atomic_write_yaml


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--session-dir", required=True, type=Path)
    p.add_argument("--field")
    p.add_argument("--value")
    p.add_argument("--increment")
    p.add_argument("--merge-yaml", type=Path)
    args = p.parse_args()

    sm = args.session_dir / "session.md"
    if not sm.exists():
        print(f"session.md missing: {sm}", file=sys.stderr)
        return 2
    try:
        data = yaml.safe_load(sm.read_text()) or {}
    except yaml.YAMLError:
        print("{halt_state: halt-session-md-unrecoverable, subreason: yaml-parse-failure, diagnostic: session.md is corrupted and unreadable}", file=sys.stderr)
        return 4

    if args.merge_yaml:
        patch = yaml.safe_load(args.merge_yaml.read_text()) or {}
        data.update(patch)
    if args.field and args.value is not None:
        data[args.field] = args.value
    if args.increment:
        data[args.increment] = data.get(args.increment, 0) + 1

    atomic_write_yaml(sm, data, bak=True, bak_dir=args.session_dir / "stages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
