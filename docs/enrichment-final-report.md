# Enrichment — Final Report (Phase 5)

**Status:** Awaiting Aaron review before launch. **Do not deploy** until Aaron signs off on this report and the 3-page spot-check.

Audited **108 HTML pages** in `public/`. Comparison baseline is the pre-enrichment audit captured in `docs/seo-thin-content-audit.md` immediately before Phase 2 began.

---

## TL;DR

- **All five enrichment phases shipped.** 33 city pages regenerated, 4 consolidated, 7 state pages expanded, 56 brand pages with FAQs, 4 hubs expanded with ItemList + FAQ schema, homepage geo coordinates wired into `LocalBusiness`, `llms.txt` published.
- **Claim-audit ban-list status: clean.** 0 unauthorized hits across 108 pages. Only the Aaron-authorized exceptions remain (Iowa same-day field response on `service-area/iowa/` + service-area hub FAQ; "warranty" in `terms-of-service/` legal disclaimer).
- **Cross-link audit clean.** 0 broken internal links. Sitemap matches disk (105 URLs, 0 missing). All 4 CONSOLIDATE city URLs covered by `_redirects`. The 2 on-disk pages not in sitemap (`amada-cnc-way-covers`, `trumpf-cnc-way-covers`) are `draft: true` with `verification_pending` — by design.
- **Uniqueness regressed slightly on city pages between Phase 2 acceptance (42.6%) and Phase 5 (36.7%).** Cause is documented below — it's the price of replacing the fabricated "Factory-trained technicians" cert string with a longer honest phrasing during Phase 5B. Editorial honesty was prioritized. Further uniqueness gain now requires Bucket B (per-city local-shop facts from Ken), exactly as flagged in the original Phase 1 acceptance.

---

## 1. Before / after by page type

Word counts and uniqueness, averaged within page-type families.

| Page type | Pages | Avg words BEFORE | Avg words AFTER | Δ words | Uniq% BEFORE | Uniq% AFTER |
|---|---:|---:|---:|---:|---:|---:|
| homepage | 1 | 749 | 761 | +12 | — | — |
| service-hub | 4 | 426 | 437 | +11 | — | — |
| state | 7 | ~268¹ | 810 | **+542** | ~38%¹ | **70%** |
| city | 33 | ~470² | 520 | +50 | ~12%² → 42%³ → 37%⁴ | **37%** |
| brand-spindle | 18 | 487 | 559 | +72 | 32% | 37% |
| brand-repair | 18 | 502 | 552 | +50 | 23% | 27% |
| brand-way-covers | 20 | 425 | 476 | +51 | 16% | 19% |
| site-shell (about/policy/quote/tos) | 4 | 334 | 334 | 0 | — | — |
| 404 | 1 | 28 | 28 | 0 | — | — |

