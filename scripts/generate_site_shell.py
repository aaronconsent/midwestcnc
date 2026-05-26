#!/usr/bin/env python3
"""
Phase 1 — site shell generator.

Builds: homepage, /about/, /get-a-quote/, four service hubs
(/repairs/, /spindle-grinding/, /way-covers/, /service-area/), the
404 page, sitemap.xml, robots.txt, and a SVG favicon. Updates
public/_redirects with the seven state-URL placeholders.

Imports CSS from markdown_to_html.py so the shell matches the brand
pages exactly. Adds SITE_SHELL_CSS for tile grids and the quote form.
"""

import html
import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import markdown_to_html as m2h
import generate_brand_pages as gbp


# ---------- Config ----------

REPO = m2h.REPO
PUBLIC = m2h.OUTDIR
CONTENT_BRAND_DIR = os.path.join(REPO, "src", "content", "spindle-brands")
CONTENT_REPAIR_DIR = os.path.join(REPO, "src", "content", "machine-repair")
CONTENT_COVERS_DIR = os.path.join(REPO, "src", "content", "way-covers")

DOMAIN = "https://midwestcncservices.com"
PHONE_DISPLAY = "319-610-4341"
PHONE_TEL = "+13196104341"
ADDRESS_CITY = "Waterloo"
ADDRESS_STATE = "IA"
WEB3FORMS_KEY = "14ef8440-a42b-4dd3-b416-30d9d6b3e906"

# Service-area state list (the 7 states Ken confirmed)
STATE_TILES = [
    ("Iowa",      "iowa",       "Des Moines, Davenport, Waterloo, Cedar Rapids",
     "/assets/images/general/view-all-iowa-cnc-service-locations.png"),
    ("Illinois",  "illinois",   "Chicago, Rockford, Peoria, Springfield",
     "/assets/images/general/illinois.png"),
    ("Wisconsin", "wisconsin",  "Milwaukee, Madison, Green Bay",
     "/assets/images/general/wisconsin.png"),
    ("Minnesota", "minnesota",  "St. Paul, Minneapolis, Rochester",
     "/assets/images/general/minnesota.png"),
    ("Nebraska",  "nebraska",   "Lincoln, Omaha, Grand Island",
     "/assets/images/general/nebraska.png"),
    ("Missouri",  "missouri",   "St. Louis, Kansas City, Springfield",
     "/assets/images/general/missouri.png"),
    ("Texas",     "texas",      "Dallas, Houston, Austin",
     "/assets/images/general/texas.png"),
]
STATE_NAMES = [n for n, *_ in STATE_TILES]

# Service tiles for the homepage — expanded descriptions (~50–60 words each)
# referencing specific brand coverage from spindle-brands.json.
SERVICE_TILES = [
    {
        "title": "Machine Repair",
        "href": "/repairs/",
        "image": "/assets/images/general/image-of-cnc-machine.png",
        "alt": "CNC machining center under service",
        "desc": ("CNC machine repair across spindle, control, ATC, drive, "
                 "and alignment work. We service Mazak, Haas, Okuma, DMG Mori, "
                 "Fanuc, Doosan, Brother, Hurco, and 12 other major OEM "
                 "platforms — plus Amada press brakes and Trumpf lasers. Field "
                 "troubleshooting where a remote diagnostic can save a teardown."),
    },
    {
        "title": "Way Covers",
        "href": "/way-covers/",
        "image": "/assets/images/general/image-of-way-covers.png",
        "alt": "Replacement CNC way covers",
        "desc": ("Replacement way covers in bellows, telescoping steel, and "
                 "roll-up styles. Built to spec for every CNC platform we "
                 "service — from Mazak Integrex multi-taskers and Haas VF "
                 "machines to legacy Fadal 4020s and Hitachi Seiki HMCs. Most "
                 "orders ship in 2–4 weeks. We measure from your original or "
                 "build to drawing."),
    },
    {
        "title": "Spindle Grinding",
        "href": "/spindle-grinding/",
        "image": "/assets/images/general/image-of-spindle-grinding.png",
        "alt": "CNC spindle on the grinding bench",
        "desc": ("Spindle rebuilds, regrinds, and rebalancing across 18 OEM "
                 "platforms — Mazak, Haas, Okuma, DMG Mori, Mori Seiki, Doosan, "
                 "and on through Fadal and Hitachi Seiki legacy work. Most "
                 "jobs run 2–6 weeks depending on bearing-pack damage and "
                 "parts availability. Each brand page has failure modes and "
                 "lead times."),
    },
]


# Homepage FAQ — 4 Q&As traceable to Ken's authorized emphasis themes
# (response, legacy, coverage, crash-recovery). Used both as visible HTML
# and as FAQPage JSON-LD.
HOMEPAGE_FAQ = [
    {
        "q": "How fast can you respond to a quote request?",
        "a": ("Most quote requests go out within one business day. If the "
              "machine is down and you need someone on the line right now, "
              "call 319-610-4341 — we'd rather talk through the symptoms "
              "than wait for an email back. Field troubleshooting on the "
              "phone often saves a full teardown."),
    },
    {
        "q": "Do you work on older or discontinued machines?",
        "a": ("Yes. We have dedicated brand pages and parts-sourcing "
              "approaches for Fadal, Hitachi Seiki, and Monarch — "
              "manufacturers whose CNC lines have been gone for years but "
              "whose machines are still cutting daily in Midwest shops. We "
              "lean on aftermarket suppliers, used-market sourcing, and "
              "custom-machined replacements where OEM components are gone."),
    },
    {
        "q": "Where do you work? Do you come on-site?",
        "a": ("We serve shops across Iowa, Illinois, Wisconsin, Minnesota, "
              "Nebraska, Missouri, and Texas from our Waterloo, Iowa shop. "
              "Field service when that's the right call for the job; spindle "
              "rebuilds and way-cover builds happen at our bench and ship "
              "back to you."),
    },
    {
        "q": "Can you recover a crashed spindle?",
        "a": ("Often, yes. Crash recovery is one of the threads of work "
              "that comes through here — taper damage, bearing-pack failure, "
              "alignment loss from impact. Customers are usually relieved "
              "to avoid the replacement lead times and the six-figure "
              "capital expense of a new spindle. Bring it in for a teardown."),
    },
]


# ---------- Shared chrome ----------

