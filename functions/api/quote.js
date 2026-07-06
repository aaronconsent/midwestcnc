/**
 * Cloudflare Pages Function — quote form handler
 *
 * Endpoint:  POST /api/quote
 * Triggers:  the form on /get-a-quote/ (classic HTML POST, no JS required)
 *
 * Behavior:
 *   1. Reads multipart/form-data from the submission.
 *   2. Silently drops bot submissions caught by the honeypot field.
 *   3. Verifies the Cloudflare Turnstile token server-side.
 *   4. Validates required fields.
 *   5. Sends a notification email to Aaron via the Resend API.
 *   6. Redirects (303 See Other) to /get-a-quote/thank-you/ on success.
 *      Redirects back to /get-a-quote/?error=<code> on failure.
 *
 * Environment bindings (set in Cloudflare Pages dashboard →
 * Settings → Environment variables. See docs/forms-setup.md for the
 * full walkthrough):
 *
 *   RESEND_API_KEY     — secret, from https://resend.com/api-keys
 *   TURNSTILE_SECRET   — secret, from the Turnstile widget settings
 *   NOTIFY_EMAIL       — comma-separated list of inbox addresses to notify
 *                        (e.g. "aaron@midwestcncservices.com,ken@midwestcncservices.com")
 *   FROM_EMAIL         — verified sender address in Resend
 *                        (e.g. "Quote Form <quotes@midwestcncservices.com>").
 *                        Domain must be verified at https://resend.com/domains
 *                        before this address will deliver.
 */

const SUCCESS_PATH = "/get-a-quote/thank-you/";
const ERROR_PATH = "/get-a-quote/";

const REQUIRED_FIELDS = ["name", "company", "phone", "email", "service", "message"];

export async function onRequestPost(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  // 1. Parse the form
  let form;
  try {
    form = await request.formData();
  } catch (e) {
    return seeOther(url, `${ERROR_PATH}?error=bad-request`);
  }

  // 2. Honeypot — bots fill this; humans never see it. Silently
  //    pretend success so the bot does not retry.
  const honeypot = (form.get("botcheck") || "").toString().trim();
  if (honeypot !== "") {
    return seeOther(url, SUCCESS_PATH);
  }

  // 3. Turnstile verification (skip only if no secret is configured —
  //    useful for local dev, but in production the secret must be set).
  if (env.TURNSTILE_SECRET) {
    const token = (form.get("cf-turnstile-response") || "").toString();
    if (!token) {
      return seeOther(url, `${ERROR_PATH}?error=captcha-missing`);
    }
    const ok = await verifyTurnstile(
      env.TURNSTILE_SECRET,
      token,
      request.headers.get("cf-connecting-ip"),
    );
    if (!ok) {
      return seeOther(url, `${ERROR_PATH}?error=captcha-failed`);
    }
  }

  // 4. Validate required fields
  for (const f of REQUIRED_FIELDS) {
    const v = (form.get(f) || "").toString().trim();
    if (!v) {
      return seeOther(url, `${ERROR_PATH}?error=missing-${f}`);
    }
  }

  // 5. Build the payload
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

  // 6. Send the notification email
  const sent = await sendNotificationEmail(env, payload);
  if (!sent.ok) {
    // Log the Resend error to the runtime console so it shows up in
    // Cloudflare Pages Functions logs. Useful when debugging delivery.
    console.error("Resend send failed:", sent.error);
    return seeOther(url, `${ERROR_PATH}?error=email-failed`);
  }

  // 7. Done — send the user to the thank-you page
  return seeOther(url, SUCCESS_PATH);
}

// Accidental GET → polite 405
export async function onRequestGet() {
  return new Response("This endpoint accepts POST only.", {
    status: 405,
    headers: { "content-type": "text/plain; charset=utf-8" },
  });
}

// ---------- Helpers ----------

function trim(form, key) {
  return (form.get(key) || "").toString().trim();
}

function seeOther(originUrl, path) {
  // Use 303 See Other so a POST → GET transition is unambiguous,
  // which is the right semantics after a form submission.
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
    console.error("Turnstile verify error:", e);
    return false;
  }
}

async function sendNotificationEmail(env, p) {
  if (!env.RESEND_API_KEY) {
    return { ok: false, error: "RESEND_API_KEY not configured" };
  }
  if (!env.FROM_EMAIL) {
    return { ok: false, error: "FROM_EMAIL not configured" };
  }
  const recipients = (env.NOTIFY_EMAIL || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (recipients.length === 0) {
    return { ok: false, error: "NOTIFY_EMAIL not configured" };
  }

  const subject = `Quote request: ${p.machine_brand} ${p.service}`.trim();

  // Plain-text body. Easy to scan in any mail client; reply-to is
  // wired to the submitter so a direct reply goes straight to them.
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

  // Minimal HTML mirror — same content, easier to scan on mobile.
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
    return { ok: false, error: String(e) };
  }
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
