#!/usr/bin/env python3
"""
Brand page generator for /spindle-grinding/*.

Reads src/data/spindle-brands.json (with Ken's confirmed content) and writes
one Markdown file per brand to src/content/spindle-brands/{slug}.md.

Discipline:
- Ken's exact sentences are the substance. Connective tissue is minimal.
- No claims that aren't traceable to ken_input or global_context (no
  "flat-rate pricing", "photo-verified", or specific certifications that
  Ken didn't mention).
- "bearing pack" wording is preferred over "front bearing wear" in our
  connective tissue only — Ken's own quotes keep his wording intact.
- Page types diverge: cnc_spindle vs press_brake_service vs
  laser_punch_service get framing-appropriate language. Amada and Trumpf
  are NOT described as spindle work.
"""

import html
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "src", "data", "spindle-brands.json")
# Three content directories, one per service kind. Markdown files are
# written here; markdown_to_html.py picks them up and outputs to the
# canonical URL inside public/.
OUTDIR_SPINDLE = os.path.join(REPO, "src", "content", "spindle-brands")
OUTDIR_REPAIR  = os.path.join(REPO, "src", "content", "machine-repair")
OUTDIR_COVERS  = os.path.join(REPO, "src", "content", "way-covers")

PHONE_DISPLAY = "319-610-4341"
PHONE_TEL = "+13196104341"
STATES = ["Iowa", "Illinois", "Minnesota", "Wisconsin", "Nebraska", "Missouri", "Texas"]


# ---------- Helpers ----------

def clean_ken(text):
    """Strip worksheet conversational artifacts from Ken's answers."""
    text = (text or "").strip()
    for prefix in ("Confirmed. ", "Confirmed.", "Confirmed "):
        if text.startswith(prefix):
            return text[len(prefix):].lstrip()
    return text


def ensure_period(s):
    s = (s or "").rstrip()
    if not s:
        return s
    return s if s[-1] in ".!?" else s + "."


def lead_short(lt):
    """Pull the 'N–M weeks' fragment out of Ken's lead-time answer."""
    if not lt:
        return ""
    m = re.search(r"\d+\s*[–—\-]\s*\d+\s*weeks?", lt)
    if m:
        return re.sub(r"\s*[–—\-]\s*", "–", m.group(0))
    # fallback: first clause
    return lt.split(".")[0].strip()


def yaml_string(s):
    """Quote a string for YAML, escaping internal double quotes."""
    s = (s or "").replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


# ---------- Brand-specific framing toggles ----------

# Brands whose ken_input.brand_specifics describes the work as
# standard/straightforward rather than brand-specifically complex. These
# get the "mainstream" "How We Approach" framing instead of the default
# "brand-specific factors drive how we plan the job" lead-in.
MAINSTREAM_BRANDS = {"fanuc", "hurco", "doosan", "amera-seiki"}

# When a brand's common_failure_mode starts with one of these words, it's
# a bare noun phrase that reads awkwardly after "What we see most on
# {Brand} spindles:". For these we use the alternative hero structure
# "{Brand} spindles tend to come in with {lowercased quote}".
NOUN_PHRASE_OPENERS = {
    "bearing", "front", "classic", "large", "heavy",
    "high", "high-speed", "motor", "pulley", "mostly",
    "optics",
}

# Page-type → machine-noun used in the noun-phrase hero variant.
MACHINE_NOUN = {
    "cnc_spindle":         "spindles",
    "press_brake_service": "machines",
    "laser_punch_service": "systems",
}

# Customer-quote framing — rotates per brand (alphabetical by slug). Both
# variants are appended *after* Ken's static opener inside the same
# blockquote, so every page still leads with his "machine was done for"
# line and only the framing changes.
QUOTE_OPENER = '"Honestly, we thought the machine was done for."'


def customer_quote_framing(brand_index, equipment_phrase):
    """Return the rotating framing sentence that follows QUOTE_OPENER.
    equipment_phrase varies by service kind (e.g. 'a new spindle',
    'a replacement machine', 'replacement way covers and the retrofit time')."""
    if brand_index % 2 == 0:
        return ("Most customers tell us they're relieved to avoid replacement "
                "lead times and six-figure capital expenses.")
    return (f"It saves shops from replacement lead times and the capital "
            f"expense of {equipment_phrase}.")


def hero_image_for(brand, service_kind):
    """Pick a hero image for a brand × service combination.
    service_kind: 'spindle', 'machine_repair', or 'way_covers'.
    Returns (path, alt) or (None, None) if nothing fits.
    """
    slug = brand["slug"]
    name = brand["brand_display_name"]

    if service_kind == "spindle":
        candidates = [
            (f"/assets/images/services/spindles-repair-{slug}-spindle-repair-image.png",
             f"{name} spindle on the rebuild bench at Midwest CNC Services"),
            (f"/assets/images/services/repairs-{slug}-cnc-machine-repair-image.png",
             f"{name} machine service work at Midwest CNC Services"),
        ]
        generic = ("/assets/images/general/image-of-spindle-grinding.png",
                   "CNC spindle grinding work at Midwest CNC Services")
    elif service_kind == "machine_repair":
        candidates = [
            (f"/assets/images/services/repairs-{slug}-cnc-machine-repair-image.png",
             f"{name} CNC machining center being serviced at Midwest CNC Services"),
            (f"/assets/images/services/spindles-repair-{slug}-spindle-repair-image.png",
             f"{name} machine service work at Midwest CNC Services"),
        ]
        generic = ("/assets/images/general/image-of-cnc-machine.png",
                   "CNC machine service work at Midwest CNC Services")
    elif service_kind == "way_covers":
        candidates = [
            (f"/assets/images/services/way-covers-{slug}-cnc-way-covers-image.png",
             f"Replacement {name} CNC way covers manufactured by Midwest CNC Services"),
        ]
        generic = ("/assets/images/general/image-of-way-covers.png",
                   "CNC way cover manufacturing at Midwest CNC Services")
    else:
        return None, None

    for path, alt in candidates:
        if os.path.exists(os.path.join(REPO, path.lstrip("/"))):
            return path, alt
    if os.path.exists(os.path.join(REPO, generic[0].lstrip("/"))):
        return generic
    return None, None


# ---------- Peer linking ----------

PEERS = {
    "mazak":          ["okuma", "dmg-mori", "mori-seiki"],
    "haas":           ["doosan", "hurco", "fadal"],
    "okuma":          ["mazak", "dmg-mori", "mori-seiki"],
    "dmg-mori":       ["mazak", "mori-seiki", "makino"],
    "mori-seiki":     ["dmg-mori", "mazak", "okuma"],
    "doosan":         ["haas", "hurco", "amera-seiki"],
    "brother":        ["makino", "fanuc", "hurco"],
    "hurco":          ["haas", "doosan", "brother"],
    "makino":         ["mazak", "dmg-mori", "brother"],
    "fanuc":          ["brother", "hurco", "makino"],
    "toyoda":         ["mazak", "dmg-mori", "niigata"],
    "fadal":          ["haas", "hurco", "monarch"],
    "hitachi-seiki":  ["mori-seiki", "mazak", "fadal"],
    "giddings-lewis": ["toyoda", "niigata", "makino"],
    "monarch":        ["fadal", "hitachi-seiki", "mazak"],
    "amera-seiki":    ["doosan", "johnford", "hurco"],
    "niigata":        ["makino", "toyoda", "mazak"],
    "johnford":       ["amera-seiki", "doosan", "hurco"],
}


def peer_lines(slug, brands_by_slug):
    peers = PEERS.get(slug, [])
    out = []
    for p in peers:
        n = brands_by_slug[p]["brand_display_name"]
        out.append(f"  - [{n} spindle grinding](/spindle-grinding/{p}-spindle-repair/)")
    return out


# ---------- Front matter ----------

