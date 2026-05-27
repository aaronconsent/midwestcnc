#!/usr/bin/env python3
"""
Insights engine — quality gate.

Runs every check that must pass before a draft is promoted from
src/content/insights/_drafts/ to src/content/insights/{pillar}/.

Usage:
    python3 scripts/insights_validators.py <draft.md>            # validate one draft
    python3 scripts/insights_validators.py --all                 # validate every draft
    python3 scripts/insights_validators.py --promote <draft.md>  # validate + promote on pass

Exit codes:
    0  — passed (or all passed in --all mode)
    1  — failed at least one gate
    2  — invocation error (bad args, missing file, etc.)

Pure stdlib. No pip install required.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

REPO = Path(__file__).resolve().parent.parent
DRAFTS_DIR = REPO / "src" / "content" / "insights" / "_drafts"
INSIGHTS_DIR = REPO / "src" / "content" / "insights"
PILLAR_DATA = REPO / "src" / "data" / "insights-pillars.json"

# ---------- Editorial / claim-audit ban list (must match docs/claim-audit.md) ----------

BAN_LIST = [
    r"\bphoto[- ]verified\b",
    r"\bfactory[- ]trained\b",
    r"\bfactory[- ]certified\b",
    r"\b24/7\b",
    r"\bISO\s*9001\b",
    r"\bISO\s+certif",
    r"\bflat[- ]rate\b",
    r"\btransparent\s+pricing\b",
    r"\bguaranteed\b",
    r"\bwarrant(y|ies)\b",
    r"\bsame[- ]day\b",
]

HYPE_WORDS = [
    # Used as self-adjectives — these specifically describe US.
    r"\bworld[- ]class\b",
    r"\bbest[- ]in[- ]class\b",
    r"\bindustry[- ]leading\b",
    r"\bpremier\b",
    r"\bcutting[- ]edge\b",
    r"\bunparalleled\b",
    r"\bunmatched\b",
]

# ---------- Quality thresholds ----------

THRESHOLDS = {
    "min_words_cluster": 1200,
    "min_words_pillar": 2500,
    "min_flesch": 60.0,
    "max_cosine_to_existing": 0.30,
    "min_signal_pieces": 3,
    "min_takeaways": 3,
    "max_takeaways": 5,
    "max_exclamations": 0,
    "min_entities_first_300_words": 2,
    "min_specific_claims_first_300": 1,
}

# ---------- Frontmatter parsing ----------

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    """Return (frontmatter_dict, body) — very small YAML subset, just
    `key: "value"` lines. We do not depend on PyYAML."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_text, body = m.group(1), text[m.end():]
    fm: Dict[str, str] = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip().strip('"').strip("'")
        fm[k.strip()] = v
    return fm, body


# ---------- Markdown utilities ----------

def strip_markdown(md: str) -> str:
    """Strip the lightweight markdown bits so word counting is honest."""
    s = md
    s = re.sub(r"```.*?```", " ", s, flags=re.DOTALL)        # fenced code
    s = re.sub(r"`[^`]*`", " ", s)                           # inline code
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", s)              # images
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)           # [text](url) -> text
    s = re.sub(r"^#+\s+", "", s, flags=re.MULTILINE)         # heading markers
    s = re.sub(r"^[-*]\s+", "", s, flags=re.MULTILINE)       # bullets
    s = re.sub(r"<details>|</details>|<summary>|</summary>", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)                           # any other HTML
    s = re.sub(r"[*_~]", "", s)                              # emphasis
    s = re.sub(r"\s+", " ", s).strip()
    return s


def word_count(md: str) -> int:
    return len(strip_markdown(md).split())


def count_sentences(plain: str) -> int:
    parts = re.split(r"[.!?]+(?=\s|$)", plain)
    return max(1, sum(1 for p in parts if p.strip()))


def count_syllables(word: str) -> int:
    """Cheap syllable approximation — good enough for Flesch."""
    w = word.lower()
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return 0
    vowels = "aeiouy"
    syllables, prev_was_vowel = 0, False
    for ch in w:
        is_vowel = ch in vowels
        if is_vowel and not prev_was_vowel:
            syllables += 1
        prev_was_vowel = is_vowel
    if w.endswith("e") and syllables > 1:
        syllables -= 1
    return max(1, syllables)


