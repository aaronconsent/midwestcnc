#!/usr/bin/env python3
"""
Midwest CNC Services — Image Migration Tool
============================================

Crawls midwestcncservices.com, finds every image from cdn.durable.co
(including ones wrapped by Next.js's _next/image optimizer), downloads the
ORIGINAL full-resolution versions, renames them semantically using alt text
and page context, and writes a URL mapping file the rebuild can consume.

Outputs (all under ~/midwestcnc/):
  assets/images/logos/       → logo files
  assets/images/states/      → state-level service area imagery
  assets/images/cities/      → city-level service area imagery
  assets/images/services/    → service detail page imagery
  assets/images/general/     → home, about, get-a-quote imagery
  assets/images/blocks/      → uncategorized fallback
  data/image-map.json        → { cdn_url: { local_path, alt, used_on_pages, category } }
  data/crawl-report.json     → pages crawled, counts, any failures

Usage:
  python3 download_images.py

Dependencies (already on Python 3.9.6 + pip3):
  pip3 install requests beautifulsoup4
"""

import json
import re
import time
from collections import OrderedDict
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# ---------- Config ----------
BASE_URL = "https://midwestcncservices.com"
PROJECT_DIR = Path.home() / "midwestcnc"
IMAGES_DIR = PROJECT_DIR / "assets" / "images"
DATA_DIR = PROJECT_DIR / "data"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}
REQUEST_DELAY = 0.4  # seconds between requests — be polite to the source
TIMEOUT = 25
VALID_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


# ---------- Helpers ----------
def setup_dirs():
    """Create the project folder structure."""
    for sub in ["logos", "states", "cities", "services", "general", "blocks"]:
        (IMAGES_DIR / sub).mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Project directory ready: {PROJECT_DIR}")


