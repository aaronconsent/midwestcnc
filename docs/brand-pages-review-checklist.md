# Brand Pages — Credibility Review Checklist

20 markdown files generated at `src/content/spindle-brands/{slug}.md`. Read this before approving HTML templating so you can catch any sentence that doesn't sound like the shop wrote it.

## Word count vs. spec

| metric | target | actual |
|---|---|---|
| visible body words / page | **500–700** | **291–407** (avg 351) |

Generated pages land **roughly 150–200 words under target.** This is by design, not laziness:

- Ken's confirmed answers are concise — 3–6 short sentences per brand, total ~80–140 words of brand-specific content.
- The editorial constraint ("if Ken didn't say it, don't say it") rules out the kind of capability-claim padding the existing live-site pages used ("flat-rate pricing", "photo-verified results", "sub-micron accuracy guaranteed" — none of which Ken authorized).
- For reference, the existing real-content pages on the live site (`/spindles-repair/mazak-spindle-repair`, `/spindles-repair/haas-spindle-repair`) are also ~305 visible body words each. The 500–700 target in the pattern doc was aspirational, written before we knew how dense Ken's input would be.

**Three paths forward — your call before HTML templating:**

1. **Ship at current density.** Honest to Ken's input, matches live-site density.
2. **Send Ken a follow-up worksheet** asking for 2–3 more sentences per brand (typical diagnostic steps, common shop scenarios, what to listen for). Then re-generate.
3. **Relax the editorial constraint** to let the template add ~150 words of brand voice per page (capability claims, process detail, a brief FAQ). I'd flag every added sentence for your review.

Currently the pages are option 1.

---

## What's templated vs. what's Ken

Every page has roughly 70% scaffolding and 30% brand-specific content. The scaffolding is intentional — it's there to look like every other page on the site and to give the schema/CTAs/cross-links a consistent home. Boilerplate by itself isn't a credibility risk; **the risk is at the seams**, where a generic lead-in introduces one of Ken's quotes.

### Boilerplate (repeated verbatim across the indicated page set)

**All 18 CNC-spindle pages:**

| Section | Templated line(s) |
|---|---|
| Eyebrow | `_{Brand} Spindle Repair & Grinding_` |
| H1 | `Eliminate Costly Downtime` |
| Hero opener | `What we see most on {Brand} spindles:` |
| Hero closer | `We rebuild, regrind, and rebalance across the {Brand} platform — {model list} — with most jobs running {N–N weeks} and field troubleshooting where it can save a teardown.` |
| Models intro | `Our {Brand} work covers the full lineup — no model left behind. Whether the job is a precision bearing pack replacement, a full rebuild, or a regrind to restore tolerance, we handle:` |
| "How We Approach" opener | `The brand-specific factors on {Brand} drive how we plan the job.` |
| "What We Focus On" | `Across every {Brand} job, our priorities are downtime reduction, field troubleshooting where that's the right call, and crash recovery on the spindles other shops have written off.` |
| War-story opener | `A recent job that's typical of what comes through on {Brand}:` |
| Lead-time intro | `Our three-step workflow keeps it transparent:` |
| 3-step workflow | Steps 1–3 (verbatim except step 3 wording per page type) |
| Trust block | Ken's certifications quote + Ken's customer quote (verbatim) |
| Related Services | 3 sibling-service links + 3 peer-brand links + service-area sentence |

**Both legacy pages (Fadal, Hitachi Seiki) additionally share:**

| Section | Templated line |
|---|---|
| Parts Sourcing intro | `{Brand} machines are still cutting daily in Midwest shops, but factory support has been gone for years and parts hunts can stretch a rebuild's timeline more than the bench work does.` |
| "What We Focus On" tail | `…and keeping legacy {Brand} machines running long after OEM support is gone.` |

**Amada and Trumpf share:**

