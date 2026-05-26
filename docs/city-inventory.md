# City Page Inventory — Durable Scrape Audit

Scanned `src/data/pages.json` for `/service-area/{city-state}/` URLs.

## Summary

- **Total city pages:** 37
- **Stubs** (no h1 or no h2s or <80 body words): 0
- **Flagged for review** (thin content — Aaron decides whether to rebuild or 301 to the state hub): 0
- **URL-typo fixes needed** (`/service-area/X-ilinois/` → `/service-area/X-illinois/`): 3

## Action key

- **rebuild** — page has enough substance to justify a rebuilt city page
- **review** — thin Durable content; Aaron decides between rebuild or 301 to the state hub
- **typo-fix** — URL had `ilinois` instead of `illinois`; corrected URL emitted plus 301 from the original

## Iowa — 6 city pages

| City | New URL | Body words | H1 present | H2 count | Action |
|---|---|---:|:-:|:-:|:-:|
| Des Moines | `/service-area/des-moines-iowa` | 437 | ✓ | 1 | rebuild |
| Waterloo | `/service-area/waterloo-iowa` | 432 | ✓ | 1 | rebuild |
| Iowa City | `/service-area/iowa-city-iowa` | 429 | ✓ | 1 | rebuild |
| Cedar Rapids | `/service-area/cedar-rapids-iowa` | 417 | ✓ | 1 | rebuild |
| Ames | `/service-area/ames-iowa` | 406 | ✓ | 1 | rebuild |
| Davenport | `/service-area/davenport-iowa` | 380 | ✓ | 1 | rebuild |

## Illinois — 5 city pages

| City | New URL | Body words | H1 present | H2 count | Action |
|---|---|---:|:-:|:-:|:-:|
| Chicago | `/service-area/chicago-illinois` | 298 | ✓ | 1 | rebuild |
| Springfield | `/service-area/springfield-illinois/` | 292 | ✓ | 1 | rebuild, typo-fix |
| Naperville | `/service-area/naperville-illinois` | 283 | ✓ | 1 | rebuild |
| Peoria | `/service-area/peoria-illinois/` | 282 | ✓ | 1 | rebuild, typo-fix |
| Rockford | `/service-area/rockford-illinois/` | 279 | ✓ | 1 | rebuild, typo-fix |

## Wisconsin — 5 city pages

| City | New URL | Body words | H1 present | H2 count | Action |
|---|---|---:|:-:|:-:|:-:|
| Kenosha | `/service-area/kenosha-wisconsin` | 296 | ✓ | 1 | rebuild |
| Milwaukee | `/service-area/milwaukee-wisconsin` | 295 | ✓ | 1 | rebuild |
| Green Bay | `/service-area/green-bay-wisconsin` | 293 | ✓ | 1 | rebuild |
| Madison | `/service-area/madison-wisconsin` | 292 | ✓ | 1 | rebuild |
| Racine | `/service-area/racine-wisconsin` | 290 | ✓ | 1 | rebuild |

## Minnesota — 5 city pages

| City | New URL | Body words | H1 present | H2 count | Action |
|---|---|---:|:-:|:-:|:-:|
| Rochester | `/service-area/rochester-minnesota` | 299 | ✓ | 1 | rebuild |
| Bloomington | `/service-area/bloomington-minnesota` | 298 | ✓ | 1 | rebuild |
| St. Paul | `/service-area/st-paul-minnesota` | 298 | ✓ | 1 | rebuild |
| Minneapolis | `/service-area/minneapolis-minnesota` | 295 | ✓ | 1 | rebuild |
| Duluth | `/service-area/duluth-minnesota` | 294 | ✓ | 1 | rebuild |

## Nebraska — 6 city pages

| City | New URL | Body words | H1 present | H2 count | Action |
|---|---|---:|:-:|:-:|:-:|
| North Platte | `/service-area/north-platte-nebraska` | 302 | ✓ | 1 | rebuild |
| Grand Island | `/service-area/grand-island-nebraska` | 299 | ✓ | 1 | rebuild |
| Lincoln | `/service-area/lincoln-nebraska` | 298 | ✓ | 1 | rebuild |
| Kearney | `/service-area/kearney-nebraska` | 297 | ✓ | 1 | rebuild |
| Omaha | `/service-area/omaha-nebraska` | 295 | ✓ | 1 | rebuild |
| Bellevue | `/service-area/bellevue-nebraska` | 293 | ✓ | 1 | rebuild |

## Missouri — 4 city pages

| City | New URL | Body words | H1 present | H2 count | Action |
|---|---|---:|:-:|:-:|:-:|
| Kansas City | `/service-area/kansas-city-missouri` | 305 | ✓ | 1 | rebuild |
| Columbia | `/service-area/columbia-missouri` | 291 | ✓ | 1 | rebuild |
| St. Louis | `/service-area/st-louis-missouri` | 291 | ✓ | 1 | rebuild |
| Springfield | `/service-area/springfield-missouri` | 290 | ✓ | 1 | rebuild |

## Texas — 6 city pages

| City | New URL | Body words | H1 present | H2 count | Action |
|---|---|---:|:-:|:-:|:-:|
| San Antonio | `/service-area/san-antonio-texas` | 302 | ✓ | 1 | rebuild |
| Fort Worth | `/service-area/fort-worth-texas` | 301 | ✓ | 1 | rebuild |
| El Paso | `/service-area/el-paso-texas` | 296 | ✓ | 1 | rebuild |
| Houston | `/service-area/houston-texas` | 296 | ✓ | 1 | rebuild |
| Dallas | `/service-area/dallas-texas` | 295 | ✓ | 1 | rebuild |
| Austin | `/service-area/austin-texas` | 294 | ✓ | 1 | rebuild |

## URL typo fixes — required 301 redirects

These will be added to `public/_redirects` when city pages generate:

```
/service-area/rockford-ilinois/  →  /service-area/rockford-illinois/  301
/service-area/peoria-ilinois/  →  /service-area/peoria-illinois/  301
/service-area/springfield-ilinois/  →  /service-area/springfield-illinois/  301
```
