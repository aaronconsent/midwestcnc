// Cloudflare Worker entry for midwestcncservices.com (Workers + Static Assets).
//
// Static files are served directly by the assets binding; this Worker only
// runs for requests that do not match a static asset — i.e. /api/quote.
//
// Deploy pattern mirrors bandrproduction: worker.js + wrangler.jsonc +
// .assetsignore at the site root. Cloudflare Git integration builds on push.
//
// Required Cloudflare env vars (Workers > Settings > Variables and Secrets):
//   RESEND_API_KEY    — secret, from https://resend.com/api-keys
//   FROM_EMAIL        — verified Resend sender (e.g. "Midwest CNC
//                       <quotes@midwestcncservices.com>"); the domain must
//                       be verified in Resend before delivery works. For a
//                       first test before the domain is verified, use
//                       "Midwest CNC <onboarding@resend.dev>" — Resend's
//                       shared sender only delivers to the Resend account
//                       owner's own address, so set NOTIFY_EMAIL to that
//                       same address while testing.
//   NOTIFY_EMAIL      — comma-separated list of inboxes to notify.
//
// Optional:
//   TURNSTILE_SECRET  — server-side secret for the Turnstile widget on the
//                       form (widget site key 0x4AAAAAADXY93Hw7DfP3PQJ is
//                       already public in the HTML). If unset, Turnstile
//                       verification is skipped — useful for a first-pass
//                       Resend-only test.

const SUCCESS_PATH = "/get-a-quote/thank-you/";
const ERROR_PATH = "/get-a-quote/";
const REQUIRED_FIELDS = ["name", "company", "phone", "email", "service", "message"];
const PHONE = "319-610-4341";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/quote") {
      if (request.method === "POST") return handleQuote(request, env);
      if (request.method === "GET") {
        return new Response("This endpoint accepts POST only.", {
          status: 405,
          headers: { "content-type": "text/plain; charset=utf-8" },
        });
      }
      return new Response("Method not allowed", { status: 405 });
    }
    return env.ASSETS.fetch(request);
  },
};

async function handleQuote(request, env) {
  const url = new URL(request.url);

  let form;
  try {
    form = await request.formData();
  } catch (e) {
    return seeOther(url, `${ERROR_PATH}?error=bad-request`);
  }

  // Honeypot — bots fill this; humans never see it. Silently pretend
  // success so the bot doesn't retry.
  const honeypot = (form.get("botcheck") || "").toString().trim();
  if (honeypot !== "") return seeOther(url, SUCCESS_PATH);

  // Turnstile verification (skipped when TURNSTILE_SECRET is not set,
  // so the form works for a Resend-only first test).
  if (env.TURNSTILE_SECRET) {
    const token = (form.get("cf-turnstile-response") || "").toString();
    if (!token) return seeOther(url, `${ERROR_PATH}?error=captcha-missing`);
    const ok = await verifyTurnstile(
      env.TURNSTILE_SECRET,
      token,
      request.headers.get("cf-connecting-ip"),
    );
    if (!ok) return seeOther(url, `${ERROR_PATH}?error=captcha-failed`);
  }

  for (const f of REQUIRED_FIELDS) {
    const v = (form.get(f) || "").toString().trim();
    if (!v) return seeOther(url, `${ERROR_PATH}?error=missing-${f}`);
  }

  const payload = {
    name: trim(form, "name"),
    company: trim(form, "company"),
    phone: trim(form, "phone"),
    email: trim(form, "email"),
    machine_brand: trim(form, "machine_brand") || "—",
    machine_model: trim(form, "machine_model") || "—",
    service: trim(form, "service"),
    message: trim(form, "message"),
    timestamp: new Date().toISOString(),
    ip: request.headers.get("cf-connecting-ip") || "unknown",
    ua: request.headers.get("user-agent") || "unknown",
  };

  const sent = await sendNotificationEmail(env, payload);
  if (!sent.ok) {
    console.log("Resend send failed:", sent.error);
    return seeOther(url, `${ERROR_PATH}?error=email-failed`);
  }

  return seeOther(url, SUCCESS_PATH);
}

