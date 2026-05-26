# Spindle Page Pattern — Template Spec for Brand Pages

## Source pages analyzed

> **Important substitution.** Task 1 confirmed that *all 20* pages under `/spindle-grinding/` are stubs (no h1, 0 body chars). There are no "real" spindle-grinding pages to reverse-engineer. Instead this doc analyzes the closest sibling pages — `/spindles-repair/mazak-spindle-repair` and `/spindles-repair/haas-spindle-repair` — which are the same brand × spindle-service content under a different URL prefix.

| | `/spindles-repair/mazak-spindle-repair` | `/spindles-repair/haas-spindle-repair` |
|---|---|---|
| Title | `Mazak Spindle Repair \| Midwest CNC Services` | `Haas Spindle Repair \| Midwest CNC Services` |
| H1 | "Eliminate Costly Downtime" | "Grinding & Repair" |
| Sections | 4 | 5 |
| Body words (all sections) | ~305 | ~291 |
| Images | 3 | 3 |
| Internal links | 3 | 3 |
| JSON-LD blocks | 0 | 0 |
| Canonical link | none | none |

## 1. Section structure

Word counts cover body text only (heading text excluded). Image counts are images that live inside the section.

### Mazak (4 sections)

| Sec | Level | Heading | Words | Imgs |
|---|---|---|---|---|
| 0 | — | *(pre-H1 eyebrow)* | 4 | 0 |
| 1 | h1 | **Eliminate Costly Downtime** | 125 | 2 |
| 2 | h2 | Mazak Spindle Repair *(3-step workflow + quote form)* | 147 | 1 |
| 3 | h2 | Recent blog posts | 29 | 0 |

H3s inside section 1: **Mazak Models We Support** (model list lives here, no separate H2)
H3s inside section 2: **Mazak Spindle Repair Quote** (form heading)
H3s inside section 3: the three blog post titles, each truncated

### Haas (5 sections)

| Sec | Level | Heading | Words | Imgs |
|---|---|---|---|---|
| 0 | — | *(pre-H1 eyebrow)* | 3 | 0 |
| 1 | h1 | **Grinding & Repair** | 37 | 1 |
| 2 | h2 | Haas Models We Support | 83 | 1 |
| 3 | h2 | Haas Spindle Repair *(3-step workflow + quote form)* | 142 | 1 |
| 4 | h2 | Recent blog posts | 29 | 0 |

H3s: **Haas Spindle Repair Quote**, plus the three blog post titles.

### Pattern divergence between the two

The Mazak page bundles the model list inside the H1 hero section; the Haas page splits it into its own H2 ("Haas Models We Support"). **The Haas layout is the better template** — the model list deserves its own anchor for navigation, SEO, and rendering — so the spec below standardizes on it.

