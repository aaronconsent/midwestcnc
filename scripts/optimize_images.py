#!/usr/bin/env python3
"""
Image optimizer — convert public/assets raster images to WebP and
rewrite the generated HTML to serve the smaller files.

Run as the final build step, after every page generator. Idempotent:
a source image is re-encoded only when it is newer than its .webp.

Design choice — we rewrite the HTML *output*, not the generator source:
  * Generators keep emitting .png/.jpg paths (their source is untouched).
  * This script converts each raster to a .webp sibling, then rewrites
    every reference in public/**/*.html to point at the .webp.
  * The original PNG/JPG files stay in place as the committed source of
    truth. If a conversion ever fails, that file's references simply
    stay pointing at the original raster — so there is no way to end up
    with a broken image reference.

The user-facing win: browsers download the ~85%-smaller WebP. The
biggest effect is on brand pages, where a ~900 KB PNG hero (the LCP
element) becomes a ~120 KB WebP.

Usage:
    python3 scripts/optimize_images.py            # convert + rewrite
    python3 scripts/optimize_images.py --quiet     # only print the summary
    python3 scripts/optimize_images.py --prune     # delete originals after
                                                   #  conversion (advanced —
                                                   #  see note at bottom)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PUBLIC = REPO / "public"
ASSETS = PUBLIC / "assets"

RASTER_EXTS = {".png", ".jpg", ".jpeg"}
WEBP_QUALITY = 82
WEBP_METHOD = 6          # 0=fast/large … 6=slow/smallest
SKIP_BELOW_BYTES = 8 * 1024   # tiny images rarely benefit; skip them


def human(n: float) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


def convert_images(quiet: bool):
    """Convert every raster under public/assets to WebP. Returns a list
    of (relative_raster_url, relative_webp_url) mappings for every raster
    that now has a .webp sibling, plus stats."""
    try:
        from PIL import Image
    except ImportError:
        print("  ! Pillow not installed — skipping image optimization. "
              "Run: pip install Pillow", file=sys.stderr)
        return [], {"converted": 0, "reused": 0, "skipped": 0, "saved": 0, "failed": 0}

    mapping = []
    stats = {"converted": 0, "reused": 0, "skipped": 0, "saved": 0, "failed": 0}

    if not ASSETS.exists():
        return mapping, stats

    for path in sorted(ASSETS.rglob("*")):
        if path.suffix.lower() not in RASTER_EXTS:
            continue
        webp = path.with_suffix(".webp")
        rel_raster = "/" + str(path.relative_to(PUBLIC))
        rel_webp = "/" + str(webp.relative_to(PUBLIC))
        src_size = path.stat().st_size

        # Already converted and current — reuse, still record the mapping.
        if webp.exists() and webp.stat().st_mtime >= path.stat().st_mtime:
            mapping.append((rel_raster, rel_webp))
            stats["reused"] += 1
            continue

        if src_size < SKIP_BELOW_BYTES:
            stats["skipped"] += 1
            continue

        try:
            img = Image.open(path)
            # Normalize palette/grayscale-alpha so WebP keeps transparency.
            if img.mode in ("P", "LA"):
                img = img.convert("RGBA")
            img.save(webp, "WEBP", quality=WEBP_QUALITY, method=WEBP_METHOD)
        except Exception as e:  # noqa: BLE001
            print(f"  ! failed: {path.relative_to(REPO)}: {e}", file=sys.stderr)
            stats["failed"] += 1
            continue

        webp_size = webp.stat().st_size
        saved = src_size - webp_size
        stats["converted"] += 1
        stats["saved"] += max(0, saved)
        mapping.append((rel_raster, rel_webp))
        if not quiet:
            print(f"  ✓ {path.name:<55} {human(src_size):>9} → {human(webp_size):>9}"
                  f"  (-{(saved / src_size * 100):.0f}%)")

    return mapping, stats


def rewrite_html(mapping, quiet: bool):
    """Rewrite every reference to a converted raster in public/**/*.html
    to the .webp path. Matches relative AND absolute URLs (the relative
    path is a substring of the absolute one). Returns (files, refs)."""
    if not mapping:
        return 0, 0
    files_changed = 0
    refs_rewritten = 0
    for html in PUBLIC.rglob("*.html"):
        text = html.read_text(encoding="utf-8")
        original = text
        for rel_raster, rel_webp in mapping:
            if rel_raster in text:
                refs_rewritten += text.count(rel_raster)
                text = text.replace(rel_raster, rel_webp)
        if text != original:
            html.write_text(text, encoding="utf-8")
            files_changed += 1
    return files_changed, refs_rewritten


def prune_originals(mapping, quiet: bool):
    """Delete the original raster for every successfully-converted image.
    Off by default. See the note at the bottom of this file before using."""
    removed = 0
    for rel_raster, _ in mapping:
        p = PUBLIC / rel_raster.lstrip("/")
        if p.exists():
            p.unlink()
            removed += 1
            if not quiet:
                print(f"  - pruned {p.name}")
    return removed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true", help="only print the summary line")
    ap.add_argument("--prune", action="store_true",
                    help="delete original PNG/JPG after conversion (advanced)")
    args = ap.parse_args()

    print("== Image optimization (PNG/JPG → WebP) ==")
    mapping, stats = convert_images(args.quiet)
    files, refs = rewrite_html(mapping, args.quiet)

    pruned = 0
    if args.prune:
        pruned = prune_originals(mapping, args.quiet)

    print()
    print(f"  Converted:   {stats['converted']}")
    print(f"  Reused:      {stats['reused']} (already current)")
    print(f"  Skipped:     {stats['skipped']} (under {human(SKIP_BELOW_BYTES)})")
    if stats["failed"]:
        print(f"  Failed:      {stats['failed']}")
    print(f"  Bytes saved: {human(stats['saved'])} (this run)")
    print(f"  HTML rewrite: {refs} references across {files} files")
    if args.prune:
        print(f"  Pruned:      {pruned} original raster files")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# ---------------------------------------------------------------------------
# NOTE on --prune
#
# By default the original PNG/JPG files are kept as the committed source of
# truth, and only the served HTML is rewritten to .webp. This is the safe
# mode: a fresh build always has the rasters available to (re)convert.
#
# --prune deletes the originals. If you ever run it, the generators will
# still emit .png references on the NEXT build, but the rasters will be
# gone — and this script can no longer convert them, leaving the rewrite
# pointing at .webp files that already exist (fine) UNLESS a new build
# regenerates a page whose raster was pruned and not re-added. In short:
# only prune if you also migrate the generator source to emit .webp
# directly. For now, leave it off.
# ---------------------------------------------------------------------------
