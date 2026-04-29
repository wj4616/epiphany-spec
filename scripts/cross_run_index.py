#!/usr/bin/env python3
"""cross_run_index.py — read/rebuild ~/docs/epiphany/spec/cross_run_index.json (§8)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml

INDEX_FILENAME = "cross_run_index.json"
FINALIZED_STATE = "FINALIZED"


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _safe_load_session_md(p: Path) -> dict | None:
    try:
        with open(p) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return None


def rebuild_from_scratch(base_dir: Path) -> dict[str, dict]:
    """Linear scan of base_dir/<session_id>/session.md, filter FINALIZED, build index, write atomically."""
    idx: dict[str, dict] = {}
    for child in base_dir.iterdir():
        if not child.is_dir():
            continue
        sm = child / "session.md"
        if not sm.exists():
            continue
        data = _safe_load_session_md(sm)
        if not data:
            continue
        if data.get("state") != FINALIZED_STATE:
            continue
        sid = data.get("session_id") or child.name
        idx[sid] = {
            "topic_slug": data.get("topic_slug", ""),
            "convergent_nodes_count": len(data.get("convergent_nodes") or []),
            "finalized_ts": data.get("finalized_ts", ""),
            "file_path": str(sm),
        }
    _atomic_write_json(base_dir / INDEX_FILENAME, idx)
    return idx


def load_or_rebuild(base_dir: Path) -> dict[str, dict]:
    base_dir = Path(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    idx_path = base_dir / INDEX_FILENAME
    if idx_path.exists():
        try:
            with open(idx_path) as f:
                return json.load(f)
        except Exception:
            pass  # fall through to rebuild
    return rebuild_from_scratch(base_dir)


def update(base_dir: Path, session_id: str, entry: dict) -> None:
    base_dir = Path(base_dir)
    idx = load_or_rebuild(base_dir)
    idx[session_id] = entry
    _atomic_write_json(base_dir / INDEX_FILENAME, idx)


def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--base-dir", required=True, type=Path)
    p.add_argument("--rebuild", action="store_true")
    args = p.parse_args()
    if args.rebuild:
        idx = rebuild_from_scratch(args.base_dir)
    else:
        idx = load_or_rebuild(args.base_dir)
    print(json.dumps(idx, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
