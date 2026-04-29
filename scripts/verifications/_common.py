#!/usr/bin/env python3
"""Shared parsing helpers for V-check scripts."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

HEADER = re.compile(r"^##\s+(\d{1,2})\.\s+", re.MULTILINE)
NEXT_SEC = re.compile(r"^##\s+\d{1,2}\.\s+", re.MULTILINE)
CITATION_STRICT = re.compile(r"\[APU-\d{3,}\]")
CITATION_BROAD  = re.compile(r"\bAPU-\d{3,}\b")
CONSTRAINT_HEADER = re.compile(r"^###\s+(C-\d+)\s+\[([^\]]+)\]", re.MULTILINE)
SEC_7 = re.compile(r"^##\s+7\.\s+Constraints", re.MULTILINE)
R_HEADER = re.compile(r"^###\s+(R-\d+)\b", re.MULTILINE)
SEC_10 = re.compile(r"^##\s+10\.\s+Falsifiability", re.MULTILINE)
WORD = re.compile(r"\b\w+\b")


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


def load_apus(session_md_path: Path) -> list[str]:
    data = yaml.safe_load(Path(session_md_path).read_text()) or {}
    return [a["id"] if isinstance(a, dict) else str(a) for a in (data.get("apus") or [])]


def word_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len(WORD.findall(path.read_text()))


def parse_constraints(spec_text: str) -> list[dict]:
    m7 = SEC_7.search(spec_text)
    if not m7:
        return []
    nxt = NEXT_SEC.search(spec_text, pos=m7.end())
    end = nxt.start() if nxt else len(spec_text)
    body = spec_text[m7.end():end]
    out: list[dict] = []
    for m in CONSTRAINT_HEADER.finditer(body):
        cid, tags = m.group(1), m.group(2)
        attrs = {}
        for part in [p.strip() for p in tags.split(",")]:
            if ":" in part:
                k, v = part.split(":", 1)
                attrs[k.strip()] = v.strip()
        out.append({"id": cid, "tags": attrs})
    return out
