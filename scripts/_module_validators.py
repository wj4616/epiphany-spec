#!/usr/bin/env python3
"""_module_validators.py — single source of truth for module-level invariants (F202).

Shared by PRC1 (validate-graph.py) and pytest frontmatter lint
(test_module_frontmatter.py). Eliminates the F202 duplicate-implementation
drift risk.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]

LEDGER_PLACEHOLDER = "{{ledger_at_dispatch}}"
MCP_REGEX = re.compile(r"mcp__[A-Za-z0-9_\-]+")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
NO_LLM_NODES = {"N-CROSS-RUN-SEED", "N-GRS-EXPORT", "N-DEFIXATION", "N-REWRITE-EVALUATOR"}
REQUIRED_FRONTMATTER_FIELDS = {"node_id", "phase", "exec_type", "required_output_sections"}
EXEC_TYPES = {"inline", "spawn"}


# ---- frontmatter I/O ---------------------------------------------------------

def parse_frontmatter(mod_path: Path) -> dict:
    """Return YAML frontmatter dict from a module file, or {}."""
    text = mod_path.read_text()
    m = FRONTMATTER.match(text)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


def _module_files() -> list[Path]:
    return sorted((REPO / "modules").glob("N-*.md"))


# ---- PRC1 checks (shared with validate-graph.py) ----------------------------

def check_module_completeness(graph: dict) -> list[str]:
    """PRC1.1 — every node in graph.json must have modules/N*.md on disk."""
    errors: list[str] = []
    for n in graph["nodes"]:
        mod_path = REPO / n["module_file"]
        if not mod_path.exists():
            errors.append(f"PRC1.1: missing module file {n['module_file']} for node {n['id']}")
    return errors


def check_ledger_placeholder(graph: dict) -> list[str]:
    """PRC1.2 — every LLM-backed module must contain {{ledger_at_dispatch}}."""
    hats = json.loads((REPO / "hats.json").read_text())
    hat_to_tier = {h: t for t, hl in hats["tiers"].items() for h in hl}
    errors: list[str] = []
    for n in graph["nodes"]:
        if n["id"] in NO_LLM_NODES:
            continue
        mod_path = REPO / n["module_file"]
        if not mod_path.exists():
            continue
        _, body_text = _read_module_body(mod_path)
        if LEDGER_PLACEHOLDER not in body_text:
            errors.append(f"PRC1.2: {n['id']} prompt missing {LEDGER_PLACEHOLDER}")
    return errors


def check_no_mcp(graph: dict) -> list[str]:
    """PRC1.3 — no module body references mcp__* tools."""
    errors: list[str] = []
    for n in graph["nodes"]:
        mod_path = REPO / n["module_file"]
        if not mod_path.exists():
            continue
        _, body_text = _read_module_body(mod_path)
        m = MCP_REGEX.search(body_text)
        if m:
            errors.append(f"PRC1.3: {n['id']} references {m.group()}")
    return errors


# ---- frontmatter lint checks (shared with test_module_frontmatter.py) --------

def check_frontmatter_shape(mod_path: Path) -> list[str]:
    """Verify required YAML frontmatter fields and exec_type validity."""
    fm = parse_frontmatter(mod_path)
    errors: list[str] = []
    missing = REQUIRED_FRONTMATTER_FIELDS - set(fm.keys())
    if missing:
        errors.append(f"{mod_path.name}: missing frontmatter fields: {sorted(missing)}")
    et = fm.get("exec_type")
    if et and et not in EXEC_TYPES:
        errors.append(f"{mod_path.name}: invalid exec_type {et!r}")
    return errors


def check_hat_resolves(mod_path: Path) -> list[str]:
    """Verify node's hat field resolves to hats.json."""
    fm = parse_frontmatter(mod_path)
    node_id = fm.get("node_id")
    hat = fm.get("hat")
    if node_id in NO_LLM_NODES or hat is None:
        return []
    hats = json.loads((REPO / "hats.json").read_text())
    hat_to_tier = {h: t for t, hl in hats["tiers"].items() for h in hl}
    if hat not in hat_to_tier:
        return [f"{mod_path.name}: hat {hat!r} not found in hats.json"]
    return []


def check_annotations_present(mod_path: Path) -> list[str]:
    """Verify ## ANNOTATIONS section exists in LLM-backed modules."""
    fm = parse_frontmatter(mod_path)
    node_id = fm.get("node_id")
    if node_id in NO_LLM_NODES or fm.get("hat") is None:
        return []
    text = mod_path.read_text()
    if "## ANNOTATIONS" not in text:
        return [f"{mod_path.name}: missing ## ANNOTATIONS section"]
    return []


# ---- internal helpers --------------------------------------------------------

def _read_module_body(mod_path: Path) -> tuple[str, str]:
    """Return (frontmatter, body) for a module file, without parse."""
    text = mod_path.read_text()
    if text.startswith("---\n"):
        end = text.index("\n---\n", 4)
        return text[4:end], text[end + 5:]
    return "", text
