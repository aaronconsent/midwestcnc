# Insights Engine — Architecture

Publishing engine with a quality gate for `/insights/` (the Midwest CNC
technical blog). Adapted from the strategic pattern, grounded in this
business's reality and editorial constraints.

The single mental shift: this is **not an auto-blog**. It is a
publishing engine with a quality gate. Google's March 2024 scaled-content
spam update is the boundary condition — the violation isn't AI authorship,
it's publishing at volume without a human-grade reason for each piece to
exist. The gate enforces that reason.

---

## Pillars (5 — locked)

Technical-depth set, chosen for defensible territory adjacent to the
existing hub-and-spoke architecture. Each pillar consolidates ranking
signal as its cluster matures and reinforces the existing brand pages
through internal links.

1. **Spindle Diagnostics & Repair Decisions** —
   Vibration analysis, bearing failure modes, runout, balance, sound
   symptoms, rebuild-vs-replace economics. Reinforces
   `/spindle-grinding/{brand}-spindle-repair/`.

2. **CNC Control Systems (Mazatrol, Fanuc, Siemens, Heidenhain, OSP)** —
   Alarm-code interpretation, retrofit decisions, legacy control
   support, parts availability per generation, control-vs-mechanical
   diagnostic logic. Reinforces every `/repairs/{brand}-cnc-machine-repair/{control-spoke}/`.

3. **Way Covers Engineering** —
   Telescoping vs bellows vs roll-up, measuring for replacement,
   mounting hardware availability, OEM-spec vs custom fabrication,
   pallet-changer interface sealing. Reinforces `/way-covers/`.

4. **Field Service & Logistics (Midwest)** —
   Drive-time radius reality, shipping for bench rebuilds, on-site
   diagnostic decisions, when the machine comes to Waterloo vs when
   we go to the shop. Reinforces `/service-area/{state}/` and `/service-area/{city}/`.

5. **Buying & Owning Used CNC** —
   Inspection checklists, common failure modes by age/generation,
   total cost of ownership, retrofit ROI for legacy iron, parts
   sourcing for discontinued machines. Reinforces every brand hub
   that has legacy-era spokes.

---

## URL structure

```
/insights/                                 — pillar landing index
/insights/{pillar-slug}/                   — pillar page (consolidates cluster)
/insights/{pillar-slug}/{article-slug}/    — cluster article
```

Pillar slugs:
- `spindle-diagnostics`
- `cnc-control-systems`
- `way-covers-engineering`
- `field-service-logistics`
- `buying-owning-used-cnc`

---

## The 6-step prompt chain

Drafting is *me-in-the-loop*: the Python pipeline runs every step
except the actual writing. For step 3 (draft), the pipeline emits a
complete, context-rich prompt to be pasted into a fresh Claude session.
The draft returns as markdown and re-enters the pipeline.

All step prompts live under `prompts/insights/` as markdown templates
with Jinja-style `{{ placeholders }}`.

1. **Research** (`01-research.md`) — given target query + pillar,
   produce: dominant intent, top-10 SERP shapes, missing angles, schema
   patterns competitors use. Output is a research brief.

2. **Outline** (`02-outline.md`) — consume research brief, produce a
   structure that addresses what's NOT on page 1. Pre-selects internal
   link targets from the existing site graph (via
   `insights_link_suggester.py`).

3. **Draft** (`03-draft.md`) — produces the actual article. Hard
   requirements:
   - **Voice**: Ken (shop owner, measured, technically credible, plain
     English, no hype, no exclamation points).
   - **Editorial constraints (claim-audit ban list)** — NO use of
     "photo-verified", "factory-trained", "24/7", "ISO certifications",
     "flat-rate", "transparent pricing", "warranty" (except in ToS),
     "same-day" (except on the Iowa state page).
   - **No fabrication** — every specific claim must be falsifiable.
   - **Proprietary signal**: at least 1 piece of original data, 1
     named-expert quote (Ken or Aaron), 1 real-job reference.
   - **Named entities**: brands, control systems, cities, model numbers
     mentioned in-body where relevant (LLMs preferentially cite
     entity-rich content).
   - **Quotable definitional opener** per major section (GEO).

4. **GEO rewrite** (`04-geo.md`) — rewrites the intro and key sections
   for AI Overviews / ChatGPT / Perplexity / Gemini citation:
   definitional sentences, statistics with attribution, key-takeaways
   block at top of article.

5. **Schema** (`05-schema.md`) — generates `Article` + `BlogPosting` +
   relevant `Service` or `LocalBusiness` schema. Validated by
   `insights_validators.py`.

6. **Human gate** (`06-human-gate.md`) — 60-second checklist for the
   final reviewer (you). Non-negotiable.

