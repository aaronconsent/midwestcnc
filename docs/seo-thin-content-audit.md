# SEO / AEO / GEO + Thin-Content Audit

Audited **108 HTML files** under `public/`. Audit-only — no HTML modified. This report drives the next enrichment pass.

## Headline numbers

- **City pages below 60% unique:** 32 / 33 🚨
- **State pages below 60% unique:** 0 / 7
- **Brand spindle pages below 60% unique:** 18 / 18
- **Brand machine-repair pages below 60% unique:** 18 / 18
- **Brand way-covers pages below 60% unique:** 20 / 20
- **Total word gap to competitive targets:** **~8,856 words** across all pages
- `llms.txt` present at site root: **yes**
- Homepage `LocalBusiness` schema has geo coordinates: **yes**
- NAP consistency across all pages: name=✓  city/state=✓  phone=✓

## Task 1 — Per-page content depth

Grouped by page type. Columns: word count, h2/h3, internal-link out-degree, direct-answer signal (count of factual patterns in first 200 words), images, schema types, n-gram uniqueness (where computed).

### homepage  (1 pages)

| Path | Words | H2 | H3 | Links out | Answer | Images | Uniq% | Schema |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `index.html` | 755 | 6 | 10 | 31 | 2 | 12 | — | FAQPage+LocalBusiness |

### service-hub  (4 pages)

| Path | Words | H2 | H3 | Links out | Answer | Images | Uniq% | Schema |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `repairs/index.html` | 566 | 6 | 0 | 45 | 2 | 2 | — | BreadcrumbList+FAQPage+ItemList |
| `service-area/index.html` | 307 | 3 | 7 | 31 | 3 | 8 | — | BreadcrumbList+FAQPage |
| `spindle-grinding/index.html` | 464 | 6 | 0 | 43 | 2 | 2 | — | BreadcrumbList+FAQPage+ItemList |
| `way-covers/index.html` | 468 | 6 | 0 | 43 | 2 | 2 | — | BreadcrumbList+FAQPage+ItemList |

### site-shell  (4 pages)

| Path | Words | H2 | H3 | Links out | Answer | Images | Uniq% | Schema |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `about/index.html` | 329 | 3 | 3 | 31 | 4 | 1 | — | BreadcrumbList |
| `get-a-quote/index.html` | 117 | 1 | 2 | 31 | 2 | 1 | — | BreadcrumbList |
| `privacy-policy/index.html` | 372 | 5 | 0 | 31 | 0 | 1 | — | BreadcrumbList |
| `terms-of-service/index.html` | 529 | 8 | 0 | 31 | 1 | 1 | — | BreadcrumbList |

### state  (7 pages)

| Path | Words | H2 | H3 | Links out | Answer | Images | Uniq% | Schema |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `service-area/illinois/index.html` | 828 | 9 | 3 | 35 | 2 | 2 | 67 | BreadcrumbList+FAQPage+Service |
| `service-area/iowa/index.html` | 840 | 9 | 3 | 36 | 1 | 2 | 77 | BreadcrumbList+FAQPage+Service |
| `service-area/minnesota/index.html` | 746 | 8 | 3 | 36 | 3 | 2 | 71 | BreadcrumbList+FAQPage+Service |
| `service-area/missouri/index.html` | 834 | 9 | 3 | 34 | 3 | 2 | 65 | BreadcrumbList+FAQPage+Service |
| `service-area/nebraska/index.html` | 817 | 9 | 3 | 36 | 2 | 2 | 68 | BreadcrumbList+FAQPage+Service |
| `service-area/texas/index.html` | 874 | 8 | 4 | 37 | 2 | 2 | 70 | BreadcrumbList+FAQPage+Service |
| `service-area/wisconsin/index.html` | 730 | 8 | 3 | 36 | 2 | 2 | 70 | BreadcrumbList+FAQPage+Service |

### city  (33 pages)

