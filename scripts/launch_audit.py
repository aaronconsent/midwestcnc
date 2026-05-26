#!/usr/bin/env python3
"""
Launch-readiness hygiene audit. Runs nine checks across the public/
tree and writes docs/launch-readiness.md.

Checks:
  a) Internal link audit (uses generate_site_shell logic)
  b) Total HTML files
  c) Sitemap URL count vs HTML count
  d) Claim-audit ban-list scan
  e) Schema validation (BreadcrumbList, LocalBusiness, FAQPage, Service)
  f) Image alt-text audit
  g) Viewport meta-tag presence
  h) Cross-page nav consistency
  i) Total asset size
"""

import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_site_shell as gss

REPO = gss.REPO
PUBLIC = gss.PUBLIC


def all_html_files():
    out = []
    for root, dirs, files in os.walk(PUBLIC):
        for f in files:
            if f.endswith(".html"):
                out.append(os.path.join(root, f))
    return sorted(out)


def relpath(p):
    return os.path.relpath(p, REPO)


# ---------- a) Link audit (delegate to existing tool) ----------

def link_audit():
    return gss.link_audit()


# ---------- b/c) HTML and sitemap counts ----------

def sitemap_urls():
    sm = os.path.join(PUBLIC, "sitemap.xml")
    if not os.path.exists(sm):
        return []
    src = open(sm).read()
    return re.findall(r'<loc>([^<]+)</loc>', src)


# ---------- d) Ban-list scan ----------

BAN_PATTERNS = [
    "24/7",
    "same-day",
    "flat-rate",
    "flat rate",
    "transparent quote",
    "transparent pricing",
    "sub-micron",
    "submicron",
    "photo-verified",
    "documented process",
    "video updates",
    "certified tech",
    "factory-authorized",
    "OEM-certified",
    "ISO 9",
    "AS9100",
    "five decades",
    "50+ Years",
    "industry-leading",
    "world-class",
    "warranty",
    "lifetime",
]

# Aaron-authorized exceptions
AUTHORIZED_EXCEPTIONS = {
    # Iowa state page uses Aaron's authorized "Same-day field response is
    # realistic" wording from the state-brief.
    "same-day": {"public/service-area/iowa/index.html"},
    # The Terms of Service contains the word "warranty" in legal-disclaimer
    # context ("warranties are governed by the service agreement signed
    # for each job, not by anything stated on this Site") — explicitly
    # disclaiming, not making, warranty claims.
    "warranty": {"public/terms-of-service/index.html"},
}


def ban_list_scan(html_files):
    findings = []
    for f in html_files:
        text = open(f).read()
        for pat in BAN_PATTERNS:
            if re.search(re.escape(pat), text, flags=re.I):
                rp = relpath(f)
                authorized = (
                    pat.lower() in AUTHORIZED_EXCEPTIONS
                    and rp in AUTHORIZED_EXCEPTIONS[pat.lower()]
                )
                findings.append((pat, rp, authorized))
    return findings


# ---------- e) Schema validation ----------

def extract_jsonld(html_src):
    out = []
    for m in re.finditer(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
        html_src, re.S
    ):
        try:
            out.append(json.loads(m.group(1)))
        except Exception as e:
            out.append({"_parse_error": str(e), "raw": m.group(1)[:200]})
    return out


