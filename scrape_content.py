#!/usr/bin/env python3
"""
Midwest CNC Services — Content Migration Tool
==============================================

Walks every page listed in src/data/crawl-report.json and extracts
structured content into src/data/pages.json. For each URL we capture:

  - url, path, HTTP status
  - <title>, meta description, canonical
  - og:title, og:description, og:image (image rewritten to local path)
  - h1, all h2s, all h3s
  - sections — body content split on h1/h2 boundaries (h3s ride along
    inside their parent section's html/text)
  - internal_links — every link inside the page's main content that
    points back into midwestcncservices.com, so the rebuild can preserve
    the editorial link graph (global nav links are layout, not content,
    and live in templates)
  - json_ld — every <script type="application/ld+json"> block parsed
  - images — every <img> on the page, rewritten to /assets/images/...
    using the mapping in src/data/image-map.json

The crawler is polite (0.4s delay) and reuses the URL list already
captured in crawl-report.json rather than re-running BFS discovery — that
way pages.json and image-map.json stay in lockstep.

Durable.co platform pages (sign-up, pricing, ai-*, durable-vs-* blog
posts, etc.) that the original crawler picked up are excluded by default
via EXCLUDE_PATHS; edit that constant if any should be kept.

Outputs (overwritten on each run):
  src/data/pages.json              — one entry per URL
  src/data/extraction-report.json  — counts and parsing issues

Usage:
  python3 scrape_content.py

Dependencies:
  pip3 install requests beautifulsoup4
"""

import html as html_lib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


# ---------- Config ----------
BASE_URL = "https://midwestcncservices.com"
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "src" / "data"
CRAWL_REPORT = DATA_DIR / "crawl-report.json"
IMAGE_MAP = DATA_DIR / "image-map.json"
PAGES_OUT = DATA_DIR / "pages.json"
REPORT_OUT = DATA_DIR / "extraction-report.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}
REQUEST_DELAY = 0.4
TIMEOUT = 25

# Durable.co platform pages the original crawler picked up that aren't
# part of the client site. Edit if any of these should be migrated.
EXCLUDE_PATHS = {
    "/sign-up", "/pricing", "/ai-website-builder", "/website-templates",
    "/ai-brand-builder", "/ai-blog-generator", "/business-name-generator",
    "/ai-logo-generator", "/invoice-builder", "/discoverability",
    "/ai-tools", "/affiliate",
    "/blog/durable-vs-squarespace", "/blog/wix-vs-durable",
    "/blog/wordpress-vs-durable", "/blog/10web-vs-durable",
}


# ---------- Helpers ----------
def load_inputs():
    """Load the URL list and image map prepared by the earlier scrape."""
    crawl = json.loads(CRAWL_REPORT.read_text())
    image_map = json.loads(IMAGE_MAP.read_text())
    return crawl, image_map


def normalize_ws(text):
    # Decode HTML entities as a final pass — Durable serves double-encoded
    # `&amp;amp;` in some <title> tags, which BS4 only decodes once.
    return re.sub(r"\s+", " ", html_lib.unescape(text or "")).strip()


def extract_cdn_url(src):
    """
    Pull the underlying cdn.durable.co URL from an <img src>.
    Handles direct CDN URLs and Next.js optimizer wrappers
    (/_next/image?url=<encoded>&w=...&q=...).
    """
    if not src or src.startswith("data:"):
        return None
    if "_next/image" in src:
        params = parse_qs(urlparse(src).query)
        wrapped = params.get("url", [None])[0]
        if wrapped:
            decoded = unquote(wrapped)
            if "cdn.durable.co" in decoded:
                return decoded
        return None
    if "cdn.durable.co" in src:
        return src
    return None


def resolve_image(src, image_map):
    """Map a raw <img src> to its local path via image_map.
    Returns (local_path or None, original_cdn_url or None)."""
    cdn = extract_cdn_url(src)
    if not cdn:
        return None, None
    entry = image_map.get(cdn)
    if entry:
        return entry.get("local_path"), cdn
    return None, cdn


def meta_content(soup, **attrs):
    """Return the content attribute of a <meta> matching attrs, or None."""
    el = soup.find("meta", attrs=attrs)
    if el and el.has_attr("content"):
        return normalize_ws(el["content"])
    return None


# ---------- Extraction ----------
def collect_jsonld(soup, path, issues):
    """Parse every JSON-LD block on the page."""
    blocks = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = tag.string or tag.get_text() or ""
        if not raw.strip():
            continue
        try:
            blocks.append(json.loads(raw))
        except json.JSONDecodeError as e:
            issues["jsonld_parse_errors"].append({"path": path, "error": str(e)})
    return blocks


