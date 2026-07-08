// Cloudflare Worker entry for midwestcncservices.com (Workers + Static Assets).
//
// Static files are served directly by the assets binding; this Worker only
// runs for requests that do not match a static asset — i.e. /api/quote.
//
// Deploy pattern mirrors bandrproduction: worker.js + wrangler.jsonc +
// .assetsignore at the site root. Cloudflare Git integration builds on push.
//
// Email routing:
//   To:       ken@midwestcncservices.com (production default, override
//             with NOTIFY_EMAIL env var — comma-separated for multiple).
//   From:     verified sender you own — CANNOT be the customer's email
//             (SPF/DKIM/DMARC would reject it as spoofing). Default is
//             quotes@midwestcncservices.com — override with FROM_EMAIL.
//   Reply-To: the customer's email, so a plain Reply in Ken's client
//             goes straight back to them. Not configurable — always
//             the submitter's email.
//
// Required Cloudflare env vars (Workers > Settings > Variables and Secrets):
//   RESEND_API_KEY    — secret, from https://resend.com/api-keys
//
// Optional (defaults live in the code below):
//   NOTIFY_EMAIL      — comma-separated list of inboxes to notify.
//                       Default: ken@midwestcncservices.com
//   FROM_EMAIL        — verified Resend sender.
//                       Default: "Midwest CNC Quote Form <quotes@midwestcncservices.com>"
//                       (requires midwestcncservices.com verified in Resend).
//                       For a first test before the domain is verified,
//                       override to "Midwest CNC <onboarding@resend.dev>" —
//                       Resend's shared sender only delivers to the Resend
//                       account owner's own address, so also set
//                       NOTIFY_EMAIL to that same address while testing.
//   TURNSTILE_SECRET  — server-side secret for the Turnstile widget on the
//                       form (widget site key 0x4AAAAAADXY93Hw7DfP3PQJ is
//                       already public in the HTML). If unset, Turnstile
//                       verification is skipped — useful for a first-pass
//                       Resend-only test.

const SUCCESS_PATH = "/get-a-quote/thank-you/";
const ERROR_PATH = "/get-a-quote/";
const REQUIRED_FIELDS = ["name", "company", "phone", "email", "service", "message"];
const PHONE = "319-610-4341";

// D1 schema — created lazily on first write. Idempotent so it's safe
// to CREATE TABLE IF NOT EXISTS on every request; SQLite short-circuits
// if the table already exists.
const QUOTES_SCHEMA = `
CREATE TABLE IF NOT EXISTS quotes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  name TEXT NOT NULL,
  company TEXT NOT NULL,
  phone TEXT NOT NULL,
  email TEXT NOT NULL,
  machine_brand TEXT,
  machine_model TEXT,
  service TEXT NOT NULL,
  message TEXT NOT NULL,
  ip TEXT,
  user_agent TEXT,
  status TEXT NOT NULL DEFAULT 'new',
  notes TEXT DEFAULT '',
  email_sent INTEGER NOT NULL DEFAULT 0,
  email_error TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_quotes_status ON quotes(status);
CREATE INDEX IF NOT EXISTS idx_quotes_created_at ON quotes(created_at DESC);
`;

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

    if (url.pathname === "/admin" || url.pathname.startsWith("/admin/")) {
      return handleAdmin(request, env, url);
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

  // Persist the submission to D1 before attempting delivery so nothing
  // is lost if email fails. Guarded — if the DB binding isn't wired yet,
  // this is a no-op and we still send the email.
  const saved = await saveToD1(env, payload);
  if (!saved.ok && saved.error !== "no-db-binding") {
    console.log("D1 save failed:", saved.error);
  }

  const sent = await sendNotificationEmail(env, payload);

  // Best-effort: annotate the D1 row with the email result so admins
  // can see delivery status alongside the submission.
  if (saved.ok) {
    await updateEmailStatus(env, saved.id, sent.ok, sent.error || "")
      .catch((e) => console.log("D1 status update failed:", e && e.message));
  }

  if (!sent.ok) {
    console.log("Resend send failed:", sent.error);
    return seeOther(url, `${ERROR_PATH}?error=email-failed`);
  }

  return seeOther(url, SUCCESS_PATH);
}