SITE_SHELL_CSS = """
/* =================================================================
   Site-shell additions: homepage, hubs, quote form, tiles, brand grid
   ================================================================= */

/* Early success-state toggle — set on <html> in <head> before paint */
.form-submitted-html .quote-form,
.form-submitted-html .quote-helpers { display: none; }
.form-submitted-html .success-message { display: block; }

.section-eyebrow {
  color: var(--accent);
  font-size: 0.78rem;
  font-style: normal;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin: 0 0 var(--s-3) 0;
  display: inline-block;
  padding: 0.3rem 0.7rem;
  background: rgba(184, 52, 26, 0.08);
  border-radius: var(--r-pill);
}

/* =================================================================
   Homepage hero — two-column with gradient backdrop band
   ================================================================= */
.page-section-hero {
  background:
    radial-gradient(circle at 18% 22%, rgba(184, 52, 26, 0.07), transparent 52%),
    radial-gradient(circle at 82% 78%, rgba(184, 52, 26, 0.05), transparent 56%),
    var(--bg);
}
.home-hero {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: var(--s-7);
  align-items: center;
  margin: 0;
  padding: var(--s-5) 0 var(--s-7) 0;
}
.home-hero-text { min-width: 0; }
.home-hero-text > h1 { margin-top: 0; font-size: clamp(2.2rem, 5vw, 3.3rem); }
.home-hero-text > p { font-size: 1.08rem; color: var(--muted); }
.home-hero-text > p:first-of-type { color: var(--fg); }
.home-hero-image { min-width: 0; }
.home-hero-image figure { margin: 0; padding: 0; }
.home-hero-image img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: var(--r-3);
  object-fit: cover;
  aspect-ratio: 4 / 3;
  box-shadow: var(--sh-4);
}
@media (max-width: 900px) {
  .home-hero {
    grid-template-columns: 1fr;
    gap: var(--s-5);
    padding: var(--s-3) 0 var(--s-5) 0;
  }
  .home-hero-image img { max-height: 360px; aspect-ratio: 16 / 10; }
}

/* =================================================================
   Tile grid (homepage services, state grid)
   ================================================================= */
.tile-grid, .state-grid {
  display: grid;
  gap: var(--s-4);
  margin: var(--s-5) 0 var(--s-6) 0;
}
.tile-grid { grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
.state-grid { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }

.tile {
  display: flex;
  flex-direction: column;
  text-decoration: none !important;
  color: var(--fg) !important;
  background: var(--surface);
  padding: var(--s-4);
  border-radius: var(--r-3);
  border: 1px solid var(--line);
  box-shadow: var(--sh-1);
  transition: transform var(--t-base), box-shadow var(--t-base), border-color var(--t-base);
  position: relative;
  overflow: hidden;
}
.tile::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: var(--r-3);
  background: linear-gradient(135deg, transparent 60%, rgba(184, 52, 26, 0.04));
  opacity: 0;
  transition: opacity var(--t-base);
  pointer-events: none;
}
.tile:hover {
  transform: translateY(-4px);
  box-shadow: var(--sh-4);
  border-color: var(--accent);
}
.tile:hover::after { opacity: 1; }
.tile img {
  width: 100%;
  height: 160px;
  object-fit: cover;
  border-radius: var(--r-2);
  margin-bottom: var(--s-3);
  display: block;
}
.tile h3 { margin: var(--s-1) 0 var(--s-2) 0; font-size: 1.15rem; }
.tile p { color: var(--muted); font-size: 0.95rem; margin: var(--s-2) 0 var(--s-3) 0; flex-grow: 1; }
.tile .learn-more {
  color: var(--accent);
  font-size: 0.9rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: gap var(--t-fast);
}
.tile:hover .learn-more { gap: 0.55rem; }

/* =================================================================
   Brand grid — hub pages
   ================================================================= */
.brand-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--s-3);
  margin: var(--s-4) 0 var(--s-6) 0;
  list-style: none;
  padding: 0;
}
.brand-grid li { margin: 0; }
.brand-grid a {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1rem;
  border: 1px solid var(--line);
  border-radius: var(--r-2);
  text-decoration: none !important;
  color: var(--fg) !important;
  font-weight: 600;
  background: var(--surface);
  box-shadow: var(--sh-1);
  transition: transform var(--t-fast), border-color var(--t-fast), color var(--t-fast), box-shadow var(--t-fast);
  position: relative;
}
.brand-grid a::after {
  content: "";
  display: inline-block;
  width: 7px;
  height: 7px;
  border-right: 2px solid currentColor;
  border-top: 2px solid currentColor;
  transform: rotate(45deg);
  opacity: 0.4;
  transition: transform var(--t-fast), opacity var(--t-fast);
}
.brand-grid a:hover {
  border-color: var(--accent);
  color: var(--accent) !important;
  transform: translateY(-2px);
  box-shadow: var(--sh-3);
}
.brand-grid a:hover::after { opacity: 1; transform: rotate(45deg) translate(2px, -2px); }

/* =================================================================
   State sections (hub) + state grid tiles
   ================================================================= */
.state-section {
  margin: var(--s-6) 0;
  padding: var(--s-5);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-1);
}
.state-section h2 { margin-top: 0; }
.state-section h2::before { display: none; }
.state-cities { color: var(--muted); margin: var(--s-1) 0 var(--s-3) 0; }

/* =================================================================
   Quote form
   ================================================================= */
.quote-form {
  display: flex;
  flex-direction: column;
  gap: var(--s-4);
  max-width: 560px;
  margin: var(--s-6) 0;
  padding: var(--s-5);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-3);
  box-shadow: var(--sh-2);
}
.quote-form .field { display: flex; flex-direction: column; gap: 0.4rem; }
.quote-form label { font-weight: 600; font-size: 0.92rem; color: var(--fg); }
.quote-form .required::after { content: " *"; color: var(--accent); }
.quote-form input,
.quote-form textarea,
.quote-form select {
  font: inherit;
  padding: 0.75rem 0.9rem;
  border: 1.5px solid var(--line);
  border-radius: var(--r-2);
  background: var(--surface);
  width: 100%;
  transition: border-color var(--t-fast), box-shadow var(--t-fast);
}
.quote-form input:hover,
.quote-form textarea:hover,
.quote-form select:hover { border-color: var(--muted); }
.quote-form input:focus,
.quote-form textarea:focus,
.quote-form select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: var(--sh-focus);
}
.quote-form textarea { min-height: 9rem; resize: vertical; }
.quote-form .radio-group { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: var(--s-2); }
.quote-form .radio-group label {
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.55rem 0.8rem;
  border: 1.5px solid var(--line);
  border-radius: var(--r-2);
  background: var(--surface);
  transition: border-color var(--t-fast), background var(--t-fast);
}
.quote-form .radio-group label:hover { border-color: var(--muted); background: var(--surface-2); }
.quote-form .radio-group input[type="radio"] { accent-color: var(--accent); }
.quote-form button {
  font: inherit;
  background: var(--accent);
  color: #fff;
  padding: 0.95rem 1.6rem;
  border: 0;
  border-radius: var(--r-pill);
  font-weight: 700;
  cursor: pointer;
  align-self: flex-start;
  box-shadow: var(--sh-2);
  transition: background var(--t-fast), transform var(--t-fast), box-shadow var(--t-fast);
}
.quote-form button:hover { background: var(--accent-dark); transform: translateY(-1px); box-shadow: var(--sh-3); }
.quote-form button:active { transform: translateY(0); box-shadow: var(--sh-1); }
.quote-form .honeypot { position: absolute; left: -9999px; opacity: 0; pointer-events: none; }

.success-message {
  display: none;
  padding: var(--s-5);
  border-radius: var(--r-3);
  background: var(--success-bg);
  border: 1px solid rgba(46, 125, 50, 0.25);
  border-left: 4px solid #2e7d32;
  color: var(--success-fg);
  margin: var(--s-6) 0;
  box-shadow: var(--sh-1);
}
.success-message h2 { margin-top: 0; color: var(--success-fg); }
.success-message h2::before { background: #2e7d32; }
body.form-submitted .success-message { display: block; }
body.form-submitted .quote-form { display: none; }
body.form-submitted .quote-helpers { display: none; }

.alt-contact {
  margin: var(--s-6) 0;
  padding: var(--s-5);
  background: var(--surface-2);
  border-radius: var(--r-3);
  border: 1px solid var(--line);
}
.alt-contact h3 { margin: 0 0 var(--s-2) 0; }
.alt-contact p { margin: var(--s-1) 0; }
"""


def head_html(title, description, canonical, schema_blocks, extra_head=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{html.escape(canonical)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="website">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap">
<style>
{m2h.CSS}{SITE_SHELL_CSS}</style>
<script>
  // Early success-state detection — runs in <head> before paint so the form
  // never flashes visible if the URL has ?success=1. Harmless on other pages.
  if (location.search.indexOf('success=1') !== -1) {{
    document.documentElement.classList.add('form-submitted-html');
  }}
</script>
{schema_blocks}
{extra_head}
</head>"""


SITE_HEADER = m2h.build_site_header()

SITE_FOOTER = """<footer class="site-footer">
  <p>Midwest CNC Services · 319-610-4341 · Waterloo, Iowa</p>
  <p>Serving shops across Iowa, Illinois, Minnesota, Wisconsin, Nebraska, Missouri, and Texas.</p>
</footer>"""

MOBILE_CTA = """<div class="mobile-cta-bar" role="region" aria-label="Quick contact">
  <a class="mcta-phone" href="tel:+13196104341">☎ 319-610-4341</a>
  <a class="mcta-quote" href="/get-a-quote/">Get a Quote</a>
</div>"""


def breadcrumbs_html(items):
    """items: list of (name, href). The last item is the current page; href may be None to render as text."""
    if not items:
        return ""
    lis = []
    for i, (name, href) in enumerate(items):
        if href and i < len(items) - 1:
            lis.append(f'<li><a href="{html.escape(href)}">{html.escape(name)}</a></li>')
        else:
            lis.append(f'<li>{html.escape(name)}</li>')
    return f'<nav class="breadcrumbs" aria-label="breadcrumb">\n  <ol>\n    {"".join(lis)}\n  </ol>\n</nav>'


def wrap_page(*, title, description, canonical, schema_blocks, crumbs_html_str, body_html, layout="default"):
    """layout='default' (--max readable column), 'wide' (--max-wide for
    homepage + hubs with tiles, brand grids, and other landscape content).
    Body is split into alternating-color full-bleed sections at <h2>
    boundaries."""
    body_class = f' class="layout-{layout}"' if layout != "default" else ""
    banded = m2h.wrap_into_sections(body_html, layout=layout)
    return f"""{head_html(title, description, canonical, schema_blocks)}
<body{body_class}>
<a class="skip-link" href="#main">Skip to content</a>
{SITE_HEADER}
{crumbs_html_str}
<main id="main">
<article>
{banded}
</article>
</main>
{SITE_FOOTER}
{MOBILE_CTA}
</body>
</html>
"""


# ---------- Shared content blocks ----------

CERT_BLOCK = (
    "Experienced field technicians with hands-on time across the major CNC OEM "
    "platforms, in-house precision spindle balancing capability, laser alignment "
    "services, and established relationships with aftermarket bearing and spindle "
    "component suppliers."
)

QUOTE_OPENER = "\"Honestly, we thought the machine was done for.\""
QUOTE_FRAMING_A = ("Most customers tell us they're relieved to avoid replacement "
                   "lead times and six-figure capital expenses.")


def trust_block_html():
    return (
        '<h2 id="why-shops-trust-us">Why Shops Trust Us</h2>\n'
        f'<p>{CERT_BLOCK}</p>\n'
        f'<blockquote><p>{html.escape(QUOTE_OPENER)} {QUOTE_FRAMING_A}</p></blockquote>\n'
    )


def hero_cta_html(label="Get a Quote", href="/get-a-quote/"):
    return (
        f'<div class="cta-row">'
        f'<a class="cta-button" href="{href}">{label}</a>'
        f'<a class="cta-phone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>'
        f'</div>'
    )


# ---------- Schema builders ----------

def organization_localbusiness_schema():
    """Authoritative LocalBusiness schema for the homepage.
    Phase 4C: includes geo coordinates for Waterloo, IA (Wikipedia infobox)
    and hasMap link to Google Maps."""
    blocks = []
    blocks.append({
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": f"{DOMAIN}/#org",
        "name": "Midwest CNC Services",
        "url": f"{DOMAIN}/",
        "telephone": PHONE_TEL,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": ADDRESS_CITY,
            "addressRegion": ADDRESS_STATE,
            "addressCountry": "US",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": 42.4928,
            "longitude": -92.3426,
        },
        "hasMap": "https://www.google.com/maps/place/Waterloo,+IA",
        "areaServed": STATE_NAMES,
    })
    return blocks


def hub_itemlist_schema(hub_title, items):
    """Phase 4B: ItemList schema for service hub brand grids.
    items: list of {name, url} dicts."""
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": hub_title,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": item["name"],
                "url": item["url"],
            }
            for i, item in enumerate(items)
        ],
    }


def hub_faq_schema(qa_pairs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in qa_pairs
        ],
    }


def hub_faq_html(qa_pairs):
    items = []
    for q, a in qa_pairs:
        items.append(
            f'<details class="faq-item">\n'
            f'  <summary>{html.escape(q)}</summary>\n'
            f'  <div class="faq-answer"><p>{html.escape(a)}</p></div>\n'
            f'</details>'
        )
    return (
        '<h2 id="faq">Frequently Asked Questions</h2>\n'
        '<div class="faq-list">\n'
        + "\n".join(items) + "\n"
        + '</div>\n'
    )


def faqpage_schema(qa_pairs):
    """Build a FAQPage JSON-LD from a list of {q, a} dicts."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": qa["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": qa["a"],
                },
            }
            for qa in qa_pairs
        ],
    }


