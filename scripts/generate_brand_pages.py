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


def machine_lookup_html():
    """Site-wide MachineLookup widget. Emits markup + inline JS that fetches
    /data/machines.json on demand, fuzzy-matches user input against
    model + alias strings (case + dash insensitive, partial match after
    3 chars), and routes to the matching series-spoke page.

    The script is inlined per page so the widget works without a build
    pipeline. CSS lives in m2h.CSS under .machine-lookup."""
    return """<div class="machine-lookup" id="machine-lookup">
  <label for="machine-lookup-input" class="machine-lookup-label">Find your machine</label>
  <input
    type="text"
    id="machine-lookup-input"
    class="machine-lookup-input"
    placeholder="Enter your machine model (e.g. QTN-250, VF-2SS, Puma 2600SY, DMU 50)"
    autocomplete="off"
    aria-controls="machine-lookup-results"
    aria-expanded="false">
  <div class="machine-lookup-results" id="machine-lookup-results" role="listbox" hidden></div>
</div>
<script>
(function () {
  var lookup  = document.getElementById('machine-lookup');
  if (!lookup) return;
  var input   = document.getElementById('machine-lookup-input');
  var results = document.getElementById('machine-lookup-results');
  var machines = null;
  var loading  = null;

  function normalize(s) {
    return (s || '').toLowerCase().replace(/[\\s\\-]/g, '');
  }
  function escapeHTML(s) {
    return String(s).replace(/[&<>\"']/g, function (c) {
      return ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[c];
    });
  }
  function loadData() {
    if (machines) return Promise.resolve(machines);
    if (loading)  return loading;
    loading = fetch('/data/machines.json')
      .then(function (r) { return r.json(); })
      .then(function (d) { machines = d.machines || []; return machines; })
      .catch(function ()  { machines = []; return machines; });
    return loading;
  }
  function scoreMachine(m, nq) {
    var candidates = [m.model].concat(m.aliases || []);
    var best = 0;
    for (var i = 0; i < candidates.length; i++) {
      var nc = normalize(candidates[i]);
      if (!nc) continue;
      if (nc === nq)            return 100;
      if (nc.indexOf(nq) === 0) best = Math.max(best, 80);
      else if (nc.indexOf(nq) >= 0) best = Math.max(best, 50);
    }
    return best;
  }
  function search(q) {
    var nq = normalize(q);
    if (nq.length < 3 || !machines) return [];
    var scored = [];
    for (var i = 0; i < machines.length; i++) {
      var s = scoreMachine(machines[i], nq);
      if (s > 0) scored.push({ m: machines[i], score: s });
    }
    scored.sort(function (a, b) { return b.score - a.score; });
    return scored.slice(0, 5).map(function (x) { return x.m; });
  }
  function renderResults(matches) {
    if (!matches.length) {
      results.innerHTML =
        '<div class=\"machine-lookup-empty\">' +
          'We service older and obscure machines too. ' +
          '<a href=\"/get-a-quote/\">Get a quote</a> or call ' +
          '<a href=\"tel:+13196104341\">319-610-4341</a>.' +
        '</div>';
    } else {
      results.innerHTML = matches.map(function (m) {
        return (
          '<a class=\"machine-lookup-result\" href=\"' + escapeHTML(m.spoke_url) + '\" role=\"option\">' +
            '<span class=\"machine-lookup-result-brand\">'  + escapeHTML(m.brand)  + '</span>' +
            '<span class=\"machine-lookup-result-model\">'  + escapeHTML(m.model)  + '</span>' +
            '<span class=\"machine-lookup-result-series\">' + escapeHTML(m.series) + '</span>' +
            '<span class=\"machine-lookup-result-arrow\" aria-hidden=\"true\">&rarr;</span>' +
          '</a>'
        );
      }).join('');
    }
    results.hidden = false;
    input.setAttribute('aria-expanded', 'true');
  }
  function hideResults() {
    results.hidden = true;
    input.setAttribute('aria-expanded', 'false');
  }
  var debounceId;
  input.addEventListener('input', function () {
    clearTimeout(debounceId);
    debounceId = setTimeout(function () {
      var q = input.value.trim();
      if (q.length < 3) { hideResults(); return; }
      loadData().then(function () { renderResults(search(q)); });
    }, 100);
  });
  input.addEventListener('focus', function () {
    var q = input.value.trim();
    if (q.length >= 3 && machines) renderResults(search(q));
  });
  document.addEventListener('click', function (e) {
    if (!lookup.contains(e.target)) hideResults();
  });
  // Pre-warm the data file on the first interaction with the page
  document.addEventListener('mousemove', function init() {
    document.removeEventListener('mousemove', init);
    loadData();
  }, { once: true });
})();
</script>
"""


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
    """Related Services on a brand's machine-repair page. Card grid
    instead of plain bullets — uses .related-grid class for the polished
    card treatment. Self = the machine-repair canonical, NOT the brand's
    main current_url (the spindle page is a valid cross-link from here)."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    self_url = f"/repairs/{slug}-cnc-machine-repair/"
    so = brand.get("services_offered", {})

    cards = []
    if so.get("spindle"):
        url = f"/spindle-grinding/{slug}-spindle-repair/"
        if url != self_url:
            cards.append(
                f'<li><a href="{url}">'
                f'<span>{html.escape(name)} spindle repair</span>'
                f'</a></li>'
            )
    if _can_link_way_covers(brand):
        url = f"/way-covers/{slug}-cnc-way-covers/"
        if url != self_url:
            cards.append(
                f'<li><a href="{url}">'
                f'<span>{html.escape(name)} CNC way covers</span>'
                f'</a></li>'
            )

    if not cards:
        return ""

    states_inline = ", ".join(STATES[:-1]) + ", and " + STATES[-1]
    return (
        f'\n<h2 id="related-services">Related {html.escape(name)} Services</h2>\n'
        f'<ul class="related-grid">{"".join(cards)}</ul>\n'
        f'<p class="related-coverage">We serve shops across {states_inline}.</p>\n'
    )


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
            f'<details class="faq-item">\n'
            f'  <summary>{html.escape(q)}</summary>\n'
            f'  <div class="faq-answer"><p>{html.escape(a)}</p></div>\n'
            f'</details>'
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
        f'<div class="faq-list">\n'
        + "\n".join(items) + "\n"
        + '</div>\n'
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


# ---------- Hub-and-spoke architecture (Mazak pilot) ----------
# Per docs/cnc-repair-hub-spoke-prompt: each brand repair hub becomes
# a true hub with three browse lenses (series / control / service)
# linking to spoke pages. Pilot on Mazak; propagate to other 5 brands
# after Aaron validates.

MAZAK_HUB_BROWSE_SERIES = [
    ("Quick Turn / QTN",                    "/repairs/mazak-cnc-machine-repair/quick-turn/",
     "Horizontal turning. QT-8 through QTN-450, MS/MSY twin-spindle variants, current Compact/Smart/Primos/Ez/Ultra."),
    ("Integrex",                            "/repairs/mazak-cnc-machine-repair/integrex/",
     "Mill-turn multitasking. 100/200/300/400 i-series, e-500H through e-1850V, j and i-V and i-H."),
    ("Variaxis",                            "/repairs/mazak-cnc-machine-repair/variaxis/",
     "5-axis trunnion verticals. i-300 through i-800, J-500/J-600, C-600, and legacy 500/630/730."),
    ("Vertical Machining Centers (VTC + VCN)", "/repairs/mazak-cnc-machine-repair/vertical-machining-centers/",
     "Production verticals, mid-size to long-bed. VTC-16 through VTC-800, VCN-410 through VCN-700, FJV and AJV."),
    ("HCN Horizontals",                     "/repairs/mazak-cnc-machine-repair/hcn-horizontal/",
     "Pallet-changer horizontals for production. HCN-4000 through HCN-10800, plus legacy PFH and H-series."),
    ("Turning Legacy",                      "/repairs/mazak-cnc-machine-repair/turning-legacy/",
     "Slant Turn, Multiplex, Megaturn, HQR. Older platforms still in service — M-Plus and Fusion 640 controls."),
]

MAZAK_HUB_BROWSE_CONTROL = [
    ("Mazatrol Legacy",   "/repairs/mazak-cnc-machine-repair/mazatrol-legacy/",
     "M-2, M-32, M-Plus, Fusion 640 — roughly 1981-2005. Battery loss, CRT failures, MDI board, floppy and PCMCIA obsolescence."),
    ("Mazatrol Matrix",   "/repairs/mazak-cnc-machine-repair/mazatrol-matrix/",
     "Matrix and Matrix 2 — roughly 2005-2013. HDD failure (SSD upgrades routine), CF card corruption, MMC board, touchscreen drift."),
    ("Mazatrol Smooth",   "/repairs/mazak-cnc-machine-repair/smooth-control/",
     "SmoothX, SmoothG, SmoothAi — 2013-present. Networking, MTConnect setup, parameter backup, USB media handling."),
]

# Expanded FAQ for the Mazak hub (≥5 Qs including the prompt-specified
# legacy-control / which-series / SSD-upgrade questions).
MAZAK_HUB_FAQ = [
    ("What can you fix on a Mazak CNC machine?",
     "Spindle, control, ATC, drive systems, and way alignment are the routine work. We diagnose before we quote — sometimes what looks like a spindle problem is something cheaper."),
    ("Which Mazak series do you see most often?",
     "Quick Turn and Quick Turn Nexus lathes plus VTC and VCN verticals are the most common. Integrex multitasking work tends to be higher-value but lower frequency. HCN horizontals come in for pallet-changer faults and B-axis indexer wear."),
    ("Do you service older Mazak machines with Mazatrol M-Plus or Fusion 640 controls?",
     "Yes. Legacy Mazatrol controls — M-2, M-32, M-Plus, and Fusion 640 — are routine work. The common issues are dead memory batteries, CRT failures (LCD retrofits are available), keyboard membrane failures, and floppy or PCMCIA media obsolescence. Board-level repair runs through remanufacturing specialists where OEM parts have gone out of stock."),
    ("Can you upgrade a Mazatrol Matrix to an SSD?",
     "Yes — SSD upgrades on Matrix and Matrix 2 controls are one of the highest-ROI service items on older Mazak machines. Replacing the original spinning HDD eliminates the single most common control failure point on that generation and recovers boot and program-load times."),
    ("How long does a typical Mazak machine repair take?",
     "Lead time on machine repair depends on what's wrong. Diagnostic is fast; parts and rebuild time vary by the job. 3 to 5 weeks is realistic on most jobs depending on cartridge damage and OEM bearing or board availability."),
    ("Do you service Mazak machines outside Iowa?",
     "Yes. We service shops across Iowa, Illinois, Wisconsin, Minnesota, Nebraska, Missouri, and Texas. Field service is most economical in Iowa and adjacent states; longer-haul jobs typically run ship-in to our Waterloo facility."),
]

# Per-spoke content. Each spoke renders an independent page nested
# under the Mazak hub. Models lists come from machines.json; here we
# carry the prose (intro, failures, controls used, lead-time framing).
MAZAK_SERIES_SPOKES = {
    "quick-turn": {
        "title":   "Mazak Quick Turn Repair & Service",
        "slug":    "mazak-quick-turn",
        "subtitle":"Quick Turn and Quick Turn Nexus",
        "url":     "/repairs/mazak-cnc-machine-repair/quick-turn/",
        "intro":   "Quick Turn and Quick Turn Nexus lathes are the highest-volume Mazak platform we see. The line spans entry QT-8 chuckers through QTN-450 large-bore turning, plus the MS and MSY twin-spindle variants and the current Compact, Smart, Primos, Ez, and Ultra families. We work on all of them — turret indexing, sub-spindle alignment, Y-axis backlash, tailstock quill wear, and chuck cylinder leaks are routine.",
        "failures": [
            "Turret indexing faults — solenoid, indexer pawl, or position-encoder issues.",
            "Sub-spindle alignment drift on MS and MSY twin-spindle machines.",
            "Y-axis backlash from ballscrew wear or backlash-comp drift after a crash.",
            "Tailstock quill wear and hydraulic pressure loss.",
            "Chuck cylinder leaks and draw-tube issues on high-cycle bar work.",
        ],
        "controls_paragraph": "Older Quick Turn machines ran the Mazatrol Fusion 640T control (see our [Mazatrol Legacy spoke](/repairs/mazak-cnc-machine-repair/mazatrol-legacy/) for memory, CRT, and PCMCIA obsolescence). Mid-2000s through early-2010s Quick Turn Nexus shipped on [Matrix and Matrix 2](/repairs/mazak-cnc-machine-repair/mazatrol-matrix/) — HDD failures and SSD upgrades are the most common service item on that generation. Current Compact, Smart, and Ultra ship on [SmoothG and SmoothAi](/repairs/mazak-cnc-machine-repair/smooth-control/).",
        "siblings": [
            ("Integrex",   "/repairs/mazak-cnc-machine-repair/integrex/"),
            ("Turning Legacy", "/repairs/mazak-cnc-machine-repair/turning-legacy/"),
        ],
    },
    "integrex": {
        "title":   "Mazak Integrex Repair & Service",
        "slug":    "mazak-integrex",
        "subtitle":"Mill-turn multitasking",
        "url":     "/repairs/mazak-cnc-machine-repair/integrex/",
        "intro":   "The Integrex line is Mazak's mill-turn multitasking platform — Integrex 100 through 400 (with S, ST, SY, IV, V, e, i, j, and i-H variants), the e-500H through e-1850V/10 family, plus the compact Integrex j and the vertical i-V. Multitasking tolerances mean spindle and B-axis work needs more careful alignment than on a straight VMC or lathe. We do the work and verify it back to spec.",
        "failures": [
            "B-axis milling spindle bearing wear, particularly on i-series and i-H models.",
            "Lower turret faults on e-series machines.",
            "ATC chain or ATC arm faults on i-H horizontals.",
            "Sub-spindle synchronization drift on multi-tasking jobs.",
            "Hydraulic counterbalance system leaks on larger e-series.",
        ],
        "controls_paragraph": "Original Integrex i-series machines shipped with [Mazatrol Matrix](/repairs/mazak-cnc-machine-repair/mazatrol-matrix/); current i-H, e-V, and i-V ship on [SmoothX](/repairs/mazak-cnc-machine-repair/smooth-control/). Older Integrex 100/200 may still be running [Mazatrol legacy controls](/repairs/mazak-cnc-machine-repair/mazatrol-legacy/) — those are still serviceable but the parts situation is increasingly aftermarket-only.",
        "siblings": [
            ("Variaxis",   "/repairs/mazak-cnc-machine-repair/variaxis/"),
            ("Quick Turn", "/repairs/mazak-cnc-machine-repair/quick-turn/"),
        ],
    },
    "variaxis": {
        "title":   "Mazak Variaxis Repair & Service",
        "slug":    "mazak-variaxis",
        "subtitle":"5-axis trunnion verticals",
        "url":     "/repairs/mazak-cnc-machine-repair/variaxis/",
        "intro":   "Variaxis covers Mazak's 5-axis trunnion-table verticals — i-300 through i-800 plus the J-series and C-series, and the older 500/630/730 platforms. The work is precision 5-axis: aerospace, mold and die, complex part work. RTCP drift after a crash, trunnion bearings, and C-axis brake faults are the common entry points.",
        "failures": [
            "Trunnion A-axis backlash and zero-point drift after a crash.",
            "C-axis brake faults — hydraulic pressure, brake disc wear, or clamp solenoid.",
            "Swarf and coolant intrusion at trunnion bearings on heavy-coolant production work.",
            "RTCP and kinematic drift after spindle or trunnion work — requires re-calibration.",
            "5-axis spindle bearing failure on higher-RPM i-series.",
        ],
        "controls_paragraph": "Variaxis i-series ships on [SmoothX](/repairs/mazak-cnc-machine-repair/smooth-control/); legacy 500/630/730 was [Mazatrol Matrix](/repairs/mazak-cnc-machine-repair/mazatrol-matrix/) or earlier. Variaxis kinematic alignment after any trunnion work is brand-specific — we run the calibration as part of the rebuild rather than handing it back for the shop to fix.",
        "siblings": [
            ("Integrex",   "/repairs/mazak-cnc-machine-repair/integrex/"),
            ("Vertical Machining Centers", "/repairs/mazak-cnc-machine-repair/vertical-machining-centers/"),
        ],
    },
    "vertical-machining-centers": {
        "title":   "Mazak Vertical Machining Center Repair (VTC + VCN)",
        "slug":    "mazak-vertical-machining-centers",
        "subtitle":"Production verticals",
        "url":     "/repairs/mazak-cnc-machine-repair/vertical-machining-centers/",
        "intro":   "VTC and VCN are Mazak's production verticals — VTC-16 through VTC-800 (the long-bed VTCs see the most wear), VCN-410A through VCN-700 (high-RPM spindle work), plus the FJV and AJV gantry platforms. These are the workhorse machines on most Mazak shop floors and the most common reason a shop calls.",
        "failures": [
            "ATC drum indexing faults — solenoid wear, indexer pawl, position sensor.",
            "Ballscrew wear on long-bed VTC-800s with heavy axial production.",
            "High-speed spindle bearing failure on VCN-510C and VCN-530C with high-coolant work.",
            "Way cover damage from chip intrusion or crash.",
            "Z-axis ballnut and bearing wear from heavy production.",
        ],
        "controls_paragraph": "Older VTC machines run [Mazatrol legacy controls](/repairs/mazak-cnc-machine-repair/mazatrol-legacy/); mid-2000s VCN and VTC ran [Matrix](/repairs/mazak-cnc-machine-repair/mazatrol-matrix/); current VCN-510C, VCN-530C, VCN-700 and VCN-Compact ship on [SmoothG](/repairs/mazak-cnc-machine-repair/smooth-control/). VTC-800 with SmoothX is the long-bed current platform.",
        "siblings": [
            ("HCN Horizontals", "/repairs/mazak-cnc-machine-repair/hcn-horizontal/"),
            ("Variaxis",        "/repairs/mazak-cnc-machine-repair/variaxis/"),
        ],
    },
    "hcn-horizontal": {
        "title":   "Mazak HCN Horizontal Machining Center Repair",
        "slug":    "mazak-hcn-horizontal",
        "subtitle":"Pallet-changer horizontals",
        "url":     "/repairs/mazak-cnc-machine-repair/hcn-horizontal/",
        "intro":   "HCN horizontals — HCN-4000 through HCN-10800, plus the legacy PFH and H-series — are production horizontals built around pallet changers and B-axis indexing. The pallet changer and B-axis are where most service calls originate; the rest is conventional horizontal machine work.",
        "failures": [
            "Pallet changer faults — clamp pressure loss, pallet seat alignment, position-sensor issues.",
            "B-axis indexer wear and backlash, especially on heavy-cut production.",
            "Coolant intrusion at the pallet seal — common on high-coolant work.",
            "Chip auger jams and chip evacuation problems.",
            "Hydraulic clamp pressure loss on the workpiece clamping system.",
        ],
        "controls_paragraph": "Mid-2000s HCN runs [Matrix](/repairs/mazak-cnc-machine-repair/mazatrol-matrix/); current HCN-8800 and HCN-10800 ship on [SmoothX](/repairs/mazak-cnc-machine-repair/smooth-control/). Legacy PFH and H-series typically run [Mazatrol Legacy](/repairs/mazak-cnc-machine-repair/mazatrol-legacy/) controls and the parts situation is increasingly aftermarket.",
        "siblings": [
            ("Vertical Machining Centers", "/repairs/mazak-cnc-machine-repair/vertical-machining-centers/"),
            ("Integrex",                   "/repairs/mazak-cnc-machine-repair/integrex/"),
        ],
    },
    "turning-legacy": {
        "title":   "Mazak Turning Legacy Repair (Slant Turn / Multiplex / Megaturn)",
        "slug":    "mazak-turning-legacy",
        "subtitle":"Slant Turn, Multiplex, Megaturn, HQR, Powermaster",
        "url":     "/repairs/mazak-cnc-machine-repair/turning-legacy/",
        "intro":   "Mazak's turning legacy platforms — Slant Turn 15/18/20 and Slant Turn Nexus, Multiplex 6000 through 6300, Megaturn vertical turning, HQR-150/200/250, and the Powermaster series — are still running on shop floors across the Midwest. The platforms are mechanically sound; what brings them in is control obsolescence and drive-side issues more often than spindle work.",
        "failures": [
            "M-Plus and Fusion 640 control board faults — board-level repair or remanufacturing where parts allow.",
            "Drive obsolescence — older servo amplifiers going scarce.",
            "Slant-bed way wear from years of production.",
            "Tailstock and turret indexing issues on Multiplex twin-turret platforms.",
            "Hydraulic system pressure loss on the older Megaturn vertical platforms.",
        ],
        "controls_paragraph": "These platforms ran [Mazatrol legacy controls](/repairs/mazak-cnc-machine-repair/mazatrol-legacy/) — M-Plus and Fusion 640 are the most common. Multiplex 6100 and later ran [Matrix](/repairs/mazak-cnc-machine-repair/mazatrol-matrix/). For the legacy generation, expect aftermarket-only parts on most boards and OEM-discontinued status on some servo amplifiers.",
        "siblings": [
            ("Quick Turn",                 "/repairs/mazak-cnc-machine-repair/quick-turn/"),
            ("Vertical Machining Centers", "/repairs/mazak-cnc-machine-repair/vertical-machining-centers/"),
        ],
    },
}

MAZAK_CONTROL_SPOKES = {
    "mazatrol-legacy": {
        "title":   "Mazatrol Legacy Control Repair (M-2 / M-32 / M-Plus / Fusion 640)",
        "slug":    "mazak-mazatrol-legacy",
        "subtitle":"Mazatrol M-2, M-32, M-Plus, Fusion 640",
        "url":     "/repairs/mazak-cnc-machine-repair/mazatrol-legacy/",
        "era":     "Roughly 1981 through 2005",
        "intro":   "Mazatrol legacy is the family of pre-Matrix controls — M-2, M-32, M-Plus, and Fusion 640 — that shipped on Mazak lathes and verticals from the early 1980s through roughly 2005. In 2026 these controls are at the obsolescence stage: most boards have gone out of OEM stock, parts come through remanufacturing specialists, and the most common service work is preventive (battery replacement, media migration) rather than reactive repair.",
        "machines_paragraph": "Mazatrol legacy controls shipped on older [Quick Turn](/repairs/mazak-cnc-machine-repair/quick-turn/) lathes (pre-Nexus), [Turning Legacy](/repairs/mazak-cnc-machine-repair/turning-legacy/) platforms (Slant Turn, Multiplex, Megaturn, HQR), [Vertical Machining Centers](/repairs/mazak-cnc-machine-repair/vertical-machining-centers/) (VTC and FJV legacy), and the [HCN horizontals'](/repairs/mazak-cnc-machine-repair/hcn-horizontal/) PFH and H-series predecessors. If your machine predates 2005 and runs Mazatrol, it's almost certainly on this generation.",
        "failures": [
            "Dead memory battery — the most common single failure mode. Memory loss takes parameters and offsets with it; battery replacement on a powered-up control is the prevention.",
            "CRT failure — original tubes are mostly out of service. LCD retrofit kits are available and routine.",
            "Keyboard membrane failure — high-cycle keys go intermittent or stop responding.",
            "MDI board faults — generally aftermarket replacement at this point.",
            "Floppy and PCMCIA media obsolescence — physical drives still work but media sourcing and reader reliability are the issue. USB or CF migration is the typical fix.",
        ],
        "parts_paragraph": "Parts on legacy Mazatrol are increasingly aftermarket-only. Remanufactured boards through specialists are the path on most board-level work. We can scope what's repairable in-place versus what needs board exchange — the worst answer is sending out a board nobody is remanufacturing anymore, so we check parts availability before we quote.",
        "recovery_paragraph": "Battery, memory, and parameter recovery on legacy Mazatrol comes up regularly. The process is: capture parameters and offsets via the existing media path before any battery work; replace the battery on a powered control where possible; restore parameters if memory was lost. Floppy and PCMCIA migration to USB or CF media is part of the same conversation — we'll scope it together so we're not opening the control twice.",
        "siblings": [
            ("Mazatrol Matrix",  "/repairs/mazak-cnc-machine-repair/mazatrol-matrix/"),
            ("Mazatrol Smooth",  "/repairs/mazak-cnc-machine-repair/smooth-control/"),
        ],
    },
    "mazatrol-matrix": {
        "title":   "Mazatrol Matrix Control Repair (Matrix / Matrix 2)",
        "slug":    "mazak-mazatrol-matrix",
        "subtitle":"Mazatrol Matrix and Matrix 2",
        "url":     "/repairs/mazak-cnc-machine-repair/mazatrol-matrix/",
        "era":     "Roughly 2005 through 2013",
        "intro":   "Matrix and Matrix 2 are the Mazatrol generation that bridged Fusion 640 and SmoothX. They shipped on Mazak's mid-2000s through early-2010s production — Quick Turn Nexus, Integrex i-series, Variaxis 500/630/730, mid-life VCN and VTC, and HCN-4000 through HCN-6000. Matrix 2 is still well supported; Matrix-1 boards are starting to go scarce. The HDD-to-SSD upgrade is one of the highest-ROI service items on this generation.",
        "machines_paragraph": "Matrix controls shipped on [Quick Turn Nexus](/repairs/mazak-cnc-machine-repair/quick-turn/) (QTN-100 through QTN-450), [Integrex](/repairs/mazak-cnc-machine-repair/integrex/) i-series originals, [Vertical Machining Centers](/repairs/mazak-cnc-machine-repair/vertical-machining-centers/) (VTC-200 through VTC-800, VCN-410 through VCN-530), [HCN horizontals](/repairs/mazak-cnc-machine-repair/hcn-horizontal/) (HCN-4000 through HCN-6000), and the [Multiplex](/repairs/mazak-cnc-machine-repair/turning-legacy/) 6100 generation.",
        "failures": [
            "Hard drive failure — the most common single issue on this generation. SSD upgrades are routine and prevent recurrence.",
            "CF card corruption on Matrix-1 (memory card slot is the primary boot media on some configurations).",
            "MMC board faults — control board sees enough thermal cycling to fail over a decade of production.",
            "Touchscreen drift and calibration loss.",
            "Fan failure and resulting thermal damage to boards if not caught.",
        ],
        "parts_paragraph": "Matrix-2 boards are still actively supported through OEM and authorized channels. Matrix-1 boards are heading the same direction as Fusion 640 — moving toward aftermarket and remanufactured-only over the next few years. We check availability before quoting board-level work.",
        "recovery_paragraph": "SSD upgrades on Matrix and Matrix 2 are the highest-value preventive service item on this generation. Replacing the original spinning HDD eliminates the single most common control failure point, recovers boot and program-load time, and reduces the thermal load that contributes to fan and MMC board failures. Backup parameters and programs before swapping; we run the swap and verify the restore as a single visit.",
        "siblings": [
            ("Mazatrol Legacy",  "/repairs/mazak-cnc-machine-repair/mazatrol-legacy/"),
            ("Mazatrol Smooth",  "/repairs/mazak-cnc-machine-repair/smooth-control/"),
        ],
    },
    "smooth-control": {
        "title":   "Mazatrol Smooth Control Repair (SmoothX / SmoothG / SmoothAi)",
        "slug":    "mazak-smooth-control",
        "subtitle":"Mazatrol SmoothX, SmoothG, SmoothAi",
        "url":     "/repairs/mazak-cnc-machine-repair/smooth-control/",
        "era":     "2013 through present",
        "intro":   "Smooth is Mazatrol's current generation — SmoothX on high-end multitasking and 5-axis platforms, SmoothG on production lathes and VMCs, SmoothAi on the latest Ultra and current-flagship machines. The Smooth generation is recent enough that hardware failure is uncommon; most service work is integration, networking, MTConnect setup, parameter backup, and USB media handling rather than reactive repair.",
        "machines_paragraph": "Smooth ships on current [Integrex](/repairs/mazak-cnc-machine-repair/integrex/) (i-H, i-V, e-V/10), current [Variaxis](/repairs/mazak-cnc-machine-repair/variaxis/) i-series, [Vertical Machining Centers](/repairs/mazak-cnc-machine-repair/vertical-machining-centers/) (VTC-800 and VCN current), current [HCN horizontals](/repairs/mazak-cnc-machine-repair/hcn-horizontal/) (HCN-8800, HCN-10800), and current [Quick Turn](/repairs/mazak-cnc-machine-repair/quick-turn/) Compact, Smart, Primos, Ez, and Ultra.",
        "failures": [
            "Networking and Ethernet configuration drift after a shop network change.",
            "MTConnect setup and parameter mapping when integrating with shop-floor monitoring.",
            "USB media reliability — periodic clean and verify on the boot media path.",
            "Touchscreen calibration drift on heavily-used panels.",
            "Parameter backup discipline — Smooth controls store more parameters than legacy generations, and a clean backup process matters.",
        ],
        "parts_paragraph": "Smooth-generation parts are fully supported through OEM channels. The work here is integration and configuration more than parts.",
        "recovery_paragraph": "Smooth controls support a clean parameter backup workflow over network or USB. The discipline is doing the backup before any service work, not after. We document the parameter set at the start of every service visit and verify the restore at sign-off.",
        "siblings": [
            ("Mazatrol Matrix",  "/repairs/mazak-cnc-machine-repair/mazatrol-matrix/"),
            ("Mazatrol Legacy",  "/repairs/mazak-cnc-machine-repair/mazatrol-legacy/"),
        ],
    },
}


def _models_for_spoke(spoke_url):
    """Pull every model entry from machines.json whose spoke_url matches."""
    p = os.path.join(REPO, "src", "data", "machines.json")
    with open(p) as f:
        data = json.load(f)
    return [m for m in data.get("machines", []) if m.get("spoke_url") == spoke_url]


def render_mazak_series_spoke(spoke_key, brand, brand_index):
    """Render one Mazak series spoke as markdown. Output lives at the
    nested URL /repairs/mazak-cnc-machine-repair/{spoke_key}/ via the
    breadcrumb-driven path mapping in m2h.output_path_for()."""
    s = MAZAK_SERIES_SPOKES[spoke_key]
    models = _models_for_spoke(s["url"])
    model_lis = "".join(f'<li>{html.escape(m["model"])}</li>' for m in models)
    failure_bullets = "\n".join(f"- {html.escape(f)}" for f in s["failures"])
    sibling_cards = "".join(
        f'<li><a href="{u}"><span>{html.escape(n)}</span></a></li>'
        for n, u in s["siblings"]
    )

    fm_lines = [
        '---',
        f'title: "{s["title"]} | Midwest CNC Services"',
        f'meta_description: "Mazak {s["subtitle"]} repair across the Midwest. Models, common failure patterns, and the Mazatrol control generations they ship on."',
        f'h1: "{s["title"]}"',
        f'slug: "{s["slug"]}"',
        'page_type: "cnc_spindle"',
        'schema_data:',
        '  service:',
        '    "@type": Service',
        f'    serviceType: "{s["title"]}"',
        '    provider:',
        '      "@id": "#org"',
        '    areaServed:',
        '      - Iowa',
        '      - Illinois',
        '      - Minnesota',
        '      - Wisconsin',
        '      - Nebraska',
        '      - Missouri',
        '      - Texas',
        '  breadcrumb:',
        '    "@type": BreadcrumbList',
        '    itemListElement:',
        '      - { position: 1, name: Home, item: "https://midwestcncservices.com/" }',
        '      - { position: 2, name: "Repairs", item: "https://midwestcncservices.com/repairs/" }',
        '      - { position: 3, name: "Mazak CNC Machine Repair", item: "https://midwestcncservices.com/repairs/mazak-cnc-machine-repair/" }',
        f'      - {{ position: 4, name: "{s["subtitle"]}", item: "https://midwestcncservices.com{s["url"]}" }}',
        '---',
        '',
    ]

    body = (
        f'<section class="brand-hero">\n'
        f'  <div class="brand-hero-overlay" aria-hidden="true"></div>\n'
        f'  <div class="brand-hero-content">\n'
        f'    <p class="eyebrow">Mazak Series Repair</p>\n'
        f'    <h1>{html.escape(s["title"])}</h1>\n'
        f'    <p>{html.escape(s["intro"])}</p>\n'
        f'    <div class="cta-row">\n'
        f'      <a class="cta-button" href="/get-a-quote/">Get a Quote</a>\n'
        f'      <a class="cta-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>\n\n'

        f'## Models in this series we service\n\n'
        f'<ul class="model-chips">{model_lis}</ul>\n\n'

        f'## Common failure patterns\n\n'
        f'{failure_bullets}\n\n'

        f'## Controls used on this series\n\n'
        f'{s["controls_paragraph"]}\n\n'

        f'## Lead time\n\n'
        f'Lead time depends on the model, the failure mode, and parts availability. Diagnostic is fast; full rebuilds run 3 to 5 weeks on most jobs. We scope each job individually rather than quoting a generic window.\n\n'

        f'[Get a Quote](/get-a-quote/) · [{PHONE_DISPLAY}](tel:{PHONE_TEL})\n\n'

        f'## Related\n\n'
        f'<ul class="related-grid">'
        f'<li><a href="/repairs/mazak-cnc-machine-repair/"><span>All Mazak repair</span></a></li>'
        f'{sibling_cards}'
        f'<li><a href="/spindle-grinding/mazak-spindle-repair/"><span>Mazak spindle repair</span></a></li>'
        f'<li><a href="/way-covers/mazak-cnc-way-covers/"><span>Mazak way covers</span></a></li>'
        f'</ul>\n'
    )
    return "\n".join(fm_lines) + body


def render_mazak_control_spoke(spoke_key, brand, brand_index):
    """Render one Mazak control-generation spoke as markdown."""
    s = MAZAK_CONTROL_SPOKES[spoke_key]
    failure_bullets = "\n".join(f"- {html.escape(f)}" for f in s["failures"])
    sibling_cards = "".join(
        f'<li><a href="{u}"><span>{html.escape(n)}</span></a></li>'
        for n, u in s["siblings"]
    )

    fm_lines = [
        '---',
        f'title: "{s["title"]} | Midwest CNC Services"',
        f'meta_description: "Mazatrol {s["subtitle"]} control repair across the Midwest. {s["era"]}. Common faults, parts availability, and battery/memory/parameter recovery."',
        f'h1: "{s["title"]}"',
        f'slug: "{s["slug"]}"',
        'page_type: "cnc_spindle"',
        'schema_data:',
        '  service:',
        '    "@type": Service',
        f'    serviceType: "{s["title"]}"',
        '    provider:',
        '      "@id": "#org"',
        '    areaServed:',
        '      - Iowa',
        '      - Illinois',
        '      - Minnesota',
        '      - Wisconsin',
        '      - Nebraska',
        '      - Missouri',
        '      - Texas',
        '  breadcrumb:',
        '    "@type": BreadcrumbList',
        '    itemListElement:',
        '      - { position: 1, name: Home, item: "https://midwestcncservices.com/" }',
        '      - { position: 2, name: "Repairs", item: "https://midwestcncservices.com/repairs/" }',
        '      - { position: 3, name: "Mazak CNC Machine Repair", item: "https://midwestcncservices.com/repairs/mazak-cnc-machine-repair/" }',
        f'      - {{ position: 4, name: "{s["subtitle"]}", item: "https://midwestcncservices.com{s["url"]}" }}',
        '---',
        '',
    ]

    body = (
        f'<section class="brand-hero">\n'
        f'  <div class="brand-hero-overlay" aria-hidden="true"></div>\n'
        f'  <div class="brand-hero-content">\n'
        f'    <p class="eyebrow">Mazak Control Generation</p>\n'
        f'    <h1>{html.escape(s["title"])}</h1>\n'
        f'    <p>{html.escape(s["intro"])}</p>\n'
        f'    <div class="cta-row">\n'
        f'      <a class="cta-button" href="/get-a-quote/">Get a Quote</a>\n'
        f'      <a class="cta-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>\n\n'

        f'## Machines this control shipped on\n\n'
        f'{s["machines_paragraph"]}\n\n'

        f'## Common failures and fixes\n\n'
        f'{failure_bullets}\n\n'

        f'## Parts availability\n\n'
        f'{s["parts_paragraph"]}\n\n'

        f'## Battery, memory, and parameter recovery\n\n'
        f'{s["recovery_paragraph"]}\n\n'

        f'[Get a Quote](/get-a-quote/) · [{PHONE_DISPLAY}](tel:{PHONE_TEL})\n\n'

        f'## Related\n\n'
        f'<ul class="related-grid">'
        f'<li><a href="/repairs/mazak-cnc-machine-repair/"><span>All Mazak repair</span></a></li>'
        f'{sibling_cards}'
        f'</ul>\n'
    )
    return "\n".join(fm_lines) + body


def _emit_mazak_spokes(brand, brand_index):
    """Write all 9 Mazak spoke markdown files (6 series + 3 controls)
    into src/content/machine-repair/ so m2h picks them up on the next
    markdown_to_html.py pass."""
    out_dir = os.path.join(REPO, "src", "content", "machine-repair")
    n = 0
    for key in MAZAK_SERIES_SPOKES:
        md = render_mazak_series_spoke(key, brand, brand_index)
        path = os.path.join(out_dir, f"{MAZAK_SERIES_SPOKES[key]['slug']}.md")
        with open(path, "w") as f:
            f.write(md)
        n += 1
    for key in MAZAK_CONTROL_SPOKES:
        md = render_mazak_control_spoke(key, brand, brand_index)
        path = os.path.join(out_dir, f"{MAZAK_CONTROL_SPOKES[key]['slug']}.md")
        with open(path, "w") as f:
            f.write(md)
        n += 1
    return n


def render_mazak_hub(brand, g, brand_index):
    """The new Mazak hub — keeps the brand-hero from the previous
    iteration, adds the MachineLookup widget, the three Browse-by
    lenses, and an expanded FAQ. Replaces the standard machine-repair
    render output for Mazak only (other brands keep the existing
    template until they get their own spokes built)."""
    name = brand["brand_display_name"]
    slug = brand["slug"]
    ki = brand["ken_input"]
    models = ki["models"]

    h1_text = f"{name} CNC Machine Repair & Service"
    eyebrow_text = "CNC Machine Repair"
    canonical_path = f"/repairs/{slug}-cnc-machine-repair/"

    meta_desc = (
        f"Expert {name} CNC machine repair across the Midwest. "
        f"Browse by series, by control generation, or by service. "
        f"Find your model with our machine lookup."
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

    img_path, img_alt = hero_image_for(brand, "machine_repair")
    bg_img_html = (
        f'<img class="brand-hero-bg" src="{img_path}" alt="{html.escape(img_alt)}" loading="eager">\n'
        if img_path else ""
    )
    hero_lede = (
        f"We service the {name} platforms running on Midwest shop floors — "
        f"Quick Turn lathes, Integrex multitasking, Variaxis 5-axis, VTC and VCN "
        f"verticals, HCN horizontals, and legacy turning. Find your model below, "
        f"or browse by series, control generation, or service type."
    )

    # Browse-by-series list
    series_lis = "".join(
        f'<li><a href="{u}"><strong>{html.escape(name)}</strong> — {html.escape(desc)}</a></li>'
        for name, u, desc in MAZAK_HUB_BROWSE_SERIES
    )
    # Browse-by-control list
    control_lis = "".join(
        f'<li><a href="{u}"><strong>{html.escape(name)}</strong> — {html.escape(desc)}</a></li>'
        for name, u, desc in MAZAK_HUB_BROWSE_CONTROL
    )

    # FAQ accordions
    faq_items = []
    for q, a in MAZAK_HUB_FAQ:
        faq_items.append(
            f'<details class="faq-item">\n'
            f'  <summary>{html.escape(q)}</summary>\n'
            f'  <div class="faq-answer"><p>{html.escape(a)}</p></div>\n'
            f'</details>'
        )
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in MAZAK_HUB_FAQ
        ],
    }
    faq_schema_script = (
        '\n<script type="application/ld+json">\n'
        + json.dumps(faq_schema, indent=2, ensure_ascii=False)
        + '\n</script>\n'
    )

    trust = trust_block(g, brand["page_type"], brand_index, "a replacement machine")
    cross_links = brand_cross_links_section(brand, {})
    related = related_block_machine_repair(brand)

    hero = (
        f'<section class="brand-hero">\n'
        f'{bg_img_html}'
        f'  <div class="brand-hero-overlay" aria-hidden="true"></div>\n'
        f'  <div class="brand-hero-content">\n'
        f'    <p class="eyebrow">{eyebrow_text}</p>\n'
        f'    <h1>{html.escape(h1_text)}</h1>\n'
        f'    <p>{html.escape(hero_lede)}</p>\n'
        f'    <div class="cta-row">\n'
        f'      <a class="cta-button" href="/get-a-quote/">Get a Quote</a>\n'
        f'      <a class="cta-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>\n\n'
        f'{machine_lookup_html()}\n'
    )

    browse_series = (
        f'<h2 id="browse-by-series">Browse by Series</h2>\n'
        f'<p>Pick the {name} platform you run for failure patterns specific to that series.</p>\n'
        f'<ul class="browse-list">{series_lis}</ul>\n'
    )
    browse_control = (
        f'<h2 id="browse-by-control">Browse by Control Generation</h2>\n'
        f'<p>{name} machines span three Mazatrol generations. Pick yours for common faults and parts notes.</p>\n'
        f'<ul class="browse-list">{control_lis}</ul>\n'
    )
    browse_service = (
        f'<h2 id="browse-by-service">Browse by Service</h2>\n'
        f'<ul class="browse-list">\n'
        f'  <li><a href="/spindle-grinding/mazak-spindle-repair/"><strong>Mazak spindle repair</strong> — bearing-pack rebuilds, taper grinding, balancing, runout verification.</a></li>\n'
        f'  <li><a href="/way-covers/mazak-cnc-way-covers/"><strong>Mazak way covers</strong> — replacement bellows, telescoping steel, and roll-up covers, built to spec.</a></li>\n'
        f'  <li><a href="#faq"><strong>ATC, drive, and alignment work</strong> — covered in the FAQ below.</a></li>\n'
        f'</ul>\n'
    )

    what_brings = (
        f'<h2 id="what-brings-mazak-machines-in-for-repair">What brings {name} machines in for repair</h2>\n'
        f'<p>Most {name} repair calls fall into a few patterns: ATC faults on production verticals, drive system wear and ballscrew issues on long-bed VTCs, way alignment after a crash, spindle bearing failure on high-RPM VCN work, and pallet-changer issues on HCN horizontals. Control-side, the Matrix generation sees HDD failure as the single most common service item; legacy Mazatrol machines see memory battery and board obsolescence; current Smooth-generation machines come in for integration and configuration work rather than reactive repair. We diagnose what\'s actually broken before we quote.</p>\n'
    )

    how_we_approach = (
        f'<h2 id="how-we-approach-mazak-repair-work">How we approach {name} repair work</h2>\n'
        f'<p>Mazak machines run Mazatrol, so diagnostics are platform-specific. Our approach starts with the control generation — legacy Mazatrol, Matrix, or Smooth — because the failure modes and the recovery paths are different across the three. From there we move to mechanical: spindle, ATC, drive, alignment. The control spokes below cover the platform-specific recovery procedures for each generation.</p>\n'
    )

    lead_time = (
        f'<h2 id="lead-time-process">Lead Time &amp; Process</h2>\n'
        f"<p>Lead time on machine repair depends on what's wrong — diagnostic is fast, but parts and rebuild time vary by the job. Our three-step workflow keeps it transparent:</p>\n"
        f'<ol class="process-steps">\n'
        f'  <li><strong>Contact us.</strong> Call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> or use the quote form. Tell us the machine, the symptoms, and how urgent it is.</li>\n'
        f'  <li><strong>Review &amp; quote.</strong> We confirm the model and control generation, scope the work, and send back a price and realistic lead time within one business day on most inquiries.</li>\n'
        f'  <li><strong>Approve &amp; rebuild.</strong> We complete the repair, verify it back to spec, and return the machine ready to run.</li>\n'
        f'</ol>\n'
    )

    faq_section = (
        f'<h2 id="faq">Frequently Asked Questions</h2>\n'
        f'<div class="faq-list">\n'
        + "\n".join(faq_items) + "\n"
        + '</div>\n'
        + faq_schema_script
    )

    return (
        fm + hero
        + browse_series + browse_control + browse_service
        + what_brings + how_we_approach
        + lead_time + "\n" + trust + "\n" + faq_section + "\n"
        + cross_links + "\n" + related + "\n"
    )


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
    data. Target 250–350 visible body words.

    PILOT GATING: if the brand is Mazak, dispatch to the new hub-and-spoke
    template (render_mazak_hub). The other 17 brands still use the
    standard template below until they get their own spokes built."""
    if brand["slug"] == "mazak":
        return render_mazak_hub(brand, g, brand_index)
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
    eyebrow_text = f"CNC Machine Repair"
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

    img_path, img_alt = hero_image_for(brand, "machine_repair")
    model_inline = _format_models_inline(models)

    # New image-background hero — same visual language as the homepage
    # video hero. The image becomes a full-bleed background; text sits
    # centred over a dark gradient overlay.
    hero_lede = (
        f"When a {name} machine isn't producing the way it used to, we come in. "
        f"We work across the {name} lineup"
        f"{ ' — ' + model_inline if model_inline else '' } — "
        f"spindle, control, ATC, drive, and alignment work. "
        f"Lead time depends on what's wrong: diagnostics move fast, "
        f"parts and rebuild time vary by the job."
    )
    bg_img_html = (
        f'<img class="brand-hero-bg" src="{img_path}" alt="{html.escape(img_alt)}" loading="eager">\n'
        if img_path else ""
    )
    hero = (
        f'<section class="brand-hero">\n'
        f'{bg_img_html}'
        f'  <div class="brand-hero-overlay" aria-hidden="true"></div>\n'
        f'  <div class="brand-hero-content">\n'
        f'    <p class="eyebrow">{html.escape(eyebrow_text)}</p>\n'
        f'    <h1>{html.escape(h1_text)}</h1>\n'
        f'    <p>{html.escape(hero_lede)}</p>\n'
        f'    <div class="cta-row">\n'
        f'      <a class="cta-button" href="#quote">Get a Quote</a>\n'
        f'      <a class="cta-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>\n\n'
    )

    # Models — pill chips instead of a bullet list. Easier to scan.
    if models:
        model_lis = "".join(f'<li>{html.escape(m)}</li>' for m in models)
        models_section = (
            f'<h2 id="models-we-service">{html.escape(name)} Models We Service</h2>\n'
            f'<p>Our {html.escape(name)} repair work covers the full lineup:</p>\n'
            f'<ul class="model-chips">{model_lis}</ul>\n'
        )
    else:
        models_section = ""

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

    # Lead Time & Process — numbered process steps (HTML ol) so the
    # workflow gets the accented numbered-circle treatment from the
    # global .process-steps style.
    lead_section = (
        f'\n<h2 id="lead-time-process">Lead Time &amp; Process</h2>\n'
        f"<p>Lead time on machine repair depends on what's wrong — diagnostic "
        f"is fast, but parts and rebuild time vary by the job. Our three-step "
        f"workflow keeps it transparent:</p>\n"
        f'<ol class="process-steps">\n'
        f'  <li><strong>Contact us.</strong> Call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> or use the quote form. Tell us the machine, the symptoms, and how urgent it is.</li>\n'
        f'  <li><strong>Review &amp; quote.</strong> We confirm the model, scope the work, and send back a price and realistic lead time within one business day on most inquiries.</li>\n'
        f'  <li><strong>Approve &amp; rebuild.</strong> We complete the repair, verify it back to spec, and return the machine ready to run.</li>\n'
        f'</ol>\n'
    )

    trust = trust_block(g, brand["page_type"], brand_index, "a replacement machine")
    related = related_block_machine_repair(brand)
    cross_links = brand_cross_links_section(brand, {})
    faq_html, faq_schema = brand_faq_section(brand, ki, "machine_repair")
    # Blog teaser placeholder removed — was rendering as ghost text.

    return (
        fm + hero + models_section + issues_section + how
        + lead_section + "\n" + trust + "\n" + faq_html + "\n"
        + cross_links + "\n" + related + "\n"
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

            # --- Mazak pilot: emit 9 spoke markdowns (6 series + 3 controls)
            # alongside the hub. Other 5 brands will get their spokes once
            # Aaron approves Mazak.
            if b["slug"] == "mazak":
                n_spokes = _emit_mazak_spokes(b, bi)
                written.append(("mazak_spokes", b["slug"], OUTDIR_REPAIR,
                                n_spokes * 500, False))

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
