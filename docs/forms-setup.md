# Quote Form Setup — Cloudflare Pages Functions + Resend + Turnstile

Replaces the legacy Web3Forms wiring with a Cloudflare-native pipeline.
Form submissions go to `/api/quote` (a Pages Function in this repo),
which verifies the Turnstile token, validates the fields, sends an
email through the Resend API, and redirects to `/get-a-quote/thank-you/`.

This document is the runbook for getting it working in production. It
assumes the `insights-engine` branch (or its successor) is merged to
`main` and Cloudflare Pages is already deploying the site.

---

## What you need to do (one-time, ~45 minutes)

### 1. Verify a sending domain in Resend (~10 min)

Resend will not deliver email from a domain you have not verified.

1. Sign up at [resend.com](https://resend.com). Free tier covers 3,000 emails / month.
2. **Domains → Add Domain →** `midwestcncservices.com`.
3. Resend gives you several DNS records (DKIM, SPF, MX). Add them to
   your DNS provider — likely Cloudflare since the site lives there.
4. Wait a few minutes. Refresh the Resend domain page until everything
   shows green.

Once verified, you can send from any address `@midwestcncservices.com`.
A good convention: `quotes@midwestcncservices.com` for the From and a
real inbox like `aaron@midwestcncservices.com` for the To.

### 2. Get a Resend API key (~2 min)

1. Resend → **API Keys → Create API Key**.
2. Name it something like `midwestcnc-pages-quote`.
3. Permission: **Sending access** is enough.
4. Domain: scope to `midwestcncservices.com` if Resend offers the option.
5. Copy the key (`re_...`). You will paste it once into Cloudflare; you
   cannot see it again afterward.

### 3. Create the Turnstile widget (~5 min)

1. Cloudflare dashboard → **Turnstile → Add site**.
2. Site name: `midwestcncservices.com`.
3. Domains: `midwestcncservices.com` and any subdomains you serve from
   (the Pages preview subdomain too if you want to test against it).
4. Widget mode: **Managed** (the standard default; lets Cloudflare
   pick the right challenge for each visitor).
5. Save. Cloudflare gives you two values:
   - **Site key** — public, goes in the HTML.
   - **Secret key** — server-side, goes in the Pages env var below.

### 4. Update the site key in the build (~1 min)

Open `scripts/generate_site_shell.py`, find:

```python
TURNSTILE_SITE_KEY = "1x00000000000000000000AA"
```

That is Cloudflare's documented **test key** — it always passes in dev.
Replace it with your real site key from step 3, then commit. The next
build will bake the real key into the rendered HTML.

### 5. Add the secrets to Cloudflare Pages (~10 min)

Cloudflare dashboard → **Pages → midwestcnc** (or whatever your project
is named) → **Settings → Environment variables**. Add these as
**Production** secrets (not plaintext variables):

| Name | Value |
| --- | --- |
| `RESEND_API_KEY` | The `re_...` key from step 2. Mark as encrypted. |
| `TURNSTILE_SECRET` | The secret key from step 3. Mark as encrypted. |
| `NOTIFY_EMAIL` | `aaron@midwestcncservices.com` (or comma-separated list of inboxes). Plaintext OK. |
| `FROM_EMAIL` | `Midwest CNC Quote Form <quotes@midwestcncservices.com>` — verified Resend sender. Plaintext OK. |

Hit **Save** at the bottom. You may also want to add the same values
to **Preview** if you want the form to work on preview deploys, but
that is optional.

### 6. Trigger a build (~30 sec)

After saving env vars, Cloudflare Pages does not automatically redeploy.
Trigger one:

- Push any commit to `main` (even an empty commit:
  `git commit --allow-empty -m "Trigger redeploy after secrets" && git push`).
- Or: **Pages → Deployments → Retry deployment** on the latest one.

### 7. Test the form (~3 min)

Open `https://midwestcncservices.com/get-a-quote/` (or your preview URL).
Fill it out with your own contact details. Submit. You should:

1. See the Turnstile widget (sometimes invisible if Cloudflare
   considers the visitor low-risk).
2. Land on `/get-a-quote/thank-you/`.
3. Receive the notification email at the address in `NOTIFY_EMAIL`,
   usually within a few seconds.

If anything goes wrong, the Pages Function logs at
**Pages → midwestcnc → Functions → Logs** show what happened.

---

## How the pipeline actually works

```
User fills form
   ↓
Form POSTs to /api/quote (multipart/form-data)
   ↓
functions/api/quote.js receives:
   1. Reads the form data
   2. Drops bots that filled the honeypot (silent)
   3. Verifies Turnstile token via siteverify API
   4. Validates required fields
   5. Calls Resend API to send email
   ↓
On success: 303 redirect to /get-a-quote/thank-you/
On failure: 303 redirect to /get-a-quote/?error=<code>
```

The form itself works without JavaScript — it is a classic HTML POST.
The only JS is the Turnstile widget (Cloudflare-hosted) and a small
inline script that displays the error banner if the user got bounced
back.

---

## Adjusting which inbox(es) get notified

Edit the `NOTIFY_EMAIL` env var in the Cloudflare Pages dashboard.
Comma-separate for multiple recipients:

```
aaron@midwestcncservices.com,ken@midwestcncservices.com
```

No code change required. Saves and applies on the next request.

---

## Failure modes

The Pages Function returns specific error codes in the redirect URL.
The form's inline JS surfaces them as readable messages.

| Code | What happened | Likely fix |
| --- | --- | --- |
| `captcha-missing` | The Turnstile token was not present | Usually a bot. If a real user reports it, check the site key matches the widget. |
| `captcha-failed` | Token did not verify against `TURNSTILE_SECRET` | Site key and secret are from different widgets, or the user is on a suspicious network. |
| `missing-<field>` | A required field was blank | The HTML `required` attribute should normally prevent this. If it happens, check that the field exists in `quote_body()` markup. |
| `email-failed` | Resend rejected the API call | Check the Function logs. Most common: API key wrong, sender domain not verified, or rate limit hit. |
| `bad-request` | Form data could not be parsed | Rare. Usually means a CDN or proxy mangled the POST. |

All errors leave the user back on `/get-a-quote/` with the form ready
to retry. None of them lose the user's typed input — the browser keeps
the values because we never sent them with the JS-form path.

---

## Removing Web3Forms

The legacy `WEB3FORMS_KEY` constant remains in
`scripts/generate_site_shell.py` for now but is unused. You can remove
it whenever convenient — nothing references it after the form switch.

You can also revoke the Web3Forms access key at
[web3forms.com](https://web3forms.com) once you have verified the new
pipeline works end-to-end.

---

## Files involved

```
functions/api/quote.js              — the Pages Function (form handler)
scripts/generate_site_shell.py      — quote_body(), quote_thanks_body(), TURNSTILE_SITE_KEY
docs/forms-setup.md                 — this file
```

---

## Cost summary

| Item | Free tier | When you pay |
| --- | --- | --- |
| Cloudflare Pages Functions | 100K req/day | Above that: $5 / 10M req |
| Cloudflare Turnstile | Unlimited | Never (free product) |
| Resend | 3,000 emails / month, 100 / day | $20 / mo for 50K above that |

For a shop site, you will be well inside the free tier on all three
unless something goes very wrong with bots.