def flesch_reading_ease(plain: str) -> float:
    """Standard Flesch RE: 206.835 − 1.015 (W/S) − 84.6 (Sy/W)."""
    words = plain.split()
    if not words:
        return 0.0
    n_words = len(words)
    n_sent = count_sentences(plain)
    n_syl = sum(count_syllables(w) for w in words)
    return 206.835 - 1.015 * (n_words / n_sent) - 84.6 * (n_syl / n_words)


# ---------- TF-IDF (stdlib) ----------

TOKEN_RE = re.compile(r"[a-z][a-z0-9]+")

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "of", "in", "on", "for",
    "to", "with", "as", "by", "is", "are", "was", "were", "be", "been",
    "this", "that", "these", "those", "it", "its", "we", "us", "our",
    "you", "your", "they", "them", "their", "he", "she", "his", "her",
    "from", "at", "into", "out", "up", "down", "over", "under", "than",
    "then", "so", "such", "do", "does", "did", "done", "has", "have",
    "had", "can", "could", "should", "would", "will", "may", "might",
    "not", "no", "yes", "also", "very", "more", "less", "most", "least",
    "some", "any", "all", "every", "each", "other", "another", "one",
    "two", "three", "first", "second", "next", "last", "between", "about",
    "what", "when", "where", "why", "how", "which", "who", "whose",
    "i", "me", "my", "mine", "well", "good", "bad", "just", "only",
}


def tokenize(text: str) -> List[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS and len(t) > 2]


def term_freq(tokens: Iterable[str]) -> Dict[str, float]:
    c = Counter(tokens)
    total = sum(c.values()) or 1
    return {t: n / total for t, n in c.items()}


def idf(docs: List[List[str]]) -> Dict[str, float]:
    n = len(docs)
    df: Counter = Counter()
    for doc in docs:
        for t in set(doc):
            df[t] += 1
    return {t: math.log((n + 1) / (df_t + 1)) + 1 for t, df_t in df.items()}


def tfidf(tokens: List[str], idf_table: Dict[str, float]) -> Dict[str, float]:
    tf = term_freq(tokens)
    return {t: f * idf_table.get(t, 0.0) for t, f in tf.items()}


