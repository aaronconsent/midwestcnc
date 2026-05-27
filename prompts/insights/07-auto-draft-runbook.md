# Auto-Draft Runbook

Self-contained instructions for an autonomous Claude session to produce
one drafted Insights article per run, pass the quality gates, and open
a PR. Triggered by `CronCreate` (built-in) or a GitHub Actions workflow
(production).

The session has no memory of prior conversations. Treat this runbook as
the complete spec.

---

## Working directory

```bash
cd /Users/aaronphillips/midwestcnc
```

If that directory doesn't exist (running in CI), the workflow checks
out the repo first; use the checkout root.

---

## Pre-flight checks

Before doing any work, verify:

1. **Repo is on `main`, clean, and current.**
   ```bash
   git fetch origin main
   git checkout main
   git reset --hard origin/main
   ```
   If anything fails (network, merge conflict, dirty tree), STOP and
   report the error in your final message. Do not try to "clean up."

2. **Required scripts exist.**
   ```bash
   test -x scripts/insights_schedule.py \
     && test -x scripts/insights_link_suggester.py \
     && test -x scripts/insights_validators.py \
     && test -x scripts/generate_insights_pages.py
   ```
   If any are missing, STOP and report.

---

## Step 1: pick this run's article

```bash
python3 scripts/insights_schedule.py status
```

Look at "Next 14 days." Pick the **earliest** scheduled article that:

- Is **not** already in `src/content/insights/{pillar}/` (published).
- Is **not** already in `src/content/insights/_drafts/` (drafted but
  not promoted).
- Does **not** already have a remote branch named `auto-draft/{slug}`.
  Check via `git ls-remote --heads origin auto-draft/{slug}`.

If no candidate exists (nothing due in 14 days, or all candidates are
already drafted/published), report "Nothing to draft this run" and stop.

Save the picked slug + its pillar slug + its title + its target_query +
its `signal_signature` requirements (from `src/data/insights-pillars.json`)
as variables. You'll need them downstream.

---

## Step 2: gather internal-link targets

```bash
python3 scripts/insights_link_suggester.py \
  --query "<article title + target query>" \
  --top-k 8 --json
```

The output is a JSON array of `{url, suggested_anchor, score, rank}`
objects. Save it. You'll weave 5-8 of these as in-body anchor links.

---

## Step 3: draft the article

Follow `prompts/insights/03-draft.md` for the full draft requirements.
Hard requirements summarized:

### Voice (non-negotiable)
- Ken's voice. Measured, technically credible, plain English.
- No exclamation points. Anywhere.
- No hype words: premier, world-class, best-in-class, leading,
  unparalleled, cutting-edge.

### Editorial constraints (claim-audit ban list)
NONE of these phrases anywhere in the article:
- "photo-verified", "factory-trained", "factory-certified"
- "24/7", "ISO 9001", "ISO certif*"
- "flat-rate", "transparent pricing"
- "guaranteed", "warranty"
- "same-day"

### Structure
- Frontmatter with: `title`, `slug`, `pillar`, `target_query`,
  `description` (145-160 chars), `author: "Ken — Midwest CNC Services"`,
  `date: "<today's date YYYY-MM-DD>"`, `signal_signature: "<phrase1; phrase2; ...>"`.
- `## Key Takeaways` H2 with 3-5 bullet points (each ending with a period,
  each containing at least one specific number or named entity).
- A lede paragraph (4 sentences max) after Key Takeaways. First 300
  words of the article must contain at least one specific number AND
  at least 2 named entities (brand names, model numbers, places).
- 4-6 content H2s. Each opens with a definitional sentence — NEVER a
  question, NEVER "Have you ever..." / "Imagine..." / "Let's...".
- A `## Sources & references` H2 listing what backs the article.
- A closing H2 like `## When to bring this work to us` with a
  CTA link to `/get-a-quote/`.

### Length
- Cluster articles: 1,200-2,000 words. Aim for the slug's
  `target_words` value from the pillar JSON.

### Internal links
- 5-8 in-body links from the link suggester's results.
- Use descriptive anchor text, not "click here" or "learn more".
- Weave them in-context, not as a "Related Posts" footer.

### Proprietary signal
- The `signal_signature` field in frontmatter MUST list 5+ short
  phrases that appear LITERALLY in the body text.
- Use phrases that are specific enough to be falsifiable. Pick from
  named entities, specific numbers, or technical patterns referenced
  in the article.

### No placeholders
- No `[TODO]`, `[FIXME]`, `[Ken to confirm]`, `<placeholder>`, etc.
- All specific claims hedged honestly. Example: "$35,000 to $55,000 in
  recent quoting we have seen" is acceptable; "$45,000" without hedging
  is fabrication unless sourced from real shop data.