---

## Quality gates (block publish)

Implemented in `scripts/insights_validators.py`. Every draft is run
through these before it can be promoted from `src/content/insights/_drafts/`
to `src/content/insights/{pillar-slug}/`.

| Gate | Threshold | Why |
| --- | --- | --- |
| Word count — cluster | ≥ 1,200 | Floor, not target. Below this, the post is thin. |
| Word count — pillar | ≥ 2,500 | Pillar pages need to consolidate cluster signal. |
| Flesch reading ease | ≥ 60 | Plain-English voice gate. |
| Cosine similarity to existing posts | ≤ 0.30 | Prevents internal cannibalization (TF-IDF MVP; embeddings later). |
| Proprietary signal | ≥ 3 of: original data / real photo / named-expert quote / real-job reference / falsifiable claim | The "human-grade reason for this piece to exist" gate. |
| Schema | Validates against schema.org | Required for AI Overviews surfacing. |
| Claim-audit ban list | 0 unauthorized hits | Existing site-wide rule, extended to insights. |
| Falsifiable-claim heuristic | ≥ 1 specific number or named entity in first 300 words | Anti-generic check. |

A failed gate routes the draft back to step 3 or step 4 with the
specific failure noted. The draft does not enter the publish queue.

---

## Internal-link automation

`scripts/insights_link_suggester.py` builds a TF-IDF index over:
- All existing brand-hub + spoke pages
- All existing service-area pages
- All existing insights pillar + cluster pages

Given a new draft, it returns the 5-8 most semantically related
existing pages with suggested anchor text. The draft step prompt
injects these as "internal link targets to weave in-body."

This is the **single mechanism most responsible for compounding ranking
gains** — orphan posts dilute signal; clustered posts compound.

v1 uses scikit-learn TF-IDF. v2 will swap in dense-vector embeddings
(sentence-transformers locally or an API), same interface.

---

## Publish cadence

2-4 high-signal articles per week, ceiling. Not a floor. The gate
will reject everything if proprietary signal is thin; that's working
as intended. Sustainable cadence is determined by how much real shop
knowledge can be captured per week, not by how fast text can be
generated.

---

## Measurement loop

After 60 days post-publish, the article's performance feeds back into
the next round of cluster planning:
- **Ranked + cited in AI Overviews** → mark as compounding asset; consider
  deepening with a follow-up cluster article.
- **Ranked, no citations** → keep; maybe rewrite intro for stronger
  definitional opener.
- **Did not rank** → deepen (more proprietary data, more depth) or
  prune. Google's site-wide helpful-content signal penalizes dead
  weight; a never-ranked article should not sit there indefinitely.

Wiring GSC + GA4 into a measurement script is a follow-up phase; the
manual review form lives in `docs/insights-measurement.md` (TODO).

---

## AI Overview / LLM citation optimization (GEO)

Baked into the draft + GEO steps:
- **Lead each H2/H3 with a clean one-sentence answer** before
  elaborating.
- **Named entities aggressively**: people (Ken, Aaron), places
  (Waterloo, Cedar Valley, the 7 states, specific cities), products
  (Mazak Integrex, Okuma OSP-P300, Heidenhain TNC, etc.), control
  systems by name and generation.
- **Key Takeaways block** at the top of every article — bullet list,
  3-5 items, each one self-contained and quote-friendly.
- **Statistics with source attribution** when claiming numbers.
- **llms.txt** already exists at root; updated to surface the
  `/insights/` index.
- **GPTBot / ClaudeBot / PerplexityBot** are not blocked in robots.txt
  (confirmed; do not block).

---

## What this engine deliberately does NOT do

- It does not auto-publish. Every article passes the human gate.
- It does not generate at volume. Output is rate-limited by available
  proprietary signal, not by how fast the model can write.
- It does not scrape competitors. Research-step prompts surface SERP
  shape from your own browser inspection, not automated scraping.
- It does not optimize for blue-link CTR at the expense of GEO. Both
  matter; GEO is harder to retrofit.
- It does not generate keyword-spreadsheet articles. Every cluster
  article exists because it answers a real question from a real shop
  owner.

---

## Files

```
docs/insights-engine.md                — this document
src/data/insights-pillars.json         — pillar + cluster definitions
prompts/insights/                      — 6-step prompt templates
src/content/insights/_drafts/          — drafts awaiting gate
src/content/insights/{pillar}/         — published markdown sources
scripts/insights_validators.py         — quality gate
scripts/insights_link_suggester.py     — TF-IDF internal-link suggester
scripts/generate_insights_pages.py     — pillar + article page renderer
public/insights/                       — generated HTML (gitignored after MVP)
```
