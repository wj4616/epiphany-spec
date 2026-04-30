#!/usr/bin/env python3
"""_yaml_io.py — atomic write helpers for YAML and JSON (I101).

Single source of truth for the tmp+fsync+rename+bak discipline used by
session_md_update.py and cross_run_index.py.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml


def atomic_write_text(path: Path, text: str, *, bak: bool = False,
                      bak_dir: Path | None = None) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, "w") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    if bak:
        bak_dir = bak_dir or path.parent
        bak_path = bak_dir / (path.name + ".bak")
        bak_dir.mkdir(parents=True, exist_ok=True)
        bak_path.write_text(path.read_text())


def atomic_write_json(path: Path, obj: Any, *, bak: bool = False,
                     bak_dir: Path | None = None) -> None:
    atomic_write_text(path, json.dumps(obj, indent=2, sort_keys=True),
                      bak=bak, bak_dir=bak_dir)


def atomic_write_yaml(path: Path, obj: Any, *, bak: bool = False,
                      bak_dir: Path | None = None) -> None:
    atomic_write_text(path, yaml.safe_dump(obj, sort_keys=False),
                      bak=bak, bak_dir=bak_dir)
