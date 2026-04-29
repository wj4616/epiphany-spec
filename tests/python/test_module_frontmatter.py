from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

import sys
sys.path.insert(0, str(REPO))
from scripts._module_validators import (
    check_annotations_present,
    check_frontmatter_shape,
    check_hat_resolves,
    LEDGER_PLACEHOLDER,
    NO_LLM_NODES,
    parse_frontmatter,
)

MODULES_DIR = REPO / "modules"


def _module_files() -> list[Path]:
    if not MODULES_DIR.exists():
        return []
    return sorted(MODULES_DIR.glob("*.md"))


def test_modules_dir_exists_or_empty():
    if not MODULES_DIR.exists():
        pytest.skip("modules/ does not exist yet (created by Tasks 23-28)")


@pytest.mark.parametrize("mod_path", _module_files(), ids=lambda p: p.name)
def test_module_has_required_frontmatter_fields(mod_path):
    errors = check_frontmatter_shape(mod_path)
    assert not errors, "\n".join(errors)


@pytest.mark.parametrize("mod_path", _module_files(), ids=lambda p: p.name)
def test_module_hat_resolves_to_known_tier(mod_path):
    errors = check_hat_resolves(mod_path)
    assert not errors, "\n".join(errors)


@pytest.mark.parametrize("mod_path", _module_files(), ids=lambda p: p.name)
def test_llm_module_contains_ledger_placeholder(mod_path):
    fm = parse_frontmatter(mod_path)
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
    errors = check_annotations_present(mod_path)
    assert not errors, "\n".join(errors)