def front_matter(brand, *, title, h1, meta_description,
                 service_type, canonical_path,
                 crumb_middle, crumb_leaf,
                 draft=False, verification_pending=None):
    """Build a page's YAML front matter. Each render function owns its
    own title, canonical, breadcrumb, and draft state — front_matter just
    formats them consistently."""
    slug = brand["slug"]
    lines = [
        "---",
        f"title: {yaml_string(title)}",
        f"meta_description: {yaml_string(meta_description)}",
        f"h1: {yaml_string(h1)}",
        f"slug: {yaml_string(slug)}",
        f"page_type: {yaml_string(brand['page_type'])}",
    ]
    if draft:
        lines.append("draft: true")
    if verification_pending:
        lines.append(f"verification_pending: {yaml_string(verification_pending)}")
    lines += [
        "schema_data:",
        "  service:",
        "    \"@type\": Service",
        f"    serviceType: {yaml_string(service_type)}",
        "    provider:",
        "      \"@id\": \"#org\"",
        "    areaServed:",
    ]
    for s in STATES:
        lines.append(f"      - {s}")
    lines += [
        "  local_business:",
        "    \"@type\": LocalBusiness",
        "    \"@id\": \"#org\"",
        f"    name: {yaml_string('Midwest CNC Services')}",
        f"    telephone: {yaml_string(PHONE_TEL)}",
        "    # address, geo, openingHours filled in by template at build time",
        "  breadcrumb:",
        "    \"@type\": BreadcrumbList",
        "    itemListElement:",
        f"      - {{ position: 1, name: Home, item: {yaml_string(absolute_url('/'))} }}",
        f"      - {{ position: 2, name: {yaml_string(crumb_middle[0])}, item: {yaml_string(absolute_url(crumb_middle[1]))} }}",
        f"      - {{ position: 3, name: {yaml_string(crumb_leaf)}, item: {yaml_string(absolute_url(canonical_path))} }}",
        "---",
        "",
    ]
    return "\n".join(lines)


CANONICAL_DOMAIN = "https://midwestcncservices.com"


def absolute_url(path):
    """Prefix an internal path with the canonical domain (for schema)."""
    if not path:
        return path
    if path.startswith(("http://", "https://")):
        return path
    return f"{CANONICAL_DOMAIN}{path}"


def make_h1_and_eyebrow(brand):
    """Per-brand H1 + eyebrow. The eyebrow is the service category
    (matching breadcrumb-style taxonomy); the H1 is the SEO-targeted
    brand+service phrase. Amada and Trumpf have no eyebrow — their H1 IS
    the service category, so a duplicated eyebrow would add nothing."""
    name = brand["brand_display_name"]
    pt = brand["page_type"]
    if pt == "press_brake_service":
        return ("Amada Press Brake & Punch Service", None)
    if pt == "laser_punch_service":
        return ("Trumpf Laser & Punch Service", None)
    # cnc_spindle — longer brand names drop the "& Rebuilds" suffix to keep
    # the H1 readable.
    if len(name) > 11:
        h1 = f"{name} Spindle Repair"
    else:
        h1 = f"{name} Spindle Repair & Rebuilds"
    return (h1, f"{name} Spindle Repair & Grinding")


def _alt_title(brand):
    if brand["slug"] == "amada":
        return "Amada Press Brake & Punch Service | Midwest CNC Services"
    if brand["slug"] == "trumpf":
        return "Trumpf Laser & Punch Service | Midwest CNC Services"
    return f"{brand['brand_display_name']} Service | Midwest CNC Services"


def _alt_breadcrumb(brand):
    if brand["slug"] == "amada":
        return "Amada Press Brake & Punch Service"
    if brand["slug"] == "trumpf":
        return "Trumpf Laser & Punch Service"
    return f"{brand['brand_display_name']} Service"


# ---------- CTAs and shared blocks ----------

def hero_cta():
    return f"[Get a Quote](#quote) · [{PHONE_DISPLAY}](tel:{PHONE_TEL})"


def workflow_block(noun, step3_body):
    """noun: 'spindle rebuild', 'service', 'job' — what gets quoted."""
    return f"""**Step 1 — Contact Us.** Call 319-610-4341 or use the quote form below. [Get a Quote](#quote)

**Step 2 — Grab Model #.** We'll fire back price, lead time, and shipping ETA after reviewing your details. [Get a Quote](#quote)

**Step 3 — Approve & Rebuild.** {step3_body}

*Quote form rendered here at build time.*
"""


def trust_block(g, brand_page_type, brand_index, equipment_phrase):
    """Trim Ken's certifications to the brand's page type, then append
    the rotating customer-quote framing with a service-appropriate
    equipment_phrase (e.g. 'a new spindle', 'a replacement machine',
    'replacement way covers and the retrofit time')."""
    if brand_page_type == "cnc_spindle":
        certs = clean_ken(g["certifications"])
    elif brand_page_type == "press_brake_service":
        certs = ("Experienced field technicians and established relationships "
                 "with aftermarket parts suppliers.")
    elif brand_page_type == "laser_punch_service":
        certs = ("Experienced field technicians, laser alignment capability, "
                 "and experience navigating Trumpf's OEM parts network on "
                 "planned-downtime jobs.")
    else:
        certs = clean_ken(g["certifications"])

    framing = customer_quote_framing(brand_index, equipment_phrase)
    return f"""## Why Shops Trust Us

{certs}

> {QUOTE_OPENER} {framing}
"""


def _self_urls(brand):
    """URLs that resolve to the current page (for self-link filtering, fix 5)."""
    s = {brand.get("current_url")}
    if brand.get("old_url"):
        s.add(brand["old_url"])
    return {u for u in s if u}


def _can_link_way_covers(b):
    """Don't link to draft way-cover pages from anywhere else (SAFEGUARD)."""
    return (b.get("services_offered", {}).get("way_covers")
            and not b.get("way_covers_verification_pending"))


def related_block_cnc(brand, brands_by_slug):
    """Related Services on a brand's spindle page. TASK 5 restores the
    cross-service links (machine repair + way covers) gated on
    services_offered, and filters out any link pointing at the current
    page or a way-covers page still flagged for verification."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    self_urls = _self_urls(brand)
    so = brand.get("services_offered", {})

    # /spindles-repair/{slug}-spindle-repair/ is intentionally NOT listed —
    # it 301-redirects to this page (see public/_redirects).
    candidate_links = []
    if so.get("machine_repair"):
        candidate_links.append(
            (f"{name} CNC machine repair", f"/repairs/{slug}-cnc-machine-repair/")
        )
    if _can_link_way_covers(brand):
        candidate_links.append(
            (f"{name} CNC way covers", f"/way-covers/{slug}-cnc-way-covers/")
        )
    sibling_links = [(t, u) for (t, u) in candidate_links if u not in self_urls]

    peer_lis = []
    for p in PEERS.get(slug, []):
        n = brands_by_slug[p]["brand_display_name"]
        url = brands_by_slug[p].get("current_url", f"/spindle-grinding/{p}-spindle-repair/")
        if url in self_urls:
            continue
        peer_lis.append(f"  - [{n} spindle grinding]({url})")

    out = [f"## Related {name} Services\n"]
    for t, u in sibling_links:
        out.append(f"- [{t}]({u})")
    if peer_lis:
        out.append("- See also spindle grinding on related platforms:")
        out.extend(peer_lis)
    out.append("")
    out.append(
        "We serve shops across " + ", ".join(STATES[:-1]) + ", and " + STATES[-1] + "."
    )
    return "\n".join(out) + "\n"


def related_block_machine_repair(brand):
    """Related Services on a brand's machine-repair page. Self = the
    machine-repair canonical, NOT the brand's main current_url (the spindle
    page is a valid cross-link from here)."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    self_url = f"/repairs/{slug}-cnc-machine-repair/"
    so = brand.get("services_offered", {})

    lines = [f"## Related {name} Services\n"]
    if so.get("spindle"):
        url = f"/spindle-grinding/{slug}-spindle-repair/"
        if url != self_url:
            lines.append(f"- [{name} spindle repair]({url})")
    if _can_link_way_covers(brand):
        url = f"/way-covers/{slug}-cnc-way-covers/"
        if url != self_url:
            lines.append(f"- [{name} CNC way covers]({url})")
    lines.append("")
    lines.append(
        "We serve shops across " + ", ".join(STATES[:-1]) + ", and " + STATES[-1] + "."
    )
    return "\n".join(lines) + "\n"


