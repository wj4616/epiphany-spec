import hashlib
from scripts.seed_similarity import (
    slugify, jaccard, stopwords_sha256, FROZEN_STOPWORDS,
    truncate_at_word_boundary,
)


def test_frozen_stopwords_count_and_hash():
    assert len(FROZEN_STOPWORDS) == 179
    h = stopwords_sha256()
    assert isinstance(h, str)
    assert len(h) == 64
    expected = hashlib.sha256(
        "\n".join(sorted(FROZEN_STOPWORDS)).encode("utf-8")
    ).hexdigest()
    assert h == expected


def test_slugify_strips_xml():
    # XML-strip removes TAGS only, not tag content (per §3 step 5).
    # `<role>foo</role>` becomes ` foo `; `foo` survives, `a` is a stop-word
    # and is filtered out → "foo-design-thing".
    assert slugify("<role>foo</role> design a thing") == "foo-design-thing"


def test_slugify_lowercases_and_hyphenates():
    assert slugify("Design a New Thing!") == "design-new-thing"


def test_slugify_removes_stopwords():
    out = slugify("the quick brown fox over a lazy dog")
    assert "the" not in out.split("-")
    assert "quick" in out


def test_slugify_empty_after_stopwords_falls_back():
    out = slugify("the a an of for in to")
    assert out and out != "unnamed"
    # First 40 chars of original (post-XML-strip), slugified — should contain something.
    assert "-" in out or len(out) >= 1


def test_slugify_truly_empty_uses_unnamed():
    assert slugify("") == "unnamed"
    assert slugify("<role></role>") == "unnamed"


def test_truncate_at_word_boundary_under_40():
    assert truncate_at_word_boundary("foo-bar", 40) == "foo-bar"


def test_truncate_at_word_boundary_at_hyphen():
    s = "abcdefghij-klmnopqrst-uvwxyz1234-extra-tail"  # 43 chars; 31st char is '-'
    out = truncate_at_word_boundary(s, 32)
    assert out.endswith("uvwxyz1234")
    assert len(out) <= 32


def test_jaccard_self_is_one():
    a = {"foo", "bar"}
    assert jaccard(a, a) == 1.0


def test_jaccard_disjoint_is_zero():
    assert jaccard({"a"}, {"b"}) == 0.0


def test_jaccard_partial_overlap():
    assert jaccard({"a", "b"}, {"b", "c"}) == 1 / 3


def test_jaccard_empty_inputs_zero():
    assert jaccard(set(), set()) == 0.0
