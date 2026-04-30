import json
from pathlib import Path

import pytest
import yaml

from scripts._yaml_io import atomic_write_text, atomic_write_json, atomic_write_yaml


def test_atomic_write_text_writes_content(tmp_path):
    target = tmp_path / "test.txt"
    atomic_write_text(target, "hello world")
    assert target.read_text() == "hello world"
    # tmp file must be cleaned up
    assert not target.with_suffix(".txt.tmp").exists()


def test_atomic_write_text_with_bak(tmp_path):
    target = tmp_path / "data.txt"
    bak_dir = tmp_path / "backups"
    atomic_write_text(target, "v1", bak=True, bak_dir=bak_dir)
    assert target.read_text() == "v1"
    bak = bak_dir / "data.txt.bak"
    assert bak.exists()
    assert bak.read_text() == "v1"

    # write again — bak should update
    atomic_write_text(target, "v2", bak=True, bak_dir=bak_dir)
    assert target.read_text() == "v2"
    assert bak.read_text() == "v2"


def test_atomic_write_text_bak_defaults_to_same_dir(tmp_path):
    target = tmp_path / "notes.md"
    atomic_write_text(target, "content", bak=True)
    bak = tmp_path / "notes.md.bak"
    assert bak.exists()
    assert bak.read_text() == "content"


def test_atomic_write_text_overwrites_existing(tmp_path):
    target = tmp_path / "counter.txt"
    target.write_text("old")
    atomic_write_text(target, "new")
    assert target.read_text() == "new"


def test_atomic_write_json_writes_valid_json(tmp_path):
    target = tmp_path / "out.json"
    data = {"a": 1, "b": [2, 3]}
    atomic_write_json(target, data)
    parsed = json.loads(target.read_text())
    assert parsed == {"a": 1, "b": [2, 3]}
    assert not target.with_suffix(".json.tmp").exists()


def test_atomic_write_json_with_bak(tmp_path):
    target = tmp_path / "cfg.json"
    atomic_write_json(target, {"x": 1}, bak=True)
    bak = tmp_path / "cfg.json.bak"
    assert bak.exists()
    assert json.loads(bak.read_text()) == {"x": 1}


def test_atomic_write_yaml_writes_valid_yaml(tmp_path):
    target = tmp_path / "out.yaml"
    data = {"name": "test", "items": [1, 2]}
    atomic_write_yaml(target, data)
    parsed = yaml.safe_load(target.read_text())
    assert parsed == data
    assert not target.with_suffix(".yaml.tmp").exists()


def test_atomic_write_yaml_with_bak(tmp_path):
    target = tmp_path / "state.yaml"
    atomic_write_yaml(target, {"k": "v"}, bak=True)
    bak = tmp_path / "state.yaml.bak"
    assert bak.exists()
    assert yaml.safe_load(bak.read_text()) == {"k": "v"}


def test_atomic_write_creates_parent_dirs(tmp_path):
    target = tmp_path / "deep" / "nested" / "file.txt"
    atomic_write_text(target, "deep content")
    assert target.read_text() == "deep content"


def test_tmp_file_absent_on_success(tmp_path):
    """Tmp file must be os.replace()'d to target, leaving no .tmp residue."""
    for i in range(5):
        target = tmp_path / f"file_{i}.txt"
        atomic_write_text(target, f"body_{i}")
        tmps = list(tmp_path.glob("*.tmp"))
        assert not tmps, f"leftover tmp: {tmps}"
