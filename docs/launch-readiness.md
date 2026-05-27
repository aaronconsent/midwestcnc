# Launch Readiness Audit

Audited **281 HTML files** under `public/` plus the `assets/` tree. Run this any time before deploy to catch regressions.

## Summary

- Total HTML files in `public/`: **281**
- Sitemap URLs:                  **278**
  (2 expected exclusions: 404 page + draft way-cover pages)
- Internal links scanned:         **18658**
- Broken internal links:          **0**
- Ban-list findings:              **1** unauthorized, **2** Aaron-authorized exceptions
- Schema issues:                  **165**
- Pages missing breadcrumb:       **0** (homepage and 404 are expected here)
- Images missing `alt`:           **0**
- Images with empty `alt`:        **0** (decorative — generally acceptable)
- Pages without viewport meta:    **0**
- Distinct `<header>` markups:    **1** (want 1 if nav is template-consistent)
- Total asset size:               **114.3 MB** across 146 files

## Verdict

**Blockers:**

- 1 unauthorized claim-audit hits
- 165 schema gaps

## a) Link audit

- Total `<a href>` scanned: 18658
- Resolved to file:        16232
- Resolved via redirect:   0
- External (skipped):      282
- Non-http skipped:        2144
- **Broken:**              **0**

## d) Claim-audit ban-list scan

**Aaron-authorized exceptions** (documented in `docs/claim-audit.md`):
- `same-day` in `public/service-area/iowa/index.html` — authorized
- `warranty` in `public/terms-of-service/index.html` — authorized

**Unauthorized hits — must fix before deploy:**
- `same-day` in `public/service-area/index.html`

## e) Schema validation

- Pages with BreadcrumbList: 279 / 279 (excluding homepage and 404)

