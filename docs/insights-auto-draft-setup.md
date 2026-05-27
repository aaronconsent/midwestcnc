# Insights Auto-Draft — Setup

Production weekly automation for the Insights publishing engine. Runs
in GitHub Actions, calls the Anthropic API, opens a feature branch
with a fully-drafted article for review.

---

## What you need to do once

### 1. Add the Anthropic API key as a repo secret

Go to: **Settings → Secrets and variables → Actions → New repository secret**

- **Name:** `ANTHROPIC_API_KEY`
- **Value:** your key from https://console.anthropic.com/settings/keys
  (starts with `sk-ant-...`)

That's the only required secret. The workflow's `GITHUB_TOKEN` is
auto-provided.

### 2. (Optional) Override the model

If you want to use a model other than `claude-opus-4-5`:

Go to: **Settings → Secrets and variables → Actions → Variables → New repository variable**

- **Name:** `ANTHROPIC_MODEL`
- **Value:** the model identifier (e.g. `claude-sonnet-4-5` for cheaper runs)

If you don't set this, the workflow uses `claude-opus-4-5`.

### 3. Verify the workflow is in `main`

The workflow only runs when it's in the default branch. After merging
the `insights-engine` branch to `main`, GitHub will pick up the
`.github/workflows/insights-auto-draft.yml` file automatically.

---

## What runs and when

**Schedule:** every Monday at 13:47 UTC
  - 8:47 AM CDT (summer)
  - 7:47 AM CST (winter)
  - Pre-business-hours Central — article is ready when you start your week

**Manual trigger:** anytime from the Actions tab via `workflow_dispatch`.
You can pass an optional `slug` input to force a specific cluster, or
toggle `dry_run` to test without pushing a branch.

---

## What the workflow does

1. Checks out `main`.
2. Sets up Python 3.11 + installs the `anthropic` SDK.
3. Runs `scripts/insights_auto_draft.py`, which:
   - Picks the earliest scheduled, undrafted article from the next
     21 days.
   - Calls the Anthropic API to draft it, with the full editorial
     constraints baked into the system prompt.
   - Runs all 11 quality gates. Up to 3 rewrite attempts on failure.
   - On pass: promotes the draft, regenerates pages + schedule report
     + site shell, runs the launch audit, creates a branch
     `auto-draft/{slug}`, commits, pushes.
4. Posts a summary to the GitHub Actions run UI with the PR URL.

**It does not:**
- Push to `main`
- Merge any PRs
- Skip the human-gate review (opening the PR IS the handoff)
- Modify the pillar JSON beyond the published-on-promotion field
- Generate more than one article per run

---

## Cost

Per article (Anthropic API pricing, claude-opus-4-5 as of late 2026):
- Input tokens: ~3,500 ($15/M input) → ~$0.05
- Output tokens: ~3,500 ($75/M output) → ~$0.26
- **Total: ~$0.30 per article**

If retries are needed (3 attempts max), worst case ~$0.90/article.

For the 73 currently-planned articles across the schedule:
- Best case (all pass first try): ~$22 total
- Worst case (all need 3 retries): ~$66 total

GitHub Actions minutes: a typical run takes 2-3 minutes. Free tier
covers 2,000 min/month on public repos and 500/month on private —
either is plenty for a weekly run.

---

## Testing it locally before trusting the cron

You can run the same orchestrator from your laptop. Make sure your
working tree is clean and on `main`:

```bash
git checkout main
git pull
ANTHROPIC_API_KEY=sk-ant-... python3 scripts/insights_auto_draft.py
```

For dry-run (drafts + validates but doesn't push):

```bash
ANTHROPIC_API_KEY=sk-ant-... AUTO_DRAFT_DRY_RUN=1 \
    python3 scripts/insights_auto_draft.py
```

For testing a specific slug:

```bash
ANTHROPIC_API_KEY=sk-ant-... AUTO_DRAFT_SLUG=spindle-bearing-failure-modes \
    python3 scripts/insights_auto_draft.py
```

---

## How you'll be notified each week

The workflow opens the PR automatically. That triggers GitHub's standard
PR notifications, which means you'll see it through whichever channels
you have subscribed (default = email + mobile push if you have the
GitHub mobile app installed).

You should see:
- **GitHub email** to your account address (default for repo owners)
- **Push notification** if you have the GitHub iOS/Android app
- **Notification in the GitHub web UI** (the inbox bell at top-right)
- **Email about workflow failure** if validation fails 3 times in a row

If you want a louder ping (Slack, Discord, SMS), add a GitHub
integration on the repo — `Settings → Integrations` — or set up a
GitHub Action notification step.

## What you do each week

After the workflow runs (Monday morning) and the PR notification arrives:

1. **Open the PR** from the notification email or mobile push.
2. **60-second human-gate review.** The PR description includes the
   checklist:
   - Voice sounds like Ken? No exclamation points? No hype?
   - All specific claims defensible? Pricing ranges in Ken's actual range?
   - Any banned phrases?
   - Internal links land in-context?
3. **Merge.** Cloudflare Pages deploys in ~2 min.
4. **(Optional) v2 edit pass later.** When you have 5 minutes with
   Ken, edit the article in place with his specific data, commit,
   push, Cloudflare re-deploys.

---

## When to pause or stop the workflow

- **Pause:** Settings → Actions → General → "Disable Actions" temporarily
- **Stop scheduled but keep manual:** edit `.github/workflows/insights-auto-draft.yml`
  and remove the `schedule:` block (keep `workflow_dispatch:`)
- **Stop entirely:** delete the workflow file or rename to `.yml.disabled`

---

## Failure modes

The orchestrator exits with these codes:

- `0` — success (article pushed, OR nothing to draft this run)
- `1` — validation failed after 3 retries. A `{slug}.review.md` file
  is created in `_drafts/`. The next run will skip this slug because
  it's now drafted. You can manually fix and commit, OR delete the
  `_drafts/{slug}.md` file to let the next run try again.
- `2` — pre-flight or environment issue (missing secret, missing
  scripts, etc.). Won't retry.
- `3` — Anthropic API failure (network, rate limit, etc.). The
  workflow will retry next Monday — no manual action needed unless
  the API key is wrong.
- `4` — git operation failed (push rejected, branch already exists,
  etc.). Usually means a previous run's branch wasn't merged and the
  current run picked the same slug. Either merge the existing PR or
  delete the remote branch.

All failure exit codes leave the repo in a clean state. The workflow
job will be marked failed in GitHub Actions, and you can re-run from
the Actions UI.

---

## Files

```
scripts/insights_auto_draft.py        — the orchestrator
.github/workflows/insights-auto-draft.yml — the schedule + runner
prompts/insights/07-auto-draft-runbook.md — human-readable spec
docs/insights-auto-draft-setup.md      — this file
```