async function saveToD1(env, p) {
  if (!env.DB) return { ok: false, error: "no-db-binding" };
  try {
    await env.DB.exec(QUOTES_SCHEMA.replace(/\n/g, " "));
    const result = await env.DB.prepare(
      `INSERT INTO quotes
        (created_at, name, company, phone, email, machine_brand,
         machine_model, service, message, ip, user_agent)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    )
      .bind(
        p.timestamp,
        p.name,
        p.company,
        p.phone,
        p.email,
        p.machine_brand,
        p.machine_model,
        p.service,
        p.message,
        p.ip,
        p.ua,
      )
      .run();
    return { ok: true, id: result.meta.last_row_id };
  } catch (e) {
    return { ok: false, error: String(e && e.message || e) };
  }
}

async function updateEmailStatus(env, id, sent, error) {
  if (!env.DB || !id) return;
  await env.DB.prepare(
    "UPDATE quotes SET email_sent = ?, email_error = ? WHERE id = ?",
  )
    .bind(sent ? 1 : 0, error || "", id)
    .run();
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

  // From: verified Resend sender you own. Cannot be the customer's email
  // (would fail SPF/DKIM/DMARC). Customer's email goes in reply_to below.
  const fromEmail = env.FROM_EMAIL ||
    "Midwest CNC Quote Form <quotes@midwestcncservices.com>";

  // To: Ken by default. NOTIFY_EMAIL env var can override (comma-separated
  // to CC additional recipients, e.g. "ken@...,aaron@...").
  const recipients = (env.NOTIFY_EMAIL || "ken@midwestcncservices.com")
    .split(",").map((s) => s.trim()).filter(Boolean);
  if (recipients.length === 0) return { ok: false, error: "NOTIFY_EMAIL empty" };

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
        from: fromEmail,
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

// =====================================================================
// Admin UI — /admin/*
// =====================================================================
// Auth: single ADMIN_PASSWORD secret. Login POST verifies password
// (constant-time), issues a signed cookie (HMAC-SHA256 over expiry
// timestamp, key = SESSION_SECRET). Session length: 7 days.
//
// Storage: reads from the D1 'quotes' table. Read-only, list, detail,
// and mutation endpoints for status + notes. CSV export. Origin-checked
// on every state-changing POST (CSRF defense).
// =====================================================================

const SESSION_COOKIE = "mwc_admin";
const SESSION_TTL_SECONDS = 60 * 60 * 24 * 7; // 7 days
const STATUS_OPTIONS = ["new", "contacted", "quoted", "won", "dead"];

async function handleAdmin(request, env, url) {
  // Config sanity check before any auth. If secrets aren't set, show
  // a clear config-error page rather than a mysterious 500.
  if (!env.ADMIN_PASSWORD || !env.SESSION_SECRET) {
    return htmlResponse(
      renderConfigError(!env.ADMIN_PASSWORD, !env.SESSION_SECRET),
      500,
    );
  }

  const path = url.pathname;
  const method = request.method;

  // Login page — the only /admin path reachable without a session.
  if (path === "/admin/login") {
    if (method === "GET") return htmlResponse(renderLogin(""));
    if (method === "POST") return handleLogin(request, env, url);
    return new Response("Method not allowed", { status: 405 });
  }

  // Logout — clears the cookie, redirects to the login page.
  if (path === "/admin/logout") {
    return new Response(null, {
      status: 303,
      headers: {
        Location: new URL("/admin/login", url).toString(),
        "Set-Cookie": `${SESSION_COOKIE}=; Path=/admin; Max-Age=0; HttpOnly; Secure; SameSite=Lax`,
      },
    });
  }

  // Everything else requires a valid session.
  const session = await getSession(request, env);
  if (!session) {
    return new Response(null, {
      status: 303,
      headers: { Location: new URL("/admin/login", url).toString() },
    });
  }

  // Origin check for state-changing methods (CSRF defense).
  if (method === "POST") {
    const origin = request.headers.get("origin") || "";
    if (origin && !origin.startsWith(`${url.protocol}//${url.host}`)) {
      return new Response("Bad origin", { status: 403 });
    }
  }

  // Routes
  if (path === "/admin" || path === "/admin/") {
    return handleAdminList(request, env, url);
  }
  if (path === "/admin/export.csv") {
    return handleAdminExport(env);
  }
  const detailMatch = path.match(/^\/admin\/quote\/(\d+)$/);
  if (detailMatch) {
    const id = parseInt(detailMatch[1], 10);
    if (method === "GET") return handleAdminDetail(env, url, id);
    if (method === "POST") return handleAdminUpdate(request, env, url, id);
    return new Response("Method not allowed", { status: 405 });
  }

  return htmlResponse(renderLayout("Not found", `<p>Not found.</p>`), 404);
}