def breadcrumb_schema(items):
    """Build a BreadcrumbList JSON-LD from items list [(name, absolute_url), ...]."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(items)
        ],
    }


def schema_script_tags(schemas):
    """Take a list of schema dicts and return inline <script> tags."""
    return "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(s, indent=2, ensure_ascii=False)}\n</script>'
        for s in schemas
    )


# ---------- Per-page body builders ----------

def homepage_body():
    """Scrubbed hero, service tiles, state tiles, trust block, closing CTA."""
    # Hero — scrubbed from pages.json["/"]. The Durable copy claimed
    # "certified techs", "transparent quotes", "unmatched response times" —
    # all replaced with Ken-authorized language.
    states_inline = ", ".join(STATE_NAMES[:-1]) + ", and " + STATE_NAMES[-1]

    hero = f"""<section class="home-hero">
  <div class="home-hero-text">
    <p class="eyebrow">Stop Losing Money</p>
    <h1>When Your Machine Stops, We Start</h1>
    <p>At Midwest CNC Services we provide CNC repair, spindle work, and replacement way covers across the U.S. Midwest. When a machine goes down, our experienced field technicians come out to diagnose and get you back to cutting. From spindle rebuilds and machine repair to custom way covers we ship anywhere, the goal is the same — keep your shop producing.</p>
    <p>We serve shops in {states_inline}.</p>
    {hero_cta_html()}
  </div>
  <div class="home-hero-image">
    <figure><img src="/assets/images/general/home-image.png" alt="Midwest CNC Services shop floor" loading="eager"></figure>
  </div>
</section>
"""

    # Service tiles
    tiles_html = []
    for t in SERVICE_TILES:
        tiles_html.append(
            f'<a class="tile" href="{t["href"]}">'
            f'<img src="{t["image"]}" alt="{html.escape(t["alt"])}" loading="lazy">'
            f'<h3>{html.escape(t["title"])}</h3>'
            f'<p>{html.escape(t["desc"])}</p>'
            f'<span class="learn-more">Learn More →</span>'
            f'</a>'
        )
    services = (
        '<h2 id="our-services">Our Services</h2>\n'
        '<p>Three lines of work, one shop. We do machine repair on production CNC equipment, manufacture replacement way covers to spec, and rebuild and grind spindles back to factory tolerance — across every major OEM platform we service.</p>\n'
        f'<div class="tile-grid">{"".join(tiles_html)}</div>\n'
    )

    # State tiles
    state_tile_html = []
    for name, slug, cities, image in STATE_TILES:
        state_tile_html.append(
            f'<a class="tile" href="/service-area/{slug}/">'
            f'<img src="{image}" alt="{html.escape(name)} CNC service coverage" loading="lazy">'
            f'<h3>{html.escape(name)}</h3>'
            f'<p>{html.escape(cities)}</p>'
            f'<span class="learn-more">Learn More →</span>'
            f'</a>'
        )
    state_section = (
        '<h2 id="service-areas">Service Areas</h2>\n'
        '<p>We work with shops across seven Midwest and South-Central states. '
        'Production environments and job shops across the Midwest, plus '
        'specialty work where brand-specific expertise matters — from '
        'high-precision Makino aerospace and mold-die customers to legacy '
        'Fadal and Hitachi Seiki rebuilds. Field troubleshooting where a '
        'remote diagnostic can save a teardown.</p>\n'
        f'<div class="state-grid">{"".join(state_tile_html)}</div>\n'
    )

    # How We Work — condensed workflow that matches the brand pages.
    how_we_work = (
        '<h2 id="how-we-work">How We Work</h2>\n'
        '<p>Same three steps every brand page describes:</p>\n'
        '<ol class="process-steps">\n'
        '  <li><strong>Contact Us.</strong> Call 319-610-4341 or use the quote form. Tell us the machine, the symptoms, and how urgent it is.</li>\n'
        '  <li><strong>Grab Model #.</strong> We\'ll fire back price, lead time, and shipping ETA after reviewing your details.</li>\n'
        '  <li><strong>Approve &amp; Rebuild.</strong> We complete the work, verify it back to spec, and return the machine ready to run.</li>\n'
        '</ol>\n'
    )

    # Trust block
    trust = trust_block_html()

    # FAQ — 4 Q&As, structurally mirrors the FAQPage JSON-LD in <head>.
    faq_items = []
    for i, qa in enumerate(HOMEPAGE_FAQ):
        faq_items.append(
            f'<details class="faq-item" id="faq-{i+1}">\n'
            f'  <summary>{html.escape(qa["q"])}</summary>\n'
            f'  <div class="faq-answer"><p>{html.escape(qa["a"])}</p></div>\n'
            f'</details>'
        )
    faq_section = (
        '<h2 id="faq">Common Questions</h2>\n'
        '<div class="faq-list">\n'
        + "\n".join(faq_items) + "\n"
        + '</div>\n'
    )

    # Closing CTA (scrubbed — Durable said "24/7" and "transparent" and "fast quotes")
    closing = (
        '<h2 id="downtime">Don\'t Let Downtime Drain Your Profits</h2>\n'
        '<p>Every minute your CNC sits idle is money out the door. Call us with the machine and the issue — most quotes go out within one business day, and we\'ll get you back to cutting.</p>\n'
        f'{hero_cta_html()}\n'
    )

    return hero + services + state_section + how_we_work + trust + faq_section + closing


def about_body():
    """Rebuilt About — no fabricated business-age claims, no 'tighter than OEM',
    no 'beat the spec'. Only verifiable facts + Ken's authorized capabilities."""

    body = []
    body.append('<h1>About Midwest CNC Services</h1>')
    body.append(
        '<p>Midwest CNC Services is based in Waterloo, Iowa. We provide CNC '
        'machine repair, spindle rebuild and grinding, and replacement way '
        'covers to shops across Iowa, Illinois, Wisconsin, Minnesota, '
        'Nebraska, Missouri, and Texas.</p>'
    )

    body.append('<h2 id="what-we-do">What We Do</h2>')
    body.append(
        '<p>Three lines of service, organized so you can find the work you need:</p>'
    )
    tile_html = []
    for t in SERVICE_TILES:
        tile_html.append(
            f'<a class="tile" href="{t["href"]}">'
            f'<h3>{html.escape(t["title"])}</h3>'
            f'<p>{html.escape(t["desc"])}</p>'
            f'<span class="learn-more">Learn More →</span>'
            f'</a>'
        )
    body.append(f'<div class="tile-grid">{"".join(tile_html)}</div>')

    body.append('<h2 id="where-we-work">Where We Work</h2>')
    body.append(
        '<p>Our service area covers seven states across the Midwest and South-Central US. '
        'See the <a href="/service-area/">service-area hub</a> for the city-level coverage. '
        'States we work in:</p>'
    )
    state_html = []
    for name, slug, cities, _img in STATE_TILES:
        state_html.append(
            f'<li><strong>{html.escape(name)}</strong> — {html.escape(cities)}</li>'
        )
    body.append(f'<ul>{"".join(state_html)}</ul>')

    body.append('<h2 id="why-shops-choose-us">Why Shops Choose Us</h2>')
    body.append(f'<p>{CERT_BLOCK}</p>')
    body.append(
        f'<blockquote><p>{html.escape(QUOTE_OPENER)} {QUOTE_FRAMING_A}</p></blockquote>'
    )

    body.append(hero_cta_html())

    return "\n".join(body) + "\n"