def related_block_way_covers(brand):
    """Related Services on a brand's way-covers page. Self = the
    way-covers canonical. cnc_spindle brands cross-link to their spindle +
    machine-repair pages; Amada/Trumpf link back to their main service page."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    self_url = f"/way-covers/{slug}-cnc-way-covers/"
    so = brand.get("services_offered", {})

    lines = [f"## Related {name} Services\n"]
    if so.get("spindle"):
        url = f"/spindle-grinding/{slug}-spindle-repair/"
        if url != self_url:
            lines.append(f"- [{name} spindle repair]({url})")
    if so.get("machine_repair"):
        url = f"/repairs/{slug}-cnc-machine-repair/"
        if url != self_url:
            lines.append(f"- [{name} CNC machine repair]({url})")
    elif brand.get("current_url"):
        # Non-spindle brand (Amada/Trumpf): link back to the brand's main page
        main = brand["current_url"]
        if main != self_url:
            lines.append(f"- [{_alt_breadcrumb(brand)}]({main})")
    lines.append("")
    lines.append(
        "We serve shops across " + ", ".join(STATES[:-1]) + ", and " + STATES[-1] + "."
    )
    return "\n".join(lines) + "\n"


def related_block_alt(brand, brands_by_slug):
    """Related Services for Amada and Trumpf — link to each other plus the
    /repairs/ and /service-area/ hubs (fix 6). Filters self-links (fix 5)."""
    name = brand["brand_display_name"]
    self_urls = _self_urls(brand)

    # The "peer" non-spindle brand for cross-linking
    peer_slug = "trumpf" if brand["slug"] == "amada" else "amada"
    peer = brands_by_slug.get(peer_slug)

    lines = [f"## Related {name} Services\n"]
    if peer:
        peer_name = peer["brand_display_name"]
        peer_url = peer.get("current_url", "")
        if peer_url and peer_url not in self_urls:
            label = ("Trumpf laser & punch service"
                     if peer_slug == "trumpf"
                     else "Amada press brake & punch service")
            lines.append(f"- [{label}]({peer_url})")

    for label, url in (("All CNC repair services", "/repairs/"),
                       ("Service-area coverage", "/service-area/")):
        if url not in self_urls:
            lines.append(f"- [{label}]({url})")

    lines.append("")
    lines.append(
        f"We serve shops across {', '.join(STATES[:-1])}, and {STATES[-1]} "
        f"from our Waterloo, Iowa shop."
    )
    return "\n".join(lines) + "\n"


def blog_block():
    return """## Recent from the Blog

