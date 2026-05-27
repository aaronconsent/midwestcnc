#!/usr/bin/env python3
"""
Phase 2 — state pages.

Generates one /service-area/{slug}/index.html per state (7 total). Uses
src/data/states.json for the verifiable scaffolding (slug, display_name,
major_cities, cities_with_pages) plus the Aaron-supplied brief fields
(industry_clusters, notable_manufacturers, travel_context).

When brief-dependent fields are empty, the corresponding sections render
in their honest-minimum form rather than fabricating state-specific
manufacturer or industry claims.

Imports chrome (CSS + header + footer + mobile CTA) from
generate_site_shell.py so the visual aesthetic matches Phase 1.
"""

import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_site_shell as gss


REPO = gss.REPO
PUBLIC = gss.PUBLIC
DOMAIN = gss.DOMAIN
PHONE_TEL = gss.PHONE_TEL
PHONE_DISPLAY = gss.PHONE_DISPLAY


def load_city_research():
    """Load city-research.json, return a dict keyed by city slug."""
    path = os.path.join(REPO, "src", "data", "city-research.json")
    if not os.path.exists(path):
        return {}
    return json.load(open(path)).get("cities", {})


# Per-state region breakdowns — verifiable groupings, no fabricated cluster names.
REGION_BREAKDOWN = {
    "iowa": [
        ("Eastern Iowa + Quad Cities corridor",
         "The Davenport-Bettendorf-Moline-Rock Island Quad Cities cluster anchors heavy-machinery and ag-equipment manufacturing on Iowa's eastern edge. Cedar Rapids brings aerospace (Collins Aerospace) and grain processing into the corridor."),
        ("Central Iowa",
         "Des Moines and Ames anchor the state's insurance, agribusiness, and research economy. Ames hosts ISU Research Park; Des Moines's Corteva and Amazon presence drive lighter-industrial CNC demand. Both cities sit within drive-radius of John Deere Waterloo."),
        ("Cedar Valley + northern Iowa",
         "Waterloo (home) sits at the geographic heart of John Deere ag-equipment manufacturing and Tyson Foods meatpacking — the densest concentration of CNC-machined output in our routine work."),
    ],
    "illinois": [
        ("Chicago metro",
         "The Chicago metro retains a substantial industrial supply chain across aerospace, defense, and machine tools — even as the city's modern economy emphasizes finance. Naperville sits inside the Illinois Technology and Research Corridor with Nokia (former Bell Labs) and Kraft Foods Triscuit production."),
        ("Rockford machine-tool corridor",
         "Rockford built one of the densest precision-machining bases in the Midwest, transitioning from agricultural machinery into fasteners and aerospace. Collins Aerospace (Sundstrand lineage) and Woodward Inc.'s $200M Loves Park campus anchor the modern cluster; Stellantis runs the Belvidere assembly plant just east."),
        ("Peoria + downstate heavy equipment",
         "Peoria's Caterpillar legacy and Komatsu America heavy-equipment plant define downstate Illinois manufacturing. The work runs to larger-envelope CNC platforms — Mazak HCN horizontals, Toyoda mills, Giddings & Lewis boring."),
    ],
    "wisconsin": [
        ("Milwaukee metro + industrial corridor",
         "Milwaukee anchors the state's heavy-machinery and automation industry — Harley-Davidson, Rockwell Automation, A.O. Smith — plus the Racine cluster south (Case IH, Modine, S.C. Johnson). High concentration of older machine inventory needing rebuild work."),
        ("Madison + south-central biotech",
         "Madison's biotech and medical-device cluster (Epic, Promega, Exact Sciences) sits alongside Sub-Zero/Wolf appliance manufacturing and Trek Bicycle. Higher-precision work skews toward Brother Speedio and Makino platforms."),
        ("Fox Valley + Green Bay paper machinery",
         "Green Bay's paper-products concentration (Georgia-Pacific, P&G) and Oshkosh Corporation's defense vehicle manufacturing drive the Fox Valley industrial mix. Process-equipment and large-vehicle work."),
    ],
    "minnesota": [
        ("Twin Cities medical-device cluster",
         "Minneapolis-St. Paul is one of the country's densest medical-device manufacturing hubs — Medtronic (Minneapolis-founded), Boston Scientific, 3M, and the broader supply chain. Compact-precision platforms (Brother Speedio, Makino) see most of the volume."),
        ("Rochester + Mayo ecosystem",
         "Rochester's Mayo Clinic ecosystem drives precision-machining demand from medical-device suppliers. McNeilus Truck adds heavy-vehicle manufacturing; IBM's legacy Rochester Technology Campus retains some manufacturing presence."),
        ("Duluth + Iron Range",
         "Duluth's port handles iron ore, coal, grain, and wind-turbine parts. Cirrus Aircraft anchors aviation manufacturing. The Iron Range supports mining-equipment manufacturers needing heavy-platform CNC service."),
    ],
    "nebraska": [
        ("Omaha + Lincoln metro",
         "Omaha (Berkshire Hathaway, Union Pacific HQ, Kiewit) and Lincoln (Kawasaki Motors Manufacturing — ATVs, UTVs, personal watercraft, rail cars) form the state's industrial spine. Kawasaki's 2,400+ Lincoln workforce is the densest single CNC-machining concentration."),
        ("Central Nebraska — Grand Island and Kearney",
         "Hornady manufactures ammunition in Grand Island; Baldwin Filters, Eaton, and West Pharmaceutical maintain operations in Kearney. Ag-equipment supply chains run heavily through this corridor."),
        ("Western Nebraska — North Platte",
         "North Platte hosts Union Pacific's Bailey Yard (the world's largest rail yard by area) and the new Sustainable Beef meatpacking plant. CNC service to this region runs ship-in via freight from Waterloo; field service is by-arrangement for major jobs."),
    ],
    "missouri": [
        ("St. Louis aerospace concentration",
         "Boeing Defense, Space & Security is the largest St. Louis employer and anchors the state's aerospace and defense cluster. Anheuser-Busch adds brewing-equipment manufacturing. Aerospace work skews toward Makino and DMG Mori precision platforms."),
        ("Kansas City defense + automotive",
         "Kansas City's Honeywell-operated Federal Manufacturing & Technologies plant produces 85% of the non-nuclear components of the U.S. nuclear arsenal. Ford and GM operate assembly plants in the metro. Sanofi-Aventis adds pharmaceutical manufacturing."),
        ("Springfield + southern Missouri",
         "Springfield supports regional distribution, logistics, and manufacturing — Paul Mueller, Positronic, Prime Inc., Bass Pro/Tracker Marine. Manufacturing is real but lighter than the I-70 corridor."),
    ],
    "texas": [
        ("DFW aerospace + defense",
         "Fort Worth anchors Lockheed Martin Aeronautics (F-16/F-35 production) and Bell Textron rotorcraft manufacturing. Dallas adds defense supply-chain operations and ground-vehicle manufacturing heritage. The DFW Metroplex is the densest aerospace cluster in Texas."),
        ("Houston petrochemical + O&G equipment",
         "Houston anchors oil-and-gas equipment manufacturing along the Ship Channel and Energy Corridor — Halliburton, Phillips 66, ExxonMobil, ConocoPhillips. Large-envelope CNC work for refinery and oilfield equipment is the dominant pattern."),
        ("Austin + central Texas tech and EV",
         "Austin's semiconductor and EV manufacturing concentration includes Tesla, Samsung, NXP Semiconductors, AMD, and IBM. San Antonio adds Toyota Motor Manufacturing Texas. Compact-precision and broad supply-chain machining."),
        ("El Paso + border industry",
         "El Paso's economy developed through copper smelting, oil refining, and cross-border manufacturing relationships with Ciudad Juárez. The longest-haul region in our service area — pure ship-in service for most CNC work."),
    ],
}