def quote_body(brands):
    """The Get-a-Quote form page. Web3Forms handles submission."""
    # Brand dropdown options, alphabetical
    options = sorted(b["brand_display_name"] for b in brands)
    option_tags = ['<option value="">Select a brand…</option>']
    for opt in options:
        option_tags.append(f'<option value="{html.escape(opt)}">{html.escape(opt)}</option>')
    option_tags.append('<option value="Other">Other</option>')
    options_html = "\n              ".join(option_tags)

    body = f'''<h1>Get a Quote</h1>
<p>Tell us about your machine and we'll get back to you with pricing and lead time. Most quotes go out within one business day.</p>

<div class="success-message" id="success">
  <h3>Thanks — we got it.</h3>
  <p>We'll be in touch within one business day. If it's urgent, call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p>
</div>

<div class="quote-helpers">
  <h2 id="what-well-need">What we'll need from you</h2>
  <p>The faster we can give you a real number, the faster you're back to cutting. Helpful to have ready:</p>
  <ul>
    <li>Machine make, model, and approximate age</li>
    <li>Symptoms or error codes you're seeing</li>
    <li>How long the machine has been down (if it's down)</li>
    <li>Photos of the spindle, control screen, or affected area if relevant</li>
  </ul>
</div>

<form class="quote-form" action="https://api.web3forms.com/submit" method="POST">
  <input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
  <input type="hidden" name="subject" value="Quote request: {{{{machine_brand}}}} {{{{service}}}}">
  <input type="hidden" name="from_name" value="Midwest CNC Services Website">
  <input type="hidden" name="redirect" value="{DOMAIN}/get-a-quote/?success=1">

  <div class="field">
    <label class="required" for="name">Your name</label>
    <input id="name" name="name" type="text" required autocomplete="name">
  </div>

  <div class="field">
    <label class="required" for="company">Company</label>
    <input id="company" name="company" type="text" required autocomplete="organization">
  </div>

  <div class="field">
    <label class="required" for="phone">Phone</label>
    <input id="phone" name="phone" type="tel" required autocomplete="tel" placeholder="319-555-1234">
  </div>

  <div class="field">
    <label class="required" for="email">Email</label>
    <input id="email" name="email" type="email" required autocomplete="email">
  </div>

  <div class="field">
    <label for="machine_brand">Machine brand</label>
    <select id="machine_brand" name="machine_brand">
              {options_html}
    </select>
  </div>

  <div class="field">
    <label for="machine_model">Machine model</label>
    <input id="machine_model" name="machine_model" type="text" placeholder="e.g. Integrex i-200, VF-3, Genos M460">
  </div>

  <div class="field">
    <span class="label required" style="font-weight:600;">Service needed</span>
    <div class="radio-group">
      <label><input type="radio" name="service" value="Spindle" required> Spindle work</label>
      <label><input type="radio" name="service" value="Machine Repair"> Machine repair</label>
      <label><input type="radio" name="service" value="Way Covers"> Way covers</label>
      <label><input type="radio" name="service" value="Other"> Other</label>
    </div>
  </div>

  <div class="field">
    <label class="required" for="message">Describe the issue</label>
    <textarea id="message" name="message" required placeholder="Symptoms, error codes, what changed, how urgent…"></textarea>
  </div>

  <!-- Honeypot — leave blank, bots fill it in -->
  <div class="honeypot" aria-hidden="true">
    <label for="botcheck">Leave this field empty</label>
    <input id="botcheck" type="checkbox" name="botcheck" value="">
  </div>

  <button type="submit">Send Quote Request</button>
</form>

<div class="alt-contact">
  <h3>Rather call?</h3>
  <p><a href="tel:{PHONE_TEL}"><strong>{PHONE_DISPLAY}</strong></a> — we'll talk through the machine and the symptoms.</p>
  <p>Midwest CNC Services · Waterloo, IA</p>
</div>

<script>
  if (location.search.indexOf('success=1') !== -1) {{
    document.body.classList.add('form-submitted');
    var s = document.getElementById('success');
    if (s) s.scrollIntoView({{behavior: 'smooth'}});
  }}
</script>
'''
    return body


# ---------- Hub bodies ----------

def _brand_list_html(brands, *, link_for):
    """Build a brand grid. link_for: callable taking brand → (label, url) or None to skip."""
    items = []
    for b in sorted(brands, key=lambda x: x["brand_display_name"]):
        pair = link_for(b)
        if pair is None:
            continue
        label, url = pair
        items.append(f'<li><a href="{url}">{html.escape(label)}</a></li>')
    return f'<ul class="brand-grid">{"".join(items)}</ul>'


def repairs_hub_body(brands):
    body = []
    body.append('<p class="eyebrow">CNC Machine Repair</p>')
    body.append('<h1>CNC Machine Repair Across the Midwest</h1>')
    body.append(
        '<p>When a CNC machine goes down, the call we hear most is the '
        'same: get production back online. We service spindles, controls, '
        'ATC systems, drives, and alignment across every major OEM platform — '
        'plus Amada press brakes and Trumpf laser-cutting systems. Field '
        'troubleshooting where it can save a teardown; full rebuilds on the '
        'bench when that\'s what the job calls for.</p>'
    )
    body.append(hero_cta_html())
    body.append(
        '<figure class="hero-figure"><img src="/assets/images/general/image-of-cnc-machine.png" '
        'alt="CNC machining center under service" loading="lazy"></figure>'
    )

    # Expanded overview (Phase 4B)
    body.append('<h2 id="when-you-need-this">When You Need Machine Repair</h2>')
    body.append(
        "<p>The patterns that bring CNC machines to our shop fall into a few "
        "buckets: spindle issues (bearing-pack failure, runout, taper damage), "
        "control problems (alarms that don't reset, communication faults, "
        "encoder issues), ATC faults (drawbar wear, tool-change timing), drive "
        "system wear, and way alignment that's drifted out of spec after a "
        "crash or years of production. Most calls come in after the shop has "
        "tried the obvious and is now trying to decide whether to rebuild or "
        "replace. We diagnose what's actually broken before we quote — "
        "sometimes what looks like a spindle problem is something cheaper.</p>"
    )

    body.append('<h2 id="brands-we-service">Brands We Service</h2>')
    body.append(
        '<p>Every brand we repair has its own page with model coverage, '
        'lead-time notes, and what we typically see come in:</p>'
    )

    def link_for_repair(b):
        if b["page_type"] == "cnc_spindle":
            return (b["brand_display_name"], f"/repairs/{b['slug']}-cnc-machine-repair/")
        return (b["brand_display_name"], b["current_url"])

    body.append(_brand_list_html(brands, link_for=link_for_repair))

    body.append('<h2 id="how-service-works">How Service Works</h2>')
    body.append(
        '<ol class="process-steps">\n'
        '  <li><strong>Contact us.</strong> Tell us the machine and the symptoms — call 319-610-4341 or use the quote form. We respond same business day on most inquiries.</li>\n'
        '  <li><strong>Review &amp; quote.</strong> After looking at the model, the symptoms, and any photos you can send, we send back a price and a realistic lead time.</li>\n'
        '  <li><strong>Approve &amp; rebuild.</strong> We complete the work, verify it back to spec, and return the machine ready to run. Most jobs run 3–6 weeks depending on brand, failure mode, and parts availability.</li>\n'
        '</ol>'
    )

    body.append('<h2 id="industries-we-serve">Industries We Serve</h2>')
    body.append(
        "<p>Aerospace and defense, agricultural equipment, heavy machinery, "
        "medical devices, automotive supply chain, oil-and-gas equipment, "
        "food processing, and the general job-shop base across our seven-"
        "state service area. Brand specialization tends to follow industry "
        "— Makino in aerospace and mold/die, Mazak across ag and heavy, "
        "Brother Speedio in medical-device precision.</p>"
    )

    body.append(trust_block_html())

    # FAQ
    qa = [
        ("What does a typical CNC machine repair cost?",
         "Pricing depends on the diagnostic — we don't quote without scoping the actual work. Most quotes go out within one business day of getting the machine, model, and symptom description. Expect rebuild quotes to come with a lead time and a parts breakdown."),
        ("Do you service older machines from defunct manufacturers?",
         "Yes. Fadal, Hitachi Seiki, Monarch, and Giddings & Lewis platforms — all manufacturers whose CNC lines ended years ago — remain part of our routine work. We source parts from aftermarket suppliers, used inventory, and custom-machining where OEM components are gone."),
        ("Can you come on-site or do machines have to come to your shop?",
         "Both. Field service is part of routine work across Iowa and adjacent states; for substantial diagnostic work and bundled jobs we drive into Illinois, Wisconsin, Minnesota, Nebraska, and Missouri. Texas and far-out cities run ship-in via standard freight. Bench rebuilds happen at our Waterloo, IA shop."),
    ]
    body.append(hub_faq_html(qa))
    body.append(hero_cta_html())

    return "\n".join(body) + "\n", qa


def spindle_hub_body(brands):
    body = []
    body.append('<p class="eyebrow">Spindle Grinding & Repair</p>')
    body.append('<h1>CNC Spindle Repair, Rebuilds, and Grinding</h1>')
    body.append(
        '<p>Spindle work is our most-requested service. We rebuild, regrind, '
        'and rebalance to factory tolerance across the eighteen OEM platforms '
        'below. Most jobs run two to six weeks depending on brand and parts '
        'availability — each brand page has the specifics from our '
        'technicians.</p>'
    )
    body.append(hero_cta_html())
    body.append(
        '<figure class="hero-figure"><img src="/assets/images/general/image-of-spindle-grinding.png" '
        'alt="CNC spindle on the grinding bench" loading="lazy"></figure>'
    )

    body.append('<h2 id="when-you-need-this">When You Need Spindle Service</h2>')
    body.append(
        "<p>Spindles come to us in a few patterns: bearing-pack wear from "
        "high-RPM production, taper damage from a crash or toolholder failure, "
        "preload loss showing up as runout in finish work, encoder "
        "contamination, and coolant-intrusion damage that's gone past the "
        "warning signs. Sometimes the call is preventive — the shop noticed "
        "chatter or surface-finish degradation and wants the spindle pulled "
        "before it fails outright. We diagnose the damage on teardown and "
        "scope the rebuild from there.</p>"
    )

    body.append('<h2 id="brands-we-service">Brands We Service</h2>')
    body.append('<p>Pick your brand for failure modes, models, and lead-time expectations:</p>')

    def link_for_spindle(b):
        if not b.get("services_offered", {}).get("spindle"):
            return None
        return (b["brand_display_name"], f"/spindle-grinding/{b['slug']}-spindle-repair/")

    body.append(_brand_list_html(brands, link_for=link_for_spindle))

    body.append('<h2 id="how-service-works">How Service Works</h2>')
    body.append(
        '<ol class="process-steps">\n'
        '  <li><strong>Contact us with the spindle details.</strong> Brand, model, symptoms, and any noise/runout/heat data you have. Photos help if the housing is accessible.</li>\n'
        '  <li><strong>Quote &amp; lead time.</strong> We review and respond with a flat-or-range price plus a realistic lead time for the rebuild.</li>\n'
        '  <li><strong>Rebuild, verify, ship.</strong> Bearing-pack replacement, shaft repair, taper grinding, and dynamic balancing — routine across all 18 OEM platforms. We verify balance and runout, then ship back ready to install.</li>\n'
        '</ol>'
    )

    body.append('<h2 id="industries-we-serve">Industries We Serve</h2>')
    body.append(
        "<p>Aerospace and mold/die work (Makino-heavy), medical-device "
        "precision (Brother Speedio, Makino), heavy-equipment and ag (Mazak, "
        "Toyoda, Doosan), automotive supply chain (broad coverage), and "
        "legacy CNC platforms still in production (Fadal, Hitachi Seiki, "
        "Monarch) across our seven-state Midwest service area.</p>"
    )

    body.append(trust_block_html())

    qa = [
        ("How long does a typical spindle rebuild take?",
         "Most spindle rebuilds run 2-6 weeks depending on brand, failure mode, and parts availability. Mazak Integrex and DMG Mori multi-tasking work tends toward the longer end; Haas, Doosan, and Hurco platforms typically come back faster."),
        ("Do you ship spindles back nationally?",
         "Yes. We ship rebuilt spindles to any continental US destination. Return shipping is included in most rebuild quotes. Standard freight, with packaging and crating handled at our shop."),
        ("Can you grind taper damage from a crash?",
         "Often yes. Crash recovery is a routine pattern — taper damage, bearing-pack failure, alignment loss from impact. We grind the taper back to spec where the shaft survives the impact; we recommend replacement when the geometry won't recover."),
    ]
    body.append(hub_faq_html(qa))
    body.append(hero_cta_html())

    return "\n".join(body) + "\n", qa