def find_content_root(soup):
    """
    Pick the best 'main content' container, then strip scripts/styles
    inside it so they don't bleed into section HTML. Mutates the soup;
    callers should collect metadata (title, meta, OG, JSON-LD, etc.)
    before this is invoked.
    """
    root = soup.find("main") or soup.find("article")
    if not root:
        body = soup.body or soup
        for sel in ("header", "nav", "footer"):
            for el in body.find_all(sel):
                el.decompose()
        root = body
    for tag in root.find_all(["script", "style"]):
        tag.decompose()
    # Unwrap (not decompose) <noscript>: on Next.js sites the real <img>
    # with cdn.durable.co srcs lives inside <noscript> — the visible <img>
    # is a data: placeholder for JS-driven lazy loading.
    for ns in root.find_all("noscript"):
        ns.unwrap()
    return root


def collect_internal_links(content_root, page_url, base_netloc):
    """Every link in the content area that points back into the site."""
    links = []
    for a in content_root.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("tel:", "mailto:", "javascript:", "#")):
            continue
        full = urljoin(page_url, href)
        parsed = urlparse(full)
        if parsed.netloc != base_netloc:
            continue
        path = parsed.path or "/"
        text = normalize_ws(a.get_text(" ", strip=True))
        links.append({"text": text, "path": path})
    return links


def collect_images(scope, image_map, page_path, issues):
    """Every <img> in `scope`, rewritten to local paths via image_map."""
    out = []
    seen = set()
    for img in scope.find_all("img"):
        src = img.get("src", "")
        local, cdn = resolve_image(src, image_map)
        alt = normalize_ws(img.get("alt") or "")
        if local:
            if local in seen:
                continue
            seen.add(local)
            out.append({"local_path": local, "alt": alt, "original_src": cdn})
        elif cdn:
            issues["images_not_in_map"].append({"path": page_path, "src": cdn})
        # Non-CDN images (data URIs, off-site) are silently ignored.
    return out


def split_sections(content_root, image_map, page_path, issues):
    """
    Walk the content root and split into sections at h1/h2 boundaries.
    Each section captures its heading, inner HTML, plain text, and the
    local paths of images that live inside it. h3s ride along inside
    their parent section.
    """
    sections = []
    state = {
        "level": 0,
        "heading": None,
        "html_parts": [],
        "text_parts": [],
        "images": [],
    }

    def flush():
        html = "".join(state["html_parts"]).strip()
        text = normalize_ws(" ".join(state["text_parts"]))
        if html or text or state["heading"]:
            sections.append({
                "level": state["level"],
                "heading": state["heading"],
                "html": html,
                "text": text,
                "images": list(state["images"]),
            })
        state["html_parts"] = []
        state["text_parts"] = []
        state["images"] = []

    def add_image(img_tag):
        src = img_tag.get("src", "")
        local, cdn = resolve_image(src, image_map)
        if local:
            if local not in state["images"]:
                state["images"].append(local)
        elif cdn:
            issues["images_not_in_map"].append({"path": page_path, "src": cdn})

    def walk(node):
        for child in node.children:
            if isinstance(child, NavigableString):
                text = str(child)
                state["html_parts"].append(text)
                if text.strip():
                    state["text_parts"].append(text.strip())
                continue
            if not isinstance(child, Tag):
                continue
            name = (child.name or "").lower()
            if name in ("h1", "h2"):
                flush()
                state["level"] = int(name[1])
                state["heading"] = normalize_ws(child.get_text(" ", strip=True))
                continue
            if name == "img":
                add_image(child)
                state["html_parts"].append(str(child))
                continue
            # Recurse only if a heading lives deeper in this subtree —
            # otherwise capture the whole subtree as-is so we keep its HTML.
            if child.find(["h1", "h2"]):
                walk(child)
            else:
                state["html_parts"].append(str(child))
                state["text_parts"].append(child.get_text(" ", strip=True))
                for img in child.find_all("img"):
                    add_image(img)

    walk(content_root)
    flush()
    return sections


