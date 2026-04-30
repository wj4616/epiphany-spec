import re
import textwrap
from pathlib import Path

import pytest
import yaml

from scripts.verifications._common import (
    CITATION_STRICT,
    CITATION_BROAD,
    HEADER,
    NEXT_SEC,
    SEC_10,
    R_HEADER,
    CONSTRAINT_HEADER,
    SEC_7_RE,
    load_apus,
    split_sections,
    parse_constraints,
    word_count,
)


# --- Regex pattern tests ---

def test_citation_strict_matches_bracket_form():
    assert CITATION_STRICT.search("see [APU-001] for details")
    assert CITATION_STRICT.search("[APU-999]")
    assert not CITATION_STRICT.search("APU-001")  # no brackets
    assert not CITATION_STRICT.search("[APU-01]")  # < 3 digits


def test_citation_broad_matches_plain_form():
    assert CITATION_BROAD.search("APU-001 is referenced")
    assert CITATION_BROAD.search("see APU-042 above")
    assert not CITATION_BROAD.search("APU-12")  # < 3 digits


def test_header_matches_section_headers():
    m = HEADER.search("## 7. Constraints\nsome text")
    assert m is not None
    assert m.group(1) == "7"

    assert HEADER.search("## 14. Decision Log") is not None
    assert HEADER.search("## 1. Title") is not None
    assert HEADER.search("### 5. not a section") is None  # H3, not H2


def test_next_sec_finds_boundary():
    text = "## 7. Constraints\nbody\n## 8. Next\nmore"
    m = NEXT_SEC.search(text)
    assert m is not None


def test_sec_10_finds_falsifiability_section():
    assert SEC_10.search("## 10. Falsifiability\ncontent") is not None
    assert SEC_10.search("## 10. Falsifibility\ncontent") is None  # typo


def test_r_header_matches_requirement_ids():
    m = R_HEADER.search("### R-001\nSome requirement")
    assert m is not None
    assert m.group(1) == "R-001"


def test_constraint_header_parses_tags():
    text = "### C-005 [source: user, severity: high]\nbody"
    m = CONSTRAINT_HEADER.search(text)
    assert m is not None
    assert m.group(1) == "C-005"
    assert "severity: high" in m.group(2)


def test_sec_7_re_matches_constraints_section():
    assert SEC_7_RE.search("## 7. Constraints\ncontent") is not None
    assert SEC_7_RE.search("## 17. Constraints\ncontent") is None


# --- load_apus ---

def test_load_apus_dict_format(tmp_path):
    sm = tmp_path / "session.md"
    sm.write_text(yaml.safe_dump({
        "apus": [
            {"id": "APU-001", "text": "first"},
            {"id": "APU-002", "text": "second"},
        ]
    }))
    assert load_apus(sm) == ["APU-001", "APU-002"]


def test_load_apus_string_format(tmp_path):
    sm = tmp_path / "session.md"
    sm.write_text(yaml.safe_dump({"apus": ["APU-003", "APU-004"]}))
    assert load_apus(sm) == ["APU-003", "APU-004"]


def test_load_apus_empty(tmp_path):
    sm = tmp_path / "session.md"
    sm.write_text(yaml.safe_dump({"apus": []}))
    assert load_apus(sm) == []


def test_load_apus_missing_key(tmp_path):
    sm = tmp_path / "session.md"
    sm.write_text(yaml.safe_dump({"state": "RUNNING"}))
    assert load_apus(sm) == []


# --- split_sections ---

SPEC_BODY = textwrap.dedent("""\
    ## 1. Title
    Section one body.
    ## 2. Locked Vocabulary
    term1, term2
    ## 3. Invariants
    invariant content
    ## 4. Interfaces
    interface content
""")

def test_split_sections_extracts_correct_sections():
    sections = split_sections(SPEC_BODY)
    assert 1 in sections
    assert 2 in sections
    assert 3 in sections
    assert 4 in sections
    assert "Section one body." in sections[1]
    assert "term1, term2" in sections[2]


def test_split_sections_excludes_oob():
    """Sections outside 1..16 must be excluded."""
    sections = split_sections(SPEC_BODY)
    assert 0 not in sections
    assert 17 not in sections


def test_split_sections_handles_empty():
    assert split_sections("") == {}


# --- parse_constraints ---

CONSTRAINT_SPEC = textwrap.dedent("""\
    ## 7. Constraints
    ### C-001 [source: user, severity: high, type: functional]
    Must respond within 100ms.
    ### C-002 [source: derived, severity: medium]
    Must not allocate on audio thread.
    ## 8. APUs
    next section content
""")


def test_parse_constraints_extracts_entries():
    result = parse_constraints(CONSTRAINT_SPEC)
    assert len(result) == 2
    assert result[0]["id"] == "C-001"
    assert result[0]["tags"] == {
        "source": "user", "severity": "high", "type": "functional"
    }
    assert result[1]["id"] == "C-002"
    assert result[1]["tags"] == {"source": "derived", "severity": "medium"}


def test_parse_constraints_no_section_7():
    assert parse_constraints("## 1. Intro\nno constraints here") == []


def test_parse_constraints_empty_spec():
    assert parse_constraints("") == []


# --- word_count ---

def test_word_count_counts_correctly(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("hello world from pytest\n")
    assert word_count(f) == 4


def test_word_count_missing_file():
    assert word_count(Path("/nonexistent/foo.txt")) == 0


def test_word_count_empty_file(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("")
    assert word_count(f) == 0