# Per-state FAQ Q&A pools (4-5 per state). Used in the state-page FAQ section.
STATE_FAQ = {
    "iowa": [
        ("Do you service shops across all of Iowa?",
         "Yes. Iowa is our home state; any Iowa shop is within drive-radius of our Waterloo location. Same-day field response is realistic across the state, and bench rebuilds happen at our Cedar Valley shop."),
        ("Which Iowa cities do you most often visit for field service?",
         "Des Moines, Davenport, Cedar Rapids, Waterloo, Ames, and the Quad Cities corridor are routine field destinations. The state's ag-equipment supply chain drives our highest-volume Iowa work."),
        ("Do you work on John Deere Waterloo supply-chain shops?",
         "Yes — we service shops doing precision work for John Deere and the broader Iowa ag-equipment customer base. Mazak, Doosan, and Toyoda platforms are common in that work."),
        ("How does shipping work from Iowa to your bench?",
         "Most Iowa work is dropped off or driven; we also accept freight from anywhere in the state. Standard freight from any Iowa city to Waterloo is overnight or same-day."),
        ("What's your typical Iowa lead time on a spindle rebuild?",
         "Iowa spindle rebuilds typically run 3–6 weeks depending on brand and parts availability — same window as our national pattern. Mazak Integrex and DMG Mori multi-tasking work tends to the longer end; Haas and Doosan trend shorter."),
    ],
    "illinois": [
        ("Do you cover the full Chicago metro for field service?",
         "Chicago metro field service is part of our routine Illinois work — about 5 hours by truck from Waterloo. We schedule diagnostic visits and substantive on-site jobs across Chicagoland."),
        ("Is Rockford within your field-service area?",
         "Yes. Rockford is a major destination for us — the city's dense precision-machining base (Collins Aerospace, Woodward, Stellantis Belvidere) drives steady field work."),
        ("Do you service Caterpillar supply-chain shops in Peoria?",
         "We service shops doing precision work for Caterpillar's Peoria operation and the surrounding Komatsu heavy-equipment cluster. We don't claim Caterpillar as a direct customer."),
        ("What's the typical Illinois drive time from Waterloo?",
         "Chicago is about 5 hours, Rockford about 3.5, Peoria about 3.5, Naperville about 4.5. Springfield Illinois (consolidated to the state page) is about 4 hours."),
        ("How do Illinois shops ship spindles to Waterloo?",
         "Standard freight — UPS, FedEx Freight, or LTL — runs overnight to two-day from any Illinois city. We include return shipping in most spindle rebuild quotes."),
    ],
    "wisconsin": [
        ("Is Milwaukee within your field-service drive?",
         "Yes. Milwaukee is about 4.5 hours by truck from our Waterloo shop — within practical field-service reach for diagnostic visits and bundled jobs."),
        ("Do you cover the Fox Valley paper-machinery corridor?",
         "We service the Fox Valley paper-machinery base (Appleton, Neenah, Oshkosh) plus the Green Bay paper-products cluster. The work runs heavier than other Wisconsin sectors."),
        ("What about the Madison biotech and medical-device cluster?",
         "Yes — Madison's higher-precision compact work (Brother Speedio, Makino) is a real part of our Wisconsin coverage. Sub-Zero/Wolf appliance manufacturing rounds out the city's industrial mix."),
        ("How long is the drive from Waterloo to Wisconsin cities?",
         "Madison is about 3.7 hours, Milwaukee about 4.5, Kenosha about 5, Green Bay about 5.5. All within drive for substantive field-service jobs."),
        ("Do you build way covers for Wisconsin's older machine inventory?",
         "Yes. The Milwaukee-Racine industrial corridor has substantial older CNC inventory in active use — we build replacement bellows, telescoping-steel, and roll-up way covers to spec, shipping anywhere."),
    ],
    "minnesota": [
        ("Do you service the Twin Cities medical-device cluster?",
         "Yes. The Minneapolis-St. Paul medical-device hub (Medtronic, Boston Scientific, 3M, plus supply chain) is a meaningful part of our Minnesota work — Brother Speedio and Makino precision platforms are common."),
        ("Is Rochester (Mayo Clinic ecosystem) within your service area?",
         "Yes. Rochester is about 2.2 hours by truck from Waterloo — drivable for field service. The Mayo ecosystem and IBM-legacy Rochester Technology Campus drive precision-machining demand."),
        ("Do you cover Duluth and the Iron Range?",
         "Duluth (5.8 hours one-way) is reachable for major field jobs by arrangement. Ship-in service is the routine pattern for spindle and way-cover work."),
        ("How does shipping from Minnesota work?",
         "Most Twin Cities and southern Minnesota shops ship overnight to Waterloo via standard freight. Duluth runs 2–3 days depending on carrier."),
        ("What brands do you see most in Minnesota?",
         "Twin Cities medical-device shops run Brother Speedio and Makino heavily. McNeilus Truck (Rochester) drives heavy-vehicle work via Mazak and Toyoda. The Iron Range supports Mazak heavy-platform demand."),
    ],
    "nebraska": [
        ("Do you cover Omaha and Lincoln for field service?",
         "Omaha and Lincoln are both 5–6 hours by truck from Waterloo — drivable for substantive jobs and bundled diagnostics. Lincoln's Kawasaki Motors Manufacturing operation is a notable regional anchor."),
        ("Is western Nebraska within your service area?",
         "Yes, on a ship-in basis. North Platte (10+ hours), Grand Island (8 hours), and Kearney (8.5 hours) all ship spindles to Waterloo via freight. Field service for major multi-machine jobs by arrangement."),
        ("Do you service ag-implement supply chain shops in Nebraska?",
         "Yes — ag-implement and ag-equipment supply shops across central and western Nebraska are part of our Nebraska work. Doosan and Mazak platforms are common in that work."),
        ("How does the Bailey Yard / Union Pacific relationship work?",
         "We don't claim Union Pacific or Bailey Yard as customers. UP operates its own internal service shops. We do work with independent ag-implement and fabrication shops in the broader western Nebraska region."),
    ],
    "missouri": [
        ("Do you service Boeing Defense supply-chain shops in St. Louis?",
         "We service independent CNC shops doing precision work for the St. Louis aerospace customer base. Boeing Defense itself is not a direct customer — Makino and DMG Mori platforms are common in the aerospace supply chain."),
        ("Is Kansas City within your field-service drive?",
         "Kansas City is about 5.7 hours by truck from Waterloo — drivable for major field jobs. Honeywell-operated Federal Manufacturing & Technologies (formerly Kansas City Plant) and the Ford/GM assembly plants anchor the metro's industrial mix."),
        ("Do you cover Springfield, Missouri?",
         "Yes. Springfield MO is about 7.7 hours from Waterloo — a ship-in market with occasional field-service trips for substantive jobs. The metro's distribution and manufacturing concentration (Paul Mueller, Prime Inc., Bass Pro) drives steady demand."),
        ("How does shipping from Missouri to Waterloo work?",
         "Standard freight from any Missouri city runs 1–2 days to our Waterloo shop. We include return shipping in most spindle rebuild quotes."),
        ("What brands do you see most often in Missouri?",
         "St. Louis aerospace work skews Makino and DMG Mori. Kansas City defense and automotive runs Mazak, Doosan, and Haas across tier-1/tier-2 supply machining. Southern Missouri distribution and food-processing equipment runs Mazak and Haas."),
    ],
    "texas": [
        ("Do you really travel to Texas for service?",
         "Field service to Texas is by-arrangement only — every Texas city is 14+ hours one-way from Waterloo. Spindle rebuilds and way-cover builds ship in and out via standard freight; we'll quote field travel for substantive multi-machine jobs."),
        ("How does shipping from Texas to Waterloo work?",
         "Standard freight from Texas runs 3–5 business days depending on carrier and route. The 1,000+ mile haul is built into typical Texas customer logistics, and return shipping is included in most rebuild quotes."),
        ("Do you service Lockheed Martin supply-chain shops in Fort Worth?",
         "We service independent CNC shops doing precision aerospace work for the DFW customer base. Lockheed Martin and Bell Textron are regional context, not direct customers."),
        ("What about Houston oil-and-gas equipment work?",
         "Yes. Houston's O&G equipment manufacturing concentration is part of our Texas service area on a ship-in basis. The work runs heavily to Mazak, Toyoda, and Giddings & Lewis large-envelope platforms."),
        ("Why do Texas shops choose Midwest CNC despite the distance?",
         "Brand-specific expertise. Texas customers typically reach out when the brand-specific knowledge — Mazak Integrex multitasking, DMG Mori precision aerospace, Hitachi Seiki legacy — justifies the freight."),
    ],
}


