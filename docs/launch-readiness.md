# Launch Readiness Audit

Audited **297 HTML files** under `public/` plus the `assets/` tree. Run this any time before deploy to catch regressions.

## Summary

- Total HTML files in `public/`: **297**
- Sitemap URLs:                  **293**
  (3 expected exclusions: 404 page + draft way-cover pages)
- Internal links scanned:         **19932**
- Broken internal links:          **0**
- Ban-list findings:              **0** unauthorized, **3** Aaron-authorized exceptions
- Schema issues:                  **0**
- Pages missing breadcrumb:       **0** (homepage and 404 are expected here)
- Images missing `alt`:           **0**
- Images with empty `alt`:        **0** (decorative — generally acceptable)
- Pages without viewport meta:    **0**
- Distinct `<header>` markups:    **1** (want 1 if nav is template-consistent)
- Total asset size:               **114.3 MB** across 146 files

## Verdict

**READY TO DEPLOY.** No blockers found.

## a) Link audit

- Total `<a href>` scanned: 19932
- Resolved to file:        17152
- Resolved via redirect:   0
- External (skipped):      298
- Non-http skipped:        2482
- **Broken:**              **0**

## d) Claim-audit ban-list scan

**Aaron-authorized exceptions** (documented in `docs/claim-audit.md`):
- `same-day` in `public/service-area/index.html` — authorized
- `same-day` in `public/service-area/iowa/index.html` — authorized
- `warranty` in `public/terms-of-service/index.html` — authorized

## e) Schema validation

- Pages with BreadcrumbList: 295 / 295 (excluding homepage and 404)
- No structural schema issues found.

## f) Image alt-text audit

Every `<img>` has a populated `alt` attribute. 🎉

## g) Viewport meta-tag

Every page has `<meta name="viewport" content="width=device-width, initial-scale=1">`. 🎉

## h) Cross-page nav consistency

All pages share an identical `<header>` markup. 🎉

## i) Asset directory size

- Total: **114.3 MB** across 146 files

Breakdown by subdirectory:

| Subdirectory | Bytes | Pretty |
|---|---:|---:|
| `images/cities` | 47,106,262 | 44.9 MB |
| `images/services` | 27,542,983 | 26.3 MB |
| `images/blocks` | 24,614,343 | 23.5 MB |
| `images/general` | 10,740,603 | 10.2 MB |
| `images/states` | 9,868,033 | 9.4 MB |
| `images/logos` | 21,716 | 21.2 KB |

## b/c) Sitemap composition

- Total `<loc>` entries: 293
- HTML files in `public/`: 297
- Difference: 4 (404 page + drafts — expected)