// ---------- Login + session cookie ----------

async function handleLogin(request, env, url) {
  const form = await request.formData().catch(() => null);
  if (!form) return htmlResponse(renderLogin("Bad request."));
  const password = (form.get("password") || "").toString();
  if (!password) return htmlResponse(renderLogin("Enter a password."));

  const ok = await constantTimeStringEquals(password, env.ADMIN_PASSWORD);
  if (!ok) {
    // Small delay to slow a brute force on the login route itself.
    await new Promise((r) => setTimeout(r, 500));
    return htmlResponse(renderLogin("Wrong password."), 401);
  }

  const cookie = await mintSessionCookie(env.SESSION_SECRET);
  return new Response(null, {
    status: 303,
    headers: {
      Location: new URL("/admin", url).toString(),
      "Set-Cookie":
        `${SESSION_COOKIE}=${cookie}; Path=/admin; Max-Age=${SESSION_TTL_SECONDS}; ` +
        `HttpOnly; Secure; SameSite=Lax`,
    },
  });
}

async function getSession(request, env) {
  const cookieHeader = request.headers.get("cookie") || "";
  const match = cookieHeader.match(new RegExp(`(?:^|;\\s*)${SESSION_COOKIE}=([^;]+)`));
  if (!match) return null;
  return verifySessionCookie(match[1], env.SESSION_SECRET);
}

async function mintSessionCookie(secret) {
  const expiry = Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS;
  const payload = String(expiry);
  const sig = await hmacSha256B64(secret, payload);
  return `${payload}.${sig}`;
}

async function verifySessionCookie(cookie, secret) {
  const dot = cookie.lastIndexOf(".");
  if (dot < 0) return null;
  const payload = cookie.slice(0, dot);
  const providedSig = cookie.slice(dot + 1);
  const expectedSig = await hmacSha256B64(secret, payload);
  if (!(await constantTimeStringEquals(providedSig, expectedSig))) return null;
  const expiry = parseInt(payload, 10);
  if (!Number.isFinite(expiry) || expiry < Math.floor(Date.now() / 1000)) return null;
  return { expiry };
}

async function hmacSha256B64(secret, message) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(message));
  return b64UrlEncode(new Uint8Array(sig));
}