def schema_audit(html_files):
    """Verify each page has the schema types we expect for its kind."""
    rules = {
        "homepage":    ("public/index.html", {"LocalBusiness", "FAQPage"}),
        "hubs":        ({"public/repairs/index.html",
                          "public/spindle-grinding/index.html",
                          "public/way-covers/index.html",
                          "public/service-area/index.html"}, {"BreadcrumbList", "Service"}),
        "brand":       ("brand pages", {"BreadcrumbList", "Service", "LocalBusiness"}),
    }
    issues = []
    breadcrumb_ok = 0
    breadcrumb_missing = []

    for f in html_files:
        rp = relpath(f)
        if rp == "public/404.html":
            continue
        src = open(f).read()
        schemas = extract_jsonld(src)
        types = set()
        for s in schemas:
            if isinstance(s, dict):
                t = s.get("@type")
                if t:
                    types.add(t)

        # Universal: BreadcrumbList on every non-homepage, non-404 page
        if rp == "public/index.html":
            # Homepage skips breadcrumb — that's intentional
            if "LocalBusiness" not in types:
                issues.append(f"Homepage missing LocalBusiness schema ({rp})")
            if "FAQPage" not in types:
                issues.append(f"Homepage missing FAQPage schema ({rp})")
        else:
            if "BreadcrumbList" in types:
                breadcrumb_ok += 1
            else:
                breadcrumb_missing.append(rp)

        # Brand pages — should have Service + LocalBusiness reference
        if (rp.startswith("public/spindle-grinding/")
                and "spindle-repair" in rp
                and rp != "public/spindle-grinding/index.html") \
                or (rp.startswith("public/repairs/")
                    and rp != "public/repairs/index.html") \
                or (rp.startswith("public/way-covers/")
                    and "way-covers" in rp
                    and rp != "public/way-covers/index.html"):
            if "Service" not in types:
                issues.append(f"Brand page missing Service schema ({rp})")
            if "LocalBusiness" not in types:
                issues.append(f"Brand page missing LocalBusiness schema ({rp})")

    return {
        "issues": issues,
        "breadcrumb_ok": breadcrumb_ok,
        "breadcrumb_missing": breadcrumb_missing,
    }


# ---------- f) Image alt-text ----------

def image_alt_audit(html_files):
    missing = []
    empty = []
    for f in html_files:
        rp = relpath(f)
        src = open(f).read()
        for m in re.finditer(r'<img\b[^>]*>', src):
            tag = m.group(0)
            alt_match = re.search(r'\balt="([^"]*)"', tag)
            if alt_match is None:
                missing.append((rp, tag[:120]))
            elif alt_match.group(1).strip() == "":
                empty.append((rp, tag[:120]))
    return missing, empty


# ---------- g) Viewport meta-tag ----------

VIEWPORT_RE = re.compile(
    r'<meta\s+name="viewport"\s+content="width=device-width,\s*initial-scale=1"',
    re.I,
)


def viewport_audit(html_files):
    missing = []
    for f in html_files:
        src = open(f).read()
        if not VIEWPORT_RE.search(src):
            missing.append(relpath(f))
    return missing


# ---------- h) Nav consistency ----------

NAV_RE = re.compile(r'<header class="site-header">(.*?)</header>', re.S)


def nav_consistency(html_files):
    """Hash every page's site-header content; report if not unanimous."""
    seen = {}
    for f in html_files:
        src = open(f).read()
        m = NAV_RE.search(src)
        if not m:
            seen.setdefault("_no_header_", []).append(relpath(f))
            continue
        # Normalize whitespace before hashing
        nav = re.sub(r'\s+', ' ', m.group(1)).strip()
        h = hashlib.sha256(nav.encode()).hexdigest()[:12]
        seen.setdefault(h, []).append(relpath(f))
    return seen


# ---------- i) Asset size ----------

def asset_size():
    assets = os.path.join(REPO, "assets")
    total_bytes = 0
    n_files = 0
    by_dir = {}
    if not os.path.exists(assets):
        return 0, 0, {}
    for root, dirs, files in os.walk(assets):
        for f in files:
            p = os.path.join(root, f)
            sz = os.path.getsize(p)
            total_bytes += sz
            n_files += 1
            rel = os.path.relpath(root, assets)
            by_dir[rel] = by_dir.get(rel, 0) + sz
    return total_bytes, n_files, by_dir


def fmt_bytes(n):
    if n > 1024 * 1024:
        return f"{n / (1024*1024):.1f} MB"
    if n > 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} B"


# ---------- Driver ----------