def way_covers_hub_body(brands):
    body = []
    body.append('<p class="eyebrow">CNC Way Covers</p>')
    body.append('<h1>Replacement CNC Way Covers — Built to Spec</h1>')
    body.append(
        '<p>We manufacture replacement way covers in bellows, telescoping '
        'steel, and roll-up styles to fit the machine in front of you. Most '
        'orders ship in two to four weeks depending on dimensions and '
        'material. Send us the original or the machine specs and we\'ll '
        'match or build to drawing.</p>'
    )
    body.append(hero_cta_html())
    body.append(
        '<figure class="hero-figure"><img src="/assets/images/general/image-of-way-covers.png" '
        'alt="Replacement CNC way covers manufactured by Midwest CNC Services" loading="lazy"></figure>'
    )

    body.append('<h2 id="when-you-need-this">When You Need Replacement Way Covers</h2>')
    body.append(
        "<p>Way covers get replaced for a few reasons: chip and coolant "
        "intrusion has worn the existing cover beyond its useful life, the "
        "shop is upgrading machine guards for a particular operation, the "
        "OEM no longer sells replacement covers for an older machine, or a "
        "crash damaged the cover and the machine is down waiting for it. "
        "Most jobs start with the original cover or measurements of the way "
        "system; we build to that spec.</p>"
    )

    body.append('<h2 id="brands-we-build-for">Brands We Build For</h2>')
    body.append(
        '<p>Brand-specific way-cover pages include the model coverage and '
        'photos of typical builds:</p>'
    )

    def link_for_way_covers(b):
        so = b.get("services_offered", {})
        if not so.get("way_covers"):
            return None
        if b.get("way_covers_verification_pending"):
            return None
        return (b["brand_display_name"], f"/way-covers/{b['slug']}-cnc-way-covers/")

    body.append(_brand_list_html(brands, link_for=link_for_way_covers))

    body.append('<h2 id="how-service-works">How Service Works</h2>')
    body.append(
        '<ol class="process-steps">\n'
        '  <li><strong>Send measurements or the original cover.</strong> We work from either — overall dimensions, way spacing, mounting details, or the failed cover itself.</li>\n'
        '  <li><strong>Quote the build.</strong> We confirm style (bellows, telescoping steel, or roll-up), material, and lead time.</li>\n'
        '  <li><strong>Fabricate &amp; ship.</strong> On approval we build to spec and ship anywhere in the continental US. Most orders are out the door in 2–4 weeks; rush options are available.</li>\n'
        '</ol>'
    )

    body.append('<h2 id="industries-we-serve">Industries We Serve</h2>')
    body.append(
        "<p>Heavy-equipment manufacturing, aerospace, ag-equipment supply "
        "chain, mold/die, and the broader job-shop base. Older machine "
        "inventory (Fadal, Hitachi Seiki, Monarch) is a strong driver — "
        "OEM cover replacement is often discontinued, and we build "
        "drop-in replacements that match the original.</p>"
    )

    body.append(trust_block_html())

    qa = [
        ("What way-cover styles do you build?",
         "Three styles: bellows for protected ways with limited debris, telescoping steel for heavier chip and coolant environments, and roll-up for retrofits and specific clearance constraints. We match the original or build to drawing."),
        ("Can you build for older machines whose OEM covers are discontinued?",
         "Yes. We routinely build replacement way covers for Fadal, Hitachi Seiki, Monarch, and other legacy machine platforms where the OEM no longer supplies covers. Measure from the original or the machine; we'll build to those dimensions."),
        ("How fast can you ship a replacement way cover?",
         "Most way-cover orders ship in 2-4 weeks depending on dimensions and material. We offer rush options for machine-down situations — call to discuss what's possible for your timeline."),
    ]
    body.append(hub_faq_html(qa))
    body.append(hero_cta_html())

    return "\n".join(body) + "\n", qa


def service_area_hub_body():
    """Service-area hub — links out to the 7 state pages now that they
    exist. The Phase 1 in-page anchor sections are gone; each state has
    its own page."""
    body = []
    body.append('<p class="eyebrow">Service Areas</p>')
    body.append('<h1>Midwest CNC Service Coverage</h1>')
    body.append(
        '<p>We work with production shops, job shops, and OEM customers '
        'across seven states from our Waterloo, Iowa location. Field '
        'service where it can save a teardown; bench work and shipped '
        'builds when that\'s what the repair calls for.</p>'
    )
    body.append(hero_cta_html())

    # State tile grid linking to the real state pages
    body.append('<h2 id="states-we-serve">States We Serve</h2>')
    body.append(
        '<p>Pick a state for local coverage detail and the cities we serve there:</p>'
    )
    tiles = []
    for name, slug, cities, image in STATE_TILES:
        tiles.append(
            f'<a class="tile" href="/service-area/{slug}/">'
            f'<img src="{image}" alt="{html.escape(name)} CNC service coverage" loading="lazy">'
            f'<h3>{html.escape(name)}</h3>'
            f'<p>{html.escape(cities)}</p>'
            f'<span class="learn-more">Learn More →</span>'
            f'</a>'
        )
    body.append(f'<div class="tile-grid">{"".join(tiles)}</div>')

    body.append(trust_block_html())

    qa = [
        ("Do you cover all seven states equally?",
         "Iowa is our home state — same-day field response is realistic across the state. Adjacent states (Illinois, Wisconsin, Minnesota) are within drive radius for substantial field jobs. Nebraska, Missouri, and Texas run primarily ship-in service, with field travel by arrangement for major work."),
        ("How far do you travel for field service?",
         "Field service across Iowa is routine. Major-job field visits routinely run into Illinois, Wisconsin, Minnesota, eastern Nebraska, and the Missouri metros. Texas is by-arrangement only; way covers and spindle rebuilds ship in via standard freight."),
        ("Can you support shops outside your listed seven states?",
         "On a ship-in basis, yes. Way covers ship anywhere in the continental US; spindle rebuilds ship in and out via standard freight. Field service outside our routine seven-state area is quoted separately for major jobs."),
    ]
    body.append(hub_faq_html(qa))
    body.append(hero_cta_html())

    return "\n".join(body) + "\n", qa


def privacy_body():
    """Privacy policy — scoped to what this site actually collects.
    Verified by audit: no analytics/cookies/tracking present; only
    Google Fonts as external load. Web3Forms is the sole third-party
    processor of form submissions."""
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    return f"""<h1>Privacy Policy</h1>
<p><em>Last updated: {today}</em></p>

<p>Midwest CNC Services collects only the information you provide directly
through this site, and uses it only to respond to your inquiry. We don't
run ads, we don't track you, and we don't share your information with
anyone beyond what's needed to deliver the service you're asking about.</p>

<h2 id="what-we-collect">What we collect</h2>
<p>The Get a Quote form on <a href="/get-a-quote/">/get-a-quote/</a>
collects the following information when you submit it:</p>
<ul>
  <li>Your name</li>
  <li>Your company name</li>
  <li>Your phone number</li>
  <li>Your email address</li>
  <li>The machine brand and model you're asking about</li>
  <li>The service type (spindle, machine repair, way covers, other)</li>
  <li>Your description of the issue or the work needed</li>
</ul>
<p>We don't collect this information any other way. There is no analytics
script, no tag manager, no Facebook Pixel, no Hotjar, and no marketing
automation running on this site. We don't set cookies.</p>
<p>This site loads the Inter typeface from Google Fonts
(<code>fonts.googleapis.com</code>). Google may log your IP address and
user-agent as part of standard CDN operation when your browser fetches
the font; Google does not set a tracking cookie via the font request.
Our hosting provider (Cloudflare Pages) keeps standard web-server access
logs (IP, browser, request path, timestamp) as part of infrastructure
operation; we don't analyze those for marketing.</p>

<h2 id="how-we-use-it">How we use it</h2>
<p>Information you submit through the quote form is used for one purpose:
to respond to your quote request and follow up about the work you're
inquiring about. We don't add you to a marketing list, send unrequested
email, or share your contact information with third parties.</p>

<h2 id="who-we-share-it-with">Who we share it with</h2>
<p>Quote form submissions are processed through Web3Forms
(<a href="https://web3forms.com" rel="noopener nofollow">web3forms.com</a>),
a form-handling service that receives your submission and delivers it
to our email. Web3Forms is the only third party that touches your form
data. Their privacy policy applies to their handling of submissions; you
can review it on their site.</p>
<p>We don't sell, rent, or trade your information.</p>

<h2 id="your-rights">Your rights</h2>
<p>If you submitted a quote request and want a copy of the data we have
about you, or want it deleted from our records, call us at
<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>. We'll handle the request
the same business day.</p>

<h2 id="contact">How to reach us</h2>
<p>Midwest CNC Services<br>
Waterloo, Iowa<br>
<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
"""