*Rendered by the blog teaser component at build time.*
"""


# ---------- Brand → regional emphasis (Phase 4 cross-links) ----------
# Maps each brand to 2–3 states + cities where the brand has the strongest
# presence per Aaron's state briefs + Ken's brand_specifics. Used for
# inline cross-links on brand pages.

BRAND_REGIONAL_EMPHASIS = {
    "mazak":          [("iowa", ["waterloo-iowa", "davenport-iowa"]),
                       ("illinois", ["peoria-illinois"]),
                       ("texas", ["fort-worth-texas"])],
    "haas":           [("wisconsin", ["milwaukee-wisconsin", "kenosha-wisconsin"]),
                       ("illinois", ["chicago-illinois", "naperville-illinois"]),
                       ("minnesota", ["minneapolis-minnesota"])],
    "okuma":          [("minnesota", ["minneapolis-minnesota", "rochester-minnesota"]),
                       ("illinois", ["rockford-illinois"]),
                       ("wisconsin", ["madison-wisconsin"])],
    "dmg-mori":       [("missouri", ["st-louis-missouri"]),
                       ("texas", ["fort-worth-texas"]),
                       ("illinois", ["rockford-illinois"])],
    "mori-seiki":     [("iowa", ["cedar-rapids-iowa"]),
                       ("illinois", ["rockford-illinois"]),
                       ("minnesota", ["minneapolis-minnesota"])],
    "doosan":         [("iowa", ["davenport-iowa", "waterloo-iowa"]),
                       ("illinois", ["peoria-illinois"]),
                       ("nebraska", ["lincoln-nebraska"])],
    "brother":        [("minnesota", ["rochester-minnesota", "minneapolis-minnesota"]),
                       ("wisconsin", ["madison-wisconsin"]),
                       ("texas", ["austin-texas"])],
    "hurco":          [("iowa", ["cedar-rapids-iowa", "ames-iowa"]),
                       ("illinois", ["naperville-illinois"]),
                       ("wisconsin", ["madison-wisconsin"])],
    "makino":         [("missouri", ["st-louis-missouri"]),
                       ("texas", ["fort-worth-texas"]),
                       ("minnesota", ["rochester-minnesota"])],
    "fanuc":          [("wisconsin", ["milwaukee-wisconsin"]),
                       ("illinois", ["rockford-illinois", "chicago-illinois"]),
                       ("texas", ["austin-texas"])],
    "toyoda":         [("iowa", ["davenport-iowa"]),
                       ("illinois", ["peoria-illinois"]),
                       ("texas", ["houston-texas"])],
    "fadal":          [("iowa", ["cedar-rapids-iowa"]),
                       ("illinois", ["rockford-illinois"]),
                       ("missouri", ["springfield-missouri"])],
    "hitachi-seiki":  [("illinois", ["rockford-illinois"]),
                       ("wisconsin", ["milwaukee-wisconsin"]),
                       ("missouri", ["kansas-city-missouri"])],
    "giddings-lewis": [("illinois", ["peoria-illinois"]),
                       ("iowa", ["davenport-iowa"]),
                       ("texas", ["houston-texas"])],
    "monarch":        [("iowa", ["cedar-rapids-iowa"]),
                       ("illinois", ["rockford-illinois"]),
                       ("wisconsin", ["milwaukee-wisconsin"])],
    "amera-seiki":    [("iowa", ["ames-iowa"]),
                       ("nebraska", ["kearney-nebraska"]),
                       ("missouri", ["springfield-missouri"])],
    "niigata":        [("wisconsin", ["green-bay-wisconsin"]),
                       ("illinois", ["peoria-illinois"]),
                       ("texas", ["houston-texas"])],
    "johnford":       [("iowa", ["davenport-iowa"]),
                       ("nebraska", ["kearney-nebraska"]),
                       ("texas", ["houston-texas"])],
    "amada":          [("wisconsin", ["green-bay-wisconsin"]),
                       ("illinois", ["chicago-illinois"]),
                       ("texas", ["fort-worth-texas"])],
    "trumpf":         [("missouri", ["st-louis-missouri"]),
                       ("texas", ["fort-worth-texas", "dallas-texas"]),
                       ("wisconsin", ["milwaukee-wisconsin"])],
}


# Manufacturer sameAs URLs (Service schema enrichment)
BRAND_SAMEAS = {
    "mazak":          "https://www.mazakusa.com/",
    "haas":           "https://www.haascnc.com/",
    "okuma":          "https://www.okuma.com/americas",
    "dmg-mori":       "https://us.dmgmori.com/",
    "mori-seiki":     "https://us.dmgmori.com/",
    "doosan":         "https://www.dn-solutions.com/",
    "brother":        "https://www.brothermachinetools.com/",
    "hurco":          "https://www.hurco.com/",
    "makino":         "https://www.makino.com/",
    "fanuc":          "https://www.fanucamerica.com/",
    "toyoda":         "https://www.toyoda.com/",
    "fadal":          None,  # defunct manufacturer
    "hitachi-seiki":  None,
    "giddings-lewis": None,
    "monarch":        None,
    "amera-seiki":    "https://www.ameraseiki.com/",
    "niigata":        "https://www.niigatausa.com/",
    "johnford":       "https://www.absolutemachine.com/johnford/",
    "amada":          "https://www.amada.com/america",
    "trumpf":         "https://www.trumpf.com/en_US/",
}


def brand_industry_phrase(brand, ki):
    """Return a short industries phrase for the hero industry-tie sentence.
    Pulls from brand_specifics + cross-references known industry-brand ties."""
    slug = brand["slug"]
    # Industry shorthand by brand — Ken-derived where possible
    industry_map = {
        "mazak":          "Iowa and Illinois ag-equipment and heavy-machinery supply chains",
        "haas":           "Midwest job shops doing broad-coverage CNC work",
        "okuma":          "Minnesota medical-device and Illinois aerospace shops",
        "dmg-mori":       "St. Louis and Fort Worth aerospace and defense supply chains",
        "mori-seiki":     "long-running mid-sized Mori shops across the Midwest",
        "doosan":         "ag-equipment supply chains and Midwest production shops",
        "brother":        "Twin Cities medical-device and Madison biotech precision work",
        "hurco":          "small and mid-sized Midwest job shops running mixed work",
        "makino":         "aerospace, mold/die, and high-precision medical operations",
        "fanuc":          "broad production environments — controls familiarity matters",
        "toyoda":         "heavy-machining Iowa, Illinois, and Houston O&G work",
        "fadal":          "long-running Fadal installs still cutting daily across the Midwest",
        "hitachi-seiki":  "legacy HMC and mill-turn shops from the 1980s–90s, still in service",
        "giddings-lewis": "heavy-bore and large-part work — Peoria, Quad Cities, Houston",
        "monarch":        "older Monarch lathe shops doing heritage rebuild and restoration work",
        "amera-seiki":    "value-oriented Taiwanese installs in mid-sized Midwest shops",
        "niigata":        "Wisconsin HMC and specialty-gear shops",
        "johnford":       "heavy Taiwanese-built machines in price-conscious shops",
        "amada":          "press brake and turret punch shops across the Wisconsin–Illinois corridor",
        "trumpf":         "DFW aerospace laser cutting and Milwaukee fabrication shops",
    }
    return industry_map.get(slug, "Midwest manufacturing shops across our service area")


def brand_cross_links_section(brand, brands_by_slug):
    """Phase 4 cross-link section — links to states + cities where this brand
    has strongest documented presence. Skip if brand has no emphasis mapping."""
    slug = brand["slug"]
    name = brand["brand_display_name"]
    emphasis = BRAND_REGIONAL_EMPHASIS.get(slug, [])
    if not emphasis:
        return ""

    items = []
    for state_slug, city_slugs in emphasis:
        state_display = state_slug.replace("-", " ").title()
        if state_slug == "dmg-mori":  # safety
            state_display = "DMG Mori"
        state_link = f'<a href="/service-area/{state_slug}/">{state_display}</a>'
        city_links = []
        for cs in city_slugs:
            city_disp = cs.replace(f"-{state_slug}", "").replace("-", " ").title()
            city_disp = city_disp.replace("St ", "St. ")
            city_links.append(f'<a href="/service-area/{cs}/">{html.escape(city_disp)}</a>')
        if city_links:
            cities_phrase = " and ".join(city_links) if len(city_links) <= 2 \
                else ", ".join(city_links[:-1]) + ", and " + city_links[-1]
            items.append(f"<li>{state_link} — particularly {cities_phrase}</li>")
        else:
            items.append(f"<li>{state_link}</li>")

    return (
        f'<h2 id="regional-presence">Where {html.escape(name)} Work Concentrates</h2>\n'
        f"<p>{name} platforms have strong regional concentration in our service "
        f"area:</p>\n"
        f"<ul>{''.join(items)}</ul>\n"
    )


def brand_faq_section(brand, ki, service_kind):
    """Phase 4: 3-4 FAQs per brand page, pulling from Ken's data.
    service_kind: 'spindle', 'machine_repair', 'way_covers'."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    failure = clean_ken(ki.get("common_failure_mode", ""))
    lead_time = clean_ken(ki.get("typical_lead_time", ""))
    specifics = clean_ken(ki.get("brand_specifics", ""))
    is_legacy = "legacy_context" in brand
    parts = clean_ken(ki.get("parts_situation", ""))

    qa_pairs = []

    if service_kind == "spindle":
        # Q1: lead time
        if lead_time:
            qa_pairs.append((
                f"What's the typical lead time on a {name} spindle rebuild?",
                f"{lead_time} Each job is scoped during the quote — bearing-pack "
                f"damage, parts availability, and crash-related work all shift the "
                f"window.",
            ))
        # Q2: common failure mode
        if failure:
            qa_pairs.append((
                f"What's the most common {name} spindle failure you see?",
                f"{failure}",
            ))
        # Q3: brand-specifics or grinding
        if specifics:
            qa_pairs.append((
                f"What should I know about {name} spindle rebuilds specifically?",
                f"{specifics}",
            ))
        # Q4: parts (legacy brands) or general
        if is_legacy and parts:
            qa_pairs.append((
                f"How do you handle {name} parts sourcing on a rebuild?",
                f"{parts}",
            ))
        else:
            qa_pairs.append((
                f"Do you grind {name} spindles back to factory tolerance?",
                f"Yes — precision spindle balancing and grinding to runout is "
                f"part of every rebuild we do, with photo verification at sign-off.",
            ))

    elif service_kind == "machine_repair":
        qa_pairs.append((
            f"What can you fix on a {name} CNC machine?",
            f"Spindle, control, ATC, drive systems, and way alignment are the "
            f"routine work. We diagnose before we quote — sometimes what looks "
            f"like a spindle problem is something cheaper.",
        ))
        if lead_time:
            qa_pairs.append((
                f"How long is a typical {name} machine repair?",
                f"Lead time varies more than spindle work — diagnostic is fast, "
                f"parts and rebuild time depend on the job. {lead_time}",
            ))
        if specifics:
            qa_pairs.append((
                f"Anything unusual about {name} machine repair?",
                f"{specifics}",
            ))
        if is_legacy and parts:
            qa_pairs.append((
                f"Can you still get parts for older {name} machines?",
                f"{parts}",
            ))
        else:
            qa_pairs.append((
                f"Do you service older {name} machines?",
                f"Yes — older {name} platforms are routine work. Bring us the "
                f"machine model and the symptoms; we'll scope what's repairable "
                f"versus what's better replaced.",
            ))

    elif service_kind == "way_covers":
        qa_pairs.append((
            f"What way-cover styles do you build for {name} machines?",
            f"Three styles — bellows, telescoping steel, and roll-up — selected "
            f"based on machine design, debris environment, and clearance constraints. "
            f"We measure from your original or build to drawing.",
        ))
        qa_pairs.append((
            f"How long does a replacement {name} way cover take to build?",
            f"Most way-cover orders ship in 2–4 weeks depending on dimensions and "
            f"material. Rush options are available — call to discuss.",
        ))
        qa_pairs.append((
            f"Can you match an existing {name} way cover I have?",
            f"Yes. Send us the original (or measurements) and we'll build a "
            f"replacement to spec. We routinely match older inventory across the "
            f"full {name} platform range.",
        ))
        qa_pairs.append((
            f"Do you ship {name} way covers nationally?",
            f"Yes. We ship anywhere in the continental US. The build happens at "
            f"our Waterloo, IA shop; freight is included in most quotes for major "
            f"metros.",
        ))

    if not qa_pairs:
        return "", None

    items = []
    for q, a in qa_pairs:
        items.append(
            f'<div class="faq-item">\n'
            f'  <h3>{html.escape(q)}</h3>\n'
            f'  <p>{html.escape(a)}</p>\n'
            f'</div>'
        )

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in qa_pairs
        ],
    }
    schema_script = (
        '\n<script type="application/ld+json">\n'
        + json.dumps(schema, indent=2, ensure_ascii=False)
        + '\n</script>\n'
    )
    return (
        f'<h2 id="faq">Frequently Asked Questions</h2>\n'
        + "\n".join(items) + "\n"
        + schema_script,
        schema,
    )


