# Step 5 — Schema generation

Generate JSON-LD schema for the article. The generator script handles
this automatically based on article frontmatter — this prompt is the
spec the generator implements.

---

## Inputs

- **Final article markdown** (with frontmatter): {{final_article}}
- **Pillar slug**: {{pillar_slug}}
- **Article slug**: {{article_slug}}
- **Canonical URL**: `https://midwestcncservices.com/insights/{{pillar_slug}}/{{article_slug}}/`

---

## Schema blocks to emit

The generator emits these as separate `<script type="application/ld+json">`
tags, in order:

### 1. BreadcrumbList

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://midwestcncservices.com/" },
    { "@type": "ListItem", "position": 2, "name": "Insights", "item": "https://midwestcncservices.com/insights/" },
    { "@type": "ListItem", "position": 3, "name": "[pillar title]", "item": "https://midwestcncservices.com/insights/{{pillar_slug}}/" },
    { "@type": "ListItem", "position": 4, "name": "[article title]" }
  ]
}
```

### 2. Article + BlogPosting

```json
{
  "@context": "https://schema.org",
  "@type": ["Article", "BlogPosting"],
  "headline": "[article title]",
  "description": "[meta description from frontmatter]",
  "image": "[hero image URL, absolute]",
  "datePublished": "[YYYY-MM-DD from frontmatter]",
  "dateModified": "[YYYY-MM-DD — same as published until updated]",
  "author": {
    "@type": "Person",
    "name": "Ken",
    "jobTitle": "Shop owner",
    "worksFor": { "@id": "https://midwestcncservices.com/#org" }
  },
  "publisher": { "@id": "https://midwestcncservices.com/#org" },
  "mainEntityOfPage": "[canonical URL]",
  "articleSection": "[pillar title]",
  "keywords": "[target_query + 3-4 related entities from the article]",
  "wordCount": [int],
  "inLanguage": "en-US"
}
```

### 3. LocalBusiness reference

Reuses the existing site-wide LocalBusiness `@id` (`#org`). No new
block — the Article references it via `worksFor` and `publisher`.

### 4. FAQPage (conditional)

If the article body includes a `<details><summary>` accordion block of
FAQs, emit an FAQPage schema mapping each Q (summary text) to its A
(the details body). The generator detects this automatically.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    { "@type": "Question", "name": "[Q]", "acceptedAnswer": { "@type": "Answer", "text": "[A as plaintext]" } }
  ]
}
```

### 5. Service (conditional)

If the pillar is `spindle-diagnostics`, `cnc-control-systems`, or
`way-covers-engineering` (the service-line-aligned pillars), emit a
Service schema referencing the corresponding service URL.

```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "[service name]",
  "serviceType": "[service type]",
  "provider": { "@id": "https://midwestcncservices.com/#org" },
  "url": "https://midwestcncservices.com/[service-path]/"
}
```

---

## Validation

The generator runs the emitted JSON through `insights_validators.py`'s
schema gate, which checks:
- Valid JSON
- Required fields present per type
- URLs are absolute
- Dates in YYYY-MM-DD
- No invented @type values

A failed schema gate routes the article back to step 5 (regenerate) or
step 3 (if frontmatter is missing data).

---

## Output

This step is normally **executed by the generator**, not by Claude.
The prompt exists as a spec for the generator's behavior. If for some
reason the schema must be authored by hand, follow the exact templates
above and return as a fenced JSON code block per schema type.
