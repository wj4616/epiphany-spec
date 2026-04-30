#!/usr/bin/env python3
"""V2 — Vocabulary lock (§10).

For each locked-vocabulary entry {term, synonyms}: scan the spec for synonym
occurrences as whole words. Each synonym occurrence is leakage if the canonical
term does not also appear in the same section.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

HEADER = re.compile(r"^##\s+\d{1,2}\.\s+", re.MULTILINE)


def _split_sections(text: str) -> list[str]:
    matches = list(HEADER.finditer(text))
    out: list[str] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append(text[m.start():end])
    return out


def _word_re(s: str) -> re.Pattern:
    return re.compile(r"\b" + re.escape(s) + r"\b", re.IGNORECASE)


def run(spec_path: Path, session_md_path: Path) -> dict:
    text = Path(spec_path).read_text()
    sections = _split_sections(text)
    sm = yaml.safe_load(Path(session_md_path).read_text()) or {}
    vocab = sm.get("locked_vocabulary") or []

    leaks: list[dict] = []
    for entry in vocab:
        term = entry["term"] if isinstance(entry, dict) else str(entry)
        synonyms = entry.get("synonyms", []) if isinstance(entry, dict) else []
        term_re = _word_re(term)
        for s_idx, sec in enumerate(sections):
            term_present = bool(term_re.search(sec))
            for syn in synonyms:
                syn_re = _word_re(syn)
                if syn_re.search(sec) and not term_present:
                    leaks.append({"section_index": s_idx, "synonym": syn, "canonical": term})
    if leaks:
        return {"status": "fail", "details": {"leakage_sites": leaks}}
    return {"status": "pass", "details": {}}


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="V2 — Vocabulary lock check: ensures spec body does not introduce terms outside the locked vocabulary.")
    p.add_argument("--spec",       required=True, type=Path)
    p.add_argument("--session-md", required=True, type=Path)
    args = p.parse_args(argv)
    r = run(args.spec, args.session_md)
    print(r)
    return 0 if r["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