def write_redirects(brands, outpath, extras=None):
    """Emit public/_redirects covering brand-page URL moves plus any
    `extras` list of (group_title, [(source, destination, code), ...]).
       1. URL relocations (Amada, Trumpf) — old_url → current_url.
       2. /spindles-repair/ duplicates → canonical URLs.
       3. extras — additional groups (e.g. Phase-1 state-page placeholders).
    """
    moves, dups = [], []
    for b in brands:
        if b.get("old_url") and b.get("current_url"):
            moves.append((b["old_url"], b["current_url"]))
    for b in brands:
        old = f"/spindles-repair/{b['slug']}-spindle-repair/"
        new = b.get("current_url")
        if not new or old == new:
            continue
        dups.append((old, new))

    groups = []
    if moves:
        groups.append((
            "Brand page URL relocations — Amada and Trumpf aren't spindle work",
            [(s, d, 301) for s, d in moves],
        ))
    if dups:
        groups.append((
            "/spindles-repair/ URLs duplicate the spindle-grinding / repairs pages",
            [(s, d, 301) for s, d in dups],
        ))
    if extras:
        groups.extend(extras)

    all_rows = [(s, d) for _, rows in groups for (s, d, _) in rows]
    width_src = max((len(s) for s, _ in all_rows), default=60)
    width_dst = max((len(d) for _, d in all_rows), default=55)

    lines = []
    n = 0
    for title, rows in groups:
        if not rows:
            continue
        lines.append(f"# {title}")
        for src, dst, code in rows:
            lines.append(f"{src:<{width_src}}  {dst:<{width_dst}}  {code}")
            n += 1
        lines.append("")

    with open(outpath, "w") as f:
        f.write("\n".join(lines))
    return n


# ---------- CNC spindle page ----------

def render_cnc_spindle(brand, g, brands_by_slug, brand_index):
    name = brand["brand_display_name"]
    slug = brand["slug"]
    ki = brand["ken_input"]
    is_legacy = "legacy_context" in brand

    failure   = ensure_period(clean_ken(ki["common_failure_mode"]))
    specifics = ensure_period(clean_ken(ki["brand_specifics"]))
    war_story = ensure_period(clean_ken(ki["war_story"]))
    lead_time = ensure_period(clean_ken(ki["typical_lead_time"]))
    lead_pref = lead_short(ki["typical_lead_time"])
    models    = ki["models"]
    parts     = clean_ken(ki.get("parts_situation", ""))

    legacy_tag = " (legacy platform)" if is_legacy else ""
    service_type = f"{name} CNC Spindle Repair and Grinding{legacy_tag}"

    meta_extra = " — keeping legacy machines running" if is_legacy else ""
    meta_desc = (
        f"Expert {name} spindle repair across the Midwest{meta_extra}. "
        f"{lead_pref} on most rebuilds. Experienced field technicians."
    )

    h1_text, eyebrow_text = make_h1_and_eyebrow(brand)
    fm = front_matter(
        brand,
        title=f"{name} Spindle Repair | Midwest CNC Services",
        h1=h1_text,
        meta_description=meta_desc,
        service_type=service_type,
        canonical_path=brand["current_url"],
        crumb_middle=("Spindle Grinding", "/spindle-grinding/"),
        crumb_leaf=f"{name} Spindle Repair",
    )

    eyebrow_md = f"_{eyebrow_text}_\n\n" if eyebrow_text else ""
    h1 = f"# {h1_text}"

    # Hero image — handled by markdown_to_html via standard markdown img syntax
    img_path, img_alt = hero_image_for(brand, "spindle")
    hero_img_md = f"\n![{img_alt}]({img_path})\n" if img_path else ""

    # Inline model list for the hero (use Ken's exact names). Apply Oxford
    # comma only for 3+ items; "A and B" reads more naturally than "A, and B".
    if not models:
        model_inline = ""
    elif len(models) == 1:
        model_inline = models[0]
    elif len(models) == 2:
        model_inline = f"{models[0]} and {models[1]}"
    else:
        model_inline = ", ".join(models[:-1]) + f", and {models[-1]}"

    # Hero — opens with Ken's failure mode for brand specificity.
    # Two patterns based on how Ken's quote starts:
    #   - sentence (verb-led): "What we see most on {Brand} spindles: {quote}"
    #   - noun phrase: "{Brand} spindles tend to come in with {lowercased quote}"
    first_word = re.match(r"\w+", failure or "")
    is_noun_phrase = (
        first_word is not None
        and first_word.group(0).lower() in NOUN_PHRASE_OPENERS
    )

    if is_noun_phrase:
        # Strip awkward " are common"/" is common" predicates so Ken's noun
        # phrase reads cleanly after "tend to come in with".
        cleaned_failure = re.sub(
            r"\s+(?:are|is)\s+common(?=[,.])",
            "",
            failure,
        )
        hero_opener = (
            f"{name} spindles tend to come in with "
            f"{_lower_first(cleaned_failure)}"
        )
    else:
        hero_opener = (
            f"What we see most on {name} spindles: {_lower_first(failure)}"
        )

    hero = (
        f"{eyebrow_md}{h1}\n\n"
        f"{hero_opener} "
        f"We rebuild, regrind, and rebalance across the {name} platform"
        f"{' — ' + model_inline if model_inline else ''} — "
        f"with most jobs running {lead_pref} and field troubleshooting "
        f"where it can save a teardown.\n\n"
        f"{hero_cta()}\n"
        f"{hero_img_md}"
    )

    # Models — fix 9: removed "no model left behind"
    model_bullets = "\n".join(f"- {m}" for m in models) if models else ""
    models_section = (
        f"\n## {name} Models We Support\n\n"
        f"Our {name} work covers the full lineup. "
        f"Whether the job is a precision bearing pack replacement, a full rebuild, "
        f"or a regrind to restore tolerance, we handle:\n\n"
        f"{model_bullets}\n\n"
        f"[Get a Quote](#quote)\n"
    )

    # "How We Approach" — two variants. Default lead-in implies brand-specific
    # complexity worth planning around. Mainstream variant is used where Ken
    # explicitly described the work as standard/straightforward.
    if slug in MAINSTREAM_BRANDS:
        # If the hero already used failure_mode in noun-phrase form (e.g.
        # Fanuc, Amera-Seiki), skip repeating it here — drop the "What we
        # focus on" tail and let brand_specifics carry the section.
        if is_noun_phrase:
            how = (
                f"\n## How We Approach {name} Spindle Work\n\n"
                f"{name} work is one of the more straightforward calls in our "
                f"queue — {_lower_first(specifics)}\n"
            )
        else:
            how = (
                f"\n## How We Approach {name} Spindle Work\n\n"
                f"{name} work is one of the more straightforward calls in our "
                f"queue — {_lower_first(specifics)} "
                f"What we focus on is the spindle condition itself: "
                f"{_lower_first(failure)}\n"
            )
    else:
        # Fix 3: drop the generic "brand-specific factors on {name} drive
        # how we plan the job" lead-in. Lead directly with Ken's specifics.
        # The H2 itself supplies the brand-name context.
        how = (
            f"\n## How We Approach {name} Spindle Work\n\n"
            f"{specifics}\n"
        )

    # Parts sourcing (legacy only). Two patterns:
    #   - Fadal / Hitachi Seiki: legacy_context is a directive ("pages should
    #     mention..."), so don't render it. Use ken_input.parts_situation as
    #     the section body.
    #   - Monarch: legacy_context is written as direct page content. Use it
    #     as the section body when parts_situation isn't present.
    parts_section = ""
    if is_legacy:
        legacy_ctx = brand.get("legacy_context", "")
        is_directive = (
            "pages should" in legacy_ctx.lower()
            or "should mention" in legacy_ctx.lower()
        )
        if parts:
            body = ensure_period(parts)
            intro = (
                f"{name} machines are still cutting daily in Midwest shops, "
                f"but factory support has been gone for years and parts hunts "
                f"can stretch a rebuild's timeline more than the bench work does."
            )
        elif legacy_ctx and not is_directive:
            body = ensure_period(legacy_ctx)
            intro = (
                f"{name} machines are still cutting daily in Midwest shops, "
                f"but factory support has been gone for years."
            )
        else:
            body = (
                "_Parts sourcing details for this brand are still being "
                "confirmed — call us for the latest._"
            )
            intro = (
                f"{name} machines are still cutting daily in Midwest shops, "
                f"but factory support has been gone for years."
            )
        parts_section = (
            f"\n## Parts Sourcing for Legacy {name} Machines\n\n"
            f"{intro} {body}\n"
        )

    # Fix 11: "What We Focus On" section removed — themes will live on the
    # home page hero instead.

    # War story
    war_section = (
        f"\n## A Recent {name} Job\n\n"
        f"A recent example of the kind of work that comes through here: "
        f"{_lower_first(war_story)}\n"
    )

    # Lead time + workflow
    step3 = "We rebuild the spindle, verify balance and runout, and return it ready to run."
    lead_section = (
        f"\n## Lead Time & Process\n\n"
        f"{lead_time} Our three-step workflow keeps it transparent:\n\n"
        f"{workflow_block('rebuild', step3)}\n"
    )

    trust = trust_block(g, brand["page_type"], brand_index, "a new spindle")
    related = related_block_cnc(brand, brands_by_slug)
    cross_links = brand_cross_links_section(brand, brands_by_slug)
    faq_html, faq_schema = brand_faq_section(brand, ki, "spindle")
    blog = blog_block()

    return (
        fm + hero + models_section + how + parts_section + war_section
        + lead_section + "\n" + trust + "\n" + faq_html + "\n"
        + cross_links + "\n" + related + "\n" + blog
    )


