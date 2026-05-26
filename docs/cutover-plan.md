# Midwest CNC — Cutover Plan

The launch sequence to flip midwestcncservices.com from Durable to the
rebuilt static site on Cloudflare Pages.

Aaron coordinates the actual flip. This doc is the runbook — work top
to bottom, check the box on each step before moving to the next.

---

## T−24h — Pre-launch prep

- [ ] **Commit + push the working tree.** Confirm `git status` is clean
      under `~/midwestcnc/` and the `main` branch has every script,
      template, and generated file. Push to the GitHub repo.
- [ ] **Lower current Durable DNS TTL.** In the DNS provider managing
      midwestcncservices.com (probably whoever owns the registrar — Aaron
      knows), drop the TTL on the A record currently pointing at Durable's
      IPs to **300 seconds**. This shortens the propagation window once
      we flip later.
- [ ] **Verify `public/_redirects` is in place** and that the rule count
      is sane:
      ```
      $ wc -l public/_redirects
      ```
      Expect around 35 rules (brand URL relocations, /spindles-repair/
      duplicates, Illinois URL typo fixes, deferred-content redirects).
- [ ] **Run the launch audit one more time** and confirm "READY TO DEPLOY":
      ```
      $ python3 scripts/launch_audit.py
      ```
      Open `docs/launch-readiness.md` and skim. No blockers should be
      listed.
- [ ] **Final visual click-through on local server.** Start a simple
      local server from `public/` and click through:
      - Homepage, scroll the full thing
      - One brand page in each of the three service categories
      - Two state pages (Iowa + Texas — the extremes)
      - The quote form (submit a test if you want to verify Web3Forms
        config; otherwise just confirm the form renders)
      - About, Privacy, Terms
      - Tap-test on a phone-sized viewport (Chrome DevTools is fine)
        — confirm the sticky mobile CTA bar appears and works

```
$ cd ~/midwestcnc/public && python3 -m http.server 8000
# Then open http://localhost:8000/ in the browser
```

---

## T−2h — Stage on Cloudflare Pages preview

- [ ] **Create the Cloudflare Pages project.** In the Cloudflare dashboard
      → Workers & Pages → Create application → Pages → Connect to Git.
      Pick the GitHub repo for midwestcncservices.
- [ ] **Build settings:**
      - Framework preset: **None**
      - Build command: *(leave blank)*
      - Build output directory: **`public`**
      - Root directory: *(leave at repository root)*
- [ ] **Deploy to the preview `*.pages.dev` URL.** Cloudflare will build
      and give you something like `midwestcnc.pages.dev`. Wait for the
      first deploy to finish (~30 seconds for a static site this size).
- [ ] **Click through on the preview URL** in this order:
      - Homepage
      - 3 brand pages (suggested: `/spindle-grinding/mazak-spindle-repair/`,
        `/repairs/haas-cnc-machine-repair/`, `/way-covers/dmg-mori-cnc-way-covers/`)
      - 2 state pages (Iowa + Texas)
      - The quote form: load `/get-a-quote/` and confirm the form renders
        and all dropdown options are present
- [ ] **Run Lighthouse on three pages** via Chrome DevTools (or PageSpeed
      Insights):
      - Homepage
      - `/get-a-quote/`
      - One brand page (Mazak is a good pick)

      Targets: Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95,
      SEO ≥ 95. If anything trips below, decide whether to ship and fix
      or hold.
- [ ] **Submit a real Web3Forms test through the preview URL.** Fill the
      quote form with real-looking data, submit, and confirm:
      - You land on `/get-a-quote/?success=1` with the success state
        visible
      - The submission arrives at the configured Web3Forms inbox
      - The subject line uses the `Quote request: {brand} {service}`
        template substitution

---

## T−0 — DNS flip

- [ ] **In Cloudflare Pages → Custom domains** for the project: add
      `midwestcncservices.com` and `www.midwestcncservices.com`. Cloudflare
      will give you the CNAME target (looks like `midwestcnc.pages.dev`).
- [ ] **In Cloudflare DNS** (or whichever DNS provider holds the zone):
      replace the existing A record pointing at Durable with a CNAME
      (or A/AAAA if Cloudflare DNS is proxied) pointing at the Pages
      target. **Keep TTL at 300s** for the next 24 hours so any mistake
      is fast to revert.