def main():
    html_files = all_html_files()
    print(f"Auditing {len(html_files)} HTML files…\n")

    # a) Link audit
    audit = link_audit()
    n_broken = sum(len(v) for v in audit["broken_by_source"].values())

    # b/c) Sitemap vs HTML
    urls = sitemap_urls()
    n_sitemap = len(urls)
    drafts_excluded = (
        len(html_files)
        - 1  # 404
        - n_sitemap
    )

    # d) Ban-list
    findings = ban_list_scan(html_files)
    authorized = [x for x in findings if x[2]]
    unauthorized = [x for x in findings if not x[2]]

    # e) Schema
    sch = schema_audit(html_files)

    # f) Images
    missing_alt, empty_alt = image_alt_audit(html_files)

    # g) Viewport
    no_viewport = viewport_audit(html_files)

    # h) Nav consistency
    nav_groups = nav_consistency(html_files)
    distinct_navs = len(nav_groups)

    # i) Assets
    total_bytes, n_assets, by_dir = asset_size()

    # ---------- Compose report ----------
    lines = ["# Launch Readiness Audit\n",
             f"Audited **{len(html_files)} HTML files** under `public/` plus "
             f"the `assets/` tree. Run this any time before deploy to catch "
             f"regressions.\n",
             "## Summary",
             "",
             f"- Total HTML files in `public/`: **{len(html_files)}**",
             f"- Sitemap URLs:                  **{n_sitemap}**",
             f"  ({drafts_excluded} expected exclusions: 404 page + draft way-cover pages)",
             f"- Internal links scanned:         **{audit['total']}**",
             f"- Broken internal links:          **{n_broken}**",
             f"- Ban-list findings:              **{len(unauthorized)}** unauthorized, "
             f"**{len(authorized)}** Aaron-authorized exceptions",
             f"- Schema issues:                  **{len(sch['issues'])}**",
             f"- Pages missing breadcrumb:       **{len(sch['breadcrumb_missing'])}** "
             f"(homepage and 404 are expected here)",
             f"- Images missing `alt`:           **{len(missing_alt)}**",
             f"- Images with empty `alt`:        **{len(empty_alt)}** "
             f"(decorative — generally acceptable)",
             f"- Pages without viewport meta:    **{len(no_viewport)}**",
             f"- Distinct `<header>` markups:    **{distinct_navs}** "
             f"(want 1 if nav is template-consistent)",
             f"- Total asset size:               **{fmt_bytes(total_bytes)}** "
             f"across {n_assets} files",
             ""]

    # Verdict
    blockers = []
    if n_broken: blockers.append(f"{n_broken} broken internal links")
    if unauthorized: blockers.append(f"{len(unauthorized)} unauthorized claim-audit hits")
    if sch["issues"]: blockers.append(f"{len(sch['issues'])} schema gaps")
    if missing_alt: blockers.append(f"{len(missing_alt)} images missing alt attribute")
    if no_viewport: blockers.append(f"{len(no_viewport)} pages missing viewport meta")
    if distinct_navs > 1: blockers.append(f"navigation drift ({distinct_navs} distinct headers)")

    if not blockers:
        lines.append("## Verdict\n\n**READY TO DEPLOY.** No blockers found.\n")
    else:
        lines.append("## Verdict\n\n**Blockers:**\n")
        for b in blockers:
            lines.append(f"- {b}")
        lines.append("")

    # Detail sections
    lines.append("## a) Link audit\n")
    lines.append(f"- Total `<a href>` scanned: {audit['total']}")
    lines.append(f"- Resolved to file:        {audit['ok']}")
    lines.append(f"- Resolved via redirect:   {audit['redirect']}")
    lines.append(f"- External (skipped):      {audit['external']}")
    lines.append(f"- Non-http skipped:        {audit['skip']}")
    lines.append(f"- **Broken:**              **{n_broken}**")
    if n_broken:
        lines.append("\nBroken targets:")
        for src_file, hrefs in sorted(audit["broken_by_source"].items()):
            for href, text in hrefs:
                lines.append(f"- `{href}` from `{src_file}`")
    lines.append("")

    lines.append("## d) Claim-audit ban-list scan\n")
    if not findings:
        lines.append("Clean across all pages. 🎉\n")
    else:
        if authorized:
            lines.append("**Aaron-authorized exceptions** (documented in `docs/claim-audit.md`):")
            for pat, path, _ in authorized:
                lines.append(f"- `{pat}` in `{path}` — authorized")
            lines.append("")
        if unauthorized:
            lines.append("**Unauthorized hits — must fix before deploy:**")
            for pat, path, _ in unauthorized:
                lines.append(f"- `{pat}` in `{path}`")
            lines.append("")

    lines.append("## e) Schema validation\n")
    lines.append(f"- Pages with BreadcrumbList: {sch['breadcrumb_ok']} / "
                 f"{len(html_files) - 2} (excluding homepage and 404)")
    if sch["breadcrumb_missing"]:
        lines.append(f"- Unexpected missing breadcrumb:")
        for p in sch["breadcrumb_missing"]:
            lines.append(f"  - `{p}`")
    if sch["issues"]:
        lines.append(f"\n**Schema issues:**")
        for issue in sch["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append(f"- No structural schema issues found.")
    lines.append("")

    lines.append("## f) Image alt-text audit\n")
    if not missing_alt and not empty_alt:
        lines.append("Every `<img>` has a populated `alt` attribute. 🎉\n")
    else:
        if missing_alt:
            lines.append(f"**`<img>` tags missing the `alt` attribute entirely** "
                         f"({len(missing_alt)}):")
            for path, tag in missing_alt[:25]:
                lines.append(f"- `{path}` — `{tag}`")
            if len(missing_alt) > 25:
                lines.append(f"- *…and {len(missing_alt) - 25} more*")
            lines.append("")
        if empty_alt:
            lines.append(f"**`<img>` tags with empty `alt=\"\"`** ({len(empty_alt)}) — "
                         f"acceptable for decorative imagery; flag if any should "
                         f"actually describe content:")
            # Only list a few
            for path, tag in empty_alt[:10]:
                lines.append(f"- `{path}` — `{tag}`")
            if len(empty_alt) > 10:
                lines.append(f"- *…and {len(empty_alt) - 10} more*")
            lines.append("")

    lines.append("## g) Viewport meta-tag\n")
    if not no_viewport:
        lines.append("Every page has `<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">`. 🎉\n")
    else:
        lines.append(f"**{len(no_viewport)} pages missing viewport meta:**")
        for p in no_viewport:
            lines.append(f"- `{p}`")
        lines.append("")

    lines.append("## h) Cross-page nav consistency\n")
    if distinct_navs == 1:
        lines.append("All pages share an identical `<header>` markup. 🎉\n")
    else:
        lines.append(f"**{distinct_navs} distinct `<header>` markups detected.** "
                     f"Want 1 — if more, the template has drifted somewhere:")
        for h, pages in sorted(nav_groups.items(), key=lambda kv: -len(kv[1])):
            lines.append(f"- `{h}` — {len(pages)} pages")
            for p in pages[:3]:
                lines.append(f"  - `{p}`")
            if len(pages) > 3:
                lines.append(f"  - *…and {len(pages) - 3} more*")
        lines.append("")

    lines.append("## i) Asset directory size\n")
    lines.append(f"- Total: **{fmt_bytes(total_bytes)}** across {n_assets} files\n")
    lines.append("Breakdown by subdirectory:\n")
    lines.append("| Subdirectory | Bytes | Pretty |")
    lines.append("|---|---:|---:|")
    for rel, sz in sorted(by_dir.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{rel}` | {sz:,} | {fmt_bytes(sz)} |")
    lines.append("")

    lines.append("## b/c) Sitemap composition\n")
    lines.append(f"- Total `<loc>` entries: {n_sitemap}")
    lines.append(f"- HTML files in `public/`: {len(html_files)}")
    lines.append(f"- Difference: {len(html_files) - n_sitemap} "
                 f"(404 page + drafts — expected)\n")

    # Write report
    out_path = os.path.join(REPO, "docs", "launch-readiness.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    # Print summary to stdout
    print(f"HTML files:          {len(html_files)}")
    print(f"Sitemap URLs:        {n_sitemap}")
    print(f"Broken links:        {n_broken}")
    print(f"Ban-list hits:       {len(unauthorized)} unauthorized, {len(authorized)} authorized")
    print(f"Schema issues:       {len(sch['issues'])}")
    print(f"Missing alt:         {len(missing_alt)}")
    print(f"Empty alt:           {len(empty_alt)}")
    print(f"Missing viewport:    {len(no_viewport)}")
    print(f"Distinct nav:        {distinct_navs}")
    print(f"Asset size:          {fmt_bytes(total_bytes)} ({n_assets} files)")
    print(f"\nReport: {os.path.relpath(out_path, REPO)}")

    if blockers:
        print(f"\nBlockers: {blockers}")
    else:
        print(f"\nVERDICT: READY TO DEPLOY")


if __name__ == "__main__":
    main()