def _lower_first(s):
    """Lowercase the first letter so Ken's sentence-start lands inside ours."""
    if not s:
        return s
    return s[0].lower() + s[1:]


# ---------- Amada (press brake / punch) ----------

def render_amada(brand, g, brands_by_slug, brand_index):
    ki = brand["ken_input"]
    failure   = ensure_period(clean_ken(ki["common_failure_mode"]))
    specifics = ensure_period(clean_ken(ki["brand_specifics"]))
    war_story = ensure_period(clean_ken(ki["war_story"]))
    lead_time = ensure_period(clean_ken(ki["typical_lead_time"]))
    lead_pref = lead_short(ki["typical_lead_time"])

    meta_desc = (
        "Amada press brake and turret punch service across the Midwest. "
        "Hydraulic service, ram alignment, backgauge calibration, and "
        "tooling-related troubleshooting. Experienced field technicians."
    )

    h1_text, eyebrow_text = make_h1_and_eyebrow(brand)
    fm = front_matter(
        brand,
        title="Amada Press Brake & Punch Service | Midwest CNC Services",
        h1=h1_text,
        meta_description=meta_desc,
        service_type="Amada Press Brake and Turret Punch Service",
        canonical_path=brand["current_url"],
        crumb_middle=("Repairs", "/repairs/"),
        crumb_leaf="Amada Press Brake & Punch Service",
    )

    eyebrow_md = f"_{eyebrow_text}_\n\n" if eyebrow_text else ""
    h1 = f"# {h1_text}"

    img_path, img_alt = hero_image_for(brand, "machine_repair")
    hero_img_md = f"\n![{img_alt}]({img_path})\n" if img_path else ""

    # Fix 7: extend noun-phrase detection to Amada. ("Hydraulic" isn't a
    # trigger, so Amada keeps the verb-led opener.)
    first_word = re.match(r"\w+", failure or "")
    is_noun_phrase = (
        first_word is not None
        and first_word.group(0).lower() in NOUN_PHRASE_OPENERS
    )

    if is_noun_phrase:
        cleaned_failure = re.sub(
            r"\s+(?:are|is)\s+common(?=[,.])", "", failure,
        )
        hero_opener = (
            f"Amada {MACHINE_NOUN['press_brake_service']} tend to come in with "
            f"{_lower_first(cleaned_failure)}"
        )
    else:
        hero_opener = (
            f"When your Amada brake or punch goes down, the call we hear most "
            f"is the same: {_lower_first(failure)}"
        )

    hero = (
        f"{eyebrow_md}{h1}\n\n"
        f"{hero_opener} "
        f"We service press brakes and turret punches across the Amada lineup — "
        f"ram alignment, hydraulic troubleshooting, backgauge calibration, "
        f"and turret tooling work. Simple alignments turn around quickly; "
        f"major hydraulic work is typically {lead_pref}.\n\n"
        f"{hero_cta()}\n"
        f"{hero_img_md}"
    )

    # No model list for Amada (Ken didn't supply one). Use service scope instead.
    scope = (
        "\n## Amada Service We Provide\n\n"
        "Most of our Amada work falls into a few buckets — ram alignment and "
        "hydraulic service on press brakes, backgauge calibration, and "
        "turret punch tooling and maintenance. We come in on the calls where "
        "a brake or punch isn't producing the part the way it used to.\n\n"
        f"[Get a Quote](#quote)\n"
    )

    how = (
        f"\n## How We Approach Amada Work\n\n"
        f"{specifics}\n"
    )

    war_section = (
        f"\n## A Recent Amada Job\n\n"
        f"A recent example of the kind of work that comes through here: "
        f"{_lower_first(war_story)}\n"
    )

    step3 = "We complete the service, verify the machine is back to spec, and return it ready to run."
    lead_section = (
        f"\n## Lead Time & Process\n\n"
        f"{lead_time} Our three-step workflow keeps it transparent:\n\n"
        f"{workflow_block('job', step3)}\n"
    )

    trust = trust_block(g, brand["page_type"], brand_index, "new equipment")
    related = related_block_alt(brand, brands_by_slug)
    blog = blog_block()

    return fm + hero + scope + how + war_section + lead_section + "\n" + trust + "\n" + related + "\n" + blog


# ---------- Trumpf (laser / punch) ----------