function trim(form, key) {
  return (form.get(key) || "").toString().trim();
}

function seeOther(originUrl, path) {
  return new Response(null, {
    status: 303,
    headers: { Location: new URL(path, originUrl).toString() },
  });
}

async function verifyTurnstile(secret, token, ip) {
  const body = new URLSearchParams();
  body.set("secret", secret);
  body.set("response", token);
  if (ip) body.set("remoteip", ip);
  try {
    const resp = await fetch(
      "https://challenges.cloudflare.com/turnstile/v0/siteverify",
      { method: "POST", body },
    );
    const data = await resp.json();
    return data && data.success === true;
  } catch (e) {
    console.log("Turnstile verify error:", e && e.message);
    return false;
  }
}

async function sendNotificationEmail(env, p) {
  if (!env.RESEND_API_KEY) return { ok: false, error: "RESEND_API_KEY not configured" };
  if (!env.FROM_EMAIL) return { ok: false, error: "FROM_EMAIL not configured" };

  const recipients = (env.NOTIFY_EMAIL || "")
    .split(",").map((s) => s.trim()).filter(Boolean);
  if (recipients.length === 0) return { ok: false, error: "NOTIFY_EMAIL not configured" };

  const subject = `Quote request: ${p.machine_brand} ${p.service}`.trim();

  const text = [
    `New quote request from the Midwest CNC Services website.`,
    ``,
    `Name:           ${p.name}`,
    `Company:        ${p.company}`,
    `Phone:          ${p.phone}`,
    `Email:          ${p.email}`,
    `Machine brand:  ${p.machine_brand}`,
    `Machine model:  ${p.machine_model}`,
    `Service needed: ${p.service}`,
    ``,
    `--- Message ---`,
    p.message,
    `---`,
    ``,
    `Submitted: ${p.timestamp}`,
    `IP:        ${p.ip}`,
    `Browser:   ${p.ua}`,
  ].join("\n");

  const html = [
    `<p><strong>New quote request from the Midwest CNC Services website.</strong></p>`,
    `<table style="border-collapse:collapse;font-family:system-ui,sans-serif;">`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Name:</td><td>${esc(p.name)}</td></tr>`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Company:</td><td>${esc(p.company)}</td></tr>`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Phone:</td><td><a href="tel:${esc(p.phone)}">${esc(p.phone)}</a></td></tr>`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Email:</td><td><a href="mailto:${esc(p.email)}">${esc(p.email)}</a></td></tr>`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Machine brand:</td><td>${esc(p.machine_brand)}</td></tr>`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Machine model:</td><td>${esc(p.machine_model)}</td></tr>`,
    `<tr><td style="padding:4px 12px 4px 0;color:#666;">Service needed:</td><td>${esc(p.service)}</td></tr>`,
    `</table>`,
    `<h3 style="margin:24px 0 4px 0;font-family:system-ui,sans-serif;">Message</h3>`,
    `<p style="font-family:system-ui,sans-serif;white-space:pre-wrap;">${esc(p.message)}</p>`,
    `<hr style="border:none;border-top:1px solid #eee;margin:24px 0;">`,
    `<p style="font-family:system-ui,sans-serif;color:#888;font-size:12px;">`,
    `Submitted ${esc(p.timestamp)} from ${esc(p.ip)}<br>`,
    `User agent: ${esc(p.ua)}`,
    `</p>`,
  ].join("");

  try {
    const resp = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: env.FROM_EMAIL,
        to: recipients,
        reply_to: p.email,
        subject,
        text,
        html,
      }),
    });
    if (!resp.ok) {
      const body = await resp.text();
      return { ok: false, error: `Resend HTTP ${resp.status}: ${body}` };
    }
    return { ok: true };
  } catch (e) {
    return { ok: false, error: String(e && e.message || e) };
  }
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
