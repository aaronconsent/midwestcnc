#!/usr/bin/env python3
"""
Convert a generated brand markdown (src/content/spindle-brands/{slug}.md)
into a standalone HTML page. CSS lives in a single <style> block inside
<head> — we'll extract to /assets/css/ later once the design is locked.

This is a deliberately small, dependency-free Markdown converter that only
handles the constructs our generator emits:
  - YAML-ish front matter (one level of nesting + tiny inline objects)
  - Headings: `#`, `##`
  - Italic eyebrow: `_text_` on its own line
  - Paragraphs
  - Bulleted lists (single + 2-space-indented sublist)
  - Bold: `**text**`
  - Links: `[text](url)`
  - Blockquote: `> text`
  - Italic placeholders: `*text*`
"""

import html
import json
import os
import re
import sys


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Three content directories — bulk runs scan all of them.
CONTENT_DIRS = [
    os.path.join(REPO, "src", "content", "spindle-brands"),
    os.path.join(REPO, "src", "content", "machine-repair"),
    os.path.join(REPO, "src", "content", "way-covers"),
]
# Back-compat alias — used by older tests + the targeted-by-slug code path.
CONTENT = CONTENT_DIRS[0]
OUTDIR  = os.path.join(REPO, "public")


# ---------- Front-matter parser ----------

def parse_frontmatter(src):
    """Pull the YAML-like header out of `src`. Returns (data, body)."""
    if not src.startswith("---\n"):
        return {}, src
    end = src.find("\n---\n", 4)
    if end < 0:
        return {}, src
    raw = src[4:end]
    body = src[end + 5:]

    # Tiny YAML reader. Handles:
    #   key: "string"
    #   key: number
    #   key:               <- nested object follows
    #     subkey: ...
    #   key:               <- list of (scalar | inline-object) follows
    #     - item
    #     - { k: v, k2: "v2" }
    lines = raw.split("\n")
    data = {}
    stack = [(data, -1)]  # (container, indent)

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1; continue
        indent = len(line) - len(line.lstrip())
        # Pop stack to current indent
        while stack and indent <= stack[-1][1]:
            stack.pop()
        if not stack:
            stack = [(data, -1)]
        parent, _ = stack[-1]

        stripped = line.lstrip()

        # List item under previous key
        if stripped.startswith("- "):
            item_raw = stripped[2:].strip()
            if isinstance(parent, list):
                parent.append(_parse_scalar_or_inline(item_raw))
            i += 1; continue

        # key: value
        m = re.match(r"([^:]+):\s*(.*)$", stripped)
        if not m:
            i += 1; continue
        key, val = m.group(1).strip(), m.group(2).strip()
        # Strip wrapping quotes from the key ("@type" → @type)
        if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
            key = key[1:-1]

        if val == "":
            # Look ahead: list or nested object?
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent > indent:
                    if next_line.lstrip().startswith("- "):
                        new_container = []
                    else:
                        new_container = {}
                    parent[key] = new_container
                    stack.append((new_container, indent))
                    i += 1; continue
            parent[key] = ""
        else:
            parent[key] = _parse_scalar_or_inline(val)
        i += 1

    return data, body


def _parse_scalar_or_inline(v):
    """Parse one YAML scalar or inline object/array literal."""
    v = v.strip()
    # Strip quotes
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    # Inline object: { key: val, key2: "val2" }
    if v.startswith("{") and v.endswith("}"):
        inner = v[1:-1].strip()
        obj = {}
        # Split by commas not inside quotes
        parts = _split_smart(inner, ",")
        for part in parts:
            if not part.strip():
                continue
            m = re.match(r"([^:]+):\s*(.*)$", part.strip())
            if m:
                k = m.group(1).strip()
                if (k.startswith('"') and k.endswith('"')) or (k.startswith("'") and k.endswith("'")):
                    k = k[1:-1]
                obj[k] = _parse_scalar_or_inline(m.group(2))
        return obj
    # Number?
    if re.match(r"^-?\d+$", v):
        return int(v)
    return v


def _split_smart(s, delim):
    """Split on delim, respecting quoted strings and {}/[] nesting."""
    out, buf, depth, q = [], [], 0, None
    for c in s:
        if q:
            buf.append(c)
            if c == q: q = None
            continue
        if c in ('"', "'"):
            buf.append(c); q = c; continue
        if c in "{[":
            buf.append(c); depth += 1; continue
        if c in "}]":
            buf.append(c); depth -= 1; continue
        if c == delim and depth == 0:
            out.append("".join(buf)); buf = []
            continue
        buf.append(c)
    if buf:
        out.append("".join(buf))
    return out


