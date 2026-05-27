# Step 2 — Outline

Produce a complete outline for the article based on the research brief
and the internal-link targets from the suggester.

---

## Inputs

- **Research brief**: {{research_brief}}
- **Article slug**: {{article_slug}}
- **Working title**: {{article_title}}
- **Target word count**: {{target_words}}
- **Internal-link targets (from suggester)**:
{{internal_link_targets}}

Each link target is a tuple: `(URL, suggested-anchor, relevance-rank)`.

---

## Tasks

1. **Final title and meta description.** The working title is a
   placeholder. Replace it with the actual H1. Write a 145-160 char
   meta description that includes the target query and a definitional
   opener.

2. **Key Takeaways block.** Draft 3-5 bullets that go at the very top
   of the article. Each bullet must be:
   - Self-contained (readable without the rest of the article).
   - Quote-friendly (an AI Overview could lift it verbatim).
   - Specific (a number, named entity, or falsifiable claim where
     possible).

3. **H2 structure.** Pick 4-7 H2 sections that address the missing
   angles from the research brief. Each H2 gets:
   - The quotable definitional opener (already drafted in the brief).
   - 2-3 H3 sub-points (or 2-3 paragraph topics).
   - The internal links that should land in this section (from the
     suggester list above).
   - The proprietary signal that should appear in this section
     (which piece of original data / quote / real-job reference).

4. **Closing section.** Not a hype CTA. Either:
   - A useful summary that reinforces the Key Takeaways.
   - A "When to call us" framing that names the specific scenario.
   - A "What to do next" with a concrete next step.

   Plus the standard quote-form link to `/get-a-quote/` for the CTA.

---

## Output format

```markdown
# Outline — {{article_slug}}

## Final title
[H1]

## Meta description
[145-160 chars]

## Key Takeaways
- [bullet 1 — specific, quotable, falsifiable]
- [bullet 2]
- [bullet 3]
- (optional 4, 5)

## H2 #1: [title]
**Quotable opener**: [one sentence]
**Content**:
- [paragraph topic 1]
- [paragraph topic 2]
- [paragraph topic 3]
**Internal links to land here**:
- [URL] — anchor: "[text]"
**Proprietary signal**:
- [which piece appears here]

## H2 #2: [title]
[same structure]

[...]

## Closing
[Summary / when-to-call framing / next-step paragraph]
```

Stop. Do not write the article. The draft step uses this outline.
