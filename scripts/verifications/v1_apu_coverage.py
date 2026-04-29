#!/usr/bin/env python3
"""V1 — APU coverage (§10, F207 merger of V1a + V1b).

Two checks in one pass:
  (a) per-section citation discipline — sections 3-11, 15-16 must each
      contain at least one bracketed [APU-NNN] reference. Strict regex.
  (b) orphan APU detection — every APU declared in session.md.apus must
      appear at least once in the spec body (excluding Section 8, the APU
      registry itself). Broader regex matches both bracketed AND bare
      references (Section 14 `dependencies` uses bare form).

Either or both failures → status: fail; details carries each failure
mode separately.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from ._common import CITATION_STRICT, CITATION_BROAD, HEADER, split_sections, load_apus

EXEMPT_SECTIONS = {1, 2, 12, 13, 14}
SECTION_8_HEADER = re.compile(r"^##\s+8\.\s+", re.MULTILINE)
SECTION_9_HEADER = re.compile(r"^##\s+9\.\s+", re.MULTILINE)


def _strip_section_8(text: str) -> str:
    m8 = SECTION_8_HEADER.search(text)
    if not m8:
        return text
    m9 = SECTION_9_HEADER.search(text, pos=m8.end())
    end = m9.start() if m9 else len(text)
    return text[: m8.start()] + text[end:]


def run(spec_path: Path, session_md_path: Path) -> dict:
    text = Path(spec_path).read_text()
    # (a) per-section citation discipline
    sections = split_sections(text)
    missing_sections: list[int] = []
    for sec in range(1, 17):
        if sec in EXEMPT_SECTIONS:
            continue
        body = sections.get(sec, "")
        if not CITATION_STRICT.search(body):
            missing_sections.append(sec)

    # (b) orphan APUs
    cite_corpus = _strip_section_8(text)
    cited = set(CITATION_BROAD.findall(cite_corpus))
    declared = load_apus(Path(session_md_path))
    uncited = [a for a in declared if a not in cited]

    if missing_sections or uncited:
        return {"status": "fail", "details": {
            "sections_without_citation": missing_sections,
            "uncited_apus": uncited,
        }}
    return {"status": "pass", "details": {}}


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--spec",       required=True, type=Path)
    p.add_argument("--session-md", required=True, type=Path)
    args = p.parse_args(argv)
    r = run(args.spec, args.session_md)
    print(r)
    return 0 if r["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