def cosine(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    if not v1 or not v2:
        return 0.0
    dot = sum(v1.get(t, 0.0) * v2.get(t, 0.0) for t in set(v1) | set(v2))
    n1 = math.sqrt(sum(v * v for v in v1.values()))
    n2 = math.sqrt(sum(v * v for v in v2.values()))
    if not n1 or not n2:
        return 0.0
    return dot / (n1 * n2)


# ---------- Gates ----------

def gate_word_count(body: str, target: str) -> Tuple[bool, str]:
    wc = word_count(body)
    floor = THRESHOLDS["min_words_pillar"] if target == "pillar" else THRESHOLDS["min_words_cluster"]
    return (wc >= floor, f"words={wc} (floor={floor}, target={target})")


def gate_flesch(body: str) -> Tuple[bool, str]:
    plain = strip_markdown(body)
    score = flesch_reading_ease(plain)
    floor = THRESHOLDS["min_flesch"]
    return (score >= floor, f"flesch={score:.1f} (floor={floor})")


def gate_ban_list(body: str) -> Tuple[bool, str]:
    plain = strip_markdown(body)
    hits = []
    for pat in BAN_LIST:
        for m in re.finditer(pat, plain, re.IGNORECASE):
            hits.append(f"{pat}: {m.group(0)!r}")
    return (not hits, f"hits={len(hits)}: {hits[:3]}")


def gate_hype(body: str) -> Tuple[bool, str]:
    plain = strip_markdown(body)
    hits = []
    for pat in HYPE_WORDS:
        for m in re.finditer(pat, plain, re.IGNORECASE):
            hits.append(m.group(0))
    return (not hits, f"hype_hits={hits}")


def gate_exclamation(body: str) -> Tuple[bool, str]:
    plain = strip_markdown(body)
    n = plain.count("!")
    return (n <= THRESHOLDS["max_exclamations"], f"exclamations={n}")


def gate_key_takeaways(body: str) -> Tuple[bool, str]:
    m = re.search(r"^##\s*Key Takeaways\s*\n(.+?)(?=^##\s|\Z)", body, re.MULTILINE | re.DOTALL)
    if not m:
        return False, "Key Takeaways section missing"
    bullets = re.findall(r"^[-*]\s+.+$", m.group(1), re.MULTILINE)
    n = len(bullets)
    ok = THRESHOLDS["min_takeaways"] <= n <= THRESHOLDS["max_takeaways"]
    return ok, f"takeaways={n} (need {THRESHOLDS['min_takeaways']}-{THRESHOLDS['max_takeaways']})"


def gate_definitional_h2(body: str) -> Tuple[bool, str]:
    """Each H2 (besides 'Key Takeaways' and 'Sources & references') should
    be followed by a paragraph that opens with a definitional-style sentence
    — heuristic: first sentence under the H2 contains the H2's noun phrase
    or a noun + 'is/are/means/refers to'."""
    h2s = re.findall(r"^##\s+([^\n]+)\n(.*?)(?=^##\s|\Z)", body, re.MULTILINE | re.DOTALL)
    bad = []
    for title, content in h2s:
        if title.strip() in ("Key Takeaways", "Sources & references", "Sources and references"):
            continue
        first_para = content.strip().split("\n\n", 1)[0].strip()
        if not first_para:
            bad.append(title)
            continue
        first_sent = re.split(r"[.!?](?:\s|$)", first_para, 1)[0]
        # Heuristic check: opener should be declarative-definitional. We
        # reject openers that begin with a question or with "Have you" /
        # "Imagine" / "Picture" / "Let's".
        if re.match(r"^(Have you|Imagine|Picture|Let'?s|Ever\s|Do you)\b", first_sent, re.IGNORECASE):
            bad.append(title)
            continue
        if first_sent.strip().endswith("?"):
            bad.append(title)
    return (not bad, f"non_definitional_h2s={bad}")


def gate_internal_links(body: str) -> Tuple[bool, str]:
    """At least 3 in-body internal links. (Plus the CTA at the end, which
    we don't count.)"""
    links = re.findall(r"\[([^\]]+)\]\((/[^)]+)\)", body)
    in_body = [l for l in links if l[1] != "/get-a-quote/" or len([x for x in links if x[1] == l[1]]) > 1]
    n = len(in_body)
    return (n >= 3, f"in_body_links={n}")


def gate_proprietary_signal(fm: Dict[str, str], body: str) -> Tuple[bool, str]:
    """Heuristic: signal pieces from frontmatter must be referenced
    in-body. Frontmatter `signal_signature` is a semicolon-list of short
    phrases the draft step was supposed to embed. We just check the
    article body contains at least N of them (case-insensitive
    substring), where N is THRESHOLDS['min_signal_pieces']."""
    sig_raw = fm.get("signal_signature", "")
    if not sig_raw:
        return False, "frontmatter missing signal_signature"
    pieces = [p.strip() for p in sig_raw.split(";") if p.strip()]
    if not pieces:
        return False, "signal_signature parsed empty"
    plain = strip_markdown(body).lower()
    present = [p for p in pieces if p.lower() in plain]
    n = len(present)
    floor = THRESHOLDS["min_signal_pieces"]
    return (n >= floor, f"signal_pieces_present={n} (floor={floor}); pieces={pieces}; matched={present}")


def gate_first_300_words(body: str) -> Tuple[bool, str]:
    plain = strip_markdown(body)
    head = " ".join(plain.split()[:300])

    # Specific claims: any token that is a number OR a multi-word
    # ProperNoun phrase (heuristic — capital-word followed by capital-word).
    has_number = bool(re.search(r"\b\d", head))
    cap_phrase = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\b", head)
    n_entities = len([c for c in cap_phrase if c not in {"The", "This", "That", "When", "Where", "Why", "How"}])

    ok_claims = has_number  # at least 1 specific number
    ok_entities = n_entities >= THRESHOLDS["min_entities_first_300_words"]
    ok = ok_claims and ok_entities
    return ok, (
        f"first_300_words: has_number={has_number} entities={n_entities} "
        f"(need {THRESHOLDS['min_entities_first_300_words']}+ entities)"
    )


def gate_schema_validity(schema_jsonld: str) -> Tuple[bool, str]:
    if not schema_jsonld:
        return False, "no schema provided"
    try:
        obj = json.loads(schema_jsonld)
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e}"
    # Spot-check required fields
    if isinstance(obj, dict):
        objs = [obj]
    elif isinstance(obj, list):
        objs = obj
    else:
        return False, "schema is not object or list"
    for o in objs:
        if not isinstance(o, dict):
            return False, "schema entry not object"
        t = o.get("@type")
        if not t:
            return False, "schema entry missing @type"
    return True, f"schema_blocks={len(objs)}"


# ---------- Similarity gate (vs all existing content) ----------