# ---------- Markdown body converter ----------

def md_inline(s):
    """Apply inline markdown to a string. Returns HTML-safe markup."""
    # Escape any raw HTML first.
    s = html.escape(s, quote=False)
    # Images: ![alt](src) — must run before the [text](url) link rule
    s = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: (
            f'<figure class="hero-figure">'
            f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">'
            f'</figure>'
        ),
        s,
    )
    # Links: [text](url)
    s = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
        s,
    )
    # Bold: **text**
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    # Italic: *text* (single asterisk) — must run after bold
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    # Italic: _text_ (underscore) — only matches when delimited by word boundaries
    s = re.sub(r"(?<!\w)_([^_\n]+)_(?!\w)", r"<em>\1</em>", s)
    return s


def md_body_to_html(body):
    """Convert the body (after front matter) into structured HTML.

    Produces top-level <p>, <h1>, <h2>, <ul>, <blockquote>, and a sentinel
    HTML comment per H2 so the wrapping template can group sections.
    """
    out = []
    paragraph_buf = []

    def flush_para():
        nonlocal paragraph_buf
        if paragraph_buf:
            joined = " ".join(paragraph_buf).strip()
            if joined:
                out.append(f"<p>{md_inline(joined)}</p>")
            paragraph_buf = []

    lines = body.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Blank line — paragraph break
        if not stripped:
            flush_para()
            i += 1; continue

        # Raw <script> blocks (for inline JSON-LD schema injection) — pass
        # through verbatim until the closing </script>. The brand-page FAQ
        # schemas use this to inject FAQPage JSON-LD from markdown.
        if stripped.startswith("<script"):
            flush_para()
            block_lines = [line]
            i += 1
            while i < len(lines) and "</script>" not in lines[i]:
                block_lines.append(lines[i])
                i += 1
            if i < len(lines):
                block_lines.append(lines[i])  # include closing line
                i += 1
            out.append("\n".join(block_lines))
            continue

        # Standalone image — render as a figure outside any <p>
        if stripped.startswith("!["):
            flush_para()
            out.append(md_inline(stripped))
            i += 1; continue

        # Headings
        if stripped.startswith("# "):
            flush_para()
            out.append(f"<h1>{md_inline(stripped[2:].strip())}</h1>")
            i += 1; continue
        if stripped.startswith("## "):
            flush_para()
            heading = stripped[3:].strip()
            slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
            out.append(f'<h2 id="{slug}">{md_inline(heading)}</h2>')
            i += 1; continue

        # Blockquote
        if stripped.startswith("> "):
            flush_para()
            quote_lines = []
            while i < len(lines) and lines[i].lstrip().startswith("> "):
                quote_lines.append(lines[i].lstrip()[2:].strip())
                i += 1
            out.append(f'<blockquote><p>{md_inline(" ".join(quote_lines))}</p></blockquote>')
            continue

        # Bullet list (with optional one-level nested sublist)
        if stripped.startswith("- "):
            flush_para()
            out.append("<ul>")
            while i < len(lines) and lines[i].lstrip().startswith("- "):
                raw = lines[i]
                indent = len(raw) - len(raw.lstrip())
                item_text = raw.lstrip()[2:].strip()
                if indent == 0:
                    out.append(f"<li>{md_inline(item_text)}")
                    # Check for nested items
                    nested_start = i + 1
                    nested_items = []
                    while (nested_start < len(lines)
                           and lines[nested_start].lstrip().startswith("- ")
                           and (len(lines[nested_start]) - len(lines[nested_start].lstrip())) > 0):
                        nested_items.append(lines[nested_start].lstrip()[2:].strip())
                        nested_start += 1
                    if nested_items:
                        out.append("<ul>")
                        for ni in nested_items:
                            out.append(f"<li>{md_inline(ni)}</li>")
                        out.append("</ul>")
                        i = nested_start
                    else:
                        i += 1
                    out.append("</li>")
                else:
                    # Stray nested item with no parent at indent 0; treat as flat.
                    out.append(f"<li>{md_inline(item_text)}</li>")
                    i += 1
            out.append("</ul>")
            continue

        # Default — accumulate into paragraph
        paragraph_buf.append(stripped)
        i += 1

    flush_para()
    return "\n".join(out)


# ---------- Schema JSON-LD ----------

def schema_jsonld(fm):
    """Emit the schema_data front-matter block as one or more JSON-LD scripts."""
    schema = fm.get("schema_data", {}) or {}
    scripts = []
    for key in ("service", "local_business", "breadcrumb"):
        if key not in schema:
            continue
        block = _expand_schema_block(schema[key], key, fm)
        json_str = json.dumps(block, indent=2, ensure_ascii=False)
        scripts.append(
            f'<script type="application/ld+json">\n{json_str}\n</script>'
        )
    return "\n".join(scripts)