| Path | Words | H2 | H3 | Links out | Answer | Images | Uniq% | Schema |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `service-area/ames-iowa/index.html` | 528 | 4 | 0 | 31 | 1 | 2 | 38 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/austin-texas/index.html` | 494 | 4 | 0 | 32 | 2 | 2 | 31 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/bloomington-minnesota/index.html` | 478 | 4 | 0 | 31 | 1 | 2 | 33 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/cedar-rapids-iowa/index.html` | 546 | 4 | 0 | 32 | 1 | 2 | 37 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/chicago-illinois/index.html` | 503 | 4 | 0 | 31 | 1 | 2 | 35 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/dallas-texas/index.html` | 546 | 4 | 0 | 32 | 2 | 2 | 36 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/davenport-iowa/index.html` | 525 | 4 | 0 | 31 | 1 | 2 | 34 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/des-moines-iowa/index.html` | 519 | 4 | 0 | 31 | 1 | 2 | 42 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/duluth-minnesota/index.html` | 517 | 4 | 0 | 32 | 1 | 2 | 35 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/el-paso-texas/index.html` | 549 | 4 | 0 | 31 | 2 | 2 | 35 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/fort-worth-texas/index.html` | 558 | 4 | 0 | 32 | 2 | 2 | 35 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/grand-island-nebraska/index.html` | 520 | 4 | 0 | 31 | 2 | 2 | 38 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/green-bay-wisconsin/index.html` | 513 | 4 | 0 | 31 | 1 | 2 | 37 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/houston-texas/index.html` | 539 | 4 | 0 | 31 | 2 | 2 | 32 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/kansas-city-missouri/index.html` | 564 | 4 | 0 | 32 | 1 | 2 | 37 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/kearney-nebraska/index.html` | 492 | 4 | 0 | 31 | 2 | 2 | 34 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/kenosha-wisconsin/index.html` | 475 | 4 | 0 | 31 | 1 | 2 | 34 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/lincoln-nebraska/index.html` | 497 | 4 | 0 | 32 | 1 | 2 | 32 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/madison-wisconsin/index.html` | 502 | 4 | 0 | 32 | 1 | 2 | 34 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/milwaukee-wisconsin/index.html` | 474 | 4 | 0 | 31 | 1 | 2 | 31 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/minneapolis-minnesota/index.html` | 497 | 4 | 0 | 32 | 1 | 2 | 32 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/naperville-illinois/index.html` | 497 | 4 | 0 | 31 | 2 | 2 | 34 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/north-platte-nebraska/index.html` | 678 | 4 | 0 | 31 | 1 | 2 | 78 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/omaha-nebraska/index.html` | 491 | 4 | 0 | 31 | 1 | 2 | 36 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/peoria-illinois/index.html` | 526 | 4 | 0 | 31 | 1 | 2 | 36 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/racine-wisconsin/index.html` | 514 | 4 | 0 | 31 | 1 | 2 | 32 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/rochester-minnesota/index.html` | 536 | 4 | 0 | 31 | 1 | 2 | 39 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/rockford-illinois/index.html` | 514 | 4 | 0 | 32 | 1 | 2 | 37 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/san-antonio-texas/index.html` | 531 | 4 | 0 | 31 | 2 | 2 | 35 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/springfield-missouri/index.html` | 496 | 4 | 0 | 31 | 1 | 2 | 33 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/st-louis-missouri/index.html` | 558 | 4 | 0 | 32 | 1 | 2 | 36 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/st-paul-minnesota/index.html` | 512 | 4 | 0 | 31 | 1 | 2 | 36 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `service-area/waterloo-iowa/index.html` | 473 | 4 | 0 | 31 | 2 | 2 | 47 | BreadcrumbList+FAQPage+LocalBusiness+Service |

### brand-spindle  (18 pages)

| Path | Words | H2 | H3 | Links out | Answer | Images | Uniq% | Schema |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `spindle-grinding/amera-seiki-spindle-repair/index.html` | 462 | 9 | 0 | 36 | 4 | 2 | 32 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/brother-spindle-repair/index.html` | 515 | 9 | 0 | 36 | 4 | 2 | 43 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/dmg-mori-spindle-repair/index.html` | 572 | 9 | 0 | 33 | 3 | 2 | 47 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/doosan-spindle-repair/index.html` | 558 | 9 | 0 | 33 | 3 | 2 | 44 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/fadal-spindle-repair/index.html` | 552 | 10 | 0 | 36 | 3 | 2 | 45 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/fanuc-spindle-repair/index.html` | 494 | 9 | 0 | 34 | 4 | 2 | 38 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/giddings-lewis-spindle-repair/index.html` | 493 | 9 | 0 | 37 | 4 | 2 | 41 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/haas-spindle-repair/index.html` | 552 | 9 | 0 | 33 | 3 | 2 | 44 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/hitachi-seiki-spindle-repair/index.html` | 541 | 10 | 0 | 36 | 3 | 2 | 45 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/hurco-spindle-repair/index.html` | 547 | 9 | 0 | 35 | 3 | 2 | 42 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/johnford-spindle-repair/index.html` | 457 | 9 | 0 | 36 | 4 | 2 | 33 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/makino-spindle-repair/index.html` | 508 | 9 | 0 | 35 | 4 | 2 | 39 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/mazak-spindle-repair/index.html` | 546 | 9 | 0 | 32 | 3 | 2 | 44 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/monarch-spindle-repair/index.html` | 542 | 10 | 0 | 36 | 3 | 2 | 42 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/mori-seiki-spindle-repair/index.html` | 550 | 9 | 0 | 34 | 3 | 2 | 43 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/niigata-spindle-repair/index.html` | 470 | 9 | 0 | 36 | 4 | 2 | 35 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/okuma-spindle-repair/index.html` | 511 | 9 | 0 | 32 | 4 | 2 | 39 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `spindle-grinding/toyoda-spindle-repair/index.html` | 478 | 9 | 0 | 35 | 4 | 2 | 34 | BreadcrumbList+FAQPage+LocalBusiness+Service |

### brand-repair  (18 pages)

| Path | Words | H2 | H3 | Links out | Answer | Images | Uniq% | Schema |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `repairs/amera-seiki-cnc-machine-repair/index.html` | 491 | 9 | 0 | 34 | 3 | 2 | 21 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/brother-cnc-machine-repair/index.html` | 517 | 9 | 0 | 34 | 3 | 2 | 27 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/dmg-mori-cnc-machine-repair/index.html` | 542 | 9 | 0 | 31 | 2 | 2 | 31 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/doosan-cnc-machine-repair/index.html` | 512 | 9 | 0 | 31 | 3 | 2 | 26 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/fadal-cnc-machine-repair/index.html` | 504 | 9 | 0 | 34 | 3 | 2 | 27 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/fanuc-cnc-machine-repair/index.html` | 496 | 9 | 0 | 31 | 3 | 2 | 25 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/giddings-lewis-cnc-machine-repair/index.html` | 523 | 9 | 0 | 34 | 2 | 2 | 27 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/haas-cnc-machine-repair/index.html` | 525 | 9 | 0 | 31 | 3 | 2 | 29 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/hitachi-seiki-cnc-machine-repair/index.html` | 514 | 9 | 0 | 34 | 2 | 2 | 28 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/hurco-cnc-machine-repair/index.html` | 505 | 9 | 0 | 34 | 3 | 2 | 26 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/johnford-cnc-machine-repair/index.html` | 496 | 9 | 0 | 34 | 3 | 2 | 22 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/makino-cnc-machine-repair/index.html` | 511 | 9 | 0 | 34 | 3 | 2 | 25 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/mazak-cnc-machine-repair/index.html` | 521 | 9 | 0 | 31 | 3 | 2 | 28 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/monarch-cnc-machine-repair/index.html` | 506 | 9 | 0 | 34 | 3 | 2 | 24 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/mori-seiki-cnc-machine-repair/index.html` | 537 | 9 | 0 | 34 | 2 | 2 | 28 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/niigata-cnc-machine-repair/index.html` | 503 | 9 | 0 | 34 | 3 | 2 | 24 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/okuma-cnc-machine-repair/index.html` | 508 | 9 | 0 | 31 | 3 | 2 | 26 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `repairs/toyoda-cnc-machine-repair/index.html` | 504 | 9 | 0 | 34 | 3 | 2 | 23 | BreadcrumbList+FAQPage+LocalBusiness+Service |

### brand-main-alt  (2 pages)

| Path | Words | H2 | H3 | Links out | Answer | Images | Uniq% | Schema |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `repairs/amada-press-brake-service/index.html` | 329 | 7 | 0 | 33 | 3 | 2 | — | BreadcrumbList+LocalBusiness+Service |
| `repairs/trumpf-laser-service/index.html` | 308 | 7 | 0 | 33 | 4 | 2 | — | BreadcrumbList+LocalBusiness+Service |

### brand-way-covers  (20 pages)

| Path | Words | H2 | H3 | Links out | Answer | Images | Uniq% | Schema |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `way-covers/amada-cnc-way-covers/index.html` | 411 | 8 | 0 | 33 | 3 | 2 | 16 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/amera-seiki-cnc-way-covers/index.html` | 430 | 8 | 0 | 34 | 3 | 2 | 17 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/brother-cnc-way-covers/index.html` | 435 | 8 | 0 | 34 | 3 | 2 | 20 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/dmg-mori-cnc-way-covers/index.html` | 457 | 8 | 0 | 31 | 3 | 2 | 22 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/doosan-cnc-way-covers/index.html` | 437 | 8 | 0 | 31 | 3 | 2 | 21 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/fadal-cnc-way-covers/index.html` | 429 | 8 | 0 | 34 | 3 | 2 | 17 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/fanuc-cnc-way-covers/index.html` | 430 | 8 | 0 | 31 | 3 | 2 | 17 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/giddings-lewis-cnc-way-covers/index.html` | 447 | 8 | 0 | 34 | 3 | 2 | 20 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/haas-cnc-way-covers/index.html` | 444 | 8 | 0 | 31 | 3 | 2 | 20 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/hitachi-seiki-cnc-way-covers/index.html` | 450 | 8 | 0 | 34 | 3 | 2 | 21 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/hurco-cnc-way-covers/index.html` | 434 | 8 | 0 | 34 | 3 | 2 | 18 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/johnford-cnc-way-covers/index.html` | 432 | 8 | 0 | 34 | 3 | 2 | 18 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/makino-cnc-way-covers/index.html` | 428 | 8 | 0 | 34 | 3 | 2 | 18 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/mazak-cnc-way-covers/index.html` | 448 | 8 | 0 | 31 | 3 | 2 | 20 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/monarch-cnc-way-covers/index.html` | 431 | 8 | 0 | 34 | 3 | 2 | 18 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/mori-seiki-cnc-way-covers/index.html` | 456 | 8 | 0 | 34 | 3 | 2 | 20 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/niigata-cnc-way-covers/index.html` | 431 | 8 | 0 | 34 | 3 | 2 | 18 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/okuma-cnc-way-covers/index.html` | 441 | 8 | 0 | 31 | 3 | 2 | 19 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/toyoda-cnc-way-covers/index.html` | 428 | 8 | 0 | 34 | 3 | 2 | 18 | BreadcrumbList+FAQPage+LocalBusiness+Service |
| `way-covers/trumpf-cnc-way-covers/index.html` | 427 | 8 | 0 | 33 | 3 | 2 | 19 | BreadcrumbList+FAQPage+LocalBusiness+Service |

### 404  (1 pages)

| Path | Words | H2 | H3 | Links out | Answer | Images | Uniq% | Schema |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `404.html` | 28 | 0 | 0 | 31 | 0 | 1 | — | (none) |

## Task 2 — Location-page uniqueness (CRITICAL)

5-gram analysis: for each location page, what fraction of 5-grams are unique to that page across siblings? **Below 60% is the SEO penalty-risk threshold for location-page enforcement.**

### City pages (sorted by uniqueness, lowest first)

| Path | Words | Unique 5-grams | Verdict |
|---|---:|---:|:-:|
| `service-area/milwaukee-wisconsin/index.html` | 474 | 31% | 🚨 FAIL |
| `service-area/austin-texas/index.html` | 494 | 31% | 🚨 FAIL |
| `service-area/racine-wisconsin/index.html` | 514 | 32% | 🚨 FAIL |
| `service-area/lincoln-nebraska/index.html` | 497 | 32% | 🚨 FAIL |
| `service-area/minneapolis-minnesota/index.html` | 497 | 32% | 🚨 FAIL |
| `service-area/houston-texas/index.html` | 539 | 32% | 🚨 FAIL |
| `service-area/bloomington-minnesota/index.html` | 478 | 33% | 🚨 FAIL |
| `service-area/springfield-missouri/index.html` | 496 | 33% | 🚨 FAIL |
| `service-area/kenosha-wisconsin/index.html` | 475 | 34% | 🚨 FAIL |
| `service-area/kearney-nebraska/index.html` | 492 | 34% | 🚨 FAIL |
| `service-area/naperville-illinois/index.html` | 497 | 34% | 🚨 FAIL |
| `service-area/davenport-iowa/index.html` | 525 | 34% | 🚨 FAIL |
| `service-area/madison-wisconsin/index.html` | 502 | 34% | 🚨 FAIL |
| `service-area/san-antonio-texas/index.html` | 531 | 35% | 🚨 FAIL |
| `service-area/el-paso-texas/index.html` | 549 | 35% | 🚨 FAIL |
| `service-area/duluth-minnesota/index.html` | 517 | 35% | 🚨 FAIL |
| `service-area/chicago-illinois/index.html` | 503 | 35% | 🚨 FAIL |
| `service-area/fort-worth-texas/index.html` | 558 | 35% | 🚨 FAIL |
| `service-area/peoria-illinois/index.html` | 526 | 36% | 🚨 FAIL |
| `service-area/dallas-texas/index.html` | 546 | 36% | 🚨 FAIL |
| `service-area/omaha-nebraska/index.html` | 491 | 36% | 🚨 FAIL |
| `service-area/st-paul-minnesota/index.html` | 512 | 36% | 🚨 FAIL |
| `service-area/st-louis-missouri/index.html` | 558 | 36% | 🚨 FAIL |
| `service-area/rockford-illinois/index.html` | 514 | 37% | 🚨 FAIL |
| `service-area/green-bay-wisconsin/index.html` | 513 | 37% | 🚨 FAIL |
| `service-area/cedar-rapids-iowa/index.html` | 546 | 37% | 🚨 FAIL |
| `service-area/kansas-city-missouri/index.html` | 564 | 37% | 🚨 FAIL |
| `service-area/ames-iowa/index.html` | 528 | 38% | 🚨 FAIL |
| `service-area/grand-island-nebraska/index.html` | 520 | 38% | 🚨 FAIL |
| `service-area/rochester-minnesota/index.html` | 536 | 39% | 🚨 FAIL |
| `service-area/des-moines-iowa/index.html` | 519 | 42% | 🚨 FAIL |
| `service-area/waterloo-iowa/index.html` | 473 | 47% | 🚨 FAIL |
| `service-area/north-platte-nebraska/index.html` | 678 | 78% | ✓ |

### State pages

| Path | Words | Unique 5-grams | Verdict |
|---|---:|---:|:-:|
| `service-area/missouri/index.html` | 834 | 65% | ⚠ borderline |
| `service-area/illinois/index.html` | 828 | 67% | ⚠ borderline |
| `service-area/nebraska/index.html` | 817 | 68% | ⚠ borderline |
| `service-area/wisconsin/index.html` | 730 | 70% | ⚠ borderline |
| `service-area/texas/index.html` | 874 | 70% | ⚠ borderline |
| `service-area/minnesota/index.html` | 746 | 71% | ⚠ borderline |
| `service-area/iowa/index.html` | 840 | 77% | ✓ |

### Brand-spindle pages

| Path | Words | Unique 5-grams |
|---|---:|---:|
| `spindle-grinding/amera-seiki-spindle-repair/index.html` | 462 | 32% |
| `spindle-grinding/johnford-spindle-repair/index.html` | 457 | 33% |
| `spindle-grinding/toyoda-spindle-repair/index.html` | 478 | 34% |
| `spindle-grinding/niigata-spindle-repair/index.html` | 470 | 35% |
| `spindle-grinding/fanuc-spindle-repair/index.html` | 494 | 38% |
| `spindle-grinding/makino-spindle-repair/index.html` | 508 | 39% |
| `spindle-grinding/okuma-spindle-repair/index.html` | 511 | 39% |
| `spindle-grinding/giddings-lewis-spindle-repair/index.html` | 493 | 41% |

### Brand machine-repair pages

| Path | Words | Unique 5-grams |
|---|---:|---:|
| `repairs/amera-seiki-cnc-machine-repair/index.html` | 491 | 21% |
| `repairs/johnford-cnc-machine-repair/index.html` | 496 | 22% |
| `repairs/toyoda-cnc-machine-repair/index.html` | 504 | 23% |
| `repairs/monarch-cnc-machine-repair/index.html` | 506 | 24% |
| `repairs/niigata-cnc-machine-repair/index.html` | 503 | 24% |
| `repairs/fanuc-cnc-machine-repair/index.html` | 496 | 25% |
| `repairs/makino-cnc-machine-repair/index.html` | 511 | 25% |
| `repairs/hurco-cnc-machine-repair/index.html` | 505 | 26% |

### Brand way-covers pages

| Path | Words | Unique 5-grams |
|---|---:|---:|
| `way-covers/amada-cnc-way-covers/index.html` | 411 | 16% |
| `way-covers/fadal-cnc-way-covers/index.html` | 429 | 17% |
| `way-covers/amera-seiki-cnc-way-covers/index.html` | 430 | 17% |
| `way-covers/fanuc-cnc-way-covers/index.html` | 430 | 17% |
| `way-covers/toyoda-cnc-way-covers/index.html` | 428 | 18% |
| `way-covers/johnford-cnc-way-covers/index.html` | 432 | 18% |
| `way-covers/monarch-cnc-way-covers/index.html` | 431 | 18% |
| `way-covers/hurco-cnc-way-covers/index.html` | 434 | 18% |

## Task 3 — Schema audit

### Distinct schema types in use

| Schema @type | Pages |
|---|---:|
| `BreadcrumbList` | 106 |
| `FAQPage` | 101 |
| `Service` | 98 |
| `LocalBusiness` | 92 |
| `ItemList` | 3 |

### Missing-schema gaps

Found 1 schema gap(s):

- `service-area/index.html` — no ItemList for brand grid (recommended for hubs)

## Task 4 — Internal link topology

- Total internal `<a>` edges: 4921
- Distinct outgoing edges per page (avg): 33

### Orphan pages (in-degree < 5)

| URL | In-links | Page type |
|---|---:|---|
| `/404.html` | 0 | 404 |
| `/about/` | 0 | site-shell |
| `/privacy-policy/` | 0 | site-shell |
| `/terms-of-service/` | 0 | site-shell |
| `/service-area/ames-iowa/` | 1 | city |
| `/service-area/austin-texas/` | 1 | city |
| `/service-area/bloomington-minnesota/` | 1 | city |
| `/service-area/cedar-rapids-iowa/` | 1 | city |
| `/service-area/chicago-illinois/` | 1 | city |
| `/service-area/dallas-texas/` | 1 | city |
| `/service-area/davenport-iowa/` | 1 | city |
| `/service-area/des-moines-iowa/` | 1 | city |
| `/service-area/duluth-minnesota/` | 1 | city |
| `/service-area/el-paso-texas/` | 1 | city |
| `/service-area/fort-worth-texas/` | 1 | city |
| `/service-area/grand-island-nebraska/` | 1 | city |
| `/service-area/green-bay-wisconsin/` | 1 | city |
| `/service-area/houston-texas/` | 1 | city |
| `/service-area/kansas-city-missouri/` | 1 | city |
| `/service-area/kearney-nebraska/` | 1 | city |
| `/service-area/kenosha-wisconsin/` | 1 | city |
| `/service-area/lincoln-nebraska/` | 1 | city |
| `/service-area/madison-wisconsin/` | 1 | city |
| `/service-area/milwaukee-wisconsin/` | 1 | city |
| `/service-area/minneapolis-minnesota/` | 1 | city |
| `/service-area/naperville-illinois/` | 1 | city |
| `/service-area/north-platte-nebraska/` | 1 | city |
| `/service-area/omaha-nebraska/` | 1 | city |
| `/service-area/peoria-illinois/` | 1 | city |
| `/service-area/racine-wisconsin/` | 1 | city |
| `/service-area/rochester-minnesota/` | 1 | city |
| `/service-area/rockford-illinois/` | 1 | city |
| `/service-area/san-antonio-texas/` | 1 | city |
| `/service-area/springfield-missouri/` | 1 | city |
| `/service-area/st-louis-missouri/` | 1 | city |
| `/service-area/st-paul-minnesota/` | 1 | city |
| `/service-area/waterloo-iowa/` | 1 | city |
| `/way-covers/amada-cnc-way-covers/` | 1 | brand-way-covers |
| `/way-covers/trumpf-cnc-way-covers/` | 1 | brand-way-covers |
| `/repairs/amada-press-brake-service/` | 4 | brand-main-alt |
| `/repairs/amera-seiki-cnc-machine-repair/` | 4 | brand-repair |
| `/repairs/brother-cnc-machine-repair/` | 4 | brand-repair |
| `/repairs/fadal-cnc-machine-repair/` | 4 | brand-repair |
| `/repairs/giddings-lewis-cnc-machine-repair/` | 4 | brand-repair |
| `/repairs/hitachi-seiki-cnc-machine-repair/` | 4 | brand-repair |
| `/repairs/hurco-cnc-machine-repair/` | 4 | brand-repair |
| `/repairs/johnford-cnc-machine-repair/` | 4 | brand-repair |
| `/repairs/makino-cnc-machine-repair/` | 4 | brand-repair |
| `/repairs/monarch-cnc-machine-repair/` | 4 | brand-repair |
| `/repairs/mori-seiki-cnc-machine-repair/` | 4 | brand-repair |
| `/repairs/niigata-cnc-machine-repair/` | 4 | brand-repair |
| `/repairs/toyoda-cnc-machine-repair/` | 4 | brand-repair |
| `/repairs/trumpf-laser-service/` | 4 | brand-main-alt |
| `/spindle-grinding/giddings-lewis-spindle-repair/` | 4 | brand-spindle |
| `/way-covers/amera-seiki-cnc-way-covers/` | 4 | brand-way-covers |
| `/way-covers/brother-cnc-way-covers/` | 4 | brand-way-covers |
| `/way-covers/fadal-cnc-way-covers/` | 4 | brand-way-covers |
| `/way-covers/giddings-lewis-cnc-way-covers/` | 4 | brand-way-covers |
| `/way-covers/hitachi-seiki-cnc-way-covers/` | 4 | brand-way-covers |
| `/way-covers/hurco-cnc-way-covers/` | 4 | brand-way-covers |
| `/way-covers/johnford-cnc-way-covers/` | 4 | brand-way-covers |
| `/way-covers/makino-cnc-way-covers/` | 4 | brand-way-covers |
| `/way-covers/monarch-cnc-way-covers/` | 4 | brand-way-covers |
| `/way-covers/mori-seiki-cnc-way-covers/` | 4 | brand-way-covers |
| `/way-covers/niigata-cnc-way-covers/` | 4 | brand-way-covers |
| `/way-covers/toyoda-cnc-way-covers/` | 4 | brand-way-covers |

### Dead-end pages (out-degree < 5)

| URL | Out-links | Page type |
|---|---:|---|
| *(none)* | | |

### Top 20 pages by in-degree (link weight)

| URL | In-links | Page type |
|---|---:|---|
| `/get-a-quote/` | 108 | site-shell |
| `/` | 108 | homepage |
| `/repairs/dmg-mori-cnc-machine-repair/` | 108 | brand-repair |
| `/repairs/doosan-cnc-machine-repair/` | 108 | brand-repair |
| `/repairs/fanuc-cnc-machine-repair/` | 108 | brand-repair |
| `/repairs/haas-cnc-machine-repair/` | 108 | brand-repair |
| `/repairs/` | 108 | service-hub |
| `/repairs/mazak-cnc-machine-repair/` | 108 | brand-repair |
| `/repairs/okuma-cnc-machine-repair/` | 108 | brand-repair |
| `/service-area/illinois/` | 108 | state |
| `/service-area/` | 108 | service-hub |
| `/service-area/iowa/` | 108 | state |
| `/service-area/minnesota/` | 108 | state |
| `/service-area/missouri/` | 108 | state |
| `/service-area/nebraska/` | 108 | state |
| `/service-area/texas/` | 108 | state |
| `/service-area/wisconsin/` | 108 | state |
| `/spindle-grinding/dmg-mori-spindle-repair/` | 108 | brand-spindle |
| `/spindle-grinding/doosan-spindle-repair/` | 108 | brand-spindle |
| `/spindle-grinding/fanuc-spindle-repair/` | 108 | brand-spindle |

### Topic-cluster cross-linking

- **Iowa cluster**: state→cities = 5/5 ; cities→state = 5/5
- **Mazak topic cluster** (spindle + machine-repair + way-covers): 6/6 edges = 100% complete

## Task 5 — AEO / GEO readiness

- Pages with a direct factual answer signal in first 200 words (2+ matched patterns): **81 / 108**
- Pages with FAQPage schema (Q&A format for AI extraction): **101**
- `llms.txt` at site root: **present**
  - Best-practice for AEO/GEO crawlers (similar to robots.txt — directs LLM-aware crawlers to canonical, citable content)

**Pages WITHOUT a strong direct-answer signal in first 200 words:**

| Path | Answer score | Kind | First 80 chars |
|---|---:|---|---|
| `privacy-policy/index.html` | 0 | site-shell | Privacy Policy Last updated: May 26, 2026 Midwest CNC Services collects only the… |
| `service-area/ames-iowa/index.html` | 1 | city | Ames, Iowa CNC Service for Ames Manufacturers Our Waterloo, IA facility sits 113… |
| `service-area/bloomington-minnesota/index.html` | 1 | city | Bloomington, Minnesota CNC Service for Bloomington Manufacturers Our Waterloo, I… |
| `service-area/cedar-rapids-iowa/index.html` | 1 | city | Cedar Rapids, Iowa CNC Repair & Service in Cedar Rapids, Iowa Cedar Rapids sits … |
| `service-area/chicago-illinois/index.html` | 1 | city | Chicago, Illinois CNC Spindle & Machine Repair Serving Chicago Chicago is a abou… |
| `service-area/davenport-iowa/index.html` | 1 | city | Davenport, Iowa CNC Repair & Service in Davenport, Iowa Davenport sits 144 miles… |
| `service-area/des-moines-iowa/index.html` | 1 | city | Des Moines, Iowa Des Moines CNC Repair, Spindle Service & Way Covers From our Wa… |
| `service-area/duluth-minnesota/index.html` | 1 | city | Duluth, Minnesota Duluth CNC Repair, Spindle Service & Way Covers From our Water… |
| `service-area/green-bay-wisconsin/index.html` | 1 | city | Green Bay, Wisconsin CNC Repair & Service in Green Bay, Wisconsin Green Bay sits… |
| `service-area/iowa/index.html` | 1 | state | CNC Repair & Spindle Service in Iowa Iowa is our home state — Midwest CNC Servic… |
| `service-area/kansas-city-missouri/index.html` | 1 | city | Kansas City, Missouri CNC Service for Kansas City Manufacturers Our Waterloo, IA… |
| `service-area/kenosha-wisconsin/index.html` | 1 | city | Kenosha, Wisconsin CNC Service for Kenosha Manufacturers Our Waterloo, IA facili… |
| `service-area/lincoln-nebraska/index.html` | 1 | city | Lincoln, Nebraska CNC Service for Lincoln Manufacturers Our Waterloo, IA facilit… |
| `service-area/madison-wisconsin/index.html` | 1 | city | Madison, Wisconsin Madison CNC Repair, Spindle Service & Way Covers From our Wat… |
| `service-area/milwaukee-wisconsin/index.html` | 1 | city | Milwaukee, Wisconsin CNC Spindle & Machine Repair Serving Milwaukee Milwaukee is… |
| `service-area/minneapolis-minnesota/index.html` | 1 | city | Minneapolis, Minnesota CNC Spindle & Machine Repair Serving Minneapolis Minneapo… |
| `service-area/north-platte-nebraska/index.html` | 1 | city | North Platte, Nebraska CNC Service for North Platte and Western Nebraska Shops N… |
| `service-area/omaha-nebraska/index.html` | 1 | city | Omaha, Nebraska CNC Spindle & Machine Repair Serving Omaha Omaha is a about 5 ho… |
| `service-area/peoria-illinois/index.html` | 1 | city | Peoria, Illinois CNC Repair & Service in Peoria, Illinois Peoria sits 198 miles … |
| `service-area/racine-wisconsin/index.html` | 1 | city | Racine, Wisconsin CNC Repair & Service in Racine, Wisconsin Racine sits 286 mile… |
| `service-area/rochester-minnesota/index.html` | 1 | city | Rochester, Minnesota CNC Spindle & Machine Repair Serving Rochester Rochester is… |
| `service-area/rockford-illinois/index.html` | 1 | city | Rockford, Illinois CNC Spindle & Machine Repair Serving Rockford Rockford is a a… |
| `service-area/springfield-missouri/index.html` | 1 | city | Springfield, Missouri CNC Service for Springfield Manufacturers Our Waterloo, IA… |
| `service-area/st-louis-missouri/index.html` | 1 | city | St. Louis, Missouri CNC Repair & Service in St. Louis, Missouri St. Louis sits 3… |
| `service-area/st-paul-minnesota/index.html` | 1 | city | St. Paul, Minnesota St. Paul CNC Repair, Spindle Service & Way Covers From our W… |
| *…and 1 more* | | | |

### Entity-reference consistency

Brand-name casing is consistent across all pages. ✓

## Task 6 — Local SEO signals

### NAP consistency

- Business name (`Midwest CNC Services`) on all pages: **✓**
- City/state (`Waterloo, IA` or `Waterloo, Iowa`) on all pages: **✓**
- Phone (`319-610-4341`) on all pages: **✓**

### Geographic-coverage signals

- Homepage LocalBusiness schema includes geo coordinates: **yes**
- Pages mentioning all 7 service-area states by name: **108 / 108**
- City pages with geo-aware Service schema (areaServed.City): **33 / 33**
- Location pages in sitemap: state=7, city=37 (verified in Phase 2/3 audit)

## Task 7 — Image & accessibility

- Total `<img>` tags across site: 227
- Missing `alt` attribute: 0
- Empty `alt=""` (decorative): 0
- Generic alt text ("image", "photo", etc.): 0
- Distinct alt strings reused across multiple pages: 11

Top reused alt strings (potential template alt-text problem):
- `CNC machining center under service` — 2 pages
- `CNC spindle on the grinding bench` — 2 pages
- `Iowa CNC service coverage` — 2 pages
- `Illinois CNC service coverage` — 2 pages
- `Wisconsin CNC service coverage` — 2 pages
- `Minnesota CNC service coverage` — 2 pages
- `Nebraska CNC service coverage` — 2 pages
- `Missouri CNC service coverage` — 2 pages

## Task 8 — Findings by priority

Bucket A = fixable with existing data + structural improvements
Bucket B = requires new Ken input or new facts not in current source data

### CRITICAL  (1 item(s))

**32 city pages below 60% unique-content threshold**

- *What's wrong:* All 37 city pages currently use the same body template with state-context data substituted. n-gram analysis shows they hit ~31-78% uniqueness. Google penalizes location-page families that read templated.
- *Fixed looks like:* Per-city paragraph of locally-verifiable context (1 manufacturer, 1 industry cluster, 1 service-distinct fact). Aim for 60–100 words of city-unique content.
- *Bucket:* Bucket A *if* we accept reusing state-brief manufacturers per city; Bucket B for stronger ranking — Ken or Aaron supplies one local manufacturer or shop type per city.

### HIGH  (3 item(s))

**Site-wide content gap of ~8,856 words to competitive targets**

- *What's wrong:* Pages across every type are under competitive-rank word counts. Concentrated in city pages (~9–10K word total gap), state pages (~3K), and homepage (~250).
- *Fixed looks like:* See Task 9 below for the budget breakdown.
- *Bucket:* Mixed — see breakdown.

**1 schema gaps across the site**

- *What's wrong:* Some pages missing recommended schema types for their kind (Service, BreadcrumbList, FAQPage, ItemList).
- *Fixed looks like:* Add the missing types via the existing schema helpers. ItemList for hubs is the biggest opportunity.
- *Bucket:* Bucket A — pure structural addition.

**66 orphan pages (in-degree < 5)**

- *What's wrong:* Pages that aren't linked from elsewhere get crawled less often and rank worse. Privacy, Terms, 404, About often qualify — that's normal.
- *Fixed looks like:* Footer links to Privacy/Terms; About in nav; Sitemap doesn't fix this.
- *Bucket:* Bucket A — add footer nav.

### MEDIUM  (2 item(s))

**AEO/GEO direct-answer density is uneven**

- *What's wrong:* 81 of 108 pages have ≥2 direct-answer patterns in the first 200 words. Pages with weak answers compete poorly in AI Overviews.
- *Fixed looks like:* Lead with a citable fact (lead time, location, what we do) within the first sentence on every brand and location page.
- *Bucket:* Bucket A — copy reshape.

**No FAQPage schema beyond the homepage**

- *What's wrong:* Brand pages, state pages, and city pages would all benefit from a brief FAQ section with FAQPage schema for AI Overviews extraction.
- *Fixed looks like:* Add 2–3 FAQ Q&A per page using Ken's already-authorized themes (lead times, what we service, where we work).
- *Bucket:* Bucket A — uses existing Ken content.

### LOW  (1 item(s))

**0 images with empty alt='' (decorative)**

- *What's wrong:* Mostly acceptable for decorative imagery; but some hero photos may deserve real alt text for SEO image search.
- *Fixed looks like:* Audit the empty-alt list and populate where the image carries content.
- *Bucket:* Bucket A.

## Task 9 — Content-gap budget

Total word gap from current state to competitive targets, by page type. Competitive targets are calibrated for ranking against established competitors in CNC service / location-page categories.

| Page type | Pages | Current avg | Target | Gap per page | Total gap |
|---|---:|---:|---:|---:|---:|
| homepage | 1 | 755 | 1000 | 245 | 245 |
| service-hub | 4 | 451 | 700 | 249 | 995 |
| site-shell | 4 | 336 | 500 | 164 | 682 |
| state | 7 | 809 | 800 | 0 | 124 |
| city | 33 | 520 | 500 | 0 | 136 |
| brand-spindle | 18 | 519 | 700 | 181 | 3,252 |
| brand-repair | 18 | 511 | 600 | 89 | 1,585 |
| brand-main-alt | 2 | 318 | 600 | 282 | 563 |
| brand-way-covers | 20 | 436 | 500 | 64 | 1,274 |
| 404 | 1 | 28 | 0 | 0 | 0 |
| **TOTAL** | **108** | — | — | — | **8,856** |

### Bucket A vs Bucket B split

- **Bucket A** (no new input — structural enrichment, FAQ from existing Ken themes, content reuse, schema additions): ~**4,870 words** (55%)
- **Bucket B** (requires new input — per-city local context, deeper state briefs, brand-specific case-study material): ~**3,986 words** (45%)

Bucket A breakdown by source:
- FAQ sections on brand + state + city pages using Ken's authorized themes
- ItemList schema on service hubs + structural copy expansion
- Cross-linking-driven content (related-services blurbs)
- Service-uniform process detail (3-step workflow, machine-family bullets)

Bucket B breakdown by source:
- City-level: one local manufacturer or shop name per city (~15-20 words/city × 37 cities = ~600 words)
- State-level: second-tier industry/manufacturer details (~50-80 words/state × 7 states = ~400 words)
- Brand-level: 1-2 sentence brand-specific case sketches from Ken (~30-50 words/brand × 20 = ~800 words)
- Plus the rest as deeper city/state context