- [ ] **Watch curl output** on the production hostname for the first 10
      minutes:
      ```
      $ while true; do curl -sIo /dev/null -w '%{http_code} %{redirect_url}\n' https://midwestcncservices.com/; sleep 10; done
      ```
      Expect `200` once Cloudflare picks up the new origin. While DNS
      propagates you may see mixed `200` (new) and Durable responses —
      that's normal until the cached A record TTL expires on the
      resolver.
- [ ] **Smoke-test 10 random URLs** via curl (substitute paths):
      ```
      $ for p in / /repairs/mazak-cnc-machine-repair/ /spindle-grinding/haas-spindle-repair/ \
                 /way-covers/dmg-mori-cnc-way-covers/ /service-area/iowa/ \
                 /service-area/des-moines-iowa/ /service-area/texas/ \
                 /get-a-quote/ /about/ /privacy-policy/; do
          printf "%-60s %s\n" "$p" "$(curl -sIo /dev/null -w '%{http_code}' https://midwestcncservices.com$p)"
        done
      ```
      All should return `200`.
- [ ] **Spot-check a redirect.** Hit one of the old `/spindles-repair/`
      URLs that should 301 to the new `/spindle-grinding/` canonical:
      ```
      $ curl -sIo /dev/null -w '%{http_code} %{redirect_url}\n' \
          https://midwestcncservices.com/spindles-repair/mazak-spindle-repair/
      ```
      Expect `301 https://midwestcncservices.com/spindle-grinding/mazak-spindle-repair/`.

---

## T+1h — Post-launch wiring

- [ ] **Resubmit the sitemap to Google Search Console** at
      `https://midwestcncservices.com/sitemap.xml`. (If GSC isn't already
      set up for this domain, do that first — verify ownership via the
      DNS TXT record method, since DNS is in Cloudflare now.)
- [ ] **Request reindex** for the priority pages — Google's "Request
      Indexing" feature on:
      - `/` (homepage)
      - `/repairs/mazak-cnc-machine-repair/`
      - `/spindle-grinding/mazak-spindle-repair/`
      - `/way-covers/mazak-cnc-way-covers/`
- [ ] **Notify Ken** with the live URL and a short note that the new
      site is up and the existing phone + form path still works. Mention
      the brand pages by name so he can poke around his sections.
- [ ] **Submit one more production quote form** end-to-end to verify
      the live flow matches the preview test from T−2h. Confirm the
      email lands in Aaron's inbox.

---

## T+14d — Stabilize + retire Durable

- [ ] **Cancel the Durable subscription.** Wait two weeks first so any
      stale DNS resolvers have aged out and so any short-window backlinks
      from search engines have been re-crawled.
- [ ] **Review the Google Search Console Coverage report.** Look for:
      - 404s on URLs you didn't expect — add to `_redirects` if any
        legitimate inbound paths surface
      - "Crawled, currently not indexed" pages — check the page is
        actually substantive
      - Submitted-but-not-indexed counts vs total — should be close
- [ ] **Consider the Cloudflare Worker for quote-routing migration.**
      Web3Forms is the current path. If we want to move to Cloudflare
      Email Workers, MailChannels, or another route, that work goes
      here — out of scope for the cutover itself.

---

## Rollback (in case anything goes wrong)

If you need to revert during the first 24 hours after T−0:

1. In Cloudflare DNS, swap the A/CNAME record back to Durable's IP
   addresses (Aaron should keep these noted before the cutover —
   `dig +short midwestcncservices.com` *before* T−0).
2. With TTL at 300s, traffic will return to Durable within ~5 minutes.
3. Don't cancel the Cloudflare Pages project — you may want to ship
   again after fixing.

---

## Notes

- **DNS TTL.** Keep at 300s until T+24h, then bump back to 3600+ once
  things look healthy.
- **Email.** No email infrastructure is changing in this cutover — the
  contact path is the same Web3Forms → Aaron inbox.
- **Analytics.** Currently zero analytics installed. If GA4 or similar
  goes in later, that's a separate change and requires a privacy policy
  update.
- **/blog, /guides, /customer-stories** — Phase 5 added wildcard 301s to
  the homepage for these deferred sections. When/if we build real blog
  posts, the specific URLs become available again automatically (real
  files beat wildcards in `_redirects`).
