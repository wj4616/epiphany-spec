import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
MODULES_DIR = REPO / "modules"
HATS = yaml.safe_load((REPO / "hats.json").read_text()) if (REPO / "hats.json").exists() else None

REQUIRED_FIELDS = {"node_id", "phase", "exec_type", "required_output_sections"}
EXEC_TYPES = {"inline", "spawn"}
LEDGER_PLACEHOLDER = "{{ledger_at_dispatch}}"

# Modules whose tier is no-llm -- exempt from PRC1 check #2.
NO_LLM_NODES = {"N-CROSS-RUN-SEED", "N-GRS-EXPORT", "N-DEFIXATION", "N-REWRITE-EVALUATOR"}

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def _parse_frontmatter(p: Path) -> dict:
    text = p.read_text()
    m = FRONTMATTER.match(text)
    assert m, f"{p.name}: missing YAML frontmatter"
    return yaml.safe_load(m.group(1)) or {}


def _module_files() -> list[Path]:
    if not MODULES_DIR.exists():
        return []
    return sorted(MODULES_DIR.glob("*.md"))


def test_modules_dir_exists_or_empty():
    if not MODULES_DIR.exists():
        pytest.skip("modules/ does not exist yet (created by Tasks 23-28)")


@pytest.mark.parametrize("mod_path", _module_files(), ids=lambda p: p.name)
def test_module_has_required_frontmatter_fields(mod_path):
    fm = _parse_frontmatter(mod_path)
    missing = REQUIRED_FIELDS - set(fm.keys())
    assert not missing, f"{mod_path.name}: missing fields {missing}"
    assert fm["exec_type"] in EXEC_TYPES, f"{mod_path.name}: bad exec_type {fm['exec_type']}"


@pytest.mark.parametrize("mod_path", _module_files(), ids=lambda p: p.name)
def test_module_hat_resolves_to_known_tier(mod_path):
    if HATS is None:
        pytest.skip("hats.json not loaded")
    fm = _parse_frontmatter(mod_path)
    hat = fm.get("hat")
    if hat is None:
        return  # silent default to no-llm
    all_hats = set()
    for tier_hats in HATS["tiers"].values():
        all_hats.update(tier_hats)
    assert hat in all_hats, f"{mod_path.name}: hat {hat!r} not in hats.json"


@pytest.mark.parametrize("mod_path", _module_files(), ids=lambda p: p.name)
def test_llm_module_contains_ledger_placeholder(mod_path):
    fm = _parse_frontmatter(mod_path)
    node_id = fm.get("node_id", mod_path.stem)
    if node_id in NO_LLM_NODES or fm.get("hat") is None:
        return
    body = mod_path.read_text()
    assert LEDGER_PLACEHOLDER in body, f"{mod_path.name}: missing {LEDGER_PLACEHOLDER}"


@pytest.mark.parametrize("mod_path", _module_files(), ids=lambda p: p.name)
def test_module_does_not_reference_mcp_tools(mod_path):
    body = mod_path.read_text()
    assert "mcp__dify-" not in body, f"{mod_path.name}: references mcp__dify-* tool"


@pytest.mark.parametrize("mod_path", _module_files(), ids=lambda p: p.name)
def test_llm_module_has_annotations_subsection(mod_path):
    """F011 -- LLM-backed modules must guide the LLM to write `## annotations:`
    blocks; no-llm modules are exempt (no LLM to instruct)."""
    fm = _parse_frontmatter(mod_path)
    node_id = fm.get("node_id", mod_path.stem)
    if node_id in NO_LLM_NODES or fm.get("hat") is None:
        return
    body = mod_path.read_text()
    assert "## ANNOTATIONS" in body, (
        f"{mod_path.name}: LLM-backed module missing `## ANNOTATIONS` sub-section"
    )
    # Sanity-check that the literal annotation format example is present.
    assert "[ann-001]" in body or "[ann-NNN]" in body or "annotations:" in body, (
        f"{mod_path.name}: ANNOTATIONS sub-section missing format example"
    )