**Schema issues:**
- Brand page missing LocalBusiness schema (public/repairs/dmg-mori-cnc-machine-repair/celos/index.html)
- Brand page missing LocalBusiness schema (public/repairs/dmg-mori-cnc-machine-repair/cmx/index.html)
- Brand page missing LocalBusiness schema (public/repairs/dmg-mori-cnc-machine-repair/ctx-clx-turning/index.html)
- Brand page missing LocalBusiness schema (public/repairs/dmg-mori-cnc-machine-repair/dmp-milltap/index.html)
- Brand page missing LocalBusiness schema (public/repairs/dmg-mori-cnc-machine-repair/dmu-dmc/index.html)
- Brand page missing LocalBusiness schema (public/repairs/dmg-mori-cnc-machine-repair/heidenhain-tnc/index.html)
- Brand page missing LocalBusiness schema (public/repairs/dmg-mori-cnc-machine-repair/nhx-horizontals/index.html)
- Brand page missing LocalBusiness schema (public/repairs/dmg-mori-cnc-machine-repair/nlx-turning/index.html)
- Brand page missing LocalBusiness schema (public/repairs/dmg-mori-cnc-machine-repair/ntx/index.html)
- Brand page missing LocalBusiness schema (public/repairs/dmg-mori-cnc-machine-repair/nvx-verticals/index.html)
- Brand page missing LocalBusiness schema (public/repairs/dmg-mori-cnc-machine-repair/siemens-840d/index.html)
- Brand page missing LocalBusiness schema (public/repairs/dmg-mori-cnc-machine-repair/sprint-multisprint/index.html)
- Brand page missing LocalBusiness schema (public/repairs/doosan-cnc-machine-repair/5-axis-verticals/index.html)
- Brand page missing LocalBusiness schema (public/repairs/doosan-cnc-machine-repair/dnm-verticals/index.html)
- Brand page missing LocalBusiness schema (public/repairs/doosan-cnc-machine-repair/horizontals/index.html)
- Brand page missing LocalBusiness schema (public/repairs/doosan-cnc-machine-repair/lynx/index.html)
- Brand page missing LocalBusiness schema (public/repairs/doosan-cnc-machine-repair/puma-mx-smx/index.html)
- Brand page missing LocalBusiness schema (public/repairs/doosan-cnc-machine-repair/puma-vertical-turning/index.html)
- Brand page missing LocalBusiness schema (public/repairs/doosan-cnc-machine-repair/puma/index.html)
- Brand page missing LocalBusiness schema (public/repairs/doosan-cnc-machine-repair/swiss-turning/index.html)
- Brand page missing LocalBusiness schema (public/repairs/fanuc-cnc-machine-repair/power-mate-i/index.html)
- Brand page missing LocalBusiness schema (public/repairs/fanuc-cnc-machine-repair/series-0-legacy/index.html)
- Brand page missing LocalBusiness schema (public/repairs/fanuc-cnc-machine-repair/series-0i/index.html)
- Brand page missing LocalBusiness schema (public/repairs/fanuc-cnc-machine-repair/series-16i-18i-21i/index.html)
- Brand page missing LocalBusiness schema (public/repairs/fanuc-cnc-machine-repair/series-30i-31i-32i/index.html)
- Brand page missing LocalBusiness schema (public/repairs/fanuc-cnc-machine-repair/series-6-15-legacy/index.html)
- Brand page missing LocalBusiness schema (public/repairs/haas-cnc-machine-repair/ec-series/index.html)
- Brand page missing LocalBusiness schema (public/repairs/haas-cnc-machine-repair/haas-classic-control/index.html)
- Brand page missing LocalBusiness schema (public/repairs/haas-cnc-machine-repair/haas-ngc/index.html)
- Brand page missing LocalBusiness schema (public/repairs/haas-cnc-machine-repair/mini-mill-toolroom/index.html)
- Brand page missing LocalBusiness schema (public/repairs/haas-cnc-machine-repair/st-series/index.html)
- Brand page missing LocalBusiness schema (public/repairs/haas-cnc-machine-repair/toolroom-lathes/index.html)
- Brand page missing LocalBusiness schema (public/repairs/haas-cnc-machine-repair/umc-series/index.html)
- Brand page missing LocalBusiness schema (public/repairs/haas-cnc-machine-repair/vf-series/index.html)
- Brand page missing LocalBusiness schema (public/repairs/mazak-cnc-machine-repair/hcn-horizontal/index.html)
- Brand page missing LocalBusiness schema (public/repairs/mazak-cnc-machine-repair/integrex/index.html)
- Brand page missing LocalBusiness schema (public/repairs/mazak-cnc-machine-repair/mazatrol-legacy/index.html)
- Brand page missing LocalBusiness schema (public/repairs/mazak-cnc-machine-repair/mazatrol-matrix/index.html)
- Brand page missing LocalBusiness schema (public/repairs/mazak-cnc-machine-repair/quick-turn/index.html)
- Brand page missing LocalBusiness schema (public/repairs/mazak-cnc-machine-repair/smooth-control/index.html)
- Brand page missing LocalBusiness schema (public/repairs/mazak-cnc-machine-repair/turning-legacy/index.html)
- Brand page missing LocalBusiness schema (public/repairs/mazak-cnc-machine-repair/variaxis/index.html)
- Brand page missing LocalBusiness schema (public/repairs/mazak-cnc-machine-repair/vertical-machining-centers/index.html)
- Brand page missing LocalBusiness schema (public/repairs/okuma-cnc-machine-repair/genos/index.html)
- Brand page missing LocalBusiness schema (public/repairs/okuma-cnc-machine-repair/heavy-lathes/index.html)
- Brand page missing LocalBusiness schema (public/repairs/okuma-cnc-machine-repair/lb-lu-lathes/index.html)
- Brand page missing LocalBusiness schema (public/repairs/okuma-cnc-machine-repair/mb-ma-verticals/index.html)
- Brand page missing LocalBusiness schema (public/repairs/okuma-cnc-machine-repair/multus/index.html)
- Brand page missing LocalBusiness schema (public/repairs/okuma-cnc-machine-repair/osp-legacy/index.html)
- Brand page missing LocalBusiness schema (public/repairs/okuma-cnc-machine-repair/osp-p200/index.html)
- Brand page missing LocalBusiness schema (public/repairs/okuma-cnc-machine-repair/osp-p300/index.html)
- Brand page missing LocalBusiness schema (public/repairs/okuma-cnc-machine-repair/osp-p500/index.html)
- Brand page missing LocalBusiness schema (public/repairs/okuma-cnc-machine-repair/twin-spindle-twin-turret/index.html)
- Brand page missing LocalBusiness schema (public/repairs/okuma-cnc-machine-repair/v-bridge-mills/index.html)
- Brand page missing LocalBusiness schema (public/repairs/okuma-cnc-machine-repair/vtm/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/dmg-mori-spindle-repair/celos/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/dmg-mori-spindle-repair/cmx/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/dmg-mori-spindle-repair/ctx-clx-turning/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/dmg-mori-spindle-repair/dmp-milltap/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/dmg-mori-spindle-repair/dmu-dmc/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/dmg-mori-spindle-repair/heidenhain-tnc/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/dmg-mori-spindle-repair/nhx-horizontals/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/dmg-mori-spindle-repair/nlx-turning/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/dmg-mori-spindle-repair/ntx/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/dmg-mori-spindle-repair/nvx-verticals/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/dmg-mori-spindle-repair/siemens-840d/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/dmg-mori-spindle-repair/sprint-multisprint/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/doosan-spindle-repair/5-axis-verticals/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/doosan-spindle-repair/dnm-verticals/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/doosan-spindle-repair/horizontals/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/doosan-spindle-repair/lynx/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/doosan-spindle-repair/puma-mx-smx/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/doosan-spindle-repair/puma-vertical-turning/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/doosan-spindle-repair/puma/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/doosan-spindle-repair/swiss-turning/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/fanuc-spindle-repair/power-mate-i/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/fanuc-spindle-repair/series-0-legacy/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/fanuc-spindle-repair/series-0i/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/fanuc-spindle-repair/series-16i-18i-21i/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/fanuc-spindle-repair/series-30i-31i-32i/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/fanuc-spindle-repair/series-6-15-legacy/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/haas-spindle-repair/ec-series/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/haas-spindle-repair/haas-classic-control/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/haas-spindle-repair/haas-ngc/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/haas-spindle-repair/mini-mill-toolroom/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/haas-spindle-repair/st-series/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/haas-spindle-repair/toolroom-lathes/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/haas-spindle-repair/umc-series/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/haas-spindle-repair/vf-series/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/mazak-spindle-repair/hcn-horizontal/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/mazak-spindle-repair/integrex/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/mazak-spindle-repair/mazatrol-legacy/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/mazak-spindle-repair/mazatrol-matrix/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/mazak-spindle-repair/quick-turn/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/mazak-spindle-repair/smooth-control/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/mazak-spindle-repair/turning-legacy/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/mazak-spindle-repair/variaxis/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/mazak-spindle-repair/vertical-machining-centers/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/okuma-spindle-repair/genos/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/okuma-spindle-repair/heavy-lathes/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/okuma-spindle-repair/lb-lu-lathes/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/okuma-spindle-repair/mb-ma-verticals/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/okuma-spindle-repair/multus/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/okuma-spindle-repair/osp-legacy/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/okuma-spindle-repair/osp-p200/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/okuma-spindle-repair/osp-p300/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/okuma-spindle-repair/osp-p500/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/okuma-spindle-repair/twin-spindle-twin-turret/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/okuma-spindle-repair/v-bridge-mills/index.html)
- Brand page missing LocalBusiness schema (public/spindle-grinding/okuma-spindle-repair/vtm/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/dmg-mori-cnc-way-covers/celos/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/dmg-mori-cnc-way-covers/cmx/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/dmg-mori-cnc-way-covers/ctx-clx-turning/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/dmg-mori-cnc-way-covers/dmp-milltap/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/dmg-mori-cnc-way-covers/dmu-dmc/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/dmg-mori-cnc-way-covers/heidenhain-tnc/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/dmg-mori-cnc-way-covers/nhx-horizontals/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/dmg-mori-cnc-way-covers/nlx-turning/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/dmg-mori-cnc-way-covers/ntx/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/dmg-mori-cnc-way-covers/nvx-verticals/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/dmg-mori-cnc-way-covers/siemens-840d/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/dmg-mori-cnc-way-covers/sprint-multisprint/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/doosan-cnc-way-covers/5-axis-verticals/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/doosan-cnc-way-covers/dnm-verticals/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/doosan-cnc-way-covers/horizontals/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/doosan-cnc-way-covers/lynx/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/doosan-cnc-way-covers/puma-mx-smx/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/doosan-cnc-way-covers/puma-vertical-turning/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/doosan-cnc-way-covers/puma/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/doosan-cnc-way-covers/swiss-turning/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/fanuc-cnc-way-covers/power-mate-i/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/fanuc-cnc-way-covers/series-0-legacy/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/fanuc-cnc-way-covers/series-0i/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/fanuc-cnc-way-covers/series-16i-18i-21i/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/fanuc-cnc-way-covers/series-30i-31i-32i/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/fanuc-cnc-way-covers/series-6-15-legacy/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/haas-cnc-way-covers/ec-series/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/haas-cnc-way-covers/haas-classic-control/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/haas-cnc-way-covers/haas-ngc/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/haas-cnc-way-covers/mini-mill-toolroom/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/haas-cnc-way-covers/st-series/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/haas-cnc-way-covers/toolroom-lathes/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/haas-cnc-way-covers/umc-series/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/haas-cnc-way-covers/vf-series/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/mazak-cnc-way-covers/hcn-horizontal/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/mazak-cnc-way-covers/integrex/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/mazak-cnc-way-covers/mazatrol-legacy/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/mazak-cnc-way-covers/mazatrol-matrix/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/mazak-cnc-way-covers/quick-turn/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/mazak-cnc-way-covers/smooth-control/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/mazak-cnc-way-covers/turning-legacy/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/mazak-cnc-way-covers/variaxis/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/mazak-cnc-way-covers/vertical-machining-centers/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/okuma-cnc-way-covers/genos/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/okuma-cnc-way-covers/heavy-lathes/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/okuma-cnc-way-covers/lb-lu-lathes/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/okuma-cnc-way-covers/mb-ma-verticals/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/okuma-cnc-way-covers/multus/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/okuma-cnc-way-covers/osp-legacy/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/okuma-cnc-way-covers/osp-p200/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/okuma-cnc-way-covers/osp-p300/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/okuma-cnc-way-covers/osp-p500/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/okuma-cnc-way-covers/twin-spindle-twin-turret/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/okuma-cnc-way-covers/v-bridge-mills/index.html)
- Brand page missing LocalBusiness schema (public/way-covers/okuma-cnc-way-covers/vtm/index.html)

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

- Total `<loc>` entries: 278
- HTML files in `public/`: 281
- Difference: 3 (404 page + drafts — expected)