The Haas H1 ("Grinding & Repair") is suspiciously brand-less, suggesting a hasty edit. We should standardize the H1 on a value-prop hook (not the brand name) but make sure it makes sense on its own (Mazak's "Eliminate Costly Downtime" is the better model).

## 2. Tone calibration

**Technical depth: medium.** The pages namedrop specific machine families with model-number ranges (e.g. "VTC-200B → VTC-800/30", "EC-300 → EC-1600") to demonstrate breadth and SEO-target the model searches a maintenance manager would type. They do **not** go deeper than that — no service-bulletin language, no torque specs, no engineering diagrams. The reader is expected to know what a spindle is and what runout means, but not to be an engineer.

**Audience.** Shop manager or maintenance lead, not the operator and not the procurement director. They have a broken spindle, they know the machine model, they want a flat price, a fast turnaround, and a phone number that picks up. Keywords like "downtime", "flat rate", and "same day" speak to that buyer.

**Formality: low-medium.** Contractions are common ("Don't", "We'll"). Casual phrases: "watch chips fly", "friendly call", "fire back price", "no surprises", "no machine left behind". Industry-correct nouns are mixed with marketing voice — feels like a service writer wrote it, not an engineer.

**Repeated phrases / terminology across both pages:**

- "flat rates" / "flat-rate pricing"
- "sub-micron accuracy" (Mazak) / "sub-micron runout guaranteed" (Haas)
- "factory-trained techs" / "factory-grade"
- "no machine left behind" / "no model left behind"
- "photo-verified" (Mazak only — worth keeping for all)
- "{Brand} spindle grinding, repair, and full rebuilds"
- "Get a Quote" — the universal button copy
- "Step 1 Contact Us / Step 2 Grab Model # / Step 3 Approve & Relax" — identical 3-step workflow on both
- "319-610-4341" — the same phone number, appears once or twice per page

**Quirks present in the source pages that the rebuild should NOT carry forward:**

- The Haas page has way-cover boilerplate accidentally pasted into the spindle section: *"Need a Haas spindle **cover** quote right now? ... lock in custom CNC way-cover pricing"* and *"We laser-cut, form, and ship"* (that's way-cover production language, not spindle rebuild language).
- Typo on the Haas page: "online forrm" (should be "form").
- Empty `alt` text on all 6 images across the two pages.
- The Haas page reuses Mazak's brand image (`/assets/images/services/spindles-repair-mazak-spindle-repair-image.png`).
- No JSON-LD on either page.
- No `<link rel="canonical">` on either page.

## 3. CTA pattern

Both pages are heavily CTA-loaded. Exact button counts:

- Mazak: **7 buttons total** — 5× "Get a Quote", 1× "Submit" (form), 2× phone link `319-610-4341`
- Haas: **6 buttons total** — 5× "Get a Quote" / "Get A Quote", 1× "Submit", 2× phone link

Placement:

| Location | Mazak | Haas |
|---|---|---|
| H1 hero — inline after value prop | "Get a Quote" + phone | "Get a Quote" + phone |
| Models section closing | (no — list ends in H1 sec) | "Get A Quote" *(capital A — likely typo)* |
| 3-step workflow — one CTA per step | 3× "Get a Quote" | 3× "Get a Quote" |
| Quote form footer | "Submit" + phone | "Submit" + phone |

Button targets aren't internal links — they're form-triggering buttons (no `href` on the `<button>` element). The phone link uses `tel:319-610-4341` (Mazak has one as `tel:+13196104341`, Haas has one as `tel:319-610-4341` — inconsistent E.164 formatting, rebuild should normalize).

**Exact button copy to standardize on:** `Get a Quote` (lowercase "a"). The single occurrence of `Get A Quote` is almost certainly an editing error.

## 4. Schema markup

**Zero JSON-LD on both source pages.** This is a gap, not a pattern. The rebuild is an opportunity to add proper structured data. The template spec below assumes we'll add it.

## 5. Internal linking

Both pages have **exactly 3 internal links**, and they are the *same* 3 links — the three evergreen blog posts referenced in the "Recent blog posts" section:

- `/blog/precision-cnc-machining--how-it-drives-efficiency-in-manufacturing`
- `/blog/understanding-the-true-cost--usa-made-way-covers-vs--overseas-options`
- `/blog/choosing-the-right-way-covers-for-your-cnc-machines--a-comprehensive-buyer-s-guide`

This is a significant SEO miss. Real brand pages on a multi-brand service site should cross-link to:

- The sibling service for the same brand (e.g. Mazak spindle page → Mazak way-covers page, Mazak CNC machine repair page)
- A handful of peer brand pages (e.g. "We also service Okuma, Haas, DMG Mori spindles")
- A few service-area pages where the brand is common
- The contact / quote landing page

**The rebuild should target ~8–12 internal links per brand page**, contextually placed (not a link dump).

## 6. Image usage

3 images per page in identical positions:

| Slot | File on disk | Notes |
|---|---|---|
| 1. Hero (top of H1 section) | `/assets/images/general/image-of-spindle-grinding.png` | Generic spindle-grinding photo, reused across all brands |
| 2. Mid-page (inside Models or H2 workflow) | `/assets/images/services/spindles-repair-{brand}-spindle-repair-image.png` | **Brand-specific slot** — but Haas reuses Mazak's image (bug) |
| 3. End (above blog posts or above form) | `/assets/images/general/about-image-3.png` | Generic — looks decorative |

**Alt text on all 6 images is empty.** This is the biggest accessibility/SEO gap. The rebuild must populate alt text for every image. Pattern: `"{Brand} {machine type/scene}"`, e.g. `"Mazak INTEGREX spindle on the grinding bench"`, `"Haas VF-3 with spindle cartridge removed"`.

## 7. Other observations

- **Pre-H1 eyebrow.** Both pages open with a short eyebrow line above the H1: "Mazak Spindle Repair & Grinding" / "Haas Spindle Repair". This is text inside section 0 (level 0, no heading). The rebuild should treat this as a styled `<p class="eyebrow">` or similar — short, brand-named, sets context for the value-prop H1.
- **Title + H1 mismatch is intentional.** Title says the brand and the service; H1 says the *benefit*. Don't merge them.
- **The 3-step workflow + quote form is boilerplate.** Identical text, identical structure across brands. In the rebuild this should be a partial/component rendered once and included on every brand page, not hand-authored 20 times.
- **The "Recent blog posts" trailer is also boilerplate.** Currently the same 3 posts on every page. The rebuild should render this from the blog index dynamically (or at least from a single config) so a new blog post propagates everywhere.

---

## Template Specification

Numbered contract for every new spindle-grinding brand page. A page that ships under `/spindle-grinding/{slug}-spindle-repair/` MUST include every section below, in this order, hitting the listed word counts.

**Brand-authored content** (sections 2, 3, 4, 5) needs Ken's input per brand — see `src/data/spindle-brands.json`. **Boilerplate** sections (6, 7) come from shared partials.

### 1. Page metadata (in `<head>`)

| Field | Spec |
|---|---|
| `<title>` | `{Brand} Spindle Repair \| Midwest CNC Services` (≤ 65 chars) |
| `<meta name="description">` | 150–180 chars, brand-named, value-prop. Must include: on-site/Midwest, brand name, flat-rate, one brand-specific differentiator |
| `<link rel="canonical">` | `https://midwestcncservices.com/spindle-grinding/{slug}-spindle-repair/` |
| `<meta property="og:title">` | Mirror `<title>` |
| `<meta property="og:description">` | Mirror meta description (or shorter, ≤ 140 chars) |
| `<meta property="og:image">` | Brand-specific image at `/assets/images/services/spindle-grinding-{slug}-hero.jpg` (TBD — needs photo sourcing) |
| `<meta property="og:type">` | `website` |
| `<meta name="robots">` | `index, follow` |

### 2. Eyebrow line — pre-H1 (no heading tag)

- **1 line, 3–5 words:** `{Brand} Spindle Repair & Grinding`
- Rendered as a styled paragraph above the H1.

### 3. H1 hero section

- **H1 text:** 2–4 word benefit hook. NOT the brand name. NOT the service name. Examples: "Eliminate Costly Downtime", "Stop the Bleeding", "Back to Tolerance Fast". One per brand or shared.
- **Body copy:** **60–100 words.** Opens with a downtime/pain hook. Names the brand. Lists primary machine families inline. Closes with the proof-points triad: flat rates / sub-micron accuracy / photo-verified.
- **Inline CTAs in the hero:** one "Get a Quote" button + one `tel:` phone link.
- **1 hero image,** alt text populated.

### 4. H2 — "{Brand} Models We Support"

- **Lead-in sentence:** 1–2 sentences (~25–40 words). Names the brand, names the service breadth, leaves no model behind.
- **Bulleted model list:** 5–8 machine families, each formatted as `{Family name} ({first model} → {last model})`. Brand-specific — needs Ken's input (`brand_specifics` field).
- **Optional closing flourish:** one-liner like "If it wears a {Brand} badge, we restore its spindle."
- **Inline CTA:** one "Get a Quote" button.
- **Total: 80–130 words** + the bulleted model list.
- **1 brand-specific image,** alt text populated.

### 5. H2 — "{Brand} Spindle Repair: How It Works" *(or shorter heading)*

- **Brand-specific intro:** 1 short paragraph (~30–50 words) calling out anything notable for this brand — common failure mode, lead-time expectation, or a parts-availability note. Pulled from Ken's `common_failure_mode` / `typical_lead_time` fields.
- This section anchors the boilerplate workflow + form (section 7) but adds the brand-personalized intro so the page doesn't feel like a Mad-Libs template.

### 6. H2 — Trust & differentiators *(optional, recommended)*

- 3–5 short bullets or a 3-card row covering: certifications (Ken's `certifications`), parts situation (Ken's `parts_situation`), and one brand-specific differentiator.
- **Total: 60–120 words.** Skip the section entirely if Ken's inputs are empty for the brand — better blank than padded.

### 7. H2 — "Get Your {Brand} Spindle Repair Quote" *(boilerplate partial)*

- The shared 3-step workflow component:
  - Step 1 Contact Us — friendly-call/form copy + "Get a Quote" CTA
  - Step 2 Grab Model # — "We'll fire back price, lead time, and shipping ETA usually same day." + CTA
  - Step 3 Approve & Restore — spindle-correct copy (NOT "laser-cut, form, and ship" — that's way-cover boilerplate that leaked into the Haas page). Replacement: "We rebuild, balance to sub-micron runout, and ship."
- Then the quote form: Name / Email / Phone / Company / City / State / Postal Code / Machine Model & Details / Submit.
- reCAPTCHA notice with linked Google Privacy Policy and Terms of Service.
- **Total component: ~140 words** + form fields. Same on every brand page.

### 8. H2 — "Related {Brand} Services" *(new — fixes the cross-link gap)*

- 3 internal links to sibling pages for the same brand:
  - `/repairs/{slug}-cnc-machine-repair`
  - `/spindles-repair/{slug}-spindle-repair`
  - `/way-covers/{slug}-cnc-way-covers`
- 2–4 internal links to peer brand spindle-grinding pages (e.g. for Mazak: link to Okuma, DMG Mori, Mori Seiki).
- 1–2 links to relevant service-area pages.
- **Word count: 40–80 words of framing copy + the link list.**

### 9. H2 — "Recent from the blog" *(boilerplate partial)*

- The shared 3-up blog teaser block, rendered from the blog index (not hard-coded per page).
- Keep the existing 3 evergreen posts as the default until newer ones exist.

### 10. JSON-LD structured data *(new — none on source pages)*

In `<head>` or just before `</body>`, emit:

- **`Service`** — `serviceType: "{Brand} CNC Spindle Repair and Grinding"`, `provider: { "@id": "#org" }`, `areaServed`: list of Midwest states, `hasOfferCatalog` with the machine families from section 4.
- **`LocalBusiness`** (or `Organization`) with `@id: "#org"` — name, phone (`+1-319-610-4341`), address, geo, hours, sameAs (social profiles if any).
- **`BreadcrumbList`** — Home → Spindle Grinding → {Brand} Spindle Repair.
- **`FAQPage`** *(optional, recommended)* — 3–5 Q&As specific to the brand pulled from Ken's `brand_specifics` and `common_failure_mode`.

### Target totals per page

| Metric | Target |
|---|---|
| Visible body words (sections 2–9, excluding form fields and JSON-LD) | **500–700** |
| Internal links (excluding nav/footer) | **8–12** |
| Images | **3–5** (all with populated alt text) |
| H1 | exactly 1 |
| H2s | 5–7 (sections 4, 5, 6, 7, 8, 9) |
| JSON-LD blocks | 3–4 |
| CTAs ("Get a Quote" buttons + phone links) | 4–6 |
