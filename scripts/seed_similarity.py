#!/usr/bin/env python3
"""seed_similarity.py — slug + Jaccard for epiphany-spec cross-run seed (§3 step 5, §8).

The 179-word NLTK 3.8 English stop-word list is FROZEN as a constant. We do not
import nltk at runtime to avoid dependency drift. SHA-256 of the sorted list
is logged in session.md.cross_run_seed.stopwords_hash for cross-session audit.
"""
from __future__ import annotations

import hashlib
import re
import sys
import unicodedata

# NLTK 3.8 English stop-words, alphabetically sorted (179 words).
FROZEN_STOPWORDS: frozenset[str] = frozenset({
    "a","about","above","after","again","against","ain","all","am","an","and","any",
    "are","aren","aren't","as","at","be","because","been","before","being","below",
    "between","both","but","by","can","couldn","couldn't","d","did","didn","didn't",
    "do","does","doesn","doesn't","doing","don","don't","down","during","each","few",
    "for","from","further","had","hadn","hadn't","has","hasn","hasn't","have","haven",
    "haven't","having","he","her","here","hers","herself","him","himself","his","how",
    "i","if","in","into","is","isn","isn't","it","it's","its","itself","just","ll","m",
    "ma","me","mightn","mightn't","more","most","mustn","mustn't","my","myself","needn",
    "needn't","no","nor","not","now","o","of","off","on","once","only","or","other",
    "our","ours","ourselves","out","over","own","re","s","same","shan","shan't","she",
    "she's","should","should've","shouldn","shouldn't","so","some","such","t","than",
    "that","that'll","the","their","theirs","them","themselves","then","there","these",
    "they","this","those","through","to","too","under","until","up","ve","very","was",
    "wasn","wasn't","we","were","weren","weren't","what","when","where","which","while",
    "who","whom","why","will","with","won","won't","wouldn","wouldn't","y","you","you'd",
    "you'll","you're","you've","your","yours","yourself","yourselves",
})

assert len(FROZEN_STOPWORDS) == 179, f"stop-word list count drift: {len(FROZEN_STOPWORDS)}"

_XML_TAG = re.compile(r"<[^>]+>")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def stopwords_sha256() -> str:
    payload = "\n".join(sorted(FROZEN_STOPWORDS)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _strip_xml(s: str) -> str:
    return _XML_TAG.sub(" ", s)


def _normalize(s: str) -> str:
    nfc = unicodedata.normalize("NFC", s).lower()
    nfkd = unicodedata.normalize("NFKD", nfc)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _hyphenate(tokens: list[str]) -> str:
    return "-".join(t for t in tokens if t)


def _tokenize(s: str) -> list[str]:
    cleaned = _NON_ALNUM.sub(" ", s)
    return [t for t in cleaned.split() if t]


def slugify(input_str: str, max_chars: int = 200) -> str:
    """§3 step 5 canonical slugification.

    Steps:
      1. Truncate to max_chars=200.
      2. Strip XML tags.
      3. NFC-normalize, lowercase.
      4. Tokenize on non-alphanumeric.
      5. Remove stop-words.
      6. Hyphenate.
    Empty fallback: re-slugify first 40 chars of input[:200] WITHOUT stop-word removal.
    Still-empty fallback: return "unnamed".
    """
    head = input_str[:max_chars] if input_str else ""
    stripped = _strip_xml(head)
    norm = _normalize(stripped)
    toks = _tokenize(norm)
    pruned = [t for t in toks if t not in FROZEN_STOPWORDS]
    slug = _hyphenate(pruned)
    if len(slug) >= 2:
        return slug

    # Fallback 1: first 40 chars without stop-word removal
    fallback_head = (input_str or "")[:40]
    fb_norm = _normalize(_strip_xml(fallback_head))
    fb_toks = _tokenize(fb_norm)
    slug2 = _hyphenate(fb_toks)
    if len(slug2) >= 1:
        return slug2

    return "unnamed"


def truncate_at_word_boundary(slug: str, max_len: int = 40) -> str:
    """Trim slug at the last hyphen at or before character `max_len`.

    Keeps the content from the second-to-last hyphen boundary to max_len,
    producing a trimmed suffix that ends on the last complete word within max_len.
    """
    if len(slug) <= max_len:
        return slug
    head = slug[:max_len]
    last_hyphen = head.rfind("-")
    if last_hyphen <= 0:
        return head  # no boundary — hard cut
    prev_hyphen = head.rfind("-", 0, last_hyphen)
    if prev_hyphen < 0:
        return head  # only one hyphen — keep as-is
    return head[prev_hyphen + 1 : max_len]


def jaccard(a: set[str], b: set[str]) -> float:
    """Token Jaccard similarity. 0.0 when both sets empty (degenerate case)."""
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def slug_tokens(slug: str) -> set[str]:
    return set(slug.split("-")) - {""}


def main() -> int:
    """CLI: print stopword hash and an example slug for a given input."""
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--input", help="Text to slugify")
    p.add_argument("--hash", action="store_true", help="Print stopword SHA-256 only")
    args = p.parse_args()
    if args.hash:
        print(stopwords_sha256())
        return 0
    if args.input is None:
        print("Provide --input or --hash", file=sys.stderr)
        return 2
    print(slugify(args.input))
    return 0


if __name__ == "__main__":
    sys.exit(main())