def _expand_schema_block(block, key, fm):
    """Convert a parsed schema_data sub-block into a JSON-LD-shaped dict."""
    if not isinstance(block, dict):
        return block
    out = {"@context": "https://schema.org"}
    # Reorder to put @type / @id first
    if "@type" in block:
        out["@type"] = block["@type"]
    if "@id" in block:
        out["@id"] = block["@id"]
    for k, v in block.items():
        if k in ("@type", "@id"):
            continue
        out[k] = v
    return out


# ---------- Page template ----------

CSS = """\
:root {
  --bg: #ffffff;
  --fg: #1a1a1a;
  --muted: #5a5a5a;
  --accent: #b8341a;
  --accent-dark: #8c2510;
  --line: #e5e5e5;
  --soft: #f6f4f1;
  --max: 72ch;
  --sticky-cta-height: 64px;
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 17px;
  line-height: 1.55;
  color: var(--fg);
  background: var(--bg);
}

a { color: var(--accent); text-decoration: underline; text-underline-offset: 2px; }
a:hover { color: var(--accent-dark); }

.site-header {
  border-bottom: 1px solid var(--line);
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
.site-header .brand {
  font-weight: 700;
  letter-spacing: -0.01em;
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  color: var(--fg);
}
.site-header .brand img {
  height: 36px;
  width: auto;
  display: block;
}
.site-header nav a { margin-left: 1.25rem; text-decoration: none; color: var(--fg); }
.site-header nav a:hover { color: var(--accent); }

nav.breadcrumbs {
  font-size: 0.85rem;
  color: var(--muted);
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--line);
  background: var(--soft);
}
nav.breadcrumbs ol { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 0.5rem; }
nav.breadcrumbs li:not(:last-child)::after { content: "›"; margin-left: 0.5rem; color: var(--muted); }
nav.breadcrumbs a { color: var(--muted); text-decoration: none; }
nav.breadcrumbs a:hover { color: var(--accent); }

main { padding: 0 1.25rem; }

article { max-width: var(--max); margin: 2rem auto; }

.eyebrow { color: var(--muted); font-size: 0.95rem; font-style: italic; margin: 0 0 0.5rem 0; }

h1 {
  font-size: clamp(1.8rem, 4vw, 2.6rem);
  line-height: 1.15;
  letter-spacing: -0.02em;
  margin: 0 0 1.25rem 0;
}

h2 {
  font-size: 1.35rem;
  margin: 2.5rem 0 0.75rem 0;
  letter-spacing: -0.01em;
  border-top: 1px solid var(--line);
  padding-top: 1.5rem;
}
h2:first-of-type { border-top: 0; padding-top: 0; }

p { margin: 0.85rem 0; }

ul { padding-left: 1.5rem; margin: 0.75rem 0; }
li { margin: 0.25rem 0; }

blockquote {
  margin: 1.5rem 0;
  padding: 1rem 1.25rem;
  border-left: 3px solid var(--accent);
  background: var(--soft);
  font-style: italic;
  color: var(--fg);
}
blockquote p { margin: 0; }

.cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 1.5rem 0;
}
.cta-button {
  display: inline-block;
  background: var(--accent);
  color: #fff !important;
  padding: 0.75rem 1.4rem;
  border-radius: 4px;
  text-decoration: none !important;
  font-weight: 600;
  letter-spacing: 0.01em;
}
.cta-button:hover { background: var(--accent-dark); }
.cta-phone {
  display: inline-block;
  padding: 0.75rem 0.5rem;
  color: var(--fg) !important;
  text-decoration: none !important;
  font-weight: 600;
}
.cta-phone::before { content: "☎ "; color: var(--muted); }

.quote-form-placeholder {
  margin: 1.5rem 0;
  padding: 1.25rem;
  border: 1px dashed var(--line);
  background: var(--soft);
  color: var(--muted);
  font-style: italic;
  font-size: 0.9rem;
}

.hero-figure {
  margin: 1.5rem 0 0 0;
  padding: 0;
}
.hero-figure img {
  width: 100%;
  height: auto;
  max-height: 400px;
  object-fit: cover;
  object-position: center;
  border-radius: 6px;
  display: block;
}

/* Sticky mobile CTA bar — fix 14. Hidden on desktop, fixed to bottom on
   narrow viewports so the phone/quote actions stay in reach. */
.mobile-cta-bar {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 0.5rem;
  gap: 0.5rem;
  background: #fff;
  border-top: 1px solid var(--line);
  box-shadow: 0 -2px 8px rgba(0,0,0,0.06);
}
.mobile-cta-bar a {
  flex: 1 1 0;
  text-align: center;
  padding: 0.85rem 0.5rem;
  font-weight: 600;
  text-decoration: none !important;
  border-radius: 4px;
}
.mobile-cta-bar .mcta-phone {
  color: var(--fg) !important;
  border: 1px solid var(--line);
}
.mobile-cta-bar .mcta-quote {
  color: #fff !important;
  background: var(--accent);
}
.mobile-cta-bar .mcta-quote:hover { background: var(--accent-dark); }

@media (max-width: 767px) {
  .mobile-cta-bar { display: flex; }
  body { padding-bottom: var(--sticky-cta-height); }
}

.site-footer {
  border-top: 1px solid var(--line);
  padding: 2rem 1.25rem;
  color: var(--muted);
  font-size: 0.9rem;
  text-align: center;
  margin-top: 4rem;
}

@media (max-width: 600px) {
  .site-header { flex-direction: column; align-items: flex-start; }
  .site-header nav a { margin-left: 0; margin-right: 1rem; }
}
"""


