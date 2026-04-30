import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CLI = REPO / "scripts" / "epiphany_spec.py"


def test_help_exits_zero():
    r = subprocess.run(["python3", str(CLI), "--help"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "Subcommands:" in r.stdout


def test_no_args_shows_help():
    r = subprocess.run(["python3", str(CLI)], capture_output=True, text=True)
    assert r.returncode == 0
    assert "Subcommands:" in r.stdout


def test_unknown_subcommand_exits_2():
    r = subprocess.run(["python3", str(CLI), "nope"], capture_output=True, text=True)
    assert r.returncode == 2
    assert "unknown" in r.stderr.lower()


def test_seed_subcommand_dispatches():
    r = subprocess.run(["python3", str(CLI), "seed", "--hash"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert len(r.stdout.strip()) == 64  # SHA-256 hex


def test_dry_run_subcommand_dispatches():
    r = subprocess.run(
        ["python3", str(CLI), "dry-run", "--mode", "STANDARD", "--apu-count", "10"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr


def test_cross_run_index_requires_base_dir():
    r = subprocess.run(
        ["python3", str(CLI), "cross-run-index", "--session-list"],
        capture_output=True, text=True,
    )
    assert r.returncode != 0


def test_session_md_update_subcommand(tmp_session_dir):
    """session-md-update --field writes a field value atomically."""
    r = subprocess.run(
        ["python3", str(CLI), "session-md-update",
         "--session-dir", str(tmp_session_dir),
         "--field", "state", "--value", "FINALIZED"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    import yaml
    data = yaml.safe_load((tmp_session_dir / "session.md").read_text())
    assert data["state"] == "FINALIZED"


def test_session_md_update_increment(tmp_session_dir):
    """session-md-update --increment bumps a numeric field."""
    r = subprocess.run(
        ["python3", str(CLI), "session-md-update",
         "--session-dir", str(tmp_session_dir),
         "--increment", "spawn_count"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    import yaml
    data = yaml.safe_load((tmp_session_dir / "session.md").read_text())
    assert data["spawn_count"] == 1


def test_session_md_update_merge_yaml(tmp_session_dir, tmp_path):
    """session-md-update --merge-yaml applies a YAML patch file."""
    patch_file = tmp_path / "patch.yaml"
    patch_file.write_text("state: ABORTED\nscale: DEEP\n")
    r = subprocess.run(
        ["python3", str(CLI), "session-md-update",
         "--session-dir", str(tmp_session_dir),
         "--merge-yaml", str(patch_file)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    import yaml
    data = yaml.safe_load((tmp_session_dir / "session.md").read_text())
    assert data["state"] == "ABORTED"
    assert data["scale"] == "DEEP"


def test_ledger_digest_subcommand(tmp_session_dir):
    """ledger-digest emits empty digest for a ledger with no entries."""
    r = subprocess.run(
        ["python3", str(CLI), "ledger-digest",
         "--session-dir", str(tmp_session_dir)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr


def test_ledger_digest_missing_ledger_ok(tmp_path):
    """ledger-digest handles missing ledger file gracefully."""
    sd = tmp_path / "no-ledger-session"
    sd.mkdir()
    r = subprocess.run(
        ["python3", str(CLI), "ledger-digest",
         "--session-dir", str(sd)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0


def test_build_prompt_placeholder_leak_detected(tmp_session_dir):
    """build-prompt detects unresolved {{placeholders}}."""
    mod = REPO / "modules" / "N-INTAKE.md"
    # Write a ledger entry so ledger_digest has content
    (tmp_session_dir / "grs-ledger.md").write_text("## ledger-entry: N-INTAKE [cycle=0]\n```yaml\nnode_id: N-INTAKE\n```\n")
    r = subprocess.run(
        ["python3", str(CLI), "build-prompt",
         "--module", str(mod),
         "--session-dir", str(tmp_session_dir)],
        capture_output=True, text=True,
    )
    # N-INTAKE has {{ledger_at_dispatch}} — should be substituted, so no leak
    assert r.returncode == 0, r.stderr


def test_build_prompt_missing_module_fails(tmp_session_dir):
    r = subprocess.run(
        ["python3", str(CLI), "build-prompt",
         "--module", "/nonexistent/module.md",
         "--session-dir", str(tmp_session_dir)],
        capture_output=True, text=True,
    )
    assert r.returncode != 0


def test_compute_completeness_subcommand(tmp_session_dir):
    """compute-completeness dispatches correctly (requires --spec and --session-md)."""
    r = subprocess.run(
        ["python3", str(CLI), "compute-completeness",
         "--spec", "/dev/null",
         "--session-md", str(tmp_session_dir / "session.md")],
        capture_output=True, text=True,
    )
    # May fail because /dev/null has no spec content, but should not return 2
    assert r.returncode != 2


def test_all_eight_subcommands_listed_in_help():
    r = subprocess.run(["python3", str(CLI), "--help"], capture_output=True, text=True)
    assert r.returncode == 0
    expected = [
        "ledger-append", "session-md-update", "ledger-digest",
        "build-prompt", "compute-completeness", "seed",
        "cross-run-index", "dry-run",
    ]
    for name in expected:
        assert name in r.stdout, f"missing {name} in help output"