function b64UrlEncode(bytes) {
  let s = "";
  for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function constantTimeStringEquals(a, b) {
  // Hash both first so we never leak length via early return.
  const enc = new TextEncoder();
  const [ha, hb] = await Promise.all([
    crypto.subtle.digest("SHA-256", enc.encode(a)),
    crypto.subtle.digest("SHA-256", enc.encode(b)),
  ]);
  const av = new Uint8Array(ha), bv = new Uint8Array(hb);
  let diff = 0;
  for (let i = 0; i < av.length; i++) diff |= av[i] ^ bv[i];
  return diff === 0;
}

// ---------- Admin list ----------

async function handleAdminList(request, env, url) {
  if (!env.DB) {
    return htmlResponse(renderLayout(
      "Admin — no database",
      `<p class="empty">The D1 database binding isn't wired. Ask engineering to add
       <code>d1_databases</code> to <code>wrangler.jsonc</code>.</p>`,
    ));
  }
  // Ensure schema exists so a fresh DB doesn't throw before any writes.
  await env.DB.exec(QUOTES_SCHEMA.replace(/\n/g, " ")).catch(() => {});

  const q = url.searchParams.get("q") || "";
  const status = url.searchParams.get("status") || "";

  let sql = "SELECT id, created_at, name, company, phone, email, service, status, email_sent FROM quotes";
  const where = [];
  const args = [];
  if (status) {
    where.push("status = ?");
    args.push(status);
  }
  if (q) {
    where.push("(name LIKE ? OR company LIKE ? OR email LIKE ? OR phone LIKE ?)");
    const wc = `%${q}%`;
    args.push(wc, wc, wc, wc);
  }
  if (where.length) sql += " WHERE " + where.join(" AND ");
  sql += " ORDER BY datetime(created_at) DESC LIMIT 500";

  const { results } = await env.DB.prepare(sql).bind(...args).all();
  return htmlResponse(renderList(results || [], { q, status }));
}

// ---------- Admin detail ----------

async function handleAdminDetail(env, url, id) {
  const row = await env.DB.prepare("SELECT * FROM quotes WHERE id = ?").bind(id).first();
  if (!row) return htmlResponse(renderLayout("Not found", `<p>Quote #${id} not found.</p>`), 404);
  const saved = url.searchParams.get("saved") === "1";
  return htmlResponse(renderDetail(row, saved));
}

// ---------- Admin update (status + notes) ----------

async function handleAdminUpdate(request, env, url, id) {
  const form = await request.formData().catch(() => null);
  if (!form) return new Response("Bad request", { status: 400 });

  const newStatus = (form.get("status") || "").toString();
  const notes = (form.get("notes") || "").toString();

  if (!STATUS_OPTIONS.includes(newStatus)) {
    return new Response("Invalid status", { status: 400 });
  }

  await env.DB.prepare("UPDATE quotes SET status = ?, notes = ? WHERE id = ?")
    .bind(newStatus, notes, id)
    .run();

  return new Response(null, {
    status: 303,
    headers: { Location: new URL(`/admin/quote/${id}?saved=1`, url).toString() },
  });
}

// ---------- CSV export ----------

async function handleAdminExport(env) {
  const { results } = await env.DB.prepare(
    "SELECT id, created_at, name, company, phone, email, machine_brand, machine_model, " +
    "service, message, status, notes, email_sent, email_error FROM quotes " +
    "ORDER BY datetime(created_at) DESC",
  ).all();
  const header = [
    "id","created_at","name","company","phone","email","machine_brand",
    "machine_model","service","message","status","notes","email_sent","email_error",
  ];
  const rows = [header.join(",")];
  for (const r of results || []) {
    rows.push(header.map((k) => csvCell(r[k])).join(","));
  }
  return new Response(rows.join("\n"), {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="midwestcnc-quotes-${todayStamp()}.csv"`,
      "Cache-Control": "no-store",
    },
  });
}

function csvCell(v) {
  if (v === null || v === undefined) return "";
  const s = String(v);
  if (/[,"\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

function todayStamp() {
  return new Date().toISOString().slice(0, 10);
}

// ---------- Rendering ----------

function htmlResponse(body, status = 200) {
  return new Response(body, {
    status,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "DENY",
      "Referrer-Policy": "same-origin",
    },
  });
}

const BASE_CSS = `
  :root {
    --accent: #b8341a; --accent-dark: #8f2814; --line: #e4e2df;
    --surface: #ffffff; --surface-2: #f7f5f2; --bg: #fbf9f6;
    --fg: #1a1a1a; --muted: #6b6b6b;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; font: 16px/1.55 -apple-system, BlinkMacSystemFont,
      "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: var(--bg); color: var(--fg);
  }
  a { color: var(--accent-dark); }
  header.admin-nav {
    background: #1a1a1a; color: #fff; padding: 12px 24px;
    display: flex; align-items: center; gap: 20px;
  }
  header.admin-nav a { color: #fff; text-decoration: none; opacity: 0.85; }
  header.admin-nav a:hover { opacity: 1; }
  header.admin-nav .brand { font-weight: 700; letter-spacing: 0.02em; }
  header.admin-nav .spacer { flex: 1; }
  main.admin {
    max-width: 1200px; margin: 0 auto; padding: 24px;
  }
  h1 { margin: 0 0 16px 0; font-size: 1.5rem; }
  h2 { margin: 24px 0 8px 0; font-size: 1.1rem; }
  .filters {
    display: flex; gap: 12px; margin-bottom: 16px; align-items: center;
    flex-wrap: wrap;
  }
  .filters input, .filters select {
    padding: 8px 10px; border: 1px solid var(--line); border-radius: 6px;
    font: inherit; background: #fff;
  }
  .filters .grow { flex: 1; min-width: 200px; }
  .btn {
    display: inline-block; padding: 8px 14px; background: var(--accent);
    color: #fff; text-decoration: none; border: 0; border-radius: 6px;
    cursor: pointer; font: inherit; font-weight: 600;
  }
  .btn:hover { background: var(--accent-dark); }
  .btn.secondary { background: #fff; color: var(--fg); border: 1px solid var(--line); }
  .btn.secondary:hover { background: var(--surface-2); }
  table.admin-table {
    width: 100%; border-collapse: collapse; background: #fff;
    border-radius: 8px; overflow: hidden; box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  }
  table.admin-table th, table.admin-table td {
    padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left;
    vertical-align: top;
  }
  table.admin-table th {
    background: var(--surface-2); font-weight: 600; font-size: 0.85rem;
    text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted);
  }
  table.admin-table tr:last-child td { border-bottom: 0; }
  table.admin-table tr:hover { background: #fafafa; }
  .status {
    display: inline-block; padding: 3px 8px; border-radius: 10px;
    font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .status.new       { background: #fff4e6; color: #a55b00; }
  .status.contacted { background: #e6f2ff; color: #0057b3; }
  .status.quoted    { background: #efe6ff; color: #5a2ea6; }
  .status.won       { background: #e6f9ee; color: #1b7a3a; }
  .status.dead      { background: #f0f0f0; color: #6b6b6b; }
  .empty {
    padding: 40px; text-align: center; color: var(--muted); background: #fff;
    border-radius: 8px; border: 1px dashed var(--line);
  }
  .toast {
    padding: 10px 14px; background: #e6f9ee; border: 1px solid #b8e6c5;
    border-radius: 6px; color: #1b7a3a; margin-bottom: 16px;
  }
  .detail {
    background: #fff; border-radius: 8px; padding: 24px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  }
  .kv { display: grid; grid-template-columns: 160px 1fr; gap: 8px 16px; }
  .kv dt { color: var(--muted); font-weight: 600; }
  .kv dd { margin: 0; word-break: break-word; }
  .message-block {
    background: var(--surface-2); border-left: 3px solid var(--accent);
    padding: 12px 16px; border-radius: 4px; white-space: pre-wrap;
    margin: 4px 0;
  }
  form.update-form {
    margin-top: 24px; padding-top: 24px; border-top: 1px solid var(--line);
    display: flex; flex-direction: column; gap: 12px;
  }
  form.update-form label { font-weight: 600; font-size: 0.9rem; }
  form.update-form select, form.update-form textarea {
    font: inherit; padding: 8px 10px; border: 1px solid var(--line);
    border-radius: 6px; background: #fff;
  }
  form.update-form textarea { min-height: 120px; resize: vertical; }
  .email-badge {
    display: inline-block; padding: 3px 8px; border-radius: 10px;
    font-size: 0.75rem; font-weight: 600;
  }
  .email-badge.ok { background: #e6f9ee; color: #1b7a3a; }
  .email-badge.fail { background: #ffe6e6; color: #a11616; }
  .login-wrap {
    max-width: 380px; margin: 80px auto; padding: 32px;
    background: #fff; border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  }
  .login-wrap h1 { text-align: center; margin-bottom: 24px; }
  .login-wrap form { display: flex; flex-direction: column; gap: 12px; }
  .login-wrap input {
    font: inherit; font-size: 1rem; padding: 12px;
    border: 1px solid var(--line); border-radius: 6px;
  }
  .login-wrap .btn { padding: 12px; font-size: 1rem; }
  .login-wrap .error {
    color: #a11616; background: #ffe6e6; padding: 10px;
    border-radius: 6px; text-align: center; font-size: 0.9rem;
  }
`;

function renderLayout(title, body, opts = {}) {
  const nav = opts.hideNav ? "" : `
    <header class="admin-nav">
      <span class="brand">Midwest CNC — Admin</span>
      <a href="/admin">Leads</a>
      <a href="/admin/export.csv">Export CSV</a>
      <span class="spacer"></span>
      <a href="/admin/logout">Sign out</a>
    </header>`;
  return `<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>${esc(title)}</title>
<style>${BASE_CSS}</style>
</head><body>
${nav}
<main class="admin">${body}</main>
</body></html>`;
}

function renderLogin(errorMsg) {
  return renderLayout("Sign in", `
    <div class="login-wrap">
      <h1>Sign in</h1>
      ${errorMsg ? `<div class="error">${esc(errorMsg)}</div>` : ""}
      <form method="POST" action="/admin/login" autocomplete="off">
        <input type="password" name="password" placeholder="Admin password"
               required autofocus autocomplete="current-password">
        <button type="submit" class="btn">Sign in</button>
      </form>
    </div>
  `, { hideNav: true });
}

function renderConfigError(missingPassword, missingSecret) {
  const items = [];
  if (missingPassword) items.push("<code>ADMIN_PASSWORD</code>");
  if (missingSecret)   items.push("<code>SESSION_SECRET</code>");
  return renderLayout("Admin — configuration error", `
    <div class="empty">
      <p><strong>Admin is not fully configured.</strong></p>
      <p>Missing Cloudflare Worker secret${items.length > 1 ? "s" : ""}:
      ${items.join(" and ")}.</p>
      <p>Add ${items.length > 1 ? "them" : "it"} in the Cloudflare dashboard
      under Workers &amp; Pages → midwestcnc → Settings → Variables and Secrets.</p>
    </div>
  `, { hideNav: true });
}

function renderList(rows, params) {
  const statusOptions = ["", ...STATUS_OPTIONS]
    .map((s) => `<option value="${esc(s)}"${s === params.status ? " selected" : ""}>${s || "All statuses"}</option>`)
    .join("");

  const body = `
    <h1>Leads <span style="color:var(--muted);font-weight:400;">(${rows.length}${rows.length === 500 ? "+, showing latest 500" : ""})</span></h1>

    <form class="filters" method="GET" action="/admin">
      <input type="search" name="q" class="grow" value="${esc(params.q)}"
             placeholder="Search name, company, email, phone…">
      <select name="status">${statusOptions}</select>
      <button type="submit" class="btn">Filter</button>
      ${params.q || params.status ? `<a href="/admin" class="btn secondary">Reset</a>` : ""}
    </form>

    ${rows.length === 0 ? `
      <div class="empty">
        <p>No leads yet.</p>
        <p style="font-size:0.9rem;">Submissions to the quote form will appear here.</p>
      </div>
    ` : `
      <table class="admin-table">
        <thead>
          <tr>
            <th>Date</th><th>Name</th><th>Company</th><th>Phone</th>
            <th>Service</th><th>Status</th><th>Email</th><th></th>
          </tr>
        </thead>
        <tbody>
          ${rows.map((r) => `
            <tr>
              <td>${esc(formatDate(r.created_at))}</td>
              <td>${esc(r.name)}</td>
              <td>${esc(r.company)}</td>
              <td><a href="tel:${esc(r.phone)}">${esc(r.phone)}</a></td>
              <td>${esc(r.service)}</td>
              <td><span class="status ${esc(r.status)}">${esc(r.status)}</span></td>
              <td>${r.email_sent
                ? '<span class="email-badge ok">sent</span>'
                : '<span class="email-badge fail">no</span>'}</td>
              <td><a href="/admin/quote/${r.id}" class="btn secondary">View</a></td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `}
  `;
  return renderLayout("Leads — Midwest CNC Admin", body);
}

function renderDetail(r, saved) {
  const statusOptions = STATUS_OPTIONS
    .map((s) => `<option value="${esc(s)}"${s === r.status ? " selected" : ""}>${s}</option>`)
    .join("");

  const body = `
    <p><a href="/admin">&larr; All leads</a></p>
    <h1>Quote #${r.id} &mdash; ${esc(r.name)}</h1>
    ${saved ? `<div class="toast">Changes saved.</div>` : ""}

    <div class="detail">
      <dl class="kv">
        <dt>Submitted</dt>            <dd>${esc(formatDate(r.created_at))}</dd>
        <dt>Name</dt>                 <dd>${esc(r.name)}</dd>
        <dt>Company</dt>              <dd>${esc(r.company)}</dd>
        <dt>Phone</dt>                <dd><a href="tel:${esc(r.phone)}">${esc(r.phone)}</a></dd>
        <dt>Email</dt>                <dd><a href="mailto:${esc(r.email)}">${esc(r.email)}</a></dd>
        <dt>Machine brand</dt>        <dd>${esc(r.machine_brand || "—")}</dd>
        <dt>Machine model</dt>        <dd>${esc(r.machine_model || "—")}</dd>
        <dt>Service needed</dt>       <dd>${esc(r.service)}</dd>
        <dt>Message</dt>              <dd><div class="message-block">${esc(r.message)}</div></dd>
        <dt>Email delivery</dt>       <dd>${r.email_sent
          ? '<span class="email-badge ok">sent to Ken</span>'
          : `<span class="email-badge fail">not sent</span> ${r.email_error ? `<br><small style="color:var(--muted);">${esc(r.email_error)}</small>` : ""}`}</dd>
        <dt>Source IP</dt>            <dd style="font-family:monospace;font-size:0.85rem;color:var(--muted);">${esc(r.ip || "—")}</dd>
      </dl>

      <form class="update-form" method="POST" action="/admin/quote/${r.id}">
        <label for="status-select">Status</label>
        <select id="status-select" name="status">${statusOptions}</select>

        <label for="notes-field">Notes (called, quoted, follow-up dates, etc.)</label>
        <textarea id="notes-field" name="notes" placeholder="Freeform notes on this lead…">${esc(r.notes || "")}</textarea>

        <button type="submit" class="btn">Save changes</button>
      </form>
    </div>
  `;
  return renderLayout(`Quote #${r.id} — Midwest CNC Admin`, body);
}

function formatDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString("en-US", {
    year: "numeric", month: "short", day: "numeric",
    hour: "numeric", minute: "2-digit",
  });
}