def collect_corpus() -> Dict[str, str]:
    """Return {url: content} for every markdown file under src/content/
    EXCEPT _drafts. Used as the comparison corpus for the cosine gate."""
    out: Dict[str, str] = {}
    content_root = REPO / "src" / "content"
    if not content_root.exists():
        return out
    for path in content_root.rglob("*.md"):
        if "_drafts" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        # Use relative path as id
        rel = path.relative_to(content_root)
        out[str(rel)] = text
    return out


def gate_cosine_similarity(body: str) -> Tuple[bool, str]:
    corpus = collect_corpus()
    if len(corpus) < 5:
        # Not enough corpus to measure; pass with a note.
        return True, f"corpus_size={len(corpus)} (skip — too small)"
    docs_tokens = [tokenize(strip_markdown(c)) for c in corpus.values()]
    idf_table = idf(docs_tokens + [tokenize(strip_markdown(body))])
    body_vec = tfidf(tokenize(strip_markdown(body)), idf_table)
    worst: Tuple[float, str] = (0.0, "")
    for path, content in corpus.items():
        v = tfidf(tokenize(strip_markdown(content)), idf_table)
        s = cosine(body_vec, v)
        if s > worst[0]:
            worst = (s, path)
    ok = worst[0] <= THRESHOLDS["max_cosine_to_existing"]
    return ok, f"max_cosine={worst[0]:.3f} vs {worst[1]} (ceiling={THRESHOLDS['max_cosine_to_existing']})"


# ---------- Main run ----------

def run_gates(path: Path) -> Tuple[bool, List[Tuple[str, bool, str]]]:
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    target = "pillar" if fm.get("type") == "pillar" else "cluster"

    results: List[Tuple[str, bool, str]] = []
    for name, fn in [
        ("word_count", lambda: gate_word_count(body, target)),
        ("flesch", lambda: gate_flesch(body)),
        ("ban_list", lambda: gate_ban_list(body)),
        ("hype_words", lambda: gate_hype(body)),
        ("exclamations", lambda: gate_exclamation(body)),
        ("key_takeaways", lambda: gate_key_takeaways(body)),
        ("definitional_h2", lambda: gate_definitional_h2(body)),
        ("internal_links", lambda: gate_internal_links(body)),
        ("proprietary_signal", lambda: gate_proprietary_signal(fm, body)),
        ("first_300_words", lambda: gate_first_300_words(body)),
        ("cosine_similarity", lambda: gate_cosine_similarity(body)),
    ]:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"gate raised: {e}"
        results.append((name, ok, detail))
    all_ok = all(ok for _, ok, _ in results)
    return all_ok, results


def report(path: Path, ok: bool, results: List[Tuple[str, bool, str]]) -> None:
    print(f"\n=== {path.relative_to(REPO)} ===")
    print(f"Result: {'PASS' if ok else 'FAIL'}")
    for name, gate_ok, detail in results:
        mark = "✓" if gate_ok else "✗"
        print(f"  [{mark}] {name:<22} {detail}")


def promote(draft_path: Path, fm: Dict[str, str]) -> Path:
    pillar = fm.get("pillar")
    if not pillar:
        raise SystemExit(f"Cannot promote {draft_path}: frontmatter missing 'pillar'")
    target_dir = INSIGHTS_DIR / pillar
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / draft_path.name
    target.write_text(draft_path.read_text(encoding="utf-8"), encoding="utf-8")
    draft_path.unlink()
    return target


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("draft", nargs="?", help="path to draft markdown file")
    ap.add_argument("--all", action="store_true", help="validate every file under _drafts/")
    ap.add_argument("--promote", action="store_true", help="promote on pass (move to pillar dir)")
    args = ap.parse_args()

    paths: List[Path] = []
    if args.all:
        paths = sorted(DRAFTS_DIR.rglob("*.md"))
    elif args.draft:
        p = Path(args.draft)
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        if not p.exists():
            print(f"file not found: {p}", file=sys.stderr)
            return 2
        paths = [p]
    else:
        ap.print_help()
        return 2

    if not paths:
        print(f"No drafts found under {DRAFTS_DIR}")
        return 0

    any_fail = False
    for path in paths:
        ok, results = run_gates(path)
        report(path, ok, results)
        if not ok:
            any_fail = True
            continue
        if args.promote:
            text = path.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)
            promoted = promote(path, fm)
            print(f"  → promoted to {promoted.relative_to(REPO)}")

    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
