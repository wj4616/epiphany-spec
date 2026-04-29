import sys
from pathlib import Path

# Make scripts/ importable as a package
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

import pytest
import shutil
import tempfile


@pytest.fixture
def tmp_session_dir(tmp_path):
    """Create a minimal session directory mirroring §3 layout."""
    session_dir = tmp_path / "session-uuid-fixture"
    (session_dir / "stages").mkdir(parents=True)
    (session_dir / "input.md").write_text("test input\n")
    (session_dir / "session.md").write_text("session_id: session-uuid-fixture\nstate: RUNNING\n")
    (session_dir / "grs-ledger.md").touch()
    (session_dir / "topology-trace.md").touch()
    return session_dir


@pytest.fixture
def fixtures_dir():
    return Path(__file__).resolve().parents[1] / "fixtures"