¹ pre-Phase-3 state-page baseline (200-370 words / templated regional fill).
² pre-Phase-2 city-page baseline (the thin-content audit's 12.4% mean).
³ post-Phase-2 (after city restructure + phrase-rotation) — the figure Aaron accepted under "Ship at 42%."
⁴ post-Phase-5 (after replacing "Factory-trained technicians" with longer honest phrasing).

**Total word count delta site-wide vs. pre-enrichment baseline: ≈ +5,000 words.** Remaining gap to competitive targets: **6,667 words** (down from 33,929 at audit baseline).

---

## 2. Cities — ENRICH vs. CONSOLIDATE final count

- **ENRICH:** 33 cities. All 33 received per-city Wikipedia-sourced economy paragraphs, distance/freight context, brand-recommendation inline links by industry, and a 4-question FAQ block with FAQPage schema.
  - Including **North Platte, NE** under Aaron's borderline-ENRICH constraint (no rail-MRO customer claims; Bailey Yard / Union Pacific as regional context only). Final result: **678 words, 78% unique**, passes the 400-word + 60%-uniqueness floor.
- **CONSOLIDATE:** 4 cities — Iowa City IA, Springfield IL, Bellevue NE, Columbia MO. Pages removed from `public/`, 301 redirects in `_redirects`, content absorbed into the parent state page's "Smaller Markets We Serve" section with bespoke 40-word per-city paragraphs.

| Verdict | Count |
|---|---:|
| Pages built (ENRICH) | 33 |
| Pages removed + redirected (CONSOLIDATE) | 4 |
| North Platte (BORDERLINE → ENRICH under constraint) | 1 of the 33 |

---

## 3. Schema additions

| Schema @type | Pages BEFORE | Pages AFTER | Δ |
|---|---:|---:|---:|
| `BreadcrumbList` | 0 | 106 | +106 |
| `FAQPage` | 1 (homepage only) | 101 | +100 |
| `LocalBusiness` | 1 | 92 | +91 |
| `Service` | 0 | 98 | +98 |
| `ItemList` (hub brand grids) | 0 | 3 (repairs / spindle / way-covers hubs) | +3 |
| `Organization` (homepage) | 0 | 1 | +1 |
| Homepage `LocalBusiness.geo` (lat/lon) | absent | present | ✓ |
| Homepage `LocalBusiness.hasMap` | absent | present | ✓ |

Remaining schema gap: 1 — the `/service-area/` hub does not have an ItemList grouping the 7 state pages. Low-impact (it has FAQPage + BreadcrumbList) but a future-pass candidate.

---

## 4. Claim-audit ban-list scan (Phase 5B)

Scanner: `/tmp/claim_scan.py` — covers all 7 categories from `docs/claim-audit.md` (Accuracy, Certifications, Service guarantees, Warranty, Pricing, Capability superlatives, Documentation).

| Result | Count |
|---|---:|
| Files scanned | 108 |
| Total ban-list hits in regenerated HTML | 8 |
| **Unauthorized hits** | **0** |
| Aaron-authorized exceptions surfaced | 8 |

Authorized exceptions surfaced (expected, allowed):

| Category | Phrase | Path | Notes |
|---|---|---|---|
| Guarantees | `same-day` | `/service-area/iowa/` (3×) | Iowa state page — Aaron-authorized "same-day field response is realistic" |
| Guarantees | `same-day` | `/service-area/` (1×) | Hub FAQ re-renders the same Iowa-scoped sentence — same authorized phrasing |
| Warranty | `warranty` | `/terms-of-service/` (4×) | Legal disclaimer language; Aaron-authorized for ToS context |

**Pre-fix state:** the regenerated HTML had 146 unauthorized hits from a templated `"Factory-trained technicians, precision spindle balancing capability, laser alignment services..."` cert string in the trust-footer / certifications boilerplate of city pages, brand pages, and the homepage. This string was inherited from `src/data/spindle-brands.json` and replicated by `generate_city_pages.py`, `generate_brand_pages.py`, and `generate_site_shell.py`.

**Fix:** replaced "Factory-trained technicians" with **"Experienced field technicians with hands-on time across the major CNC OEM platforms"** in the data file plus all three generators. The new phrasing makes a verifiable experience claim (hands-on time across OEM platforms) without asserting an OEM training credential. Other capabilities in the same paragraph — precision spindle balancing, laser alignment, aftermarket supplier relationships — were already verifiable and were preserved verbatim.

Side-effect: the replacement string is ~37 characters longer than the original. Because it appears in templated form across all city + brand pages, it adds shared 5-grams across siblings and **drove average city uniqueness from 42.6% (post-Phase-2) down to 36.7%**. This is the trade-off the editorial constraints required.

---

## 5. Cross-link audit (Phase 5C)

Scanner: `/tmp/cross_link_audit.py` plus the existing audit baked into `scripts/generate_site_shell.py`.

| Check | Result |
|---|---|
| Internal `<a href>` links scanned | 2,013 |
| Broken internal links | **0** ✓ |
| Sitemap URLs | 105 |
| Sitemap URLs missing on-disk file | **0** ✓ |
| Pages on disk not in sitemap | 2 (intentional: `amada-cnc-way-covers` and `trumpf-cnc-way-covers` are `draft: true`, pending Ken confirmation that Midwest CNC makes way covers for press brakes / laser cutters) |
| CONSOLIDATE city URLs covered by `_redirects` | **4 / 4** ✓ |
| `_redirects` rules total | 39 |

The `_redirects` file covers: 4 CONSOLIDATE city URLs → state page; legacy `/spindles-repair/*` URLs → new `/spindle-grinding/*` paths; legacy brand URL relocations; Illinois typo fixes; and deferred-content stubs (`/blog/`, `/guides/`, `/customer-stories/`) pointing to the homepage.

---

## 6. AEO / GEO readiness

| Signal | Status |
|---|---|
| Pages with FAQPage schema (Q&A for AI extraction) | 101 / 108 |
| Pages with direct factual answer in first 200 words | 81 / 108 |
| `llms.txt` at site root | present (2.2 KB) |
| Homepage `LocalBusiness` schema | includes geo coordinates + `hasMap` |
| City pages with geo-aware `Service` schema (`areaServed.City`) | 33 / 33 |
| Pages mentioning all 7 service-area states | 108 / 108 |
| NAP consistency (name / city-state / phone) across all 108 pages | ✓ |

---

## 7. Remaining gaps

Documented honestly. None are blockers for launch.

1. **City-page uniqueness sits at 32–47% across 32 of 33 cities.** North Platte is the lone passing city at 78%. The remaining lift requires Bucket B input — one verifiable local manufacturer name or shop type per city, supplied by Ken or Aaron. The structural enrichment (Wikipedia industry context, FAQ rotation, hero/logistics phrase pools) has been pushed as far as it can go without new facts.
2. **78 orphan pages (in-degree < 5).** Most are by design: 4 site-shell pages (about/privacy/terms/quote) link from footer only; 33 city pages link only from their parent state page (sound topic-cluster shape per AEO best practice); 19 brand-repair pages and 19 brand-way-covers pages link only from their hub + sibling spindle page. Not a real ranking risk for this topology, but flagged for completeness.
3. **One schema gap:** `/service-area/` hub has no ItemList for the 7 state pages. Low-impact, future pass.
4. **2 draft brand pages** (`way-covers/amada-cnc-way-covers`, `way-covers/trumpf-cnc-way-covers`) excluded from sitemap. Awaiting Ken confirmation that Midwest CNC makes way covers / shielding for press brakes (Amada) and laser cutters (Trumpf) — these aren't conventional CNC mill way covers.
5. **Site-wide word-count gap to competitive targets:** 6,667 words remaining (was 33,929 at baseline). Concentrated in brand-spindle (~2,700 words from competitive 700/page target) and brand-repair (~1,000 words from 600/page). All current text is honest — gap closes only with new Ken case-sketch input (Phase 1 / Bucket B).

---

## 8. 3-page spot-check (for Aaron review)

Paste-ready paths covering one of each enriched page type. Open these to read end-to-end before authorizing deploy.

| Type | Path | Words | Uniq% | Notes |
|---|---|---:|---:|---|
| **Enriched city** | `public/service-area/north-platte-nebraska/index.html` | 678 | 78% | Aaron-constrained borderline case. Verify: weak rail tie-back is honestly framed; Bailey Yard / Union Pacific appear as regional context only, never as customers. |
| **Expanded state** | `public/service-area/iowa/index.html` | 840 | 77% | Home-state page. Verify: regional breakdown, smaller-markets absorption of Iowa City, logistics table, FAQ section, Aaron-authorized "same-day field response is realistic" wording. |
| **Enriched brand** | `public/spindle-grinding/mazak-spindle-repair/index.html` | (586 words) | (~42%) | Hub-anchor brand page. Verify: FAQ section, regional emphasis dict (Iowa / Wisconsin / Texas), cross-links to city pages + machine-repair + way-covers, no fabricated certifications. |

A second recommended spot-check pair if time allows:

- **Brand machine-repair:** `public/repairs/amera-seiki-cnc-machine-repair/index.html` — lowest-uniqueness brand-repair page at 21%, useful as the "worst-case still-shipped" example.
- **Hub:** `public/spindle-grinding/index.html` — verify ItemList schema, FAQ section, and the brands-grid rendering.

---

## 9. Phase delivery summary

| Phase | Scope | Status |
|---|---|---|
| 1 | Wikipedia city research (37 cities), consolidation gate, North Platte constraint | ✓ shipped (`docs/city-research.md`, `src/data/city-research.json`) |
| 2 | Template restructure + 33-city regeneration | ✓ shipped, Aaron-accepted at 42% with "Ship at 42%" |
| 3 | State-page expansion: regional breakdowns, smaller-markets absorption, logistics tables, FAQs | ✓ shipped, all 7 states at 65-78% uniqueness, 730-874 words |
| 4 | Brand-page FAQs (56), hub ItemList + FAQ schema, homepage geo + hasMap, llms.txt | ✓ shipped |
| 5 | Final audit + claim-audit ban-list scan + cross-link audit + this report | ✓ shipped |
| 5B-fix | Removed templated "Factory-trained technicians" cert phrase from all generators + data file; replaced with verifiable phrasing | ✓ shipped (this pass) |

---

## 10. Sign-off gate

Before launch:

1. Aaron reads this report end-to-end.
2. Aaron opens the 3 spot-check pages in §8 and confirms editorial framing.
3. Aaron confirms the city-uniqueness trade-off (42.6% → 36.7%) is acceptable given the claim-audit cleanup, OR directs a next-pass effort to recover uniqueness via per-city Bucket B facts.
4. Aaron resolves the 2 draft brand pages (Amada way-covers, Trumpf way-covers) by either getting Ken's confirmation and removing `draft: true`, or by adding 301 redirects from those URLs to the way-covers hub.

After Aaron sign-off, deploy is unblocked.