def render_trumpf(brand, g, brands_by_slug, brand_index):
    ki = brand["ken_input"]
    failure   = ensure_period(clean_ken(ki["common_failure_mode"]))
    specifics = ensure_period(clean_ken(ki["brand_specifics"]))
    war_story = ensure_period(clean_ken(ki["war_story"]))
    lead_time = ensure_period(clean_ken(ki["typical_lead_time"]))
    lead_pref = lead_short(ki["typical_lead_time"])

    meta_desc = (
        "Trumpf laser and punch service across the Midwest. Optics service, "
        "resonator work on older CO2 systems, cooling-related faults, and "
        "punch press maintenance. Experienced field technicians."
    )

    h1_text, eyebrow_text = make_h1_and_eyebrow(brand)
    fm = front_matter(
        brand,
        title="Trumpf Laser & Punch Service | Midwest CNC Services",
        h1=h1_text,
        meta_description=meta_desc,
        service_type="Trumpf Laser and Punch Press Service",
        canonical_path=brand["current_url"],
        crumb_middle=("Repairs", "/repairs/"),
        crumb_leaf="Trumpf Laser & Punch Service",
    )

    eyebrow_md = f"_{eyebrow_text}_\n\n" if eyebrow_text else ""
    h1 = f"# {h1_text}"

    img_path, img_alt = hero_image_for(brand, "machine_repair")
    hero_img_md = f"\n![{img_alt}]({img_path})\n" if img_path else ""

    # Fix 7: noun-phrase detection now applies to Trumpf too. "Optics" is in
    # the trigger list, so Trumpf's failure mode triggers the new opener.
    first_word = re.match(r"\w+", failure or "")
    is_noun_phrase = (
        first_word is not None
        and first_word.group(0).lower() in NOUN_PHRASE_OPENERS
    )

    if is_noun_phrase:
        cleaned_failure = re.sub(
            r"\s+(?:are|is)\s+common(?=[,.])", "", failure,
        )
        hero_opener = (
            f"Trumpf {MACHINE_NOUN['laser_punch_service']} tend to come in with "
            f"{_lower_first(cleaned_failure)}"
        )
    else:
        hero_opener = (
            f"What we see most on Trumpf systems: {_lower_first(failure)}"
        )

    hero = (
        f"{eyebrow_md}{h1}\n\n"
        f"{hero_opener} "
        f"We service laser source and optics work on TruLaser and older CO2 "
        f"systems, plus drive and tooling work on TruPunch machines — "
        f"most jobs run {lead_pref}.\n\n"
        f"{hero_cta()}\n"
        f"{hero_img_md}"
    )

    scope = (
        "\n## Trumpf Service We Provide\n\n"
        "Most of our Trumpf work falls into laser source service, resonator "
        "work on older CO2 systems, optics contamination cleanup and "
        "alignment, and punch press drive issues on TruPunch machines. "
        "We come in on the calls where cut quality has fallen off or the "
        "system is faulting on cooling or power.\n\n"
        f"[Get a Quote](#quote)\n"
    )

    how = (
        f"\n## How We Approach Trumpf Work\n\n"
        f"{specifics}\n"
    )

    war_section = (
        f"\n## A Recent Trumpf Job\n\n"
        f"A recent example of the kind of work that comes through here: "
        f"{_lower_first(war_story)}\n"
    )

    step3 = "We complete the work, verify alignment and cut quality, and return the machine ready to run."
    lead_section = (
        f"\n## Lead Time & Process\n\n"
        f"{lead_time} Our three-step workflow keeps it transparent:\n\n"
        f"{workflow_block('job', step3)}\n"
    )

    trust = trust_block(g, brand["page_type"], brand_index, "new laser equipment")
    related = related_block_alt(brand, brands_by_slug)
    blog = blog_block()

    return fm + hero + scope + how + war_section + lead_section + "\n" + trust + "\n" + related + "\n" + blog


# ---------- Machine repair page (TASK 2) ----------

def _format_models_inline(models):
    if not models:
        return ""
    if len(models) == 1:
        return models[0]
    if len(models) == 2:
        return f"{models[0]} and {models[1]}"
    return ", ".join(models[:-1]) + f", and {models[-1]}"


def render_machine_repair(brand, g, brand_index):
    """Brand × machine-repair page. Lives at /repairs/{slug}-cnc-machine-repair/.
    Process-focused — no fabricated brand specifics beyond Ken's existing
    data. Target 250–350 visible body words."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    ki = brand["ken_input"]
    models = ki["models"]
    control_system = brand.get("control_system", "varies by model")

    # H1 / eyebrow / canonical
    if len(name) > 11:
        h1_text = f"{name} CNC Repair"
    else:
        h1_text = f"{name} CNC Machine Repair & Service"
    eyebrow_text = f"{name} CNC Machine Repair"
    canonical_path = f"/repairs/{slug}-cnc-machine-repair/"

    meta_desc = (
        f"Expert {name} CNC machine repair across the Midwest. "
        f"Spindle, control, ATC, drive, and alignment work. "
        f"Experienced field technicians."
    )

    fm = front_matter(
        brand,
        title=f"{name} CNC Machine Repair | Midwest CNC Services",
        h1=h1_text,
        meta_description=meta_desc,
        service_type=f"{name} CNC Machine Repair and Service",
        canonical_path=canonical_path,
        crumb_middle=("Repairs", "/repairs/"),
        crumb_leaf=f"{name} CNC Machine Repair",
    )

    eyebrow_md = f"_{eyebrow_text}_\n\n"
    h1 = f"# {h1_text}"

    img_path, img_alt = hero_image_for(brand, "machine_repair")
    hero_img_md = f"\n![{img_alt}]({img_path})\n" if img_path else ""

    model_inline = _format_models_inline(models)
    hero = (
        f"{eyebrow_md}{h1}\n\n"
        f"When a {name} machine isn't producing the way it used to, we come in. "
        f"We work across the {name} lineup"
        f"{ ' — ' + model_inline if model_inline else '' } — "
        f"spindle, control, ATC, drive, and alignment work. "
        f"Lead time depends on what's wrong: diagnostics move fast, "
        f"parts and rebuild time vary by the job.\n\n"
        f"{hero_cta()}\n"
        f"{hero_img_md}"
    )

    # Models — same list Ken gave for the spindle page
    model_bullets = "\n".join(f"- {m}" for m in models) if models else ""
    models_section = (
        f"\n## {name} Models We Service\n\n"
        f"Our {name} repair work covers the full lineup:\n\n"
        f"{model_bullets}\n\n"
        f"[Get a Quote](#quote)\n"
    )

    # What Brings Machines In For Repair — process-uniform list, rotated
    # per brand so different pages don't open with the same item.
    issue_items = [
        "spindle issues",
        "control problems",
        "ATC faults",
        "drive system wear",
        "way alignment",
    ]
    rot = (sum(ord(c) for c in slug)) % len(issue_items)
    permuted = issue_items[rot:] + issue_items[:rot]
    items_text = ", ".join(permuted[:-1]) + f", or {permuted[-1]}"
    issues_section = (
        f"\n## What Brings {name} Machines In For Repair\n\n"
        f"Most {name} repair calls come in for {items_text}. "
        f"We diagnose what's actually broken before we quote — sometimes "
        f"what looks like a spindle problem is something cheaper to fix.\n"
    )

    # How We Approach — lean on Ken's control_system field. Honest fallback
    # for brands without a documented control.
    if control_system == "varies by model":
        approach = (
            f"{name} control systems vary by model, so we start with "
            f"diagnostics that match the platform in front of us rather than "
            f"assuming what we'll find."
        )
    else:
        approach = (
            f"{name} machines run {control_system}, so diagnostics need to "
            f"come from someone who knows the platform — that's us."
        )
    how = (
        f"\n## How We Approach {name} Repair Work\n\n"
        f"{approach}\n"
    )

    step3 = "We complete the repair, verify it back to spec, and return the machine ready to run."
    lead_section = (
        f"\n## Lead Time & Process\n\n"
        f"Lead time on machine repair depends on what's wrong — diagnostic "
        f"is fast, but parts and rebuild time vary by the job. Our "
        f"three-step workflow keeps it transparent:\n\n"
        f"{workflow_block('repair', step3)}\n"
    )

    trust = trust_block(g, brand["page_type"], brand_index, "a replacement machine")
    related = related_block_machine_repair(brand)
    cross_links = brand_cross_links_section(brand, {})
    faq_html, faq_schema = brand_faq_section(brand, ki, "machine_repair")
    blog = blog_block()

    return (
        fm + hero + models_section + issues_section + how
        + lead_section + "\n" + trust + "\n" + faq_html + "\n"
        + cross_links + "\n" + related + "\n" + blog
    )


# ---------- Way covers page (TASK 3) ----------

def render_way_covers(brand, g, brand_index):
    """Brand × way-covers page. Lives at /way-covers/{slug}-cnc-way-covers/.
    Manufacturing service — process-uniform across brands, with Ken's model
    list as the brand-specific anchor. For Amada/Trumpf this renders as a
    draft pending Ken's verification (SAFEGUARD).
    Target 200–280 visible body words."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    ki = brand["ken_input"]
    models = ki["models"]
    is_draft = bool(brand.get("way_covers_verification_pending"))

    h1_text = f"{name} CNC Way Cover Replacement"
    eyebrow_text = f"{name} CNC Way Covers"
    canonical_path = f"/way-covers/{slug}-cnc-way-covers/"

    meta_desc = (
        f"Replacement {name} CNC way covers manufactured to spec. Bellows, "
        f"telescoping steel, and roll-up styles. 2–4 week lead time on "
        f"most orders."
    )

    verification_msg = None
    if is_draft:
        verification_msg = (
            "Awaiting Ken confirmation that Midwest CNC makes way covers / "
            "shielding for press brakes (Amada) and laser cutters (Trumpf) — "
            "these aren't conventional CNC mill way covers."
        )

    fm = front_matter(
        brand,
        title=f"{name} CNC Way Covers | Midwest CNC Services",
        h1=h1_text,
        meta_description=meta_desc,
        service_type=f"{name} CNC Way Cover Manufacturing",
        canonical_path=canonical_path,
        crumb_middle=("Way Covers", "/way-covers/"),
        crumb_leaf=f"{name} CNC Way Covers",
        draft=is_draft,
        verification_pending=verification_msg,
    )

    eyebrow_md = f"_{eyebrow_text}_\n\n"
    h1 = f"# {h1_text}"

    img_path, img_alt = hero_image_for(brand, "way_covers")
    hero_img_md = f"\n![{img_alt}]({img_path})\n" if img_path else ""

    model_inline = _format_models_inline(models)
    hero = (
        f"{eyebrow_md}{h1}\n\n"
        f"We manufacture replacement way covers for {name} machines"
        f"{ ' across the ' + model_inline if model_inline else '' }. "
        f"Most jobs ship in 2–4 weeks depending on dimensions and "
        f"material. Bellows, telescoping steel, and roll-up styles "
        f"available — we match the original or build to spec.\n\n"
        f"{hero_cta()}\n"
        f"{hero_img_md}"
    )

    if models:
        model_bullets = "\n".join(f"- {m}" for m in models)
        models_section = (
            f"\n## Way Covers We Manufacture for {name}\n\n"
            f"We cover the {name} lineup including:\n\n"
            f"{model_bullets}\n\n"
            f"[Get a Quote](#quote)\n"
        )
    else:
        models_section = (
            f"\n## Way Covers We Manufacture for {name}\n\n"
            f"We build replacement covers and shielding sized to your "
            f"machine — bring us the dimensions or the original part and "
            f"we'll match it.\n\n"
            f"[Get a Quote](#quote)\n"
        )

    what_we_build = (
        "\n## What We Build\n\n"
        "Way covers in three styles depending on the machine's design and "
        "operating conditions:\n\n"
        "- Bellows-style for protected ways with limited debris\n"
        "- Telescoping steel for heavier chip and coolant environments\n"
        "- Roll-up for retrofits and specific clearance constraints\n\n"
        "We measure to spec from your original or your machine, fabricate, "
        "and ship anywhere in the continental US.\n"
    )

    lead_section = (
        "\n## Lead Time\n\n"
        "2–4 weeks for most way cover orders, depending on dimensions and "
        "material. Rush options available — call to discuss.\n"
    )

    trust = trust_block(
        g, brand["page_type"], brand_index,
        "replacement way covers and the retrofit time",
    )
    related = related_block_way_covers(brand)
    cross_links = brand_cross_links_section(brand, {})
    faq_html, faq_schema = brand_faq_section(brand, ki, "way_covers")
    blog = blog_block()

    return (
        fm + hero + models_section + what_we_build
        + lead_section + "\n" + trust + "\n" + faq_html + "\n"
        + cross_links + "\n" + related + "\n" + blog
    )


