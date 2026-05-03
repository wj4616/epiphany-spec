#!/usr/bin/env python3
"""V10 — Structure adherence check (BUG-12 fix).

Verifies that the output spec's section structure matches the structure
requested in input.md and the section_map produced by N-SPEC-CONSTRUCT.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


HEADER_RE = re.compile(r"^##\s+(\S+)\.?\s+", re.MULTILINE)


def _extract_requested_sections(input_text: str) -> set[str]:
    """Scan input.md for explicit section requests."""
    requested = set()
    # Patterns like "Section 5.5", "Appendix C", "Section 8"
    for match in re.finditer(
        r"(?:Section|Appendix)\s+(\S+)", input_text, re.IGNORECASE
    ):
        requested.add(match.group(1))
    # Mode matrix table request
    if re.search(r"mode\s*matrix\s*(?:table|chart)", input_text, re.IGNORECASE):
        requested.add("mode_matrix")
    # Smoke tests request
    if re.search(r"smoke\s*test", input_text, re.IGNORECASE):
        requested.add("smoke_tests")
    return requested


def _extract_spec_sections(spec_text: str) -> set[str]:
    """Extract section numbers/titles from spec file."""
    return {m.group(1) for m in HEADER_RE.finditer(spec_text)}


def run(spec_path: Path, session_md_path: Path) -> dict:
    sd = Path(session_md_path).parent
    input_path = sd / "input.md"
    construct = sd / "stages" / "N11-SPEC-CONSTRUCT.md"

    spec_text = Path(spec_path).read_text()
    spec_sections = _extract_spec_sections(spec_text)

    missing = []
    extras = []

    # Check 1: requested sections in input.md must appear in spec
    if input_path.exists():
        input_text = input_path.read_text()
        requested = _extract_requested_sections(input_text)
        for sec in requested:
            if sec not in spec_sections and sec.lower() not in {
                s.lower() for s in spec_sections
            }:
                missing.append({"source": "input.md", "section": sec})

    # Check 2: section_map from N-SPEC-CONSTRUCT must be honored
    if construct.exists():
        construct_text = construct.read_text()
        # Extract section_map entries
        map_re = re.compile(
            r"-\s+section_number:\s*(\S+)", re.MULTILINE
        )
        mapped = {m.group(1) for m in map_re.finditer(construct_text)}
        for sec in mapped:
            if sec not in spec_sections and sec.lower() not in {
                s.lower() for s in spec_sections
            }:
                missing.append({"source": "section_map", "section": sec})
        for sec in spec_sections:
            if sec not in mapped and sec.lower() not in {
                m.lower() for m in mapped
            }:
                extras.append(sec)

    if missing or extras:
        return {
            "status": "fail",
            "details": {
                "missing_sections": missing,
                "extra_sections": extras,
            },
        }
    return {"status": "pass", "details": {}}


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(
        description="V10 — Structure adherence: checks spec sections match input requests."
    )
    p.add_argument("--spec", required=True, type=Path)
    p.add_argument("--session-md", required=True, type=Path)
    args = p.parse_args(argv)
    r = run(args.spec, args.session_md)
    print(r)
    return 0 if r["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