def terms_body():
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    return f"""<h1>Terms of Service</h1>
<p><em>Last updated: {today}</em></p>

<p>These terms apply to your use of midwestcncservices.com (the "Site").
The Site is an informational marketing site for Midwest CNC Services, a
CNC machine repair, spindle work, and replacement way cover business
based in Waterloo, Iowa.</p>

<h2 id="what-this-site-is">What this site is</h2>
<p>The Site exists to describe the services Midwest CNC Services provides,
list our service area, and let you submit a quote request. It is not a
portal for placing orders, signing service contracts, or transferring
payment. Any actual service relationship between Midwest CNC and your
shop is governed by the service agreement we sign with you for a specific
job — not by anything published here.</p>

<h2 id="quote-requests">Quote requests</h2>
<p>A quote request submitted through this Site is an inquiry, not a
binding contract. Submitting a request does not obligate either party.
We respond to quote requests with pricing, lead times, and scope. A
binding service agreement begins only when we and your authorized
representative both sign the agreement covering the specific job.</p>

<h2 id="limitation-of-liability">Limitation of liability</h2>
<p>Information published on this Site is provided as-is for general
informational purposes. Lead times, service descriptions, and equipment
compatibility statements reflect typical work but do not guarantee
outcomes for any specific job. Actual service is delivered subject to a
signed service agreement, which contains the warranties, performance
commitments, and remedies that apply to that job.</p>
<p>To the maximum extent permitted by law, Midwest CNC Services, its
employees, contractors, and partners are not liable for indirect,
incidental, consequential, or punitive damages arising from your use of
the Site or your reliance on information published here. Direct damages,
if any, are limited to the value of the service agreement signed for
the specific job in question.</p>

<h2 id="warranties">Warranties</h2>
<p>Equipment and service warranties are governed by the service agreement
signed for each job, not by anything stated on this Site. If you have a
question about the warranty terms for a specific service we provided,
call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p>

<h2 id="intellectual-property">Intellectual property</h2>
<p>Content on this Site — text, images, schema markup, and code — is the
property of Midwest CNC Services or used with permission. The brand names
of CNC machine OEMs referenced on this Site (Mazak, Haas, Okuma, DMG Mori,
Fanuc, and others) are the property of their respective owners. We use
those names to describe the platforms we service; we are not affiliated
with, endorsed by, or operating under license from those OEMs unless
explicitly noted on a specific service page.</p>

<h2 id="changes">Changes to these terms</h2>
<p>We may update these terms from time to time. Changes take effect when
posted to this page. The "Last updated" date above reflects the most
recent change. If you submitted a quote request before a change, the
version of these terms in effect at the time of your submission applies
to that submission.</p>

<h2 id="jurisdiction">Jurisdiction</h2>
<p>These terms are governed by the laws of the State of Iowa, without
regard to conflict-of-law principles. Any dispute arising from your use
of this Site or from a service relationship with Midwest CNC Services
will be resolved in the state or federal courts located in Black Hawk
County, Iowa.</p>

<h2 id="contact">Contact</h2>
<p>Questions about these terms: call
<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> or write to Midwest CNC
Services, Waterloo, Iowa.</p>
"""


def not_found_body():
    return f"""<h1>Page not found</h1>
<p>Looks like that page doesn't exist (or moved). Try one of these:</p>
<ul>
  <li><a href="/repairs/">CNC machine repair</a></li>
  <li><a href="/spindle-grinding/">Spindle grinding</a></li>
  <li><a href="/way-covers/">Way covers</a></li>
  <li><a href="/service-area/">Service areas</a></li>
</ul>
<p>Or get in touch:</p>
{hero_cta_html()}
"""


# ---------- Page-write helpers ----------

def write_page(rel_url_dir, *, title, description, canonical_path, schemas, crumbs, body_html, layout="default"):
    """rel_url_dir: path like '/about/' or '/' for the URL. Writes to
    public/<rel_url_dir>/index.html (or public/index.html for the homepage)."""
    out_path = os.path.join(PUBLIC, rel_url_dir.strip("/"), "index.html") \
        if rel_url_dir.strip("/") else os.path.join(PUBLIC, "index.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    schema_blocks = schema_script_tags(schemas)
    crumbs_html_str = breadcrumbs_html(crumbs) if crumbs else ""

    page_html = wrap_page(
        title=title,
        description=description,
        canonical=f"{DOMAIN}{canonical_path}",
        schema_blocks=schema_blocks,
        crumbs_html_str=crumbs_html_str,
        body_html=body_html,
        layout=layout,
    )
    with open(out_path, "w") as f:
        f.write(page_html)
    return out_path


def absolute(path):
    return f"{DOMAIN}{path}"


# ---------- Driver per page ----------

def gen_homepage(brands):
    schemas = organization_localbusiness_schema()
    schemas.append(faqpage_schema(HOMEPAGE_FAQ))
    return write_page(
        "/",
        title="Midwest CNC Services — CNC Repair, Spindle Work & Way Covers",
        description=(
            "CNC machine repair, spindle rebuilds, and replacement way covers "
            "from Midwest CNC Services in Waterloo, IA. Serving shops across "
            "IA, IL, WI, MN, NE, MO, and TX. Call 319-610-4341."
        ),
        canonical_path="/",
        schemas=schemas,
        crumbs=None,
        body_html=homepage_body(),
        layout="wide",
    )


def gen_about():
    schemas = [breadcrumb_schema([
        ("Home", absolute("/")),
        ("About", absolute("/about/")),
    ])]
    return write_page(
        "/about/",
        title="About Midwest CNC Services | Waterloo, Iowa",
        description=(
            "Midwest CNC Services is based in Waterloo, Iowa, serving shops "
            "across the Midwest and South-Central US with CNC machine repair, "
            "spindle work, and replacement way covers."
        ),
        canonical_path="/about/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("About", None)],
        body_html=about_body(),
    )


def gen_quote(brands):
    schemas = [breadcrumb_schema([
        ("Home", absolute("/")),
        ("Get a Quote", absolute("/get-a-quote/")),
    ])]
    return write_page(
        "/get-a-quote/",
        title="Get a Quote — Midwest CNC Services",
        description=(
            "Tell us about your machine and we'll get back to you with pricing "
            "and lead time. Most quotes go out within one business day."
        ),
        canonical_path="/get-a-quote/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Get a Quote", None)],
        body_html=quote_body(brands),
    )


def _build_hub_itemlist(hub_title, brands, link_for):
    """Build an ItemList schema enumerating the brand pages in a hub."""
    items = []
    for b in sorted(brands, key=lambda x: x["brand_display_name"]):
        pair = link_for(b)
        if pair is None:
            continue
        label, url = pair
        items.append({"name": label, "url": f"{DOMAIN}{url}"})
    return hub_itemlist_schema(hub_title, items)


def gen_repairs_hub(brands):
    body_html, qa = repairs_hub_body(brands)

    def link_for(b):
        if b["page_type"] == "cnc_spindle":
            return (b["brand_display_name"], f"/repairs/{b['slug']}-cnc-machine-repair/")
        return (b["brand_display_name"], b["current_url"])

    schemas = [
        breadcrumb_schema([
            ("Home", absolute("/")),
            ("Repairs", absolute("/repairs/")),
        ]),
        _build_hub_itemlist("Brands We Service for Machine Repair", brands, link_for),
        hub_faq_schema(qa),
    ]
    return write_page(
        "/repairs/",
        title="CNC Machine Repair Services | Midwest CNC Services",
        description=(
            "CNC machine repair across the Midwest — spindle, control, ATC, "
            "drive, and alignment work on every major OEM platform. "
            "Experienced field technicians."
        ),
        canonical_path="/repairs/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Repairs", None)],
        body_html=body_html,
        layout="wide",
    )


def gen_spindle_hub(brands):
    body_html, qa = spindle_hub_body(brands)

    def link_for(b):
        if not b.get("services_offered", {}).get("spindle"):
            return None
        return (b["brand_display_name"], f"/spindle-grinding/{b['slug']}-spindle-repair/")

    schemas = [
        breadcrumb_schema([
            ("Home", absolute("/")),
            ("Spindle Grinding", absolute("/spindle-grinding/")),
        ]),
        _build_hub_itemlist("Brands We Service for Spindle Work", brands, link_for),
        hub_faq_schema(qa),
    ]
    return write_page(
        "/spindle-grinding/",
        title="CNC Spindle Repair, Rebuilds & Grinding | Midwest CNC Services",
        description=(
            "CNC spindle repair, rebuild, and grinding across 18 OEM platforms. "
            "Most jobs run 2–6 weeks. Experienced field technicians."
        ),
        canonical_path="/spindle-grinding/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Spindle Grinding", None)],
        body_html=body_html,
        layout="wide",
    )


