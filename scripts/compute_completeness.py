#!/usr/bin/env python3
"""compute_completeness.py — §15 completeness sub-dimensions + overall min."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml

from scripts.verifications._common import CITATION_BROAD

TEST_ELIGIBLE = {"functional", "requirement", "behavior"}
SEC_15_RE = re.compile(r"^##\s+15\.\s+", re.MULTILINE)
SEC_NEXT_RE = re.compile(r"^##\s+\d{1,2}\.\s+", re.MULTILINE)
R_REF = re.compile(r"\bR-\d+\b")
SEC_8_RE = re.compile(r"^##\s+8\.\s+", re.MULTILINE)


def _strip_section_8(text: str) -> str:
    m = SEC_8_RE.search(text)
    if not m:
        return text
    nxt = SEC_NEXT_RE.search(text, pos=m.end())
    end = nxt.start() if nxt else len(text)
    return text[:m.start()] + text[end:]


def _section_15_body(text: str) -> str:
    m = SEC_15_RE.search(text)
    if not m:
        return ""
    nxt = SEC_NEXT_RE.search(text, pos=m.end())
    end = nxt.start() if nxt else len(text)
    return text[m.end():end]


def _falsify_requirements(session_md_path: Path) -> list[dict]:
    sd = Path(session_md_path).parent
    fpath = sd / "stages" / "N11-FALSIFY.md"
    if not fpath.exists():
        return []
    data = yaml.safe_load(fpath.read_text()) or {}
    return data.get("requirements") or []


def compute(spec_path: Path, session_md_path: Path) -> dict:
    spec_text = Path(spec_path).read_text()
    sm = yaml.safe_load(Path(session_md_path).read_text()) or {}
    apus = sm.get("apus") or []

    cite_corpus = _strip_section_8(spec_text)
    cited = set(CITATION_BROAD.findall(cite_corpus))
    total_apus = len(apus)
    cited_apus = sum(1 for a in apus if (a["id"] if isinstance(a, dict) else a) in cited)
    coverage_apus = cited_apus / total_apus if total_apus else 1.0

    test_eligible = [a for a in apus if isinstance(a, dict) and a.get("type") in TEST_ELIGIBLE]
    requirements = _falsify_requirements(session_md_path)
    apus_with_req = {r.get("apu_id") for r in requirements if r.get("apu_id")}
    if test_eligible:
        covered = sum(1 for a in test_eligible if a["id"] in apus_with_req)
        coverage_falsifiability = covered / len(test_eligible)
    else:
        coverage_falsifiability = 1.0

    sec_15 = _section_15_body(spec_text)
    total_R = len(requirements)
    if total_R:
        edged_R: set[str] = set()
        for line in sec_15.splitlines():
            for match in R_REF.findall(line):
                if any(kw in line for kw in ("constrains", "implies", "conflicts")):
                    edged_R.add(match)
        ids = {r["id"] for r in requirements if r.get("id")}
        covered = sum(1 for rid in ids if rid in edged_R)
        coverage_dependency_map = covered / total_R
    else:
        coverage_dependency_map = 1.0

    cl = sm.get("conflict_ledger") or []
    if not cl:
        coverage_conflict_resolution = 1.0
    else:
        resolved = sum(1 for c in cl if c.get("resolved") is True)
        coverage_conflict_resolution = resolved / len(cl)

    overall_min = min(coverage_apus, coverage_falsifiability,
                      coverage_dependency_map, coverage_conflict_resolution)
    return {
        "coverage_apus": coverage_apus,
        "coverage_falsifiability": coverage_falsifiability,
        "coverage_dependency_map": coverage_dependency_map,
        "coverage_conflict_resolution": coverage_conflict_resolution,
        "overall_min": overall_min,
    }


def run(spec_path: Path, session_md_path: Path) -> int:
    print(json.dumps(compute(spec_path, session_md_path), indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--spec",       required=True, type=Path)
    p.add_argument("--session-md", required=True, type=Path)
    args = p.parse_args(argv)
    return run(args.spec, args.session_md)


if __name__ == "__main__":
    sys.exit(main())