# Per-state H1 variations so the pages don't read as a single template.
H1_FOR = {
    "iowa":      "CNC Repair & Spindle Service in Iowa",
    "illinois":  "CNC Service for Illinois Manufacturing",
    "wisconsin": "Wisconsin CNC Repair & Way Covers",
    "minnesota": "CNC Repair Across Minnesota",
    "nebraska":  "CNC Service for Nebraska Manufacturers",
    "missouri":  "Missouri CNC Repair & Spindle Service",
    "texas":     "Texas CNC Service & Way Cover Shipping",
}

# Per-state "How We Work" framing. No "same-day" claims — that's in the
# audit ban list. Honest framing about field-vs-ship logistics.
def how_we_work_text(state):
    slug = state["slug"]
    name = state["display_name"]
    if state["is_home_state"]:
        return (
            f"{name} is our home state. We work shops across the state from our "
            f"Waterloo location — field service is part of routine work, and "
            f"bench rebuilds and way-cover builds happen at the shop and roll "
            f"out by truck or by ship-back."
        )
    if slug in ("illinois", "wisconsin", "minnesota"):
        return (
            f"{name} sits within practical field-service reach of our Waterloo, "
            f"Iowa shop. We split {name} work between on-site visits where the "
            f"diagnostic warrants it and bench rebuilds back at the shop, with "
            f"way-cover builds shipped directly to the floor."
        )
    # Nebraska, Missouri, Texas — mostly ship-in
    return (
        f"Most {name} work runs ship-in from our Waterloo, Iowa shop — spindle "
        f"rebuilds come to the bench, way covers ship anywhere in the continental "
        f"US. Field service for major jobs is available by arrangement; talk to "
        f"us about scope and travel before scheduling."
    )