| Section | Templated line |
|---|---|
| Workflow + service area | Verbatim with workflow step-3 wording adapted per page type. |
| Trust block | Trimmed cert list (no "spindle balancing" claim — those aren't spindle pages). |

### Where Ken's content lives (the parts that vary)

For every brand, these come straight from `ken_input` in `src/data/spindle-brands.json`:

- Hero (after the opener) — `common_failure_mode`
- Models bullet list — `models` (empty for Amada and Trumpf)
- "How We Approach" body — `brand_specifics`
- War story body — `war_story`
- Lead-time section opener — `typical_lead_time` (full sentence, not just the week range)
- (Legacy only) Parts Sourcing body — `parts_situation`

Trust block also uses two `global_context` quotes verbatim: `certifications` and `customer_quote`.

---

## Sentences most likely to read AI-generated — spot-check these first

These are the seams where templated framing introduces a Ken quote. If any of these grate, the cleanest fix is to drop the framing sentence and let Ken's quote stand on its own.

### High-priority spot-checks (every page)

1. **Hero seam.**
   `What we see most on {Brand} spindles: {Ken's failure_mode sentence}`
   Risk: if Ken's failure_mode opens with a noun phrase rather than a "we see…" verb construction, the colon can feel awkward. Worst offenders: Toyoda ("Mostly bearing-pack wear and occasional lubrication-related damage"), Niigata ("Heavy-duty spindle bearing wear and gear-drive vibration issues"). The colon-into-noun-phrase pattern is grammatically fine but stylistically thin.

2. **"How We Approach" lead-in.**
   `The brand-specific factors on {Brand} drive how we plan the job. {Ken's brand_specifics}`
   Risk: the lead-in is generic across all 18 pages. Where Ken's brand_specifics doesn't actually describe a *factor* (e.g. Toyoda: "Very rigid machines. We don't see them as often, but when we do they're usually worth fixing.") the framing rings hollow. Consider dropping the lead-in entirely for those pages.

3. **War-story lead-in.**
   `A recent job that's typical of what comes through on {Brand}: {Ken's war_story}`
   Risk: Ken's stories vary in scope. For pages where the story doesn't really describe a "typical" job (Fanuc: "Had a mold customer chasing a finish problem for weeks before teardown showed early-stage bearing damage" — that's a *memorable* job, not necessarily typical), the lead-in slightly overpromises.

4. **"What We Focus On."**
   The whole section is paraphrased from Ken's `emphasis_themes` directive. It's defensible — he authorized those themes — but it reads as four nouns rendered into prose. The biggest risk is the legacy variant on Fadal/Hitachi Seiki, where four parallel clauses run long.

### Brand-by-brand specific concerns

Listed only where there's something to flag beyond the universal seams above.

#### Mazak
- ✓ Failure mode reads as a complete shop-voice sentence; hero seam works.
- ⚠ "How We Approach" — Ken's quote starts "MAZATROL diagnostics are brand-specific" which directly echoes the templated lead-in "brand-specific factors". Minor redundancy.

#### Haas
- ⚠ Hero seam: failure mode begins "Belt-driven VF spindles commonly show drawbar wear, pulley issues, and bearing fatigue. Direct-drive units mainly fail from bearing wear and heat." The terminology guidance says we should prefer "bearing pack failure" over "bearing wear" — Ken uses "bearing wear" twice here. Decide whether to apply his own guidance to his own words.

#### Okuma
- ✓ Failure mode flows naturally.
- ⚠ Models list is short (4 items). Brand_specifics references "OSP controls require machine-specific diagnostics" which is solid.

#### DMG Mori
- ✓ Strongest brand_specifics on the spindle pages — Ken really wrote like a tech here ("After a rebuild, we usually verify spindle cooling performance and monitor thermal growth before signoff").

#### Mori Seiki
- ⚠ Models list ("SL series, NL series, older MV mills, NH horizontals") includes the qualifier "older" which we kept. Reads naturally inside the bulleted list but check it's not jarring.
- ⚠ War story is short and could read as setup-without-payoff: "One customer was ready to scrap an older Mori horizontal because of chatter. After rebuild and alignment work, it went right back into production." Fine but uneventful.

#### Doosan
- ✓ Brand_specifics is shop-voicey: "Good parts availability compared to a lot of imports. Common machines in Midwest production shops."

#### Brother
- ✓ Brand_specifics is voicey: "The Speedio machines are compact but they run hard. Warmup routines matter more than a lot of shops realize."

#### Hurco
- ✓ Brand_specifics is voicey ("Very common in smaller job shops where one machine may run ten different kinds of work in a week").

#### Makino
- ✓ Brand_specifics is voicey ("A lot of Makino work comes from aerospace and mold shops where even small runout issues become visible fast"). Strong.

#### Fanuc
- ⚠ Brand_specifics: "The controls side is usually straightforward because most maintenance teams already know Fanuc." — solid but the templated lead-in "brand-specific factors on Fanuc drive how we plan the job" mismatches: the point is that Fanuc *doesn't* require unusual planning.

#### Toyoda
- ⚠⚠ **Highest boilerplate-feel risk page.** Ken's content is the most terse of any brand: failure_mode is 9 words, brand_specifics is "Very rigid machines. We don't see them as often, but when we do they're usually worth fixing." (notable — admits low volume). The templated framing overshadows. Strongly consider sending Ken a follow-up for this brand specifically.

#### Fadal (legacy)
- ✓ Parts Sourcing section reads well — combines templated legacy framing with Ken's parts answer.
- ⚠ Brand_specifics is a sentence fragment ("Still a huge installed base. Plenty of shops keep these alive because repair costs make sense.") — first clause has no subject. Grammatically scrappy in a shop-voice-good way, but check it doesn't read as broken.

#### Hitachi Seiki (legacy)
- ✓ Parts Sourcing answer ("Combination of used-market sourcing, remanufacturing, and custom-machined replacement parts.") is short but credible.
- ⚠ Brand_specifics is meta ("These machines are old enough now that every rebuild is a little different.") — true but not very actionable for a reader. Consider whether the framing line ("The brand-specific factors on Hitachi Seiki drive how we plan the job") is justified.

#### Giddings & Lewis
- ⚠ Brand_specifics ("Downtime on these machines is brutal because they're usually tied to big-part production.") is solid but the templated emphasis-themes section says the same thing more generically ("downtime reduction") right after. Slight redundancy.

#### Monarch
- ⚠ Brand_specifics ("Some of these machines are old enough that maintaining accuracy becomes half rebuild, half restoration work.") is great, but Monarch is NOT marked as legacy in the data — should it be? Worth a check; if yes, add `legacy_context` and re-generate.

#### Amera-Seiki
- ⚠ All Ken content is concise (failure_mode + brand_specifics + war_story total ~50 words). Page leans heavily on templated sections. Lowest brand-specific density of the cnc_spindle pages.

#### Niigata
- ⚠ Failure mode is a 9-word noun phrase ("Heavy-duty spindle bearing wear and gear-drive vibration issues.") — hero seam awkward (see universal note #1).

#### Johnford
- ⚠ War story ("Recovered a crashed spindle another shop had given up on") was extracted but actually the full last-line content is "Recovered a crashed spindle another shop had given up on." — verify this matches Ken's intent. The cascading pattern in Ken's worksheet (last line wins) sometimes leaves war stories truncated; this one looks complete.

#### Amada (press_brake_service)
- ✓ Framing avoids "spindle" terminology in hero, scope, and trust block.
- ⚠ Hero contains slight redundancy: "the call we hear most is the same: hydraulic service and ram alignment issues are probably the most common calls" — "calls" appears twice. Smooth read but not elegant.
- ⚠ **Breadcrumb still says "Spindle Grinding"** because the URL is `/spindle-grinding/amada-spindle-repair/`. URL structure should arguably change for these two brands; that's a bigger refactor.
- ⚠ Models bullet list is absent (Ken didn't supply models for press brakes); the "Amada Service We Provide" section fills the slot. Verify this feels complete.

#### Trumpf (laser_punch_service)
- ✓ Framing avoids "spindle" terminology.
- ⚠ Same breadcrumb URL issue as Amada (`/spindle-grinding/trumpf-spindle-repair/`).
- ⚠ Same models-absent / scope-section substitution as Amada — verify it reads complete.
- ⚠ Ken's brand_specifics ("Trumpf support and parts are very OEM-centric…planning downtime matters") is paired with templated framing "brand-specific factors on Trumpf drive how we plan the job" — these echo each other but the result reads OK.

---

## What's NOT in any page (deliberately)

Claims that appeared on the existing live-site pages but are absent from the rebuild because Ken didn't authorize them:

- ❌ "Flat-rate pricing" / "flat rates"
- ❌ "Photo-verified results"
- ❌ "Sub-micron accuracy guaranteed" (we say "verify balance and runout" instead)
- ❌ "24/7 emergency dispatch" (not mentioned anywhere by Ken)
- ❌ Any specific certification beyond "factory-trained technicians" (no ISO, AS9100, etc.)
- ❌ Specific warranty language

If any of these are real, get them on the worksheet and re-generate.

## Mechanical sanity checks (low-risk but worth a glance)

- [ ] All 20 files exist at `src/content/spindle-brands/{slug}.md`
- [ ] Front matter parses (YAML well-formed, no unescaped quotes)
- [ ] Phone number consistent: `319-610-4341` display, `+13196104341` href
- [ ] Schema breadcrumb item paths match `current_url` for each brand
- [ ] Peer-brand links resolve (no orphans — all 18 cnc_spindle slugs link to other valid cnc_spindle slugs)
- [ ] No `{Brand}` template placeholders leaked through
- [ ] Markdown renders cleanly (no broken bold, dangling list markers)

Read the spot-check items first; mechanical checks can run in CI later.
