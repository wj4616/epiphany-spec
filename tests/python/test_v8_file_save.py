# tests/python/test_v8_file_save.py
import yaml
from pathlib import Path
from scripts.verifications.v8_file_save import run

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "specs"


def _session(tmp_path, *, scale, version, write_progress=None):
    sm = tmp_path / "session.md"
    sm.write_text(yaml.safe_dump({
        "scale": scale,
        "current_version": version,
        "write_progress": write_progress or {},
    }))
    return sm


def test_v8_passes_on_valid_spec(tmp_path):
    spec = tmp_path / "spec-v1.md"
    body = "lorem ipsum\n" * 1500
    spec.write_text(body + "<!-- end:spec-v1 -->\n")
    sm = _session(tmp_path, scale="STANDARD", version=1,
                  write_progress={"spec_v1": list(range(1, 18))})
    r = run(spec, sm)
    assert r["status"] == "pass"


def test_v8_fails_missing_marker(tmp_path):
    # F102 — consume the missing_marker.md fixture rather than synthesizing inline.
    sm = _session(tmp_path, scale="STANDARD", version=1,
                  write_progress={"spec_v1": list(range(1, 18))})
    r = run(FIX / "missing_marker.md", sm)
    assert r["status"] == "fail"
    assert "marker" in r["details"]["reason"]


def test_v8_legitimate_small_spec_warning(tmp_path):
    # F102 — consume the under_min_size.md fixture (well under 12 KB).
    sm = _session(tmp_path, scale="STANDARD", version=1,
                  write_progress={"spec_v1": list(range(1, 18))})
    r = run(FIX / "under_min_size.md", sm)
    assert r["status"] == "pass"
    assert any("V8-SIZE-WARNING" in w for w in r["details"].get("warnings", []))


def test_v8_fails_under_size_when_progress_incomplete(tmp_path):
    spec = tmp_path / "spec-v1.md"
    spec.write_text("# tiny\n<!-- end:spec-v1 -->\n")
    sm = _session(tmp_path, scale="STANDARD", version=1,
                  write_progress={"spec_v1": [1, 2, 3]})  # incomplete
    r = run(spec, sm)
    assert r["status"] == "fail"


def test_v8_size_thresholds_per_mode(tmp_path):
    sizes = {"MINIMAL": 4 * 1024, "STANDARD": 12 * 1024, "DEEP": 24 * 1024}
    for mode, minimum in sizes.items():
        spec = tmp_path / f"spec-{mode}.md"
        body = "x" * (minimum + 100) + "\n<!-- end:spec-v1 -->\n"
        spec.write_text(body)
        sm = _session(tmp_path, scale=mode, version=1,
                      write_progress={"spec_v1": list(range(1, 18))})
        r = run(spec, sm)
        assert r["status"] == "pass", (mode, r)