# ---------- Driver ----------

def _word_count(md):
    """Visible body word count (approximate). Strips YAML front matter,
    headings, list markers, link wrappers, and italic placeholders."""
    body = re.sub(r"^---.*?^---\s*", "", md, flags=re.S | re.M)
    body = re.sub(r"`[^`]*`", "", body)
    body = re.sub(r"#+\s*\S.*", "", body)
    body = re.sub(r"\*[^*]+\*", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    body = re.sub(r"^\s*[-*]\s+", "", body, flags=re.M)
    return len(re.findall(r"\b[\w'-]+\b", body))


def main():
    data = json.load(open(DATA))
    g = data["global_context"]
    brands = data["brands"]
    brands_by_slug = {b["slug"]: b for b in brands}

    for d in (OUTDIR_SPINDLE, OUTDIR_REPAIR, OUTDIR_COVERS):
        os.makedirs(d, exist_ok=True)

    # Alphabetical brand_index drives customer-quote rotation. A single
    # index per brand keeps the rotation consistent across all of that
    # brand's pages (spindle/repair/way-covers).
    sorted_slugs = sorted(b["slug"] for b in brands)
    index_for = {s: i for i, s in enumerate(sorted_slugs)}

    written = []  # (service_kind, slug, path, words, draft)

    for b in brands:
        pt = b["page_type"]
        bi = index_for[b["slug"]]
        so = b.get("services_offered", {})

        # --- Main brand page (spindle for cnc_spindle, repair page for the others) ---
        if pt == "cnc_spindle":
            md = render_cnc_spindle(b, g, brands_by_slug, bi)
        elif pt == "press_brake_service":
            md = render_amada(b, g, brands_by_slug, bi)
        elif pt == "laser_punch_service":
            md = render_trumpf(b, g, brands_by_slug, bi)
        else:
            raise SystemExit(f"Unknown page_type: {pt}")
        path = os.path.join(OUTDIR_SPINDLE, f"{b['slug']}.md")
        with open(path, "w") as f:
            f.write(md)
        written.append(("main",         b["slug"], path, _word_count(md), False))

        # --- Machine-repair page (cnc_spindle brands only) ---
        if so.get("machine_repair"):
            md = render_machine_repair(b, g, bi)
            path = os.path.join(OUTDIR_REPAIR, f"{b['slug']}.md")
            with open(path, "w") as f:
                f.write(md)
            written.append(("machine_repair", b["slug"], path, _word_count(md), False))

        # --- Way-covers page (all 20 brands; Amada/Trumpf flagged draft) ---
        if so.get("way_covers"):
            md = render_way_covers(b, g, bi)
            path = os.path.join(OUTDIR_COVERS, f"{b['slug']}.md")
            with open(path, "w") as f:
                f.write(md)
            written.append(("way_covers", b["slug"], path,
                             _word_count(md),
                             bool(b.get("way_covers_verification_pending"))))

    n_redirects = write_redirects(brands, os.path.join(REPO, "public", "_redirects"))

    # Summary
    by_kind = {}
    for kind, slug, path, words, draft in written:
        by_kind.setdefault(kind, []).append((slug, words, draft))

    print(f"\nWrote {len(written)} markdown files across 3 content directories.")
    print(f"Wrote {n_redirects} redirects to public/_redirects.\n")

    for kind in ("main", "machine_repair", "way_covers"):
        if kind not in by_kind:
            continue
        rows = by_kind[kind]
        avg = sum(w for _, w, _ in rows) // len(rows)
        n_draft = sum(1 for _, _, d in rows if d)
        print(f"  {kind:<15} {len(rows):>3} pages  avg ~{avg:>4} words  drafts: {n_draft}")


if __name__ == "__main__":
    main()
