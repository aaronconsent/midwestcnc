#!/usr/bin/env python3
"""
Insights engine — internal-link suggester.

Builds a TF-IDF index over every existing brand-hub + spoke page,
service-area page, and insights article, then for a given draft (or
topic query) returns the top-K most semantically related URLs with
suggested anchor text.

Output is consumed by the outline + draft prompts so internal links
land in-context (not as a Related Posts footer).

Usage:
    # From a draft markdown file:
    python3 scripts/insights_link_suggester.py --draft <file.md>

    # From a free-text topic / outline:
    python3 scripts/insights_link_suggester.py --query "spindle vibration diagnosis"

    # JSON output (for piping into the prompt builder):
    python3 scripts/insights_link_suggester.py --draft <file.md> --json

Pure stdlib. v2 will swap TF-IDF for dense embeddings; same interface.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

REPO = Path(__file__).resolve().parent.parent
PUBLIC = REPO / "public"

# Reuse validator stopwords + tokenizer (avoid duplicating the lexicon).
sys.path.insert(0, str(REPO / "scripts"))
from insights_validators import tokenize, idf as _idf, tfidf as _tfidf, cosine as _cosine, strip_markdown

DEFAULT_K = 8

# ---------- HTML → text extraction ----------

class _BodyTextExtractor(HTMLParser):
    """Pull visible text + <title> + <meta description> out of a page."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: List[str] = []
        self.title: str = ""
        self.meta_desc: str = ""
        self._in_title = False
        self._in_skip = 0  # nesting count for skipped tags

    SKIP_TAGS = {"script", "style", "noscript", "svg"}

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        elif tag in self.SKIP_TAGS:
            self._in_skip += 1
        elif tag == "meta":
            d = dict(attrs)
            if d.get("name") == "description" and d.get("content"):
                self.meta_desc = d["content"]

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in self.SKIP_TAGS and self._in_skip > 0:
            self._in_skip -= 1

    def handle_data(self, data):
        if self._in_skip:
            return
        if self._in_title:
            self.title += data
            return
        if data.strip():
            self.parts.append(data)


def extract_page(path: Path) -> Tuple[str, str, str]:
    """Return (title, description, body_text)."""
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return "", "", ""
    p = _BodyTextExtractor()
    p.feed(html)
    body = " ".join(p.parts)
    return p.title.strip(), p.meta_desc.strip(), body


def url_for(html_path: Path) -> str:
    """Map public/foo/bar/index.html → /foo/bar/."""
    rel = html_path.relative_to(PUBLIC)
    if rel.name == "index.html":
        parent = rel.parent
        return "/" if str(parent) == "." else "/" + str(parent) + "/"
    return "/" + str(rel) + "/"


# ---------- Corpus discovery ----------

def discover_corpus() -> List[Tuple[str, str, str]]:
    """Walk public/ and return (url, title, text) for every page worth linking
    to. Exclude 404, get-a-quote (we link there manually as CTA), and the
    homepage (rarely the best in-body target)."""
    out: List[Tuple[str, str, str]] = []
    skip_urls = {"/", "/404.html", "/404/", "/get-a-quote/"}
    if not PUBLIC.exists():
        return out
    for path in PUBLIC.rglob("index.html"):
        url = url_for(path)
        if url in skip_urls:
            continue
        title, desc, body = extract_page(path)
        if not body:
            continue
        # Concatenate title + desc + body so headings + meta carry signal.
        text = f"{title}\n{desc}\n{body}"
        out.append((url, title or url, text))
    return out


# ---------- Suggester ----------

def suggest(query_text: str, top_k: int = DEFAULT_K, exclude_url: str | None = None) -> List[Dict]:
    corpus = discover_corpus()
    if not corpus:
        return []

    docs_tokens = [tokenize(t) for _, _, t in corpus]
    query_tokens = tokenize(query_text)
    idf_table = _idf(docs_tokens + [query_tokens])
    q_vec = _tfidf(query_tokens, idf_table)

    scored: List[Tuple[float, str, str]] = []
    for (url, title, text), toks in zip(corpus, docs_tokens):
        if url == exclude_url:
            continue
        d_vec = _tfidf(toks, idf_table)
        s = _cosine(q_vec, d_vec)
        if s > 0.05:
            scored.append((s, url, title))
    scored.sort(reverse=True)
    top = scored[:top_k]

    suggestions = []
    for rank, (score, url, title) in enumerate(top, 1):
        suggestions.append({
            "rank": rank,
            "score": round(score, 4),
            "url": url,
            "title": title,
            "suggested_anchor": _suggest_anchor(title, url),
        })
    return suggestions


def _suggest_anchor(title: str, url: str) -> str:
    """Pick a noun-phrase anchor from the title.

    Heuristics:
    - Strip site-name suffix " | Midwest CNC Services" if present.
    - Drop trailing " - 319-610-4341" tail if present.
    - Cap to 8 words.
    """
    t = title
    for tail in (" | Midwest CNC Services", " - 319-610-4341"):
        if t.endswith(tail):
            t = t[: -len(tail)]
    t = t.strip(" -—|")
    words = t.split()
    if len(words) > 8:
        t = " ".join(words[:8])
    # Lowercase 'and', 'or', 'in', 'of' in the middle (title-case cleanup).
    return t


# ---------- CLI ----------

def query_text_from_draft(path: Path) -> str:
    """Extract the substantive body of a draft markdown file for use as
    the similarity query."""
    text = path.read_text(encoding="utf-8")
    # Strip frontmatter
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    return strip_markdown(text)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--draft", help="path to draft markdown")
    ap.add_argument("--query", help="free-text topic / outline string")
    ap.add_argument("--top-k", type=int, default=DEFAULT_K)
    ap.add_argument("--exclude-url", help="exclude this URL from suggestions (e.g. the draft's own canonical)")
    ap.add_argument("--json", action="store_true", help="emit JSON for piping")
    args = ap.parse_args()

    if not args.draft and not args.query:
        ap.print_help()
        return 2

    if args.draft:
        p = Path(args.draft)
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        if not p.exists():
            print(f"file not found: {p}", file=sys.stderr)
            return 2
        q = query_text_from_draft(p)
    else:
        q = args.query

    suggestions = suggest(q, top_k=args.top_k, exclude_url=args.exclude_url)

    if args.json:
        json.dump(suggestions, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if not suggestions:
        print("No suggestions found. Has the site been generated?")
        return 1

    print(f"\nTop {len(suggestions)} internal-link targets:")
    for s in suggestions:
        print(f"  [{s['rank']}] {s['score']:.3f}  {s['url']}")
        print(f"        anchor: \"{s['suggested_anchor']}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