### Hedging language that is acceptable
- "we have seen", "we typically see"
- "in the range of X to Y"
- "usually", "most often", "in our service log"
- "varies by platform" / "varies by machine"
- "depending on scope" / "depending on what's failing"

Write the full article to:

```
src/content/insights/_drafts/<slug>.md
```

---

## Step 4: validate

```bash
python3 scripts/insights_validators.py src/content/insights/_drafts/<slug>.md
```

All 11 gates must pass:
1. word_count (≥1200 for cluster, ≥2500 for pillar)
2. flesch (≥60)
3. ban_list (0 hits)
4. hype_words (0 hits)
5. exclamations (0)
6. key_takeaways (3-5 bullets)
7. definitional_h2 (every H2 opens definitionally)
8. internal_links (≥3 in-body)
9. proprietary_signal (signal_signature phrases must appear in body)
10. first_300_words (specific number + ≥2 entities)
11. cosine_similarity (max_cosine ≤ 0.30 against existing corpus)

If FAIL:
- Read the specific gate failures.
- Rewrite the article addressing each one. Common fixes:
  - Flesch too low → shorter sentences, fewer compound clauses
  - Cosine too high → less repetition of brand names, more
    differentiation in content
  - Definitional H2 fail → rewrite the first sentence of the
    flagged H2 to be a statement, not a question
  - Proprietary signal fail → either add the declared phrases
    verbatim into the body, OR update `signal_signature` to match
    what's actually in the body (only if the actual content is
    still specific and falsifiable)
- Re-run the validator.
- Up to **3 attempts total**. After the 3rd failure, STOP. Save the
  failure log to `src/content/insights/_drafts/<slug>.review.md` and
  report in your final message that the article needs human review.

---

## Step 5: promote on pass

```bash
python3 scripts/insights_validators.py --promote \
  src/content/insights/_drafts/<slug>.md
```

This moves the draft to `src/content/insights/<pillar>/<slug>.md`.

---

## Step 6: regenerate pages + audit

```bash
python3 scripts/generate_insights_pages.py
python3 scripts/insights_schedule.py report
python3 scripts/generate_site_shell.py
```

Run a final audit:

```bash
python3 scripts/launch_audit.py
```

Confirm `Broken links: 0`. The pre-existing claim-audit hit (1 unauthorized
same-day on the service-area hub) is expected — do not try to fix it.
Same with the 165 schema gaps. These are pre-existing.

If broken links > 0, STOP. Save the audit output as the final message
and explain you couldn't ship because of broken-link regression.

---

## Step 7: branch + commit + push

```bash
git checkout -b auto-draft/<slug>
git add -A
git commit -m "Auto-drafted: <article title>

Generated by the weekly auto-draft runbook
(prompts/insights/07-auto-draft-runbook.md).

Gate results: all 11 passed.
Word count: <wc>. Flesch: <score>. Cosine: <score>.

This is a v1 draft using publicly defensible facts. A v2 edit
pass with Ken's specific shop data (real pricing ranges, named
customer scenarios, bench photos) will deepen the piece.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
git push -u origin auto-draft/<slug>
```

DO NOT merge. DO NOT push to main. Only push the feature branch.

---

## Step 8: final report

In your final message, include exactly these sections:

```
## Auto-draft complete

**Article:** <title>
**Slug:** <slug>
**Pillar:** <pillar slug>
**Branch:** auto-draft/<slug>

## Quality gates (all 11 passed)
- word_count: <words>
- flesch: <score>
- cosine_similarity: <score> vs <comparison>
- proprietary_signal: <n> phrases matched
[... etc, one line per gate]

## Open the PR
https://github.com/aaronconsent/midwestcnc/pull/new/auto-draft/<slug>

## What's still ahead
- 60-second human gate review (read the draft, check voice, check claims)
- Merge the PR — Cloudflare Pages deploys within ~2 min
- Optional v2 edit pass with Ken's specific data
```

---

## Failure modes

**Repo not clean / not on main:** STOP. Report the git state. Do not
try to recover.

**Validator fails 3x:** STOP. Save `.review.md`. Report which gates
failed and what was tried.

**Cosine gate fails repeatedly:** the article is too close to an
existing page. Pick a DIFFERENT slug from the schedule and skip this one.
Do not weaken signal_signature to bypass.

**Network failure on push:** STOP. Leave the commit on the local branch.
Report so the user can push manually.

**Multiple candidate slugs but all are too similar to existing content:**
this is unlikely but if it happens, STOP. Report. The schedule may need
manual curation.

---

## What this runbook deliberately does NOT do

- It does not modify `src/data/insights-pillars.json` beyond the
  publish_date that gets stamped on promotion (handled inside the
  schedule script).
- It does not merge PRs.
- It does not push to main.
- It does not skip the human gate review (the PR open IS the human
  gate handoff).
- It does not generate multiple articles per run. One per fire.
