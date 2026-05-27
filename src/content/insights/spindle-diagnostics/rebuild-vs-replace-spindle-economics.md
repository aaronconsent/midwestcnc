---
title: "Spindle Rebuild vs. Replace: When Each Makes Sense"
slug: "rebuild-vs-replace-spindle-economics"
pillar: "spindle-diagnostics"
target_query: "cnc spindle rebuild or replace"
description: "The economics of a CNC spindle rebuild versus replacement, framed by the three break-even questions Ken walks customers through before quoting work. Real cost ranges and the cases where each path actually wins."
author: "Ken — Midwest CNC Services"
date: "2026-05-27"
signal_signature: "three break-even questions; bearing set; runout at the taper; secondary damage; lead time"
---

## Key Takeaways

- A typical CNC spindle rebuild on a production-class machine runs $4,500 to $12,000 depending on damage scope, with parts and labor split roughly 40/60. Outright replacement of an integral-motor cartridge can run $18,000 to $45,000 before installation labor.
- The rebuild-vs-replace decision turns on three break-even questions: how much secondary damage has accumulated, what the machine is worth in resale today, and what the production cost of a longer lead time looks like for this specific shop.
- A spindle whose runout at the taper has stayed under 0.0002 inches before the failure event is almost always a rebuild candidate. Above 0.0005 inches, the shaft itself may be compromised and the math shifts.
- Lead time on rebuilds runs 3 to 6 weeks for most platforms; a replacement cartridge from the OEM can be 8 to 16 weeks if it's in stock and longer if not. Lead time alone often decides the question.
- Integral-motor spindles change the math significantly. Their rebuild path is narrower (you can't just press in new bearings), and replacement is sometimes the only honest answer.

The first question every shop asks when a spindle fails is some version of "is it worth fixing?" The honest answer depends on three variables specific to your machine, your shop, and the failure mode. The framework below is the one [Ken walks customers through](/spindle-grinding/) on the phone before we quote either path. It's not a magic decision tree — it's the math that determines which side of the break-even line you're actually on.

## A rebuild restores the spindle; a replacement swaps in a different spindle

A rebuild takes the existing spindle assembly apart, replaces the wear components (the bearing set, seals, lubrication paths, sometimes the drawbar), and verifies the result back to the manufacturer's runout and balance specs. The shaft, housing, and labyrinths stay. A replacement removes the entire spindle assembly and installs a new one — either OEM or a quality aftermarket equivalent.

The cost difference, in our service log across the last three years, runs about 3x. A Haas VF-series rebuild has come in between $4,800 and $7,200 depending on what we found inside; a replacement spindle for the same machine, depending on the year and the [VF-series generation](/repairs/haas-cnc-machine-repair/vf-series/), runs $16,000 to $24,000 before install. On a [Mazak Integrex multitasking platform](/repairs/mazak-cnc-machine-repair/integrex/), the spread is wider — rebuilds in the $9,000 to $14,000 range, replacement cartridges $32,000 to $48,000.

The rebuild number is more flexible because we can scope it. The replacement number is set by what the OEM charges.

## The three break-even questions

These are the questions we ask before quoting. None of them have a single right answer; each is shop-specific.

### Question one: how much secondary damage is there

When a bearing fails, it doesn't fail in isolation. Heat, debris, and vibration propagate. The longer the spindle ran after the first symptom, the more damage there is to assess. Secondary damage to the shaft, to the bore in the housing, to the labyrinth seals, even to the drawbar — each adds to the rebuild scope and shifts the math.

The clean rebuild case is: the operator heard the noise, called us within a week, the bearings are the only thing destroyed, and the shaft and bore measure within spec. This rebuild runs the low end of the range.

The messy rebuild case is: the spindle ran for months making noise, the inner race is gone, the shaft has spall marks, and the bore has heat-shifted enough that bearing fit is questionable. This rebuild runs the high end — sometimes high enough that replacement starts to make sense.

Across our [bench rebuilds last year](/spindle-grinding/), about one in five came in late enough that we had to either regrind the shaft, sleeve the housing, or replace components beyond the bearings. Each of those operations adds days to the lead time and dollars to the quote.

### Question two: what is the machine worth today

A rebuild restores production capacity to a specific machine. If that machine is worth $40,000 in today's market and the rebuild costs $8,000, the rebuild captures 20% of the machine's value in service cost. If the same rebuild is on a $200,000 machine, it's 4% — a completely different financial decision.

Replacement cost should be compared to the machine's resale value, not its purchase price. A 12-year-old [Okuma LB-series lathe](/repairs/okuma-cnc-machine-repair/lb-lu-lathes/) might be worth $35,000 in today's used market with a healthy spindle. A new spindle for it might cost $22,000 plus installation. At that ratio, owners often choose to live with reduced spindle performance, or to sell the machine as-is and buy a healthier used unit.

The math changes when the machine is irreplaceable in its current configuration — legacy controls with parameters that took a decade to dial in, custom fixturing built around the machine's specific geometry, or a place in the production layout that can't be easily reconfigured. In those cases, the rebuild wins even when the pure dollar math says otherwise.

### Question three: what does the lead time cost you

Production downtime cost varies by shop. A job shop running a single CNC at 40% utilization is in a different position than a high-mix production shop running three shifts on the same spindle. We've seen quoted downtime costs from $200/day to $4,800/day across our customer base.

Rebuild lead time at our shop runs 3 to 6 weeks for most platforms — 3 weeks if we can stage parts ahead, 6 weeks if the bearing set has to come in from overseas. Replacement spindle lead time varies wildly: in-stock at the OEM might be 2 weeks, special-order for a less common platform might be 16 weeks. We've seen [Mazak Variaxis cartridges](/repairs/mazak-cnc-machine-repair/variaxis/) on 4-month lead time during peak demand cycles.

If your downtime cost is $1,000/day and the difference between rebuild and replacement is 8 weeks of lead time, that's $56,000 of cost difference before we touch the comparison of part prices. Lead time alone often decides the question.

## When replacement is the right answer

Replacement is the honest answer in several specific cases:

1. **Integral-motor spindle with motor damage.** If the rotor windings are damaged or the motor stator has failed, the rebuild path is narrow. We can rewind the motor in some cases, but on many platforms the cost approaches a new cartridge anyway.
2. **Shaft damage beyond regrind.** If the shaft has cracks, heavy spall, or geometry shifts that exceed regrind tolerances, replacement is more honest than a rebuild that won't hold spec.
3. **Bore damage in the housing.** When the housing bore is shifted out of round or out of size from heat damage, bearing fit becomes unreliable. Sleeving is possible but adds cost and risk; replacement is sometimes the cleaner answer.
4. **End-of-life machine with high downtime cost.** If the machine has other failing systems (controls, ATC, ways) and the spindle is the latest in a series of repairs, a complete spindle replacement may not be the right investment. A machine swap might be.

## When rebuild is the right answer

Rebuild is the right answer for most cases — it's why we exist as a shop:

1. **Bearing damage caught early.** If the spindle has been making noise for less than 30 days and the runout is still measurable, the bearings are the failure mode and the rebuild path is clean.
2. **High-value machine, long remaining service life.** A 5-year-old [DMG Mori NTX](/repairs/dmg-mori-cnc-machine-repair/ntx/) with 15 more good years in it is a rebuild candidate even when the rebuild is expensive.
3. **Legacy machine where replacement is unavailable.** Legacy [Fanuc-controlled machines](/repairs/fanuc-cnc-machine-repair/series-0-legacy/) and discontinued OEM platforms often have no replacement spindle path. Rebuild is the only option.
4. **Shops where downtime cost makes lead time the priority.** A 4-week rebuild beats a 12-week replacement for most production shops, even when the part costs would suggest otherwise.

## The conversation we have before quoting

Before we send a number, we ask about all three break-even questions. The diagnostic visit or bench inspection tells us the secondary damage story (question one). You tell us the machine's current value and remaining service life (question two). You tell us what downtime is actually costing the shop right now (question three). With those three inputs, the quote we send back is honest — sometimes for the rebuild, sometimes for the replacement, sometimes for the option you didn't ask about.

Runout and balance verification at sign-off is part of every rebuild we do, and we [document the spindle's condition](/spindle-grinding/) before and after so the result is checkable.

## Sources & references

- Pricing ranges are from Midwest CNC Services rebuild and replacement quotes across the 2023-2025 service log (approximately 280 rebuilds and 42 cartridge replacements).
- Lead time figures reflect average vendor performance during that period; high-demand quarters skewed longer.
- Resale value benchmarks pulled from public used-CNC auction data and broker listings for the platforms cited.
- Downtime cost ranges are self-reported by our customer base; we don't audit them.

## When to bring this work to us

If a spindle has failed or started showing symptoms, the first step is the [vibration symptom decoder](/insights/spindle-diagnostics/) — that often answers the rebuild-vs-replace question on its own. After that, send us the machine model, the symptoms, and what the failure looked like. We'll come back with both options and the math behind each.

[Get a quote](/get-a-quote/) for a rebuild assessment or a replacement comparison.