# ---------- Page processing ----------
def process_page(path, image_map, issues):
    """Fetch and extract one page. Returns a dict for pages.json."""
    url = urljoin(BASE_URL, path)
    base_netloc = urlparse(BASE_URL).netloc

    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    except Exception as e:
        issues["http_errors"].append({"path": path, "error": str(e)})
        return {"url": url, "path": path, "status": None, "error": str(e)}

    if r.status_code != 200:
        issues["http_errors"].append(
            {"path": path, "error": f"HTTP {r.status_code}"}
        )
        return {
            "url": url, "path": path, "status": r.status_code,
            "error": f"HTTP {r.status_code}",
        }

    soup = BeautifulSoup(r.text, "html.parser")

    # Metadata that needs the untouched soup
    title_tag = soup.find("title")
    title = normalize_ws(title_tag.get_text(" ", strip=True)) if title_tag else None
    if not title:
        issues["missing_title"].append(path)

    description = meta_content(soup, name="description")
    if not description:
        issues["missing_meta_description"].append(path)

    canonical_el = soup.find("link", attrs={"rel": "canonical"})
    canonical = canonical_el["href"] if canonical_el and canonical_el.has_attr("href") else None
    if not canonical:
        issues["missing_canonical"].append(path)

    og_image_raw = meta_content(soup, **{"property": "og:image"})
    og_image_local, _ = resolve_image(og_image_raw or "", image_map)
    og = {
        "title": meta_content(soup, **{"property": "og:title"}),
        "description": meta_content(soup, **{"property": "og:description"}),
        "image": og_image_local or og_image_raw,
    }

    h1_tags = soup.find_all("h1")
    h1 = normalize_ws(h1_tags[0].get_text(" ", strip=True)) if h1_tags else None
    if not h1:
        issues["missing_h1"].append(path)
    elif len(h1_tags) > 1:
        issues["multiple_h1"].append({"path": path, "count": len(h1_tags)})

    json_ld = collect_jsonld(soup, path, issues)

    # Content extraction — find_content_root mutates the soup, so anything
    # that needs the original head/scripts must already have been read above.
    content_root = find_content_root(soup)

    h2s = [normalize_ws(h.get_text(" ", strip=True))
           for h in content_root.find_all("h2")]
    h3s = [normalize_ws(h.get_text(" ", strip=True))
           for h in content_root.find_all("h3")]

    sections = split_sections(content_root, image_map, path, issues)
    internal_links = collect_internal_links(content_root, url, base_netloc)
    images = collect_images(content_root, image_map, path, issues)

    return {
        "url": url,
        "path": path,
        "status": r.status_code,
        "title": title,
        "meta_description": description,
        "canonical": canonical,
        "og": og,
        "h1": h1,
        "h2s": h2s,
        "h3s": h3s,
        "sections": sections,
        "internal_links": internal_links,
        "json_ld": json_ld,
        "images": images,
    }


# ---------- Main ----------
def main():
    print("=" * 64)
    print("Midwest CNC Services — Content Migration")
    print("=" * 64)

    crawl, image_map = load_inputs()
    all_paths = crawl["pages_crawled"]
    paths = [p for p in all_paths if p not in EXCLUDE_PATHS]
    skipped = [p for p in all_paths if p in EXCLUDE_PATHS]

    print(f"  Pages in crawl report: {len(all_paths)}")
    print(f"  Skipping (excluded):   {len(skipped)}")
    print(f"  Scraping:              {len(paths)}")
    print()

    issues = {
        "missing_title": [],
        "missing_meta_description": [],
        "missing_canonical": [],
        "missing_h1": [],
        "multiple_h1": [],
        "jsonld_parse_errors": [],
        "images_not_in_map": [],
        "http_errors": [],
    }

    pages = {}
    for i, path in enumerate(paths, 1):
        page = process_page(path, image_map, issues)
        pages[path] = page
        status = page.get("status")
        marker = "✓" if status == 200 else "✗"
        print(f"  {marker} [{i:>3}/{len(paths)}] {path}  ({status})")
        time.sleep(REQUEST_DELAY)

    PAGES_OUT.write_text(json.dumps(pages, indent=2, ensure_ascii=False))

    report = {
        "base_url": BASE_URL,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "pages_in_crawl": len(all_paths),
        "pages_skipped": len(skipped),
        "skipped_paths": skipped,
        "pages_attempted": len(paths),
        "pages_extracted": sum(1 for p in pages.values() if p.get("status") == 200),
        "pages_failed": sum(1 for p in pages.values() if p.get("status") != 200),
        "issues": issues,
        "issue_counts": {k: len(v) for k, v in issues.items()},
    }
    REPORT_OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    print("\n" + "=" * 64)
    print("Summary")
    print("=" * 64)
    print(f"  Pages attempted:  {report['pages_attempted']}")
    print(f"  Pages extracted:  {report['pages_extracted']}")
    print(f"  Pages failed:     {report['pages_failed']}")
    print()
    print("  Issue counts:")
    for k, n in report["issue_counts"].items():
        print(f"    {k:<28}{n}")
    print()
    print(f"  Output: {PAGES_OUT}")
    print(f"  Report: {REPORT_OUT}")
    print("=" * 64)


if __name__ == "__main__":
    main()
