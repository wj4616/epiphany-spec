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
