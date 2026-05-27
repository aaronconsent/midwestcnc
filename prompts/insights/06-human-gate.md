# Step 6 — Human gate (60-second review)

The final, non-negotiable step. Before any article is promoted from
`src/content/insights/_drafts/` to `src/content/insights/{pillar}/`,
a human (Aaron, or a delegated VA) runs this checklist.

This step is **never automated**. It is the difference between
scaling and getting deindexed.

---

## Checklist (60 seconds, in this order)

### Voice (15 seconds)

- [ ] Does it sound like Ken talking? (Not a marketing voice, not a
      generic AI voice.)
- [ ] No exclamation points anywhere.
- [ ] No hype words ("premier", "leading", "world-class", "trusted",
      "expert" as self-adjectives).
- [ ] No "Have you ever wondered..." or similar manipulative openers.

### Editorial constraints (15 seconds)

- [ ] No banned phrases — search the article for: "photo-verified",
      "factory-trained", "factory-certified", "24/7", "ISO",
      "flat-rate", "transparent pricing", "guaranteed", "warranty"
      (unless ToS quote), "same-day" (unless Iowa-scoped).
- [ ] Named manufacturers framed as **regional context**, not as
      customers.
- [ ] No fabricated specifics — every number is either sourced or
      hedged appropriately.

### Substance (20 seconds)

- [ ] Would Ken roll his eyes at any specific claim? (If yes, fix it.)
- [ ] Is there at least one specific, falsifiable claim in the first
      300 words?
- [ ] Are all proprietary signal pieces present (Ken/Aaron quote,
      real-job reference, original data point)?
- [ ] Do the internal links land in-context (not as a "Related Posts"
      footer)?

### GEO / quotability (10 seconds)

- [ ] Key Takeaways block at the top.
- [ ] Each H2 opens with a definitional sentence.
- [ ] Sources & references tail present.

---

## Outcomes

- **All boxes checked** → Promote draft to `src/content/insights/{pillar}/`.
  Run `python3 scripts/generate_insights_pages.py` to render. Commit
  and push.

- **Any box unchecked** → Note the specific failure on the draft
  (filename `{slug}.review.md`) and route the draft back to the
  appropriate step:
  - Voice or hype issues → step 3 (draft) with the specific phrasing.
  - Editorial constraint hits → step 3 with the banned phrase noted.
  - Substance gaps → step 1 (research) if the angle is off, step 3 if
    the angle is right but the proprietary signal isn't there.
  - GEO gaps → step 4.

- **Marginal — close but not quite** → Edit by hand. This is
  acceptable for small fixes. Note the manual edit in the commit
  message so we know what the model is missing.

---

## What this step is NOT

- It is not a copyedit. Typos and minor wording fixes can be done by
  hand without routing back.
- It is not a "vibe check." It is structured failure-mode detection.
- It is not optional. Every article passes through this gate.

---

## Time discipline

If the review is taking longer than 60 seconds, something is wrong with
the draft, not with the review. Send it back.

If the review is taking less than 30 seconds, you are probably skipping
the checklist. Do the checklist.
