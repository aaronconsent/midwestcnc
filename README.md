# Midwest CNC Services — Website Rebuild

Static rebuild of [midwestcncservices.com](https://midwestcncservices.com), migrating off Durable.co to a self-hosted static site on Cloudflare Pages.

## Migration overview

The live site is built on Durable.co's hosted website builder. We're rebuilding it as a hand-written static site so we own the source, can edit it directly, and can host it cheaply on Cloudflare Pages with custom redirects, headers, and analytics.

Scope of the rebuild:

- ~138 client-owned pages: home, about, get-a-quote, blog (4 posts), and three service verticals (repairs, way covers, spindles repair, spindle grinding) each crossed with ~20 OEMs, plus 47 state/city service-area pages across IA, IL, MN, WI, NE, MO, and TX.
- 146 images already scraped from the live site into [assets/images/](assets/images/).
- Durable's own platform pages (sign-up, pricing, AI tools, etc.) that the crawler picked up are out of scope.

## Tech stack

- **HTML / CSS / JS** — vanilla, no framework, no build step.
- **Templating** — small set of HTML partials under `templates/` composed at author time (or by a simple Node script if pages get repetitive). No React/Vue/Astro/etc.
- **Assets** — images served directly from `assets/images/`.
- **No package.json** unless we add a lightweight build helper later.

## Deployment

- **Cloudflare Pages**, deployed from the `main` branch of this repo.
- Site root is the repo root — `index.html` is the entry point.
- `public/` holds any files that should be copied verbatim to the deployed site root (favicons, manifest, etc.).
- Custom redirects and headers go in `_redirects` and `_headers` at the project root (to be added).

## Current status

- [x] Images scraped from live site (146 files, 0 failures)
- [x] Crawl manifest of all 155 URLs captured
- [x] Project skeleton scaffolded
- [ ] Page text/copy scraped from live site
- [ ] Page metadata (titles, descriptions, OG tags) captured
- [ ] Design reference (screenshots, fonts, color palette) gathered
- [ ] Alt text written for the 63 images currently missing it
- [ ] HTML templates and global CSS authored
- [ ] Pages built
- [ ] `robots.txt` and `sitemap.xml` populated
- [ ] Cloudflare Pages project connected and deployed

## Repo layout

```
.
├── assets/images/    scraped imagery, organized by category
├── src/data/         crawl manifest + image map (build inputs, not served)
├── templates/        HTML partials for layout/header/footer/etc.
├── public/           static files copied to site root at deploy
├── index.html        site entry (placeholder)
├── robots.txt        placeholder
└── sitemap.xml       placeholder
```