def gen_way_covers_hub(brands):
    body_html, qa = way_covers_hub_body(brands)

    def link_for(b):
        so = b.get("services_offered", {})
        if not so.get("way_covers"): return None
        if b.get("way_covers_verification_pending"): return None
        return (b["brand_display_name"], f"/way-covers/{b['slug']}-cnc-way-covers/")

    schemas = [
        breadcrumb_schema([
            ("Home", absolute("/")),
            ("Way Covers", absolute("/way-covers/")),
        ]),
        _build_hub_itemlist("Brands We Build Way Covers For", brands, link_for),
        hub_faq_schema(qa),
    ]
    return write_page(
        "/way-covers/",
        title="CNC Way Cover Replacement | Midwest CNC Services",
        description=(
            "Replacement CNC way covers in bellows, telescoping steel, and "
            "roll-up styles. Built to spec, shipped anywhere in the continental "
            "US. 2–4 week lead times."
        ),
        canonical_path="/way-covers/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Way Covers", None)],
        body_html=body_html,
        layout="wide",
    )


def gen_service_area_hub():
    body_html, qa = service_area_hub_body()

    schemas = [
        breadcrumb_schema([
            ("Home", absolute("/")),
            ("Service Area", absolute("/service-area/")),
        ]),
        hub_faq_schema(qa),
    ]
    return write_page(
        "/service-area/",
        title="Service Area Coverage | Midwest CNC Services",
        description=(
            "Midwest CNC Service coverage across Iowa, Illinois, Wisconsin, "
            "Minnesota, Nebraska, Missouri, and Texas — field service and "
            "shipped builds from Waterloo, IA."
        ),
        canonical_path="/service-area/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Service Area", None)],
        body_html=body_html,
        layout="wide",
    )


def gen_privacy():
    schemas = [breadcrumb_schema([
        ("Home", absolute("/")),
        ("Privacy Policy", absolute("/privacy-policy/")),
    ])]
    return write_page(
        "/privacy-policy/",
        title="Privacy Policy | Midwest CNC Services",
        description=(
            "How Midwest CNC Services handles information you submit through "
            "the quote form. No analytics, no tracking, no marketing list."
        ),
        canonical_path="/privacy-policy/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Privacy Policy", None)],
        body_html=privacy_body(),
    )


def gen_terms():
    schemas = [breadcrumb_schema([
        ("Home", absolute("/")),
        ("Terms of Service", absolute("/terms-of-service/")),
    ])]
    return write_page(
        "/terms-of-service/",
        title="Terms of Service | Midwest CNC Services",
        description=(
            "Terms governing your use of midwestcncservices.com. Quote "
            "requests are inquiries; service agreements are signed "
            "separately for each job."
        ),
        canonical_path="/terms-of-service/",
        schemas=schemas,
        crumbs=[("Home", "/"), ("Terms of Service", None)],
        body_html=terms_body(),
    )


def gen_404():
    schemas = []  # No JSON-LD on the 404 itself
    out_path = os.path.join(PUBLIC, "404.html")
    page_html = wrap_page(
        title="Page not found — Midwest CNC Services",
        description="The page you were looking for isn't here. Try one of our service hubs.",
        canonical=absolute("/404.html"),
        schema_blocks="",
        crumbs_html_str="",
        body_html=not_found_body(),
    )
    with open(out_path, "w") as f:
        f.write(page_html)
    return out_path


# ---------- Sitemap + robots + favicon ----------

def gen_sitemap(brands):
    """Walk public/ for index.html files, extract canonical, skip drafts."""
    # Build set of draft canonical URLs from spindle-brands.json
    drafts = set()
    for b in brands:
        if b.get("way_covers_verification_pending"):
            drafts.add(f"{DOMAIN}/way-covers/{b['slug']}-cnc-way-covers/")

    urls = []
    for root, dirs, files in os.walk(PUBLIC):
        for f in files:
            if f != "index.html":
                continue
            path = os.path.join(root, f)
            with open(path) as h:
                src = h.read()
            m = re.search(r'<link rel="canonical" href="([^"]+)"', src)
            if not m:
                continue
            url = m.group(1)
            if url in drafts:
                continue
            # Priority by URL pattern
            if url.rstrip("/") == DOMAIN:
                priority = "1.0"
            elif url.rstrip("/") in (
                f"{DOMAIN}/repairs", f"{DOMAIN}/spindle-grinding",
                f"{DOMAIN}/way-covers", f"{DOMAIN}/service-area",
                f"{DOMAIN}/about", f"{DOMAIN}/get-a-quote",
            ):
                priority = "0.8"
            elif "/spindle-grinding/" in url or "/way-covers/" in url \
                    or "/repairs/" in url:
                priority = "0.7"
            else:
                priority = "0.6"
            urls.append((url, priority))

    urls.sort(key=lambda x: x[0])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, priority in urls:
        lines.append('  <url>')
        lines.append(f'    <loc>{url}</loc>')
        lines.append(f'    <lastmod>{today}</lastmod>')
        lines.append(f'    <priority>{priority}</priority>')
        lines.append('  </url>')
    lines.append('</urlset>')

    out = os.path.join(PUBLIC, "sitemap.xml")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    return out, len(urls), len(drafts)


def gen_robots():
    out = os.path.join(PUBLIC, "robots.txt")
    with open(out, "w") as f:
        f.write(
            "User-agent: *\n"
            "Allow: /\n"
            f"Sitemap: {DOMAIN}/sitemap.xml\n"
        )
    return out


def gen_llms_txt():
    """Phase 4D: llms.txt at site root for AEO/GEO crawlers (ChatGPT,
    Perplexity, Google AI Overviews). Format per https://llmstxt.org/"""
    content = f"""# Midwest CNC Services

> Independent CNC machine repair, spindle grinding and rebuild, and
> replacement way-cover manufacturing for shops across the U.S. Midwest.
> Based in Waterloo, Iowa; serving Iowa, Illinois, Wisconsin, Minnesota,
> Nebraska, Missouri, and Texas. Phone: 319-610-4341.

This site documents brand-specific CNC service capabilities across
twenty OEM platforms (Mazak, Haas, Okuma, DMG Mori, Mori Seiki, Doosan,
Brother, Hurco, Makino, Fanuc, Toyoda, Fadal, Hitachi Seiki, Giddings &
Lewis, Monarch, Amera-Seiki, Niigata, Johnford, Amada, Trumpf), plus
geographic service coverage for the Midwest and South-Central US.

Content is authored from first-hand technician knowledge (Ken Ehlers
at Midwest CNC Services) and supplemented with verifiable regional
context from Wikipedia city/state articles. We do not claim named
manufacturers (Boeing Defense, John Deere, Lockheed Martin, etc.) as
direct customers — those references appear as regional industry
context only.

## Authoritative starting points

- [Homepage](https://midwestcncservices.com/): business overview, service summary, FAQs
- [About Midwest CNC](https://midwestcncservices.com/about/): who we are, what we do, where we work
- [Get a Quote](https://midwestcncservices.com/get-a-quote/): contact form for service inquiries

## Service hubs

- [Machine Repair](https://midwestcncservices.com/repairs/): CNC machine repair across all 20 brand platforms
- [Spindle Grinding](https://midwestcncservices.com/spindle-grinding/): spindle rebuild, regrind, and rebalance across 18 brands
- [Way Covers](https://midwestcncservices.com/way-covers/): replacement way-cover manufacturing
- [Service Area Coverage](https://midwestcncservices.com/service-area/): 7-state geographic coverage

## Sitemaps + indexes

- [Sitemap](https://midwestcncservices.com/sitemap.xml)
- [Robots.txt](https://midwestcncservices.com/robots.txt)

## Content licensing

All content is © Midwest CNC Services. AEO/GEO crawlers are welcome
to cite specific facts (lead times, service descriptions, regional
context) with link attribution to the source URL on this site. Brand
names referenced (Mazak, Haas, etc.) are the property of their
respective OEM owners.
"""
    out = os.path.join(PUBLIC, "llms.txt")
    with open(out, "w") as f:
        f.write(content)
    return out


