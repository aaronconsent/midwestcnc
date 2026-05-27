# Step 1 — Research

Produce a research brief for the cluster article below. The brief is
consumed by the outline step and should be opinionated, not exhaustive.

---

## Inputs

- **Pillar**: {{pillar_title}} ({{pillar_slug}})
- **Article slug**: {{article_slug}}
- **Working title**: {{article_title}}
- **Target query**: {{target_query}}
- **Search intent**: {{intent}}
- **Target word count**: {{target_words}}
- **Required proprietary signal**: {{signal_list}}

---

## Tasks

1. **Dominant intent.** What is the searcher actually trying to do?
   Diagnose a symptom? Make a buy/repair decision? Understand a
   technical concept? State it in one sentence.

2. **Top-10 SERP shape.** Describe the shape of the content that
   currently ranks for the target query. Examples:
   - "Mostly OEM blog posts, all definitional, none with measurement
     procedures."
   - "Forum threads with conflicting advice, no structured guidance."
   - "Equipment-broker listicles, no diagnostic depth."

   You do not need to scrape the SERP — describe the shape from prior
   knowledge of the topic landscape. If you genuinely don't know, say so.

3. **Missing angles.** What's NOT on page 1? Concrete examples:
   - "No one shows the actual measurement procedure."
   - "Every article assumes you've already decided to repair — no one
     covers the rebuild-vs-replace economics."
   - "All the content is OEM-aligned; no one talks about the legacy
     fleet that's actually in shops."

   This is where Midwest CNC's content earns its place on page 1.

4. **Entity inventory.** List the named entities (people, places,
   products, brands, control systems, model numbers, specifications)
   that should appear in-body. Be generous — LLMs cite entity-rich
   content preferentially.

5. **Schema patterns.** What schema.org types do the top-10 use?
   Article, BlogPosting, HowTo, FAQPage, TechArticle. Recommend the
   right pattern for this piece.

6. **Quotable openers.** For each likely H2, draft a one-sentence
   definitional opener that an AI Overview would quote verbatim.

---

## Output format

```markdown
# Research Brief — {{article_slug}}

## Dominant intent
[one sentence]

## SERP shape
[2-4 sentences]

## Missing angles
- [angle 1]
- [angle 2]
- [angle 3]

## Entity inventory
- People: [Ken, Aaron, ...]
- Places: [Waterloo, ...]
- Products / controls / brands: [Mazatrol Matrix, Fanuc 30i, ...]
- Specifications / numbers: [microns, RPM, ...]

## Schema recommendation
Primary: [Article / BlogPosting / HowTo / TechArticle]
Secondary: [Service / LocalBusiness]
Rationale: [one sentence]

## Quotable openers per H2
H2: [working H2 title]
  → [one-sentence definitional opener]
```

Stop. Do not produce the outline. The outline step uses this brief.