def render_html(fm, body_html):
    """Wrap the converted body in the full page chrome."""
    title = fm.get("title", "Midwest CNC Services")
    meta_desc = fm.get("meta_description", "")
    h1 = fm.get("h1", "")
    slug = fm.get("slug", "")
    page_type = fm.get("page_type", "")

    # Breadcrumb nav from schema_data
    crumbs_html = ""
    bc = (fm.get("schema_data") or {}).get("breadcrumb", {})
    items = bc.get("itemListElement", []) if isinstance(bc, dict) else []
    if items:
        crumb_lis = []
        for item in items:
            if isinstance(item, dict):
                name = item.get("name", "")
                href = item.get("item", "")
                crumb_lis.append(
                    f'<li><a href="{html.escape(str(href))}">{html.escape(str(name))}</a></li>'
                )
        if crumb_lis:
            crumbs_html = (
                '<nav class="breadcrumbs" aria-label="breadcrumb">\n'
                f'  <ol>\n    {"".join(crumb_lis)}\n  </ol>\n'
                '</nav>'
            )

    # Convert eyebrow + CTA-row + form-placeholder markup post-hoc.
    # The generator emits these as italicized paragraphs / paragraphs that
    # contain CTA links — re-style them here for readability.
    body_html = _stylize(body_html)

    schema_blocks = schema_jsonld(fm)

    # The canonical pulls from the breadcrumb's last item, which is now an
    # absolute URL (fix 8). Use as-is.
    bc = (fm.get("schema_data") or {}).get("breadcrumb", {})
    last_item = ""
    items_for_canonical = bc.get("itemListElement", []) if isinstance(bc, dict) else []
    if items_for_canonical:
        last = items_for_canonical[-1]
        last_item = last.get("item", "") if isinstance(last, dict) else ""
    canonical = last_item if last_item.startswith("http") else f"https://midwestcncservices.com{last_item or '/'}"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(meta_desc)}">
<link rel="canonical" href="{html.escape(canonical)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(meta_desc)}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap">
<style>
{CSS}</style>
{schema_blocks}
</head>
<body>
<header class="site-header">
  <a class="brand" href="/">
    <img src="/assets/images/logos/midwest-cnc-logo.png" alt="Midwest CNC Services" height="36">
  </a>
  <nav>
    <a href="/repairs/">Repairs</a>
    <a href="/spindle-grinding/">Spindle Grinding</a>
    <a href="/way-covers/">Way Covers</a>
    <a href="/service-area/">Service Area</a>
    <a href="/get-a-quote/">Get a Quote</a>
  </nav>
</header>
{crumbs_html}
<main>
<article>
{body_html}
</article>
</main>
<footer class="site-footer">
  <p>Midwest CNC Services · 319-610-4341 · Waterloo, Iowa</p>
  <p>Serving shops across Iowa, Illinois, Minnesota, Wisconsin, Nebraska, Missouri, and Texas.</p>
</footer>
<div class="mobile-cta-bar" role="region" aria-label="Quick contact">
  <a class="mcta-phone" href="tel:+13196104341">☎ 319-610-4341</a>
  <a class="mcta-quote" href="#quote">Get a Quote</a>
