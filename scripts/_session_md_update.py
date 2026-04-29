"""Atomic mutator for session.md. Invoked by session-md-update.sh."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml


def _atomic_write(path: Path, text: str) -> None:
    tmp_dir = path.parent / "stages"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp = tmp_dir / "session.md.tmp"
    with open(tmp, "w") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    bak = tmp_dir / "session.md.bak"
    bak.write_text(path.read_text())


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
    data = yaml.safe_load(sm.read_text()) or {}

    if args.merge_yaml:
        patch = yaml.safe_load(args.merge_yaml.read_text()) or {}
        data.update(patch)
    if args.field and args.value is not None:
        data[args.field] = args.value
    if args.increment:
        data[args.increment] = data.get(args.increment, 0) + 1

    _atomic_write(sm, yaml.safe_dump(data, default_flow_style=False, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