def gen_favicon():
    """Write a small SVG favicon. We rely on SVG only (modern browsers);
    no .ico/.png raster is included this round — documented in the report."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="4" fill="#b8341a"/>
  <text x="16" y="22" font-family="Inter, Arial, sans-serif" font-size="15"
        font-weight="700" fill="#fff" text-anchor="middle">MC</text>
</svg>
'''
    out = os.path.join(PUBLIC, "favicon.svg")
    with open(out, "w") as f:
        f.write(svg)
    return out


# ---------- Link audit ----------

def parse_redirects():
    """Read public/_redirects → set of source paths."""
    redirects = set()
    path = os.path.join(PUBLIC, "_redirects")
    if not os.path.exists(path):
        return redirects
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            redirects.add(parts[0])
    return redirects


def resolve_internal(href, redirects):
    """Return one of:
       ("ok",       absolute_disk_path)
       ("redirect", source_path)
       ("broken",   absolute_disk_path that doesn't exist)
       ("skip",     reason)         # external, tel:, mailto:, anchor, etc.
    """
    if not href:
        return ("skip", "empty")
    if href.startswith(("#", "?")):
        return ("skip", "in-page")
    if href.startswith(("tel:", "mailto:", "javascript:")):
        return ("skip", "non-http")
    if href.startswith(("http://", "https://", "//")):
        if "midwestcncservices.com" in href:
            href = href.split("midwestcncservices.com", 1)[1] or "/"
        else:
            return ("skip", "external")
    if not href.startswith("/"):
        return ("skip", "relative")  # we don't use these
    # Strip query/fragment
    clean = href.split("?", 1)[0].split("#", 1)[0] or "/"
    # If matched by a redirect, treat as resolved
    if clean in redirects:
        return ("redirect", clean)
    # Map to disk
    if clean.endswith("/"):
        disk = os.path.join(PUBLIC, clean.lstrip("/"), "index.html")
    elif "." in os.path.basename(clean):
        disk = os.path.join(PUBLIC, clean.lstrip("/"))
    else:
        disk = os.path.join(PUBLIC, clean.lstrip("/"), "index.html")
    if os.path.exists(disk):
        return ("ok", disk)
    return ("broken", clean)


def link_audit():
    redirects = parse_redirects()
    broken_by_source = {}   # source_file → list of (href, source_text)
    total_links = 0
    external_count = 0
    skip_count = 0
    redirect_count = 0
    ok_count = 0

    for root, dirs, files in os.walk(PUBLIC):
        for f in files:
            if not f.endswith(".html"):
                continue
            path = os.path.join(root, f)
            src = open(path).read()
            # Match anchors with ANY inner content (including <img>/<span>/etc.) —
            # the previous [^<]* version skipped tile-style anchors entirely.
            for m in re.finditer(
                r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                src,
                flags=re.DOTALL,
            ):
                href = m.group(1)
                text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
                total_links += 1
                status, info = resolve_internal(href, redirects)
                if status == "ok":
                    ok_count += 1
                elif status == "redirect":
                    redirect_count += 1
                elif status == "broken":
                    rel_source = os.path.relpath(path, PUBLIC)
                    broken_by_source.setdefault(rel_source, []).append((href, text))
                elif status == "skip":
                    if info == "external":
                        external_count += 1
                    else:
                        skip_count += 1

    return {
        "total": total_links,
        "ok": ok_count,
        "redirect": redirect_count,
        "external": external_count,
        "skip": skip_count,
        "broken_by_source": broken_by_source,
    }


def write_audit_report(audit):
    """Write docs/phase-1-link-audit.md from the audit dict."""
    lines = ["# Phase 1 — Cross-Link Audit\n",
             f"Scanned every `<a href>` in every HTML file under `public/` "
             f"and resolved each link against the filesystem and `public/_redirects`.\n",
             "## Totals\n",
             f"- **Total `<a href>` links scanned:** {audit['total']}",
             f"- **Resolved to a real file:** {audit['ok']}",
             f"- **Resolved via `_redirects` (301):** {audit['redirect']}",
             f"- **External links (skipped from broken-check):** {audit['external']}",
             f"- **Other non-http (tel:/mailto:/anchor/etc.):** {audit['skip']}",
             ""]

    broken = audit["broken_by_source"]
    n_broken_links = sum(len(v) for v in broken.values())

    if not broken:
        lines.append("## Broken internal links\n\nNone. 🎉\n")
    else:
        # Aggregate unique broken hrefs across the site
        broken_targets = {}
        for src_file, hrefs in broken.items():
            for href, text in hrefs:
                broken_targets.setdefault(href, set()).add(src_file)

        lines.append(f"## Broken internal links ({n_broken_links} link instances pointing to "
                     f"{len(broken_targets)} unique missing targets)\n")
        lines.append("Sorted by how many source files reference each missing target.\n")
        lines.append("| Missing target | Referenced from |")
        lines.append("|---|---|")
        for href, sources in sorted(broken_targets.items(),
                                     key=lambda kv: (-len(kv[1]), kv[0])):
            srclist = ", ".join(sorted(sources))
            lines.append(f"| `{href}` | {srclist} |")
        lines.append("")

        # Group by URL pattern — what's outstanding for future phases?
        lines.append("## Likely-expected (already-planned) broken links\n")
        phase2_state = [h for h in broken_targets if h.startswith("/service-area/") and h.count("/") == 3]
        phase2_city  = [h for h in broken_targets if h.startswith("/service-area/") and h.count("/") > 3]
        other        = [h for h in broken_targets
                        if not h.startswith("/service-area/")]

        if phase2_state:
            lines.append(f"### Phase 2: state-level pages ({len(phase2_state)})")
            for h in sorted(phase2_state):
                lines.append(f"- `{h}` *(state pages — currently 301-redirected to /service-area/ hub)*")
            lines.append("")
        if phase2_city:
            lines.append(f"### Phase 2 / 3: city-level pages ({len(phase2_city)})")
            for h in sorted(phase2_city)[:25]:
                lines.append(f"- `{h}`")
            if len(phase2_city) > 25:
                lines.append(f"- *…and {len(phase2_city)-25} more*")
            lines.append("")
        if other:
            lines.append(f"### Other broken targets to investigate ({len(other)})")
            for h in sorted(other):
                lines.append(f"- `{h}`")
            lines.append("")

    out = os.path.join(REPO, "docs", "phase-1-link-audit.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write("\n".join(lines))
    return out, n_broken_links


# ---------- Main ----------

def main():
    brands = json.load(open(os.path.join(REPO, "src", "data", "spindle-brands.json")))["brands"]

    print("== Generating site shell ==\n")
    paths = []
    paths.append(("homepage",      gen_homepage(brands)))
    paths.append(("about",         gen_about()))
    paths.append(("get-a-quote",   gen_quote(brands)))
    paths.append(("repairs hub",   gen_repairs_hub(brands)))
    paths.append(("spindle hub",   gen_spindle_hub(brands)))
    paths.append(("way-covers",    gen_way_covers_hub(brands)))
    paths.append(("service-area",  gen_service_area_hub()))
    paths.append(("privacy",       gen_privacy()))
    paths.append(("terms",         gen_terms()))
    paths.append(("404",           gen_404()))

    for label, p in paths:
        size = os.path.getsize(p)
        print(f"  ✓ {label:<14} → {os.path.relpath(p, REPO):<48} ({size//1024} KB)")

    # Phase 2/3 brought real state and city pages, so the Phase-1 state
    # placeholders are removed. Instead we now need the 3 Illinois URL
    # typo fixes (Durable's "ilinois" → corrected "illinois").
    inventory_path = os.path.join(REPO, "src", "data", "city-inventory.json")
    typo_pairs = []
    if os.path.exists(inventory_path):
        for c in json.load(open(inventory_path)):
            if c.get("original_path"):
                typo_pairs.append(
                    (c["original_path"] + "/", c["path"], 301)
                )
    extras = []
    if typo_pairs:
        extras.append((
            "Phase 2/3: Illinois URL typo fixes (Durable used 'ilinois')",
            typo_pairs,
        ))

    # Phase 6 (enrichment): redirect CONSOLIDATE-marked city pages to their
    # state page. These were removed from public/ as part of Phase 2 enrichment.
    research_path = os.path.join(REPO, "src", "data", "city-research.json")
    if os.path.exists(research_path):
        research = json.load(open(research_path))
        consolidate_pairs = []
        for slug, c in research.get("cities", {}).items():
            if c.get("decision") == "CONSOLIDATE":
                consolidate_pairs.append(
                    (f"/service-area/{slug}/", f"/service-area/{c['state_slug']}/", 301)
                )
        if consolidate_pairs:
            extras.append((
                "Phase 6: CONSOLIDATE-marked city pages → state pages",
                consolidate_pairs,
            ))

    # Phase 5: redirect deferred content sections to relevant pages.
    # Four evergreen blog posts get specific 301s to relevant service hubs
    # (preserves SEO value of any inbound links). All other /blog/, /guides/,
    # and /customer-stories/ URLs fall through to wildcards → homepage.
    extras.append((
        "Phase 5: deferred content sections (blog/guides/customer-stories)",
        [
            ("/blog/precision-cnc-machining--how-it-drives-efficiency-in-manufacturing/", "/repairs/", 301),
            ("/blog/understanding-the-true-cost--usa-made-way-covers-vs--overseas-options/", "/way-covers/", 301),
            ("/blog/choosing-the-right-way-covers-for-your-cnc-machines--a-comprehensive-buyer-s-guide/", "/way-covers/", 301),
            ("/blog/emergency-cnc-repair--quick-steps-to-restore-your-machine/", "/repairs/", 301),
            ("/blog/*",             "/", 301),
            ("/blog",               "/", 301),
            ("/guides/*",           "/", 301),
            ("/guides",             "/", 301),
            ("/customer-stories/*", "/", 301),
            ("/customer-stories",   "/", 301),
        ],
    ))
    n_redirects = gbp.write_redirects(
        brands, os.path.join(PUBLIC, "_redirects"), extras=extras,
    )
    print(f"\n  ✓ _redirects     ({n_redirects} rules total)")

    # Sitemap, robots, favicon
    sm_path, n_urls, n_drafts = gen_sitemap(brands)
    print(f"  ✓ sitemap.xml    ({n_urls} URLs, {n_drafts} drafts excluded)")
    rb_path = gen_robots()
    print(f"  ✓ robots.txt")
    fv_path = gen_favicon()
    print(f"  ✓ favicon.svg")
    llms_path = gen_llms_txt()
    print(f"  ✓ llms.txt")

    # Link audit
    print("\n== Cross-link audit ==")
    audit = link_audit()
    audit_path, n_broken = write_audit_report(audit)
    print(f"  Links scanned:      {audit['total']}")
    print(f"  Resolved (file):    {audit['ok']}")
    print(f"  Resolved (301):     {audit['redirect']}")
    print(f"  External (skipped): {audit['external']}")
    print(f"  Non-http (skipped): {audit['skip']}")
    print(f"  Broken:             {n_broken}")
    print(f"  Report:             {os.path.relpath(audit_path, REPO)}")


if __name__ == "__main__":
    main()
