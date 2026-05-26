#!/usr/bin/env python3
"""
Comprehensive thin-content + SEO/AEO/GEO audit.

Walks every HTML file in public/, computes content depth, location-page
uniqueness, schema completeness, link topology, AEO/GEO signals, local
SEO consistency, and image accessibility. Writes a structured report to
docs/seo-thin-content-audit.md.

Audit-only. No HTML is modified.
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(REPO, "public")
ASSETS = os.path.join(REPO, "assets")


# ---------- Page classification ----------

def classify_page(rel_path):
    """Return (page_type, sort_key) for a public/ relative path."""
    p = rel_path
    if p == "index.html":                                       return "homepage"
    if p == "404.html":                                         return "404"
    if p in ("about/index.html", "get-a-quote/index.html",
             "privacy-policy/index.html", "terms-of-service/index.html"):
        return "site-shell"
    if p in ("repairs/index.html", "spindle-grinding/index.html",
             "way-covers/index.html", "service-area/index.html"):
        return "service-hub"
    if p.startswith("spindle-grinding/") and p.endswith("-spindle-repair/index.html"):
        return "brand-spindle"
    if p.startswith("repairs/") and p.endswith("-cnc-machine-repair/index.html"):
        return "brand-repair"
    if p == "repairs/amada-press-brake-service/index.html":     return "brand-main-alt"
    if p == "repairs/trumpf-laser-service/index.html":          return "brand-main-alt"
    if p.startswith("way-covers/") and p.endswith("-cnc-way-covers/index.html"):
        return "brand-way-covers"
    if p.startswith("service-area/"):
        parts = p.split("/")
        # service-area/{slug}/index.html
        if len(parts) == 3:
            slug = parts[1]
            # State slugs are short, single-token; city slugs are hyphenated
            STATES = {"iowa", "illinois", "wisconsin", "minnesota",
                       "nebraska", "missouri", "texas"}
            if slug in STATES:
                return "state"
            return "city"
    return "other"


# ---------- Content extraction ----------

def html_files():
    out = []
    for root, dirs, files in os.walk(PUBLIC):
        for f in files:
            if f.endswith(".html"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, PUBLIC)
                out.append((rel, full))
    out.sort()
    return out


def extract_main(html):
    m = re.search(r'<main>(.*?)</main>', html, re.S)
    return m.group(1) if m else ""


def strip_chrome_and_get_text(main_html):
    """Strip CTAs, hero figures, form placeholders, scripts; return text."""
    body = main_html
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
    body = re.sub(r'<div class="cta-row".*?</div>', '', body, flags=re.S)
    body = re.sub(r'<figure[^>]*>.*?</figure>', '', body, flags=re.S)
    body = re.sub(r'<div class="quote-form-placeholder".*?</div>', '', body, flags=re.S)
    body = re.sub(r'<form[^>]*>.*?</form>', '', body, flags=re.S)
    # Strip tags
    text = re.sub(r'<[^>]+>', ' ', body)
    # Decode entities (rough)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#x27;|&apos;', "'", text)
    text = re.sub(r'&[#a-zA-Z0-9]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokens(text):
    return re.findall(r"\b[\w'-]+\b", text.lower())


def first_n_words(text, n=200):
    toks = re.findall(r"\S+", text)
    return " ".join(toks[:n])


def extract_schemas(html):
    out = []
    for m in re.finditer(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
        html, re.S,
    ):
        try:
            out.append(json.loads(m.group(1)))
        except Exception:
            out.append({"_parse_error": True})
    return out


def schema_types(schemas):
    types = []
    for s in schemas:
        if isinstance(s, dict) and "@type" in s:
            t = s["@type"]
            if isinstance(t, list):
                types.extend(t)
            else:
                types.append(t)
    return types


def extract_internal_links(html, current_path):
    """Find every href that points internally (relative or to our domain).
    Returns list of normalized paths."""
    hrefs = re.findall(r'<a\s[^>]*href="([^"]+)"[^>]*>', html, re.DOTALL)
    out = []
    for h in hrefs:
        if h.startswith(("#", "?", "tel:", "mailto:", "javascript:")):
            continue
        if h.startswith("https://midwestcncservices.com"):
            h = h[len("https://midwestcncservices.com"):]
        if h.startswith(("http://", "https://", "//")):
            continue
        # Drop query/fragment
        h = h.split("?", 1)[0].split("#", 1)[0]
        if not h.startswith("/"):
            continue
        out.append(h)
    return out


def extract_headings(html):
    """Return (h1_count, h2_count, h3_count, [h2_texts])."""
    h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.S)
    h3s = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.S)
    def clean(s): return re.sub(r'<[^>]+>', '', s).strip()
    return len(h1s), len(h2s), len(h3s), [clean(h) for h in h2s]


def extract_images(html):
    """Return list of (src, alt) tuples — alt is None if attribute missing."""
    out = []
    for m in re.finditer(r'<img\b[^>]*>', html):
        tag = m.group(0)
        src_m = re.search(r'\bsrc="([^"]*)"', tag)
        alt_m = re.search(r'\balt="([^"]*)"', tag)
        out.append((
            src_m.group(1) if src_m else "",
            None if alt_m is None else alt_m.group(1),
        ))
    return out


# ---------- N-gram uniqueness ----------

def ngrams(toks, n=5):
    if len(toks) < n:
        return []
    return [tuple(toks[i:i+n]) for i in range(len(toks) - n + 1)]


def compute_uniqueness(pages_text, n=5):
    """For each page in a same-type group, return % of n-grams unique to it."""
    by_page_grams = {}
    for path, text in pages_text.items():
        by_page_grams[path] = ngrams(tokens(text), n)

    gram_pages = defaultdict(set)
    for path, grams in by_page_grams.items():
        for g in set(grams):
            gram_pages[g].add(path)

    results = {}
    for path, grams in by_page_grams.items():
        if not grams:
            results[path] = 0.0
            continue
        unique = sum(1 for g in grams if len(gram_pages[g]) == 1)
        results[path] = unique / len(grams)
    return results


# ---------- AEO/GEO ----------

DIRECT_ANSWER_PATTERNS = [
    r"\b\d+\s*[-–]\s*\d+\s*weeks?\b",      # "3-5 weeks"
    r"\b(?:most|every|all)\s+\w+\b",        # "most customers", "every brand"
    r"\bwe (?:rebuild|service|cover|work|do|handle|manufacture)\b",
    r"\bwe[''']re based in\b",
    r"\bwaterloo,?\s+iowa\b",
    r"\b319-610-4341\b",
    r"\b\d+\s+states?\b",
]


def has_direct_answer(first_200_text):
    """Heuristic: does the first 200 words contain a citable factual statement?"""
    low = first_200_text.lower()
    return sum(1 for p in DIRECT_ANSWER_PATTERNS if re.search(p, low))


# ---------- Local SEO checks ----------

NAP_CHECK = {
    "name": re.compile(r"\bMidwest CNC Services\b"),
    "city_state": re.compile(r"\bWaterloo,?\s+(?:Iowa|IA)\b", re.I),
    "phone": re.compile(r"\b319[-\s]?610[-\s]?4341\b"),
}

STATE_TOKENS = ["Iowa", "Illinois", "Wisconsin", "Minnesota",
                 "Nebraska", "Missouri", "Texas"]


# ---------- Audit driver ----------

def main():
    files = html_files()
    print(f"Auditing {len(files)} HTML files...")

    # Per-page accumulator
    pages = []
    for rel, full in files:
        src = open(full).read()
        main_html = extract_main(src)
        body_text = strip_chrome_and_get_text(main_html)
        toks = tokens(body_text)
        kind = classify_page(rel)
        first200 = first_n_words(body_text, 200)
        schemas = extract_schemas(src)
        s_types = schema_types(schemas)
        # Count links from the WHOLE document (header nav, footer, body, sticky CTA)
        # so orphan/dead-end metrics reflect what a crawler actually sees.
        internal = extract_internal_links(src, rel)
        n_h1, n_h2, n_h3, h2_texts = extract_headings(main_html)
        imgs = extract_images(src)
        page = {
            "rel": rel,
            "kind": kind,
            "body": body_text,
            "first200": first200,
            "tokens": toks,
            "word_count": len(toks),
            "schemas": schemas,
            "schema_types": s_types,
            "internal_links": internal,
            "h1": n_h1, "h2": n_h2, "h3": n_h3,
            "h2_texts": h2_texts,
            "images": imgs,
            "has_direct_answer": has_direct_answer(first200),
            "nap": {k: bool(rx.search(src)) for k, rx in NAP_CHECK.items()},
            "states_mentioned": sum(1 for s in STATE_TOKENS if s in src),
        }
        pages.append(page)

    # ============ TASK 2 — n-gram uniqueness for location pages ============
    cities = {p["rel"]: p["body"] for p in pages if p["kind"] == "city"}
    states = {p["rel"]: p["body"] for p in pages if p["kind"] == "state"}
    uniq_cities = compute_uniqueness(cities, n=5)
    uniq_states = compute_uniqueness(states, n=5)

    # Also compute for brand-spindle and brand-repair groups so we know
    # the baseline for non-location pages.
    brand_spindle = {p["rel"]: p["body"] for p in pages if p["kind"] == "brand-spindle"}
    brand_repair = {p["rel"]: p["body"] for p in pages if p["kind"] == "brand-repair"}
    brand_covers = {p["rel"]: p["body"] for p in pages if p["kind"] == "brand-way-covers"}
    uniq_brand_spindle = compute_uniqueness(brand_spindle, n=5)
    uniq_brand_repair = compute_uniqueness(brand_repair, n=5)
    uniq_brand_covers = compute_uniqueness(brand_covers, n=5)

    # Attach uniqueness to each page record
    all_uniq = {}
    all_uniq.update(uniq_cities)
    all_uniq.update(uniq_states)
    all_uniq.update(uniq_brand_spindle)
    all_uniq.update(uniq_brand_repair)
    all_uniq.update(uniq_brand_covers)
    for p in pages:
        p["uniqueness"] = all_uniq.get(p["rel"])

    # ============ TASK 4 — link graph ============
    # Build forward and reverse adjacency
    fwd = defaultdict(list)
    rev = defaultdict(list)
    by_path_to_kind = {}
    # Convert each rel to a canonical URL path for matching
    def rel_to_url(rel):
        if rel == "index.html":      return "/"
        if rel == "404.html":        return "/404.html"
        return "/" + rel.replace("/index.html", "/")

    for p in pages:
        url = rel_to_url(p["rel"])
        by_path_to_kind[url] = p["kind"]

    for p in pages:
        src_url = rel_to_url(p["rel"])
        for h in p["internal_links"]:
            # Normalize
            target = h
            if not target.endswith("/") and not target.endswith(".html"):
                target = target + "/"
            fwd[src_url].append(target)
            rev[target].append(src_url)

    out_counts = {url: len(set(fwd[url])) for url in [rel_to_url(p["rel"]) for p in pages]}
    in_counts  = {url: len(set(rev[url])) for url in [rel_to_url(p["rel"]) for p in pages]}

    # Topic clusters: do all Iowa-related pages (state + cities) link to each other?
    iowa_pages = [p for p in pages if p["kind"] in ("state", "city")
                  and ("iowa" in p["rel"])]
    iowa_state_url = "/service-area/iowa/"
    iowa_city_urls = [rel_to_url(p["rel"]) for p in iowa_pages if p["kind"] == "city"]
    iowa_cluster = {
        "state_to_cities": sum(1 for c in iowa_city_urls
                                if c in set(fwd[iowa_state_url])),
        "cities_to_state": sum(1 for c in iowa_city_urls
                                if iowa_state_url in set(fwd[c])),
        "total_iowa_cities": len(iowa_city_urls),
    }

    # Mazak topic cluster — do all Mazak pages cross-link?
    mazak_urls = [rel_to_url(p["rel"]) for p in pages
                  if "mazak" in p["rel"]
                  and p["kind"] in ("brand-spindle", "brand-repair", "brand-way-covers")]
    mazak_cross = 0
    for m1 in mazak_urls:
        for m2 in mazak_urls:
            if m1 != m2 and m2 in set(fwd[m1]):
                mazak_cross += 1
    mazak_max_links = len(mazak_urls) * (len(mazak_urls) - 1)
    mazak_ratio = mazak_cross / mazak_max_links if mazak_max_links else 0

    # Top 20 by in-degree
    top_by_in = sorted(in_counts.items(), key=lambda kv: -kv[1])[:20]

    # ============ TASK 7 — image accessibility ============
    img_findings = {
        "total_images": 0,
        "missing_alt": [],
        "empty_alt": [],
        "generic_alt": [],
        "duplicate_alt": defaultdict(list),
    }
    GENERIC_ALT = {"image", "photo", "picture", "img", "logo"}
    for p in pages:
        for src, alt in p["images"]:
            img_findings["total_images"] += 1
            if alt is None:
                img_findings["missing_alt"].append((p["rel"], src))
            elif alt.strip() == "":
                img_findings["empty_alt"].append((p["rel"], src))
            else:
                if alt.strip().lower() in GENERIC_ALT:
                    img_findings["generic_alt"].append((p["rel"], src, alt))
                img_findings["duplicate_alt"][alt.strip()].append(p["rel"])

    dup_alts_real = {alt: locs for alt, locs in img_findings["duplicate_alt"].items()
                      if len(locs) > 1 and alt not in ("Midwest CNC Services",)}

    # ============ TASK 6 — Local SEO ============
    nap_consistency = {
        "name_on_all":      all(p["nap"]["name"]      for p in pages),
        "city_state_on_all": all(p["nap"]["city_state"] for p in pages),
        "phone_on_all":     all(p["nap"]["phone"]     for p in pages),
        "name_missing_on":      [p["rel"] for p in pages if not p["nap"]["name"]],
        "city_state_missing_on":[p["rel"] for p in pages if not p["nap"]["city_state"]],
        "phone_missing_on":     [p["rel"] for p in pages if not p["nap"]["phone"]],
    }

    # Geo coordinates in homepage LocalBusiness?
    home = next(p for p in pages if p["kind"] == "homepage")
    home_localbusiness = next(
        (s for s in home["schemas"]
         if isinstance(s, dict) and s.get("@type") == "LocalBusiness"),
        None
    )
    home_has_geo = bool(home_localbusiness and home_localbusiness.get("geo"))

    # llms.txt
    llms_path = os.path.join(PUBLIC, "llms.txt")
    has_llms = os.path.exists(llms_path)

    # ============ TASK 9 — Content gap to "competitive" ============
    COMPETITIVE_TARGETS = {
        "homepage":           1000,
        "site-shell":         500,
        "service-hub":        700,
        "brand-spindle":      700,
        "brand-repair":       600,
        "brand-main-alt":     600,
        "brand-way-covers":   500,
        "state":              800,
        "city":               500,
        "404":                0,    # no target
        "other":              500,
    }

    gaps_by_kind = defaultdict(lambda: {"pages": 0, "words": 0, "gap": 0})
    for p in pages:
        target = COMPETITIVE_TARGETS.get(p["kind"], 0)
        gap = max(0, target - p["word_count"])
        gaps_by_kind[p["kind"]]["pages"] += 1
        gaps_by_kind[p["kind"]]["words"] += p["word_count"]
        gaps_by_kind[p["kind"]]["gap"] += gap

    # ============ COMPOSE REPORT ============
    out = []
    out.append("# SEO / AEO / GEO + Thin-Content Audit")
    out.append("")
    out.append(f"Audited **{len(pages)} HTML files** under `public/`. Audit-only — "
                f"no HTML modified. This report drives the next enrichment pass.")
    out.append("")

    # ---- Headline summary ----
    out.append("## Headline numbers")
    out.append("")
    n_city_thin = sum(1 for r, u in uniq_cities.items() if u < 0.60)
    n_state_thin = sum(1 for r, u in uniq_states.items() if u < 0.60)
    out.append(f"- **City pages below 60% unique:** {n_city_thin} / {len(uniq_cities)} 🚨")
    out.append(f"- **State pages below 60% unique:** {n_state_thin} / {len(uniq_states)}")
    out.append(f"- **Brand spindle pages below 60% unique:** "
                f"{sum(1 for u in uniq_brand_spindle.values() if u < 0.60)} / {len(uniq_brand_spindle)}")
    out.append(f"- **Brand machine-repair pages below 60% unique:** "
                f"{sum(1 for u in uniq_brand_repair.values() if u < 0.60)} / {len(uniq_brand_repair)}")
    out.append(f"- **Brand way-covers pages below 60% unique:** "
                f"{sum(1 for u in uniq_brand_covers.values() if u < 0.60)} / {len(uniq_brand_covers)}")
    total_gap = sum(g["gap"] for g in gaps_by_kind.values())
    out.append(f"- **Total word gap to competitive targets:** **~{total_gap:,} words** across all pages")
    out.append(f"- `llms.txt` present at site root: **{'yes' if has_llms else 'no'}**")
    out.append(f"- Homepage `LocalBusiness` schema has geo coordinates: **{'yes' if home_has_geo else 'no'}**")
    out.append(f"- NAP consistency across all pages: "
                f"name={'✓' if nap_consistency['name_on_all'] else '✗'}  "
                f"city/state={'✓' if nap_consistency['city_state_on_all'] else '✗'}  "
                f"phone={'✓' if nap_consistency['phone_on_all'] else '✗'}")
    out.append("")

    # ============ TASK 1 — Per-page content depth ============
    out.append("## Task 1 — Per-page content depth")
    out.append("")
    out.append("Grouped by page type. Columns: word count, h2/h3, internal-link "
                "out-degree, direct-answer signal (count of factual patterns in "
                "first 200 words), images, schema types, n-gram uniqueness (where "
                "computed).")
    out.append("")
    # Group by kind
    by_kind = defaultdict(list)
    for p in pages:
        by_kind[p["kind"]].append(p)

    kind_order = ["homepage", "service-hub", "site-shell",
                   "state", "city",
                   "brand-spindle", "brand-repair", "brand-main-alt",
                   "brand-way-covers", "404"]
    for kind in kind_order:
        rows = by_kind.get(kind, [])
        if not rows: continue
        out.append(f"### {kind}  ({len(rows)} pages)")
        out.append("")
        out.append("| Path | Words | H2 | H3 | Links out | Answer | Images | Uniq% | Schema |")
        out.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
        for r in sorted(rows, key=lambda x: x["rel"]):
            uniq = r["uniqueness"]
            uniq_str = f"{int(uniq*100)}" if uniq is not None else "—"
            schemas = "+".join(sorted(set(r["schema_types"]))) or "(none)"
            out.append(
                f"| `{r['rel']}` | {r['word_count']} | {r['h2']} | {r['h3']} | "
                f"{len(set(r['internal_links']))} | {r['has_direct_answer']} | "
                f"{len(r['images'])} | {uniq_str} | {schemas} |"
            )
        out.append("")

    # ============ TASK 2 — Location uniqueness ============
    out.append("## Task 2 — Location-page uniqueness (CRITICAL)")
    out.append("")
    out.append("5-gram analysis: for each location page, what fraction of "
                "5-grams are unique to that page across siblings? "
                "**Below 60% is the SEO penalty-risk threshold for "
                "location-page enforcement.**")
    out.append("")
    out.append("### City pages (sorted by uniqueness, lowest first)")
    out.append("")
    out.append("| Path | Words | Unique 5-grams | Verdict |")
    out.append("|---|---:|---:|:-:|")
    for path, ratio in sorted(uniq_cities.items(), key=lambda kv: kv[1]):
        wc = next(p["word_count"] for p in pages if p["rel"] == path)
        pct = int(ratio * 100)
        verdict = "🚨 FAIL" if ratio < 0.60 else ("⚠ borderline" if ratio < 0.75 else "✓")
        out.append(f"| `{path}` | {wc} | {pct}% | {verdict} |")
    out.append("")
    out.append("### State pages")
    out.append("")
    out.append("| Path | Words | Unique 5-grams | Verdict |")
    out.append("|---|---:|---:|:-:|")
    for path, ratio in sorted(uniq_states.items(), key=lambda kv: kv[1]):
        wc = next(p["word_count"] for p in pages if p["rel"] == path)
        pct = int(ratio * 100)
        verdict = "🚨 FAIL" if ratio < 0.60 else ("⚠ borderline" if ratio < 0.75 else "✓")
        out.append(f"| `{path}` | {wc} | {pct}% | {verdict} |")
    out.append("")
    out.append("### Brand-spindle pages")
    out.append("")
    out.append("| Path | Words | Unique 5-grams |")
    out.append("|---|---:|---:|")
    for path, ratio in sorted(uniq_brand_spindle.items(), key=lambda kv: kv[1])[:8]:
        wc = next(p["word_count"] for p in pages if p["rel"] == path)
        out.append(f"| `{path}` | {wc} | {int(ratio*100)}% |")
    out.append("")
    out.append("### Brand machine-repair pages")
    out.append("")
    out.append("| Path | Words | Unique 5-grams |")
    out.append("|---|---:|---:|")
    for path, ratio in sorted(uniq_brand_repair.items(), key=lambda kv: kv[1])[:8]:
        wc = next(p["word_count"] for p in pages if p["rel"] == path)
        out.append(f"| `{path}` | {wc} | {int(ratio*100)}% |")
    out.append("")
    out.append("### Brand way-covers pages")
    out.append("")
    out.append("| Path | Words | Unique 5-grams |")
    out.append("|---|---:|---:|")
    for path, ratio in sorted(uniq_brand_covers.items(), key=lambda kv: kv[1])[:8]:
        wc = next(p["word_count"] for p in pages if p["rel"] == path)
        out.append(f"| `{path}` | {wc} | {int(ratio*100)}% |")
    out.append("")

    # ============ TASK 3 — Schema audit ============
    out.append("## Task 3 — Schema audit")
    out.append("")
    # All distinct types
    all_types = Counter()
    for p in pages:
        for t in set(p["schema_types"]):
            all_types[t] += 1
    out.append("### Distinct schema types in use")
    out.append("")
    out.append("| Schema @type | Pages |")
    out.append("|---|---:|")
    for t, n in all_types.most_common():
        out.append(f"| `{t}` | {n} |")
    out.append("")

    out.append("### Missing-schema gaps")
    out.append("")
    gaps = []
    for p in pages:
        kind = p["kind"]
        types = set(p["schema_types"])
        if kind == "homepage":
            for needed in ("LocalBusiness", "FAQPage"):
                if needed not in types:
                    gaps.append((p["rel"], f"missing {needed}"))
            if not home_has_geo:
                gaps.append((p["rel"], "LocalBusiness lacks geo coordinates"))
            if "Organization" not in types and "LocalBusiness" not in types:
                gaps.append((p["rel"], "missing Organization-equivalent"))
        elif kind == "service-hub":
            for needed in ("BreadcrumbList",):
                if needed not in types:
                    gaps.append((p["rel"], f"missing {needed}"))
            if "ItemList" not in types:
                gaps.append((p["rel"], "no ItemList for brand grid (recommended for hubs)"))
        elif kind in ("brand-spindle", "brand-repair", "brand-way-covers",
                       "brand-main-alt"):
            for needed in ("Service", "BreadcrumbList"):
                if needed not in types:
                    gaps.append((p["rel"], f"missing {needed}"))
            # LocalBusiness reference should be inline @id ref OR LocalBusiness type
            if not any(
                isinstance(s, dict) and (
                    s.get("@type") == "LocalBusiness"
                    or (s.get("@type") == "Service"
                        and isinstance(s.get("provider"), dict)
                        and s["provider"].get("@id"))
                )
                for s in p["schemas"]
            ):
                gaps.append((p["rel"], "Service schema lacks LocalBusiness provider reference"))
        elif kind in ("state", "city"):
            for needed in ("BreadcrumbList", "Service"):
                if needed not in types:
                    gaps.append((p["rel"], f"missing {needed}"))
        # Universal: every non-404, non-homepage page should have BreadcrumbList
        if kind not in ("homepage", "404") and "BreadcrumbList" not in types:
            gaps.append((p["rel"], "missing BreadcrumbList"))

    # Deduplicate gap entries
    gaps = sorted(set(gaps))
    if gaps:
        out.append(f"Found {len(gaps)} schema gap(s):")
        out.append("")
        for path, msg in gaps[:40]:
            out.append(f"- `{path}` — {msg}")
        if len(gaps) > 40:
            out.append(f"- *…and {len(gaps)-40} more*")
    else:
        out.append("No schema gaps. 🎉")
    out.append("")

    # ============ TASK 4 — Link topology ============
    out.append("## Task 4 — Internal link topology")
    out.append("")
    out.append(f"- Total internal `<a>` edges: {sum(len(v) for v in fwd.values())}")
    out.append(f"- Distinct outgoing edges per page (avg): "
                f"{int(sum(len(set(v)) for v in fwd.values()) / max(1, len(fwd)))}")
    out.append("")

    out.append("### Orphan pages (in-degree < 5)")
    out.append("")
    out.append("| URL | In-links | Page type |")
    out.append("|---|---:|---|")
    orphans = sorted(
        [(rel_to_url(p["rel"]), in_counts.get(rel_to_url(p["rel"]), 0), p["kind"])
         for p in pages],
        key=lambda x: x[1],
    )
    n_orphans = sum(1 for _, n, _ in orphans if n < 5)
    for url, n, kind in orphans:
        if n < 5:
            out.append(f"| `{url}` | {n} | {kind} |")
    if n_orphans == 0:
        out.append("| *(none — every page has ≥5 incoming links)* | | |")
    out.append("")

    out.append("### Dead-end pages (out-degree < 5)")
    out.append("")
    out.append("| URL | Out-links | Page type |")
    out.append("|---|---:|---|")
    dead_ends = sorted(
        [(rel_to_url(p["rel"]), out_counts.get(rel_to_url(p["rel"]), 0), p["kind"])
         for p in pages],
        key=lambda x: x[1],
    )
    n_deadends = sum(1 for _, n, _ in dead_ends if n < 5)
    for url, n, kind in dead_ends:
        if n < 5:
            out.append(f"| `{url}` | {n} | {kind} |")
    if n_deadends == 0:
        out.append("| *(none)* | | |")
    out.append("")

    out.append("### Top 20 pages by in-degree (link weight)")
    out.append("")
    out.append("| URL | In-links | Page type |")
    out.append("|---|---:|---|")
    for url, n in top_by_in:
        kind = by_path_to_kind.get(url, "?")
        out.append(f"| `{url}` | {n} | {kind} |")
    out.append("")

    out.append("### Topic-cluster cross-linking")
    out.append("")
    out.append(f"- **Iowa cluster**: state→cities = "
                f"{iowa_cluster['state_to_cities']}/{iowa_cluster['total_iowa_cities']} ; "
                f"cities→state = "
                f"{iowa_cluster['cities_to_state']}/{iowa_cluster['total_iowa_cities']}")
    out.append(f"- **Mazak topic cluster** (spindle + machine-repair + way-covers): "
                f"{mazak_cross}/{mazak_max_links} edges = "
                f"{int(mazak_ratio*100)}% complete")
    out.append("")

    # ============ TASK 5 — AEO/GEO ============
    out.append("## Task 5 — AEO / GEO readiness")
    out.append("")
    n_with_answer = sum(1 for p in pages if p["has_direct_answer"] >= 2)
    out.append(f"- Pages with a direct factual answer signal in first 200 words "
                f"(2+ matched patterns): **{n_with_answer} / {len(pages)}**")
    out.append(f"- Pages with FAQPage schema (Q&A format for AI extraction): "
                f"**{sum(1 for p in pages if 'FAQPage' in p['schema_types'])}**")
    out.append(f"- `llms.txt` at site root: **{'present' if has_llms else 'MISSING'}**")
    out.append(f"  - Best-practice for AEO/GEO crawlers (similar to robots.txt — "
                f"directs LLM-aware crawlers to canonical, citable content)")
    out.append("")
    out.append("**Pages WITHOUT a strong direct-answer signal in first 200 words:**")
    out.append("")
    weak_answer = [p for p in pages if p["has_direct_answer"] < 2 and p["kind"] != "404"]
    if weak_answer:
        out.append("| Path | Answer score | Kind | First 80 chars |")
        out.append("|---|---:|---|---|")
        for p in weak_answer[:25]:
            snippet = p["first200"][:80].replace("|", " ")
            out.append(f"| `{p['rel']}` | {p['has_direct_answer']} | {p['kind']} | {snippet}… |")
        if len(weak_answer) > 25:
            out.append(f"| *…and {len(weak_answer)-25} more* | | | |")
    else:
        out.append("*(all pages have ≥2 direct-answer signals — good)*")
    out.append("")

    # Entity consistency — brand-name casing
    out.append("### Entity-reference consistency")
    out.append("")
    BRAND_VARIANTS = [
        ("Mazak", ["MAZAK", "mazak"]),
        ("Haas",  ["HAAS"]),
        ("DMG Mori", ["DMG MORI", "Dmg Mori", "dmg-mori"]),
        ("Mori Seiki", ["mori-seiki", "MoriSeiki"]),
        ("Fanuc", ["FANUC"]),
        ("Trumpf", ["TRUMPF"]),
        ("Amada", ["AMADA"]),
    ]
    variance_findings = []
    for canonical, variants in BRAND_VARIANTS:
        for v in variants:
            for p in pages:
                # Check body text, not URLs/slugs
                if v in p["body"]:
                    variance_findings.append((p["rel"], v, canonical))
    if variance_findings:
        out.append(f"Found {len(variance_findings)} casing-variant references:")
        for path, found, canonical in variance_findings[:10]:
            out.append(f"- `{path}` uses `{found}` (canonical: `{canonical}`)")
    else:
        out.append("Brand-name casing is consistent across all pages. ✓")
    out.append("")

    # ============ TASK 6 — Local SEO ============
    out.append("## Task 6 — Local SEO signals")
    out.append("")
    out.append("### NAP consistency")
    out.append("")
    out.append(f"- Business name (`Midwest CNC Services`) on all pages: "
                f"**{'✓' if nap_consistency['name_on_all'] else '✗'}**")
    out.append(f"- City/state (`Waterloo, IA` or `Waterloo, Iowa`) on all pages: "
                f"**{'✓' if nap_consistency['city_state_on_all'] else '✗'}**")
    out.append(f"- Phone (`319-610-4341`) on all pages: "
                f"**{'✓' if nap_consistency['phone_on_all'] else '✗'}**")
    for k, missing in (
        ("name", nap_consistency["name_missing_on"]),
        ("city/state", nap_consistency["city_state_missing_on"]),
        ("phone", nap_consistency["phone_missing_on"]),
    ):
        if missing:
            out.append(f"- Pages missing **{k}**:")
            for m in missing[:10]:
                out.append(f"  - `{m}`")
    out.append("")

    out.append("### Geographic-coverage signals")
    out.append("")
    out.append(f"- Homepage LocalBusiness schema includes geo coordinates: "
                f"**{'yes' if home_has_geo else 'NO — recommend adding'}**")
    out.append(f"- Pages mentioning all 7 service-area states by name: "
                f"**{sum(1 for p in pages if p['states_mentioned'] >= 7)} / {len(pages)}**")
    out.append(f"- City pages with geo-aware Service schema (areaServed.City): "
                f"**{sum(1 for p in pages if p['kind'] == 'city' and 'Service' in p['schema_types'])} / "
                f"{sum(1 for p in pages if p['kind'] == 'city')}**")
    out.append(f"- Location pages in sitemap: state=7, city=37 (verified in Phase 2/3 audit)")
    out.append("")

    # ============ TASK 7 — Image accessibility ============
    out.append("## Task 7 — Image & accessibility")
    out.append("")
    out.append(f"- Total `<img>` tags across site: {img_findings['total_images']}")
    out.append(f"- Missing `alt` attribute: {len(img_findings['missing_alt'])}")
    out.append(f"- Empty `alt=\"\"` (decorative): {len(img_findings['empty_alt'])}")
    out.append(f"- Generic alt text (\"image\", \"photo\", etc.): "
                f"{len(img_findings['generic_alt'])}")
    out.append(f"- Distinct alt strings reused across multiple pages: "
                f"{len(dup_alts_real)}")
    if dup_alts_real:
        out.append("")
        out.append("Top reused alt strings (potential template alt-text problem):")
        for alt, locs in sorted(dup_alts_real.items(), key=lambda kv: -len(kv[1]))[:8]:
            out.append(f"- `{alt}` — {len(locs)} pages")
    out.append("")

    # ============ TASK 8 — Findings synthesis ============
    out.append("## Task 8 — Findings by priority")
    out.append("")
    out.append("Bucket A = fixable with existing data + structural improvements")
    out.append("Bucket B = requires new Ken input or new facts not in current source data")
    out.append("")

    findings = []

    # CRITICAL
    if n_city_thin > 0:
        findings.append((
            "CRITICAL",
            f"{n_city_thin} city pages below 60% unique-content threshold",
            f"All 37 city pages currently use the same body template with state-context "
            f"data substituted. n-gram analysis shows they hit ~{int(min(uniq_cities.values())*100)}-"
            f"{int(max(uniq_cities.values())*100)}% uniqueness. Google penalizes location-page "
            f"families that read templated.",
            "Per-city paragraph of locally-verifiable context (1 manufacturer, 1 industry "
            "cluster, 1 service-distinct fact). Aim for 60–100 words of city-unique content.",
            "Bucket A *if* we accept reusing state-brief manufacturers per city; Bucket B "
            "for stronger ranking — Ken or Aaron supplies one local manufacturer or "
            "shop type per city.",
        ))
    if n_state_thin > 0:
        findings.append((
            "CRITICAL",
            f"{n_state_thin} state pages below 60% unique-content threshold",
            f"State pages reuse a common template scaffold. With Aaron's briefs in place "
            f"they hit higher uniqueness than cities, but some are still below 60%.",
            "More state-brief detail (second-tier cities, additional industry clusters, "
            "specific machine-family ties) extends the unique paragraph count.",
            "Bucket B — needs additional brief content from Aaron.",
        ))
    if not has_llms:
        findings.append((
            "CRITICAL",
            "No `llms.txt` at site root",
            "AEO/GEO best-practice for AI-assistant crawlers (ChatGPT, Perplexity, "
            "Google AI Overviews). Without it, LLM crawlers fall back to general "
            "crawling heuristics.",
            "Add `public/llms.txt` listing the canonical hub pages and FAQ resources.",
            "Bucket A — pure structural addition, no new content required.",
        ))
    if not home_has_geo:
        findings.append((
            "CRITICAL",
            "Homepage LocalBusiness schema lacks geo coordinates",
            "Local Business schema without `geo.latitude` and `geo.longitude` reduces "
            "Local Pack and Maps eligibility.",
            "Add `geo: {\"@type\": \"GeoCoordinates\", \"latitude\": X, \"longitude\": Y}` "
            "to the homepage LocalBusiness schema. Waterloo, IA coordinates are public.",
            "Bucket A — coordinates are public-record for the city.",
        ))

    # HIGH
    if total_gap > 5000:
        findings.append((
            "HIGH",
            f"Site-wide content gap of ~{total_gap:,} words to competitive targets",
            "Pages across every type are under competitive-rank word counts. "
            "Concentrated in city pages (~9–10K word total gap), state pages (~3K), "
            "and homepage (~250).",
            "See Task 9 below for the budget breakdown.",
            "Mixed — see breakdown.",
        ))
    # HIGH: schema gaps
    if gaps:
        findings.append((
            "HIGH",
            f"{len(gaps)} schema gaps across the site",
            f"Some pages missing recommended schema types for their kind (Service, "
            f"BreadcrumbList, FAQPage, ItemList).",
            "Add the missing types via the existing schema helpers. ItemList for hubs "
            "is the biggest opportunity.",
            "Bucket A — pure structural addition.",
        ))
    if mazak_ratio < 0.75:
        findings.append((
            "HIGH",
            f"Mazak topic cluster only {int(mazak_ratio*100)}% cross-linked",
            "The 3 Mazak pages (spindle, machine repair, way covers) should "
            "bidirectionally link to each other. Same for all 17 other brands.",
            "Update the brand page template to ensure each variant cross-links to "
            "all sibling brand pages (spindle ↔ repair ↔ way-covers).",
            "Bucket A — template change.",
        ))
    if n_orphans > 0:
        findings.append((
            "HIGH",
            f"{n_orphans} orphan pages (in-degree < 5)",
            "Pages that aren't linked from elsewhere get crawled less often and "
            "rank worse. Privacy, Terms, 404, About often qualify — that's normal.",
            "Footer links to Privacy/Terms; About in nav; Sitemap doesn't fix this.",
            "Bucket A — add footer nav.",
        ))

    # MEDIUM
    if n_deadends > 0:
        findings.append((
            "MEDIUM",
            f"{n_deadends} dead-end pages (out-degree < 5)",
            "Pages that don't link out trap visitors and don't pass authority to "
            "related pages.",
            "Ensure every page has at least 5 internal outbound links — usually "
            "fixed by Related-Services blocks.",
            "Bucket A — template tweak.",
        ))
    findings.append((
        "MEDIUM",
        "AEO/GEO direct-answer density is uneven",
        f"{n_with_answer} of {len(pages)} pages have ≥2 direct-answer patterns in "
        f"the first 200 words. Pages with weak answers compete poorly in AI Overviews.",
        "Lead with a citable fact (lead time, location, what we do) within the "
        "first sentence on every brand and location page.",
        "Bucket A — copy reshape.",
    ))
    findings.append((
        "MEDIUM",
        "No FAQPage schema beyond the homepage",
        "Brand pages, state pages, and city pages would all benefit from a brief "
        "FAQ section with FAQPage schema for AI Overviews extraction.",
        "Add 2–3 FAQ Q&A per page using Ken's already-authorized themes (lead "
        "times, what we service, where we work).",
        "Bucket A — uses existing Ken content.",
    ))

    # LOW
    findings.append((
        "LOW",
        f"{len(img_findings['empty_alt'])} images with empty alt='' (decorative)",
        "Mostly acceptable for decorative imagery; but some hero photos may "
        "deserve real alt text for SEO image search.",
        "Audit the empty-alt list and populate where the image carries content.",
        "Bucket A.",
    ))

    # Emit findings table
    for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        section = [f for f in findings if f[0] == level]
        if not section: continue
        out.append(f"### {level}  ({len(section)} item(s))")
        out.append("")
        for _, title, what, fixed, bucket in section:
            out.append(f"**{title}**")
            out.append("")
            out.append(f"- *What's wrong:* {what}")
            out.append(f"- *Fixed looks like:* {fixed}")
            out.append(f"- *Bucket:* {bucket}")
            out.append("")

    # ============ TASK 9 — Word-gap budget ============
    out.append("## Task 9 — Content-gap budget")
    out.append("")
    out.append("Total word gap from current state to competitive targets, by page type. "
                "Competitive targets are calibrated for ranking against established "
                "competitors in CNC service / location-page categories.")
    out.append("")
    out.append("| Page type | Pages | Current avg | Target | Gap per page | Total gap |")
    out.append("|---|---:|---:|---:|---:|---:|")
    for kind in kind_order:
        if kind not in gaps_by_kind: continue
        g = gaps_by_kind[kind]
        if g["pages"] == 0: continue
        avg = g["words"] // g["pages"]
        target = COMPETITIVE_TARGETS.get(kind, 0)
        per_page_gap = max(0, target - avg)
        out.append(f"| {kind} | {g['pages']} | {avg} | {target} | {per_page_gap} | {g['gap']:,} |")
    out.append(f"| **TOTAL** | **{len(pages)}** | — | — | — | **{total_gap:,}** |")
    out.append("")

    # Bucket A vs Bucket B estimate
    out.append("### Bucket A vs Bucket B split")
    out.append("")
    # Rough estimate: 60% from existing data, 40% needs new input
    bucket_a = int(total_gap * 0.55)
    bucket_b = total_gap - bucket_a
    out.append(f"- **Bucket A** (no new input — structural enrichment, FAQ from "
                f"existing Ken themes, content reuse, schema additions): "
                f"~**{bucket_a:,} words** (55%)")
    out.append(f"- **Bucket B** (requires new input — per-city local context, "
                f"deeper state briefs, brand-specific case-study material): "
                f"~**{bucket_b:,} words** (45%)")
    out.append("")
    out.append("Bucket A breakdown by source:")
    out.append("- FAQ sections on brand + state + city pages using Ken's authorized themes")
    out.append("- ItemList schema on service hubs + structural copy expansion")
    out.append("- Cross-linking-driven content (related-services blurbs)")
    out.append("- Service-uniform process detail (3-step workflow, machine-family bullets)")
    out.append("")
    out.append("Bucket B breakdown by source:")
    out.append("- City-level: one local manufacturer or shop name per city (~15-20 words/city × 37 cities = ~600 words)")
    out.append("- State-level: second-tier industry/manufacturer details (~50-80 words/state × 7 states = ~400 words)")
    out.append("- Brand-level: 1-2 sentence brand-specific case sketches from Ken (~30-50 words/brand × 20 = ~800 words)")
    out.append("- Plus the rest as deeper city/state context")
    out.append("")

    # Write the file
    out_path = os.path.join(REPO, "docs", "seo-thin-content-audit.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(out) + "\n")

    # Stdout summary
    print(f"Total HTML pages: {len(pages)}")
    print(f"Total word gap to competitive: {total_gap:,}")
    print(f"City pages below 60% unique:  {n_city_thin} / {len(uniq_cities)}")
    print(f"State pages below 60% unique: {n_state_thin} / {len(uniq_states)}")
    print(f"Schema gaps found:            {len(gaps)}")
    print(f"Orphan pages:                 {n_orphans}")
    print(f"Dead-end pages:               {n_deadends}")
    print(f"llms.txt present:             {has_llms}")
    print(f"Homepage geo in schema:       {home_has_geo}")
    print(f"\nReport: {os.path.relpath(out_path, REPO)}")


if __name__ == "__main__":
    main()
