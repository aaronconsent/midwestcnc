---
title: "Spindle Runout: Causes, Measurement, and When to Act"
slug: "spindle-runout-measurement"
pillar: "spindle-diagnostics"
target_query: "measure spindle runout"
description: "How to measure CNC spindle runout, what the numbers mean, and the threshold where the runout becomes the reason a part is no longer in spec. The four-point measurement procedure we use on the bench."
author: "Ken — Midwest CNC Services"
date: "2026-05-27"
signal_signature: "tooling-induced runout; spindle-induced runout; total indicator reading; test bar; gauge length"
---

## Key Takeaways

- Runout is the most measurable spindle health number you have. A 0.0002-inch reading at the taper face on a production VMC is normal. 0.0005 inch is the threshold where most shops should plan a rebuild.
- Runout splits into two sources: tooling-induced runout (the holder, pull-stud, or tool) and spindle-induced runout (the spindle bearings or shaft). Both look the same on a part. They cost different amounts to fix.
- The four-point measurement procedure isolates the source. Same indicator. Four positions. Twenty minutes of shop time. The result tells you whether the problem is the tool or the spindle.
- A typical Mazak or Haas spindle in healthy service ships from us with runout under 0.00015 inch at the taper face and under 0.0003 inch at 100 mm gauge length on a test bar.
- Runout climbing over time is the earliest reliable signal that a bearing is failing. Catching it under 0.0004 inch usually keeps the rebuild in the lower cost range. Past 0.0008 inch, secondary damage is usually already present.

Runout is the single number we ask shops to track when they suspect a spindle problem. It is more reliable than noise. It is more reliable than vibration symptoms. And it does not require any instrumentation more expensive than a dial indicator and a test bar. The challenge is not measuring runout. It is knowing what the number means and where the variation is coming from.

## What runout actually is

Runout is the total indicator reading taken at a specific point on the rotating system. With the spindle turning slowly by hand or under low RPM, the indicator picks up the high and low points of the surface being measured. The difference between the two is the runout. The standard convention is TIR — Total Indicator Reading.

Two surfaces matter for spindle health. The taper itself, where the tool holder seats. And a point further out on a test bar or known-true reference, usually at 100 millimeters or 4 inches of gauge length from the spindle face. The two readings together tell you whether the runout is at the spindle face (a taper or seat problem) or further out (a shaft, bearing, or axis-alignment problem).

## Tooling-induced runout vs spindle-induced runout

Runout has two sources. The tooling chain — pull-stud, holder, tool — can contribute. The spindle itself — bearings, shaft, taper — can contribute. Both look the same on the part. The diagnostic challenge is knowing which one is which.

Tooling-induced runout is usually the cheaper problem. A worn pull-stud. A bent or damaged holder. A tool with chip-up between the shank and the holder bore. Swap the holder for a known-good one. Re-measure. If the runout drops, the tooling chain was the cause. The fix is a new holder or pull-stud, often under $300.

Spindle-induced runout is the more expensive problem. The shaft has shifted in the bearings. The bearings themselves have spalled. The taper face has worn. Or the front bearing preload has loosened. None of those go away by swapping tooling. They need a [spindle rebuild](/spindle-grinding/) or a service call.

The [bearing failure modes piece](/insights/spindle-diagnostics/spindle-bearing-failure-modes/) covers what causes the bearings to fail in the first place. This piece is about how to know it has happened.

## The four-point measurement procedure

This is the procedure we use on the bench and the one we ask shops to use in the field. It isolates the source in about 20 minutes.

**Position 1: tool, full assembly, at gauge length.** Insert a known-good test bar or a precision tool. Indicate at 100 mm or 4 inches out. Run the spindle by hand or at low RPM. Record the TIR.

**Position 2: tool, full assembly, at the taper face.** Move the indicator to the spindle face, with the tool still installed. Record the TIR.

**Position 3: empty spindle, taper face.** Remove the tool. Indicate against the taper face directly. Record the TIR.

**Position 4: empty spindle, deeper in the taper.** Indicate at the deepest accessible point inside the taper. Record the TIR.

The four numbers tell different stories. Position 1 minus Position 2 isolates the tool's contribution. Position 2 minus Position 3 isolates the holder seat. Position 3 versus Position 4 tells you whether the taper itself is uniform or has worn unevenly. A single high reading at Position 4 suggests damage deep in the taper. Two high readings at Positions 3 and 4 suggest the shaft or front bearing.

## What the numbers should be

Acceptable runout depends on the machine class. Production VMCs and lathes tolerate more than precision platforms. Multitasking machines and grinding spindles tolerate less. The numbers below are the ranges we see across [Mazak](/spindle-grinding/mazak-spindle-repair/), [Haas](/spindle-grinding/haas-spindle-repair/), and Okuma platforms in healthy service.

**Production VMC, post-rebuild:** under 0.00015 inch at the taper face. Under 0.0003 inch at 100 mm gauge length.

**Production VMC, end-of-life-acceptable:** up to 0.0004 inch at the taper face. Up to 0.0006 inch at 100 mm gauge.

**Precision platform, post-rebuild:** under 0.00008 inch at the taper face. Under 0.00015 inch at gauge length.

**Multitasking platform (Integrex, NTX):** typically tighter than VMC, usually held under 0.00012 inch at the taper.

Runout climbing past the end-of-life-acceptable threshold is the signal to schedule a rebuild. Climbing past 0.0008 inch usually means the bearings are no longer the only problem, and the rebuild scope expands.

## When to act on the number

A single runout measurement is a data point. A trend is the signal. We ask shops with a Matrix or Smooth Mazak in production to spot-check runout monthly with the same test bar in the same conditions. Plotting six months of readings against the calendar tells you whether the spindle is degrading on a slow curve, holding steady, or jumping.

Slow degradation gives you time. Schedule the rebuild against your production calendar. Run the machine through a planned slowdown. Pull the spindle when it makes sense for the shop, not when the part rejection rate forces it.

A jump in the curve — runout doubles in a month, then doubles again — means something is failing fast. That is the moment to take the spindle out of service. Continuing to run through a fast-degrading curve almost always pushes the rebuild into the higher cost category described in [the rebuild-vs-replace economics](/insights/spindle-diagnostics/rebuild-vs-replace-spindle-economics/) piece.

## A practical caveat about test bars

The test bar matters. A worn or off-spec test bar produces a reading that does not reflect the spindle. We have had shops send us a spindle for a rebuild based on a runout reading, only to find on the bench that the spindle was within spec and the test bar was the problem. The fix in that case is a new test bar, not a rebuild.

The simplest check: indicate the test bar in a known-true reference like a precision lathe collet or a verified [tooling holder](/repairs/). If the test bar shows runout on its own, it is not telling you anything reliable about the spindle.

## Sources & references

- TIR measurement convention follows standard machine-tool inspection practice as documented in ISO 230 and ASME B5 standards (which we reference at the bench level without claiming certification against either).
- Acceptable-range numbers reflect what we see in healthy spindles across the Mazak, Haas, Okuma, and DMG Mori platforms in our service log.
- The 0.0008-inch threshold for secondary damage is approximate. The actual number varies by platform and by which bearing has failed.

## When to bring this work to us

If your runout trend is climbing and you want a sanity check before scheduling a rebuild, the cheapest first step is to ship us your test bar or the suspect tooling for verification. We can sort tooling-induced from spindle-induced before you commit to a rebuild quote.

[Get a quote](/get-a-quote/) with the runout numbers you have measured, the machine model, and how the readings have trended over time.