def slugify(text, max_length=60):
    """Convert arbitrary text into a filename-safe slug."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:max_length].strip("-")


def extract_cdn_url(src):
    """
    Pull the underlying cdn.durable.co URL from an <img src>.
    Handles direct CDN URLs and Next.js optimizer wrappers
    (/_next/image?url=<encoded>&w=...&q=...).
    Returns None for data URIs, non-Durable images, etc.
    """
    if not src or src.startswith("data:"):
        return None

    # Next.js image optimizer wrapper — unwrap to get the original
    if "_next/image" in src:
        params = parse_qs(urlparse(src).query)
        wrapped = params.get("url", [None])[0]
        if wrapped:
            decoded = unquote(wrapped)
            if "cdn.durable.co" in decoded:
                return decoded
        return None

    # Direct Durable CDN URL
    if "cdn.durable.co" in src:
        return src

    return None


def categorize_image(cdn_url, page_path):
    """Decide which folder an image belongs in based on URL + page context."""
    if "/logos/" in cdn_url:
        return "logos"
    if page_path.startswith("/service-area/"):
        slug = page_path.replace("/service-area/", "").strip("/")
        # State pages = single-token slugs (iowa, illinois)
        # City pages = hyphenated slugs (des-moines-iowa)
        return "cities" if "-" in slug else "states"
    if page_path.startswith(("/repairs/", "/way-covers/", "/spindles-repair/")):
        return "services"
    if page_path in ("/", "/about", "/get-a-quote"):
        return "general"
    return "blocks"


def build_filename(cdn_url, alt, page_path, category, used_in_category):
    """Generate a semantic filename, avoiding collisions per category folder."""
    ext = Path(urlparse(cdn_url).path).suffix.lower()
    if ext not in VALID_EXTS:
        ext = ".png"

    if category == "logos":
        base = "midwest-cnc-logo"
    elif alt and slugify(alt):
        base = slugify(alt)
    else:
        page_slug = slugify(page_path.strip("/").replace("/", "-")) or "home"
        base = f"{page_slug}-image"

    candidate = f"{base}{ext}"
    counter = 2
    while candidate in used_in_category:
        candidate = f"{base}-{counter}{ext}"
        counter += 1
    used_in_category.add(candidate)
    return candidate


# ---------- Crawl ----------
def discover_pages(start_url):
    """BFS crawl: follow internal links, return { path: html }."""
    print(f"\n→ Crawling site from {start_url}")
    seen = set()
    queue = [start_url]
    pages = OrderedDict()
    base_netloc = urlparse(BASE_URL).netloc

    while queue:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)

        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
        except Exception as e:
            print(f"  ✗ {url} — {e}")
            continue

        path = urlparse(url).path or "/"
        pages[path] = r.text
        print(f"  ✓ {path}")
        time.sleep(REQUEST_DELAY)

        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            # Skip tel:, mailto:, javascript:, fragments
            if href.startswith(("tel:", "mailto:", "javascript:", "#")):
                continue
            full = urljoin(url, href)
            parsed = urlparse(full)
            if parsed.netloc != base_netloc:
                continue
            # Strip query + fragment so /page and /page?x= are the same
            clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if clean not in seen and clean not in queue:
                queue.append(clean)

    print(f"\n✓ Discovered {len(pages)} pages")
    return pages


def extract_images(pages_html):
    """Build a deduplicated inventory of Durable CDN images across all pages."""
    print("\n→ Extracting image references")
    images = OrderedDict()

    for path, html in pages_html.items():
        soup = BeautifulSoup(html, "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src", "")
            alt = (img.get("alt") or "").strip()
            cdn_url = extract_cdn_url(src)
            if not cdn_url:
                continue

            if cdn_url not in images:
                images[cdn_url] = {
                    "alt": alt,
                    "first_page": path,
                    "all_pages": [path],
                }
            else:
                if path not in images[cdn_url]["all_pages"]:
                    images[cdn_url]["all_pages"].append(path)
                # Keep the longest/most descriptive alt seen
                if alt and len(alt) > len(images[cdn_url]["alt"]):
                    images[cdn_url]["alt"] = alt

    print(f"✓ Found {len(images)} unique images across the site")
    return images


# ---------- Download ----------
def download_images(images):
    """Download each unique image. Returns (mapping, failures)."""
    print("\n→ Downloading images")
    mapping = OrderedDict()
    used_names = {}  # { category: set(filenames) }
    failures = []

    for cdn_url, info in images.items():
        category = categorize_image(cdn_url, info["first_page"])
        used_names.setdefault(category, set())
        filename = build_filename(
            cdn_url, info["alt"], info["first_page"], category, used_names[category]
        )
        out_path = IMAGES_DIR / category / filename
        local_path = f"/assets/images/{category}/{filename}"

        try:
            r = requests.get(cdn_url, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            out_path.write_bytes(r.content)
            size_kb = max(1, len(r.content) // 1024)
            print(f"  ✓ {category}/{filename}  ({size_kb} KB)")
            mapping[cdn_url] = {
                "local_path": local_path,
                "alt": info["alt"],
                "used_on_pages": info["all_pages"],
                "category": category,
            }
        except Exception as e:
            print(f"  ✗ {cdn_url} — {e}")
            failures.append({"url": cdn_url, "error": str(e)})

        time.sleep(REQUEST_DELAY)

    return mapping, failures


# ---------- Main ----------
def main():
    print("=" * 64)
    print("Midwest CNC Services — Image Migration")
    print("=" * 64)

    setup_dirs()
    pages = discover_pages(BASE_URL)
    images = extract_images(pages)
    mapping, failures = download_images(images)

    map_path = DATA_DIR / "image-map.json"
    report_path = DATA_DIR / "crawl-report.json"

    with map_path.open("w") as f:
        json.dump(mapping, f, indent=2)

    report = {
        "base_url": BASE_URL,
        "pages_crawled": list(pages.keys()),
        "page_count": len(pages),
        "unique_images_found": len(images),
        "images_downloaded": len(mapping),
        "failures": failures,
    }
    with report_path.open("w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 64)
    print("Summary")
    print("=" * 64)
    print(f"  Pages crawled:      {len(pages)}")
    print(f"  Unique images:      {len(images)}")
    print(f"  Downloaded:         {len(mapping)}")
    print(f"  Failures:           {len(failures)}")
    print()
    print(f"  Images folder:      {IMAGES_DIR}")
    print(f"  URL mapping file:   {map_path}")
    print(f"  Crawl report:       {report_path}")
    print("=" * 64)


if __name__ == "__main__":
    main()