</div>
</body>
</html>
"""


def _stylize(body_html):
    """Light post-processing of the converted markdown:
       - First <p><em>…</em></p> becomes <p class="eyebrow">…</p>
       - Paragraphs that consist only of CTA links + bullet become a CTA row
       - The italic quote-form placeholder becomes a styled placeholder
    """
    # Placeholder replacements first — convert the italicized build-time
    # placeholders into styled divs before the eyebrow rule runs. Otherwise
    # the eyebrow regex (which matches any leading <p><em>…</em></p>) could
    # accidentally claim the placeholder paragraph on pages that don't emit
    # a real eyebrow line (Amada, Trumpf).
    body_html = re.sub(
        r'<p><em>Quote form rendered here at build time\.</em></p>',
        '<div class="quote-form-placeholder">Quote form rendered here at build time.</div>',
        body_html,
    )
    body_html = re.sub(
        r'<p><em>Rendered by the blog teaser component at build time\.</em></p>',
        '<div class="quote-form-placeholder">Blog teaser block rendered here at build time.</div>',
        body_html,
    )

    # Eyebrow paragraph — only when an <p><em>...</em></p> is the FIRST tag
    # in the article body. Anchors to start-of-string so pages without an
    # eyebrow line (Amada, Trumpf) get no .eyebrow at all.
    body_html = re.sub(
        r'\A(\s*)<p><em>([^<]+)</em></p>',
        r'\1<p class="eyebrow">\2</p>',
        body_html,
        count=1,
    )

    # CTA rows: paragraphs that are a "Get a Quote" link followed optionally
    # by a phone link separated by " · "
    def cta_row(m):
        text = m.group(1)
        text = re.sub(
            r'<a href="#quote">Get a Quote</a>',
            '<a class="cta-button" href="#quote">Get a Quote</a>',
            text,
        )
        text = re.sub(
            r'<a href="tel:\+13196104341">319-610-4341</a>',
            '<a class="cta-phone" href="tel:+13196104341">319-610-4341</a>',
            text,
        )
        return f'<div class="cta-row">{text}</div>'

    body_html = re.sub(
        r'<p>((?:[^<]*<a[^>]*>(?:Get a Quote|319-610-4341)</a>[^<]*)+)</p>',
        cta_row,
        body_html,
    )

    return body_html


# ---------- Driver ----------

def output_path_for(fm):
    """Mirror the canonical URL into the public/ tree as
    public/<canonical-path>/index.html. Falls back to public/<slug>.html
    if the canonical can't be parsed."""
    bc = (fm.get("schema_data") or {}).get("breadcrumb", {})
    items = bc.get("itemListElement", []) if isinstance(bc, dict) else []
    if items and isinstance(items[-1], dict):
        item = items[-1].get("item", "")
        if item.startswith("https://midwestcncservices.com"):
            item = item[len("https://midwestcncservices.com"):]
        item = item.strip("/")
        if item:
            return os.path.join(OUTDIR, item, "index.html")
    slug = fm.get("slug", "page")
    return os.path.join(OUTDIR, f"{slug}.html")


def _resolve_targets(args):
    """When args are given, resolve each to a markdown path. Accepts either
    a slug (looked up in every CONTENT_DIRS, returning all matches) or an
    explicit path. When no args, return every .md across all three dirs."""
    md_paths = []
    if args:
        for arg in args:
            if os.path.isabs(arg) or os.path.sep in arg:
                if arg.endswith(".md") and os.path.exists(arg):
                    md_paths.append(arg)
                continue
            # Treat as slug — find in any content dir
            for d in CONTENT_DIRS:
                p = os.path.join(d, f"{arg}.md")
                if os.path.exists(p):
                    md_paths.append(p)
    else:
        for d in CONTENT_DIRS:
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                if f.endswith(".md"):
                    md_paths.append(os.path.join(d, f))
    return md_paths


def _kind_for_path(md_path):
    """Tag the source dir for nicer reporting."""
    for d in CONTENT_DIRS:
        if md_path.startswith(d + os.sep):
            return os.path.basename(d)
    return "?"


def main():
    md_paths = _resolve_targets(sys.argv[1:])
    written = 0
    for md_path in md_paths:
        src = open(md_path).read()
        fm, body = parse_frontmatter(src)
        body_html = md_body_to_html(body)
        page_html = render_html(fm, body_html)
        out_path = output_path_for(fm)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            f.write(page_html)
        written += 1
        size_kb = max(1, os.path.getsize(out_path) // 1024)
        rel = os.path.relpath(out_path, REPO)
        kind = _kind_for_path(md_path)
        draft = " [DRAFT]" if fm.get("draft") else ""
        print(f"  ✓ [{kind:<16}] {fm.get('slug',''):<16} → {rel}  ({size_kb} KB){draft}")
    print(f"\n  Total written: {written}")


if __name__ == "__main__":
    main()
