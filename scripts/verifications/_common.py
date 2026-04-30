"""Shared utilities for verification scripts."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

# --- Regex patterns ---
CITATION_STRICT = re.compile(r"\[APU-\d{3,}\]")
CITATION_BROAD = re.compile(r"\bAPU-\d{3,}\b")
HEADER = re.compile(r"^##\s+(\d{1,2})\.\s+", re.MULTILINE)
NEXT_SEC = re.compile(r"^##\s+\d{1,2}\.\s+", re.MULTILINE)
SEC_10 = re.compile(r"^##\s+10\.\s+Falsifiability", re.MULTILINE)
R_HEADER = re.compile(r"^###\s+(R-\d+)\b", re.MULTILINE)
CONSTRAINT_HEADER = re.compile(
    r"^###\s+(C-\d+)\s+\[([^\]]+)\]", re.MULTILINE
)
SEC_7_RE = re.compile(r"^##\s+7\.\s+Constraints", re.MULTILINE)


# --- APU loading ---
def load_apus(session_md_path: Path) -> list[str]:
    data = yaml.safe_load(session_md_path.read_text()) or {}
    apus = data.get("apus") or []
    return [a["id"] if isinstance(a, dict) else str(a) for a in apus]


# --- Section splitting ---
def split_sections(spec_text: str) -> dict[int, str]:
    out: dict[int, str] = {}
    matches = list(HEADER.finditer(spec_text))
    for i, m in enumerate(matches):
        sec = int(m.group(1))
        if not (1 <= sec <= 16):
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(spec_text)
        out[sec] = spec_text[start:end]
    return out


# --- Constraint parsing ---
def parse_constraints(spec_text: str) -> list[dict]:
    m7 = SEC_7_RE.search(spec_text)
    if not m7:
        return []
    next_sec = NEXT_SEC.search(spec_text, pos=m7.end())
    end = next_sec.start() if next_sec else len(spec_text)
    body = spec_text[m7.end():end]
    out: list[dict] = []
    for m in CONSTRAINT_HEADER.finditer(body):
        cid, tags = m.group(1), m.group(2)
        attrs = dict(
            p.split(":", 1) for p in [t.strip() for t in tags.split(",")] if ":" in p
        )
        out.append(
            {"id": cid, "tags": {k.strip(): v.strip() for k, v in attrs.items()}}
        )
    return out


# --- Word count ---
def word_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len(re.findall(r"\b\w+\b", path.read_text()))


def shared_main(run_fn, extra_args: list[dict] | None = None):
    """Shared CLI entry point for verification scripts.

    Handles argparse, calls run_fn, prints result dict, and returns exit code.
    extra_args: optional list of {name, type, required, default, help} dicts
    for script-specific arguments (e.g. --threshold for v7b).
    """
    import argparse
    p = argparse.ArgumentParser(description=run_fn.__doc__ or "")
    p.add_argument("--spec", required=True, type=Path)
    p.add_argument("--session-md", required=True, type=Path)
    for ea in (extra_args or []):
        kwargs = {k: v for k, v in ea.items() if k != "name"}
        p.add_argument(f"--{ea['name']}", **kwargs)
    args = p.parse_args()
    extra_kwargs = {ea["name"]: getattr(args, ea["name"]) for ea in (extra_args or [])}
    r = run_fn(args.spec, args.session_md, **extra_kwargs)
    print(r)
    return 0 if r["status"] == "pass" else 1