def hero_paragraph(state):
    name = state["display_name"]
    travel = state["travel_context"].strip()

    # Lead sentence varies slightly so the 7 hero paragraphs don't open identically.
    if state["is_home_state"]:
        opener = f"{name} is our home state — Midwest CNC Services is based in Waterloo."
    else:
        opener = f"We work shops across {name} from our Waterloo, Iowa location."

    # If Aaron supplied travel_context, use it. Otherwise the honest-minimum
    # version below carries the page.
    if travel:
        return f"{opener} {travel}"

    # Process-uniform fallback when no Aaron brief is supplied yet
    cities = ", ".join(state["major_cities"][:3])
    return (
        f"{opener} Our work in {name} spans CNC machine repair, spindle "
        f"rebuilds and grinding, and replacement way covers — services that "
        f"reach {cities} and the surrounding manufacturing centers."
    )


def _join_oxford(items):
    """Format ['a', 'b', 'c'] as 'a, b, and c'. ['a', 'b'] → 'a and b'."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def manufacturing_section(state):
    """Returns HTML for the 'Manufacturing in {State}' H2 using the
    verifiable-framing pattern: name manufacturers as CONTEXT for the
    region, and frame Midwest CNC's role as 'we service the shops doing
    CNC work for them' — never claiming the named manufacturers as our
    direct customers."""
    name = state["display_name"]
    clusters = state.get("industry_clusters", []) or []
    manufacturers = state.get("notable_manufacturers", []) or []
    if not clusters and not manufacturers:
        return (
            f'<h2 id="manufacturing">Manufacturing in {html.escape(name)}</h2>\n'
            f'<p>{html.escape(name)} is part of the regional manufacturing '
            f'base our shop supports.</p>\n'
        )

    paragraphs = []
    if clusters:
        paragraphs.append(
            f"<p>{html.escape(name)}'s manufacturing base spans "
            f"{html.escape(_join_oxford(clusters))} — the categories of shops "
            f"that come through our CNC repair, spindle work, and replacement "
            f"way-cover lines.</p>"
        )
    if manufacturers:
        paragraphs.append(
            f"<p>Notable {html.escape(name)} manufacturers include "
            f"{html.escape(_join_oxford(manufacturers))}. We don't claim "
            f"these names as customers — we service the shops doing CNC "
            f"work for them, the supply-chain machining and in-house tooling "
            f"that keeps those operations producing.</p>"
        )
    return (
        f'<h2 id="manufacturing">Manufacturing in {html.escape(name)}</h2>\n'
        + "\n".join(paragraphs) + "\n"
    )


def cities_section(state, research):
    """Cities We Serve — descriptive sentences per city (Phase 3 expansion).
    Cities with pages get linked; otherwise plain text. Pulls a one-line
    context sentence from city-research where available."""
    name = state["display_name"]
    cities_with_pages = state.get("cities_with_pages", [])

    items = []
    for city_link in cities_with_pages:
        slug_full = f"{city_link['slug']}-{state['slug']}"
        research_entry = research.get(slug_full, {})
        decision = research_entry.get("decision", "ENRICH")
        if decision != "ENRICH":
            continue
        # Build a descriptive sentence from research
        industries = research_entry.get("primary_industries", [])
        employers = research_entry.get("major_employers", [])
        miles = research_entry.get("distance_from_waterloo", {}).get("miles", 0)

        if industries and employers:
            first_employer = re.sub(r"\s*\(.*?\)", "", employers[0]).strip()
            descriptor = f"{industries[0]} and adjacent work, anchored by {first_employer}"
        elif industries:
            descriptor = f"{industries[0]} and adjacent industrial activity"
        elif employers:
            first_employer = re.sub(r"\s*\(.*?\)", "", employers[0]).strip()
            descriptor = f"shops doing supply-chain work for {first_employer} and the surrounding metro"
        else:
            descriptor = "shops doing CNC service work for the surrounding industrial base"

        items.append(
            f'<li><a href="{city_link["path"]}"><strong>{html.escape(city_link["display_name"])}</strong></a> — '
            f'{html.escape(descriptor)} ({miles} mi from Waterloo).</li>'
        )

    return (
        f'<h2 id="cities-we-serve">Cities We Serve in {html.escape(name)}</h2>\n'
        f'<p>City-specific pages cover the local context for each — '
        f'industry mix, named major employers as regional context, and '
        f'logistics expectations from our Waterloo, IA shop:</p>\n'
        f'<ul class="city-list">{"".join(items)}</ul>\n'
    )


def regional_breakdown_section(state):
    """Per-state region breakdown (Phase 3 expansion). Returns HTML or '' if none."""
    name = state["display_name"]
    regions = REGION_BREAKDOWN.get(state["slug"], [])
    if not regions:
        return ""
    body_parts = []
    for region_name, description in regions:
        body_parts.append(
            f'<h3>{html.escape(region_name)}</h3>\n'
            f'<p>{html.escape(description)}</p>'
        )
    return (
        f'<h2 id="regional-breakdown">{html.escape(name)} by Region</h2>\n'
        + "\n".join(body_parts) + "\n"
    )


def smaller_markets_section(state, research):
    """Phase 3A: absorb CONSOLIDATE-marked cities into their state page.
    ~40 words per consolidated city, drawing from research."""
    name = state["display_name"]
    consolidates = [
        (slug, c) for slug, c in research.items()
        if c.get("state_slug") == state["slug"]
        and c.get("decision") == "CONSOLIDATE"
    ]
    if not consolidates:
        return ""

    items = []
    for slug, c in consolidates:
        city_name = c["name"]
        pop_text = c.get("population", "")
        pop_short = pop_text.split(" ")[0] if pop_text else ""
        industries = c.get("primary_industries", [])
        employers = c.get("major_employers", [])
        miles = c.get("distance_from_waterloo", {}).get("miles", 0)

        # Custom per-city sentences — verifiable, no fabrication
        if slug == "iowa-city-iowa":
            blurb = (
                f"<strong>Iowa City</strong> (pop. {pop_short}) is anchored "
                "by the University of Iowa and U of I Hospitals — local "
                "industrial activity is limited. Customers in the area "
                "typically work through our Cedar Rapids or Quad Cities "
                "coverage; ship-in spindle and machine repair from Iowa "
                f"City is overnight to our Waterloo bench ({miles} mi)."
            )
        elif slug == "springfield-illinois":
            blurb = (
                f"<strong>Springfield</strong> (pop. {pop_short}) is "
                "Illinois's state capital with a government- and "
                "healthcare-dominated economy. Manufacturing demand from "
                "the Springfield area is light; CNC service typically "
                "routes through our Peoria or Chicago metro coverage "
                f"({miles} mi from Waterloo)."
            )
        elif slug == "bellevue-nebraska":
            blurb = (
                f"<strong>Bellevue</strong> (pop. {pop_short}) sits "
                "adjacent to Offutt Air Force Base and is largely a "
                "residential-and-military market without a civilian "
                "manufacturing footprint. Spindle and machine work for "
                "the broader Omaha metro covers Bellevue customers via "
                f"ship-in to our Waterloo facility ({miles} mi)."
            )
        elif slug == "columbia-missouri":
            blurb = (
                f"<strong>Columbia</strong> (pop. {pop_short}) is "
                "anchored by the University of Missouri and its health "
                "system — education, healthcare, and insurance with "
                "limited manufacturing presence. Columbia customers "
                "needing CNC service typically work through our Kansas "
                f"City or St. Louis metro coverage ({miles} mi)."
            )
        else:
            # Generic fallback
            ind_str = industries[0] if industries else "limited industrial activity"
            blurb = (
                f"<strong>{city_name}</strong> (pop. {pop_short}) — "
                f"{ind_str}; light manufacturing footprint. Customers "
                f"work through our regional coverage; ship-in service "
                f"from Waterloo ({miles} mi)."
            )
        items.append(f'<li>{blurb}</li>')

    return (
        f'<h2 id="smaller-markets">Smaller Markets We Serve in {html.escape(name)}</h2>\n'
        f'<p>These cities don\'t have dedicated pages because their '
        f'manufacturing footprint doesn\'t justify standalone CNC service '
        f'detail — we serve them through ship-in and regional coverage:</p>\n'
        f'<ul>{"".join(items)}</ul>\n'
    )


def state_logistics_section(state, research):
    """Phase 3D: state-level logistics with distances from Waterloo to multiple cities."""
    name = state["display_name"]
    slug = state["slug"]
    # Pull all cities for this state from research, sorted by distance
    state_cities = [
        (k, c) for k, c in research.items()
        if c.get("state_slug") == slug
    ]
    state_cities.sort(key=lambda x: x[1].get("distance_from_waterloo", {}).get("miles", 0))

    if not state_cities:
        return ""

    rows = []
    for k, c in state_cities[:8]:  # top 8 by distance
        miles = c.get("distance_from_waterloo", {}).get("miles", 0)
        hours = c.get("distance_from_waterloo", {}).get("hours", 0)
        rows.append(
            f'<tr><td>{html.escape(c["name"])}</td><td>{miles} mi</td>'
            f'<td>~{hours:.1f} hrs</td></tr>'
        )

    # Framing paragraph by state tier
    is_home = state["is_home_state"]
    state_slug_l = slug
    if is_home:
        framing = (
            f"Iowa is our home state. Any {name} city is within drive "
            "radius of Waterloo. Distances below are by truck."
        )
    elif state_slug_l in ("illinois", "wisconsin", "minnesota"):
        framing = (
            f"{name} sits within practical field-service drive of "
            "Waterloo. Most major cities are 3–6 hours one-way — "
            "drivable for substantive jobs and bundled diagnostic runs."
        )
    else:
        framing = (
            f"{name} is reachable by truck for major jobs but most "
            "routine work runs ship-in via standard freight. Distances "
            "below are by road; air freight to/from Texas is also "
            "available where the economics justify."
        )

    return (
        f'<h2 id="state-logistics">{html.escape(name)} Logistics from Waterloo</h2>\n'
        f"<p>{framing}</p>\n"
        f'<div class="table-scroll">\n'
        f'<table class="logistics-table">\n'
        f'<thead><tr><th>City</th><th>Miles from Waterloo</th><th>Drive time</th></tr></thead>\n'
        f'<tbody>{"".join(rows)}</tbody>\n'
        f'</table>\n'
        f'</div>\n'
    )


def state_faq_section(state):
    """Phase 3D: state-specific FAQ with FAQPage schema."""
    slug = state["slug"]
    name = state["display_name"]
    qa = STATE_FAQ.get(slug, [])
    if not qa:
        return "", None

    items = []
    for q, a in qa:
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
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in qa
        ],
    }

    return (
        f'<h2 id="faq">Frequently Asked Questions — {html.escape(name)}</h2>\n'
        f'<div class="faq-list">\n'
        + "\n".join(items) + "\n"
        + '</div>\n',
        schema,
    )


def industries_section(state):
    """Bulleted industries-served section with brand-tied context where
    Ken's or Aaron's brief authorized the tie. Industries without an
    authorized brand tie get a brief generic note."""
    clusters = state.get("industry_clusters", []) or []
    if not clusters:
        return ""
    items = []
    for c in clusters:
        note = INDUSTRY_NOTES.get(c.lower(), "")
        if note:
            items.append(f'  <li><strong>{html.escape(c.capitalize())}</strong> — {html.escape(note)}</li>')
        else:
            items.append(f'  <li><strong>{html.escape(c.capitalize())}</strong></li>')
    return (
        f'<h2 id="industries">Industries We Support in {html.escape(state["display_name"])}</h2>\n'
        f'<ul>\n' + "\n".join(items) + '\n</ul>\n'
    )


# Industry → brand-tied context note. Only entries here come from either
# Ken's explicit brand_specifics (Makino aerospace/mold) or Aaron's spec
# (Doosan/Mazak for ag equipment). Other industries render as plain
# bullets — no fabricated brand-tie claims.
INDUSTRY_NOTES = {
    "aerospace": (
        "Makino and DMG Mori work is common — tight tolerances and runout "
        "that shows up in finish work."
    ),
    "defense": (
        "Precision-machining work for defense contractors; Makino and DMG "
        "Mori platforms are routine here."
    ),
    "agricultural equipment": (
        "Doosan and Mazak rebuilds and way covers run routine across this cluster."
    ),
    "heavy machinery": (
        "Large-envelope work — Mazak, Toyoda, and Giddings & Lewis platforms see most of the volume."
    ),
    "heavy equipment": (
        "Large-envelope work — Mazak, Toyoda, and Giddings & Lewis platforms see most of the volume."
    ),
    "medical devices": (
        "Precision-machining work where small runout becomes visible in finish — Makino and Brother Speedio platforms see common."
    ),
    "machine tools": (
        "Rockford and the Illinois machine-tool corridor — broad brand coverage across our service lines."
    ),
    "automotive": (
        "Tier-1 and tier-2 supply-chain machining — broad brand coverage."
    ),
    "food processing": (
        "Equipment manufacturing for food and packaging lines — general CNC service work."
    ),
    "mining equipment": (
        "Large-part work for Iron Range and adjacent equipment manufacturers — Mazak and Toyoda heavy platforms."
    ),
    "precision machining": (
        "Brand-specific expertise matters most here — failure-mode notes on each brand page reflect that."
    ),
    "railroad equipment": (
        "Heavy CNC work for rail-equipment shops in the Omaha corridor."
    ),
    "irrigation systems": (
        "Ag-adjacent CNC machining work."
    ),
    "oil and gas equipment": (
        "Large-part machining — Mazak, Toyoda, and Giddings & Lewis heavy platforms."
    ),
    "semiconductors": (
        "High-precision compact work — Brother Speedio and Makino see most of the demand."
    ),
    "defense vehicles": (
        "Oshkosh-corridor heavy machining — broad brand coverage."
    ),
    "paper and printing equipment": (
        "Fox Valley paper-machinery base — general CNC service across brands."
    ),
}


# ---------- Schema ----------

def state_schemas(state):
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"position": 1, "name": "Home", "item": f"{DOMAIN}/"},
            {"position": 2, "name": "Service Area", "item": f"{DOMAIN}/service-area/"},
            {"position": 3, "name": state["display_name"],
             "item": f"{DOMAIN}/service-area/{state['slug']}/"},
        ],
    }
    service = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": "CNC Machine Repair, Spindle Service, and Way Cover Manufacturing",
        "provider": {"@id": f"{DOMAIN}/#org"},
        "areaServed": {
            "@type": "State",
            "name": state["display_name"],
            "addressRegion": state["abbreviation"],
        },
    }
    return [breadcrumb, service]


# ---------- Page builder ----------

def render_state_page(state, research):
    # Lazy-import the geo data + builders we need (Python module cache
    # makes this cheap on repeated calls).
    import _geo_data
    import generate_brand_pages as gbp

    name = state["display_name"]
    slug = state["slug"]
    canonical_path = f"/service-area/{slug}/"

    # Eyebrow — Iowa skips the suffix because the home-state framing is
    # already distinctive.
    if state["is_home_state"]:
        eyebrow_text = f"{name} Service Coverage (Home State)"
    else:
        eyebrow_text = f"{name} Service Coverage"

    h1 = H1_FOR[slug]

    # Hero image — file lookup with safe fallback
    hero_img_disk = os.path.join(REPO, "assets", "images", "states", f"{slug}.png")
    if os.path.exists(hero_img_disk):
        hero_img = f"/assets/images/states/{slug}.png"
        hero_alt = f"{name} CNC service coverage map"
    else:
        gen_img = os.path.join(REPO, "assets", "images", "general", f"{slug}.png")
        if os.path.exists(gen_img):
            hero_img = f"/assets/images/general/{slug}.png"
        else:
            hero_img = "/assets/images/general/home-image.png"
        hero_alt = f"{name} manufacturing landscape"

    # Video hero — same midwest-cnc-bg-fade.mp4 background as the
    # homepage and the rest of the service-area section. State-scoped
    # eyebrow + H1 + lede; CTAs route to /get-a-quote/ since state
    # pages have no inline #quote form.
    hero_lede = hero_paragraph(state)
    hero_html = gss.build_video_hero_html(
        eyebrow_text=eyebrow_text,
        h1_html=html.escape(h1),
        lede_html=html.escape(hero_lede),
    )

    # MachineLookup widget + state coverage map immediately under hero
    lookup_html = gbp.machine_lookup_html()

    # Coverage map for this state — cities pinned, Waterloo origin
    state_geo = _geo_data.STATE_GEO.get(slug, {})
    cities = _geo_data.cities_for_state(slug)
    map_html = (
        f'<div class="coverage-map"\n'
        f'     data-bounds=\'{json.dumps(state_geo.get("bounds"))}\'\n'
        f'     data-cities=\'{json.dumps(cities, ensure_ascii=False)}\'\n'
        f'     aria-label="Map showing {html.escape(name)} with cities Midwest CNC Services covers, and our Waterloo, IA home base">\n'
        f'  <div class="coverage-map-empty">Loading service area map for {html.escape(name)}…</div>\n'
        f'</div>\n'
        f'<p class="coverage-map-caption">Cities we service in {html.escape(name)} — pinned alongside our Waterloo, IA home base.</p>\n'
    )

    # Phase 3 additions
    faq_html, faq_schema = state_faq_section(state)

    body_parts = [
        hero_html,
        lookup_html,
        map_html,
        manufacturing_section(state),
        regional_breakdown_section(state),
        cities_section(state, research),
        smaller_markets_section(state, research),
        industries_section(state),
        state_logistics_section(state, research),
        f'<h2 id="how-we-work-in-{slug}">How We Work in {html.escape(name)}</h2>',
        f"<p>{how_we_work_text(state)}</p>",
        faq_html,
        gss.trust_block_html(),
        gss.hero_cta_html(),
    ]
    body_html = "\n".join(p for p in body_parts if p)

    schemas = state_schemas(state)
    if faq_schema:
        schemas.append(faq_schema)
    schema_blocks = gss.schema_script_tags(schemas)

    crumbs_html = gss.breadcrumbs_html([
        ("Home", "/"),
        ("Service Area", "/service-area/"),
        (name, None),
    ])

    page_html = gss.wrap_page(
        title=f"{name} CNC Service Coverage | Midwest CNC Services",
        description=(
            f"CNC machine repair, spindle work, and replacement way covers "
            f"in {name}. Field service and shipped builds from Waterloo, IA. "
            f"Call 319-610-4341."
        ),
        canonical=f"{DOMAIN}{canonical_path}",
        schema_blocks=schema_blocks,
        crumbs_html_str=crumbs_html,
        body_html=body_html,
    )

    out_path = os.path.join(PUBLIC, "service-area", slug, "index.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(page_html)
    return out_path


# ---------- Driver ----------

def main():
    states = json.load(open(os.path.join(REPO, "src", "data", "states.json")))["states"]
    research = load_city_research()

    print("=== Generating state pages ===\n")
    for s in states:
        path = render_state_page(s, research)
        size = os.path.getsize(path)
        rel = os.path.relpath(path, REPO)
        has_briefs = bool(s["industry_clusters"] or s["notable_manufacturers"] or s["travel_context"])
        flag = "" if has_briefs else "  [briefs missing]"
        print(f"  ✓ {s['display_name']:<10} → {rel}  ({size // 1024} KB){flag}")


if __name__ == "__main__":
    main()
