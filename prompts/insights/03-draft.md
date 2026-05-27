# Step 3 — Draft

Write the full article based on the outline. This is the only step that
produces actual prose.

---

## Inputs

- **Outline**: {{outline}}
- **Article slug**: {{article_slug}}
- **Target word count**: {{target_words}} (floor, not target — go over
  if the topic warrants it; do not pad)
- **Internal-link targets (from suggester)**:
{{internal_link_targets}}
- **Proprietary signal pieces** (must appear in-body):
{{signal_list}}

---

## Hard requirements

1. **Voice**: Ken's voice. Measured, technically credible, plain
   English, no hype, no exclamation points. See shared context.

2. **Editorial constraints**: claim-audit ban list applies. See shared
   context. No "photo-verified", "factory-trained", "24/7", "ISO
   certifications", "flat-rate", "transparent pricing", "warranty"
   (outside ToS), "same-day" (outside Iowa).

3. **Internal links**: weave the suggester's 5-8 targets into the body
   as in-context anchor text, not as a "Related Posts" footer. The
   anchor text should be descriptive — say what the linked page is
   about, not "click here" or "learn more."

4. **Proprietary signal**: every signal piece listed above must appear
   in-body. Each one is the reason this article exists; if you can't
   place it naturally, the article isn't ready.

5. **Named entities**: brands, control systems, cities, model numbers,
   specifications named where relevant. LLMs cite entity-rich content
   preferentially.

6. **Quotable structure**:
   - Article opens with the **Key Takeaways block** from the outline
     (markdown bullet list, no heading change).
   - Each H2 opens with its **definitional opener sentence**, then
     elaborates.
   - Each H2 is independently quotable — an AI Overview could lift one
     section and have it stand alone.

7. **Markdown shape**:
   - Use `## H2` and `### H3` heading structure.
   - Use `<details><summary>` for any FAQ-shaped Q&A within the body.
   - Use numbered lists for procedures and decision trees.
   - Use tables when comparing options (markdown pipe tables).
   - Inline `[anchor text](/url/)` for internal links — relative URLs,
     trailing slash.
   - No HTML beyond `<details><summary>`.

8. **Length**: meet the target word count as a floor. Do not pad.
   If you hit the count at the natural end of the argument, stop. If
   the topic genuinely warrants more, go over.

9. **Closing**: short closing paragraph that names the scenario where
   readers should reach out, then a single CTA sentence linking to
   `/get-a-quote/`.

---

## Output format

```markdown
---
title: "[Final H1 from outline]"
slug: "{{article_slug}}"
pillar: "{{pillar_slug}}"
target_query: "{{target_query}}"
description: "[Meta description from outline]"
author: "Ken — Midwest CNC Services"
date: "[YYYY-MM-DD]"
---

[Optional eyebrow paragraph — one short sentence framing the piece, if
helpful. Skip if the H1 alone is enough.]

## Key Takeaways

- [bullet 1]
- [bullet 2]
- [bullet 3]
- (optional 4, 5)

[Opening paragraph — the lede. State what this piece is and isn't.
Sets up the rest.]

## [H2 #1 — definitional opener as a paragraph, NOT a heading prefix]

[Body of section 1, including in-context internal links and the
assigned proprietary signal.]

### [H3 sub-section if used]

[Body.]

## [H2 #2]

[...]

## [Closing H2 — e.g., "When to bring this work to us"]

[Scenario-specific framing.]

[Single CTA sentence ending with a link to `/get-a-quote/`.]
```

Stop at the end of the draft. The GEO step will refine.
