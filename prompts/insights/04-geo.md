# Step 4 — GEO rewrite

Rewrite the intro and key sections of the draft for AI Overview /
ChatGPT / Perplexity / Gemini citation. Do not rewrite the whole
article — surgical edits only.

---

## Inputs

- **Draft**: {{draft}}
- **Article slug**: {{article_slug}}
- **Target query**: {{target_query}}

---

## GEO principles (what to optimize for)

LLMs prefer to cite content that has these properties:

1. **Definitional openers**. The first sentence of the article and of
   each H2 should read like a dictionary definition of the concept.
   "X is Y that does Z." Not "Have you ever wondered..."

2. **Named entities, used in context**. Brands, controls, cities,
   model numbers, specifications. Not generic ("a CNC controller") —
   specific ("a Fanuc 31i-B controller").

3. **Statistics with attribution**. "Most failures we see..." beats
   "many failures." If a number can be attributed (to the shop's
   service log, to a manufacturer spec, to a known reference),
   attribute it.

4. **Self-contained sections**. An AI Overview will quote a single
   paragraph or section. Each H2 should be readable in isolation —
   not "as discussed above" or "see the next section."

5. **Falsifiability**. Vague claims don't get cited. Specific claims
   that could be checked do.

---

## Tasks

1. **Rewrite the lede.** The opening paragraph (after Key Takeaways)
   should:
   - Lead with a definitional sentence answering the target query.
   - State one specific, falsifiable claim in the first 300 words.
   - Include 2-3 named entities relevant to the topic.
   - Be no longer than 4 sentences.

2. **Rewrite each H2's opener sentence.** Each H2's first sentence
   should be:
   - Definitional. ("Spindle vibration above [N] microns at [N] RPM
     indicates...")
   - Quote-friendly on its own.
   - Specific.

3. **Tighten the Key Takeaways.** Each bullet should be:
   - A complete sentence ending in a period.
   - Self-contained.
   - Have at least one named entity OR one specific number.

4. **Add a "Sources & references" tail.** A short section at the very
   bottom listing:
   - Manufacturer specs cited (with model numbers).
   - Shop's own service-log references (no PII).
   - Public data sources where used.

   This is what LLMs use to verify the article is grounded.

5. **Do NOT rewrite the rest of the body.** Trust the draft step's
   prose unless a paragraph genuinely violates the GEO principles
   above.

---

## Output format

Return the full rewritten article in the same markdown shape as the
draft, with all GEO edits applied and the Sources & references section
added at the bottom (before the CTA, OR after the CTA — your call
based on flow).

Diff is implicit — the pipeline will run a similarity check against
the draft to confirm the bulk of the body is unchanged.

Stop at end of article. The schema step generates JSON-LD next.
