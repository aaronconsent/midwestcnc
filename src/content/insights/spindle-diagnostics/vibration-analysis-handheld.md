---
title: "Handheld Vibration Analysis for Shop Owners"
slug: "vibration-analysis-handheld"
pillar: "spindle-diagnostics"
target_query: "cnc spindle vibration meter"
description: "How a sub-$500 handheld vibration meter sorts spindle bearing problems from balance and tooling problems. The three-axis check pattern. What the numbers mean in practical terms."
author: "Ken — Midwest CNC Services"
date: "2026-05-27"
signal_signature: "handheld vibration meter; three-axis check; mm/s velocity; ISO 10816; baseline reading"
---

## Key Takeaways

- A handheld vibration meter under $500 can isolate the failure category in under 10 minutes on most VMCs. Stethoscope hearing is not required.
- The three-axis check is the standard procedure. Measure at the spindle nose in 3 directions: axial, horizontal radial, and vertical radial. The three readings together point at the source.
- The numbers matter less than the trend. A single reading is a data point. A monthly trend over 6 months is the diagnostic signal. A meter that reads 2.5 mm/s today and 4 mm/s a month later is telling you something.
- ISO 10816 is the standard reference for vibration severity. The thresholds are useful but not absolute. A precision spindle has a different acceptable range than a heavy production lathe.
- The single highest-value use of a handheld meter is establishing a baseline reading right after a spindle rebuild. Every subsequent reading compares against that baseline.

Vibration analysis used to require an external service call. The instrumentation was expensive, the technique took training, and the result was a report that took days to come back. None of that is true anymore. A capable handheld vibration meter costs under $500. Anyone in a shop can take a reading. The result is usable for the most common diagnostic question — is the spindle bearing healthy or not. This piece walks the equipment, the procedure, and the interpretation.

## What a handheld meter actually does

A handheld vibration meter has a single accelerometer probe on one end and a digital display on the other. Press the probe against a surface attached to whatever you want to measure. The meter reads the vibration in one of several units. Most common is mm/s velocity, which is the standard for machinery vibration analysis.

The reading is a single number representing the overall vibration energy at that point. Higher numbers mean more vibration. The point of the measurement is to compare the number against a baseline or against an industry threshold.

More expensive instruments do frequency analysis. They tell you not just how much vibration but what frequencies the energy is at. That extra capability is useful for advanced diagnostics. For shop-floor sorting of bearing problems from balance and tooling problems, the basic overall reading is enough.

## The three-axis check

The standard procedure for spindle vibration is the three-axis check at the spindle nose.

**Axis 1: axial.** Place the probe against the spindle face, pointing along the spindle axis. The reading captures vibration in the direction the spindle would push or pull. Axial vibration is highest with preload or drawbar problems.

**Axis 2: horizontal radial.** Place the probe against the side of the spindle housing, pointing horizontally toward the spindle axis. The reading captures vibration perpendicular to the spindle axis in the horizontal direction. Radial vibration is highest with bearing or balance problems.

**Axis 3: vertical radial.** Place the probe against the top of the spindle housing, pointing vertically toward the spindle axis. The reading is the radial vibration in the vertical direction.

Run the spindle at the RPM you most often use for the work you do. Hold each probe position for 10 to 15 seconds. The meter usually averages over that window and displays a stable number. Record all three numbers.

## What the three numbers tell you

The three readings together tell more than any one reading alone.

**All three similar and low.** The spindle is healthy. Whatever you came to investigate is probably not the spindle. The [vibration symptom decoder](/insights/spindle-diagnostics/diagnose-cnc-spindle-vibration/) walks the next places to look.

**Axial high, radial low.** Preload or drawbar problem. The [drawbar diagnostics piece](/insights/spindle-diagnostics/spindle-drawbar-diagnostics/) covers what each of those looks like.

**Radial high, axial low.** Bearing or balance problem. Run an RPM sweep with the meter. If the reading scales smoothly with RPM, bearing. If the reading spikes at one RPM and drops, balance.

**All three high.** Multiple issues, or a severe single issue. Take the spindle out of service for bench diagnostics.

The pattern matters more than the absolute numbers. A pattern that points at one direction tells you more than three numbers that are all "kind of high."

## The ISO 10816 reference

ISO 10816 is the international standard for evaluating machine vibration. It gives thresholds for what is acceptable and what is not, broken into machine categories. For shop-floor purposes, the simplified version is this.

**Below 2.8 mm/s (Zone A).** The machine is operating in the "good" range. New or recently-rebuilt spindles should be here.

**2.8 to 4.5 mm/s (Zone B).** Acceptable for long-term operation, but trending upward in this zone is the signal to start planning a rebuild.

**4.5 to 7.1 mm/s (Zone C).** The machine is in the warning zone. Rebuild scheduling should be active.

**Above 7.1 mm/s (Zone D).** Damage is occurring. The spindle should be taken out of service.

These thresholds are for general industrial machinery. Precision platforms have tighter expectations. Heavy production machinery sometimes lives higher. Use ISO 10816 as a starting reference, not as the final word.

## The trend matters more than the reading

A single vibration reading is one data point. It is useful but limited. The diagnostic power of a handheld meter is in the trend over time.

The pattern we look for is the rate of change. A spindle that has read 2.5 mm/s for 6 months and suddenly reads 3.5 mm/s has changed. The absolute number is still in Zone B. But the change itself is the signal that something has shifted. The bearing is starting to fail, or the preload is changing, or some other factor has shifted.

Catching the change at this stage is where the handheld meter pays back its cost. The shop has time to schedule a rebuild against its production calendar. The rebuild scope is in the cheap end of the range because the failure has not progressed. The [rebuild-vs-replace economics piece](/insights/spindle-diagnostics/rebuild-vs-replace-spindle-economics/) covers what that planning conversation looks like.

## Establishing the baseline

The highest-leverage use of a handheld meter is right after a spindle rebuild or replacement. The spindle is at its known-good state. Take readings at all three positions. Record them. Date them.

Every subsequent reading compares against that baseline. The threshold for "act" is no longer ISO 10816 thresholds, which are general. It is "the reading has moved this much from the baseline this shop established." That is a much tighter signal.

Most shops do not have a baseline. We recommend taking one for any spindle that has been [recently rebuilt](/spindle-grinding/) or that you suspect will need work in the next year. Five minutes of measurement now saves a much larger conversation later.

## Sources & references

- ISO 10816 thresholds are quoted from the published standard, simplified for shop-floor use.
- Three-axis procedure follows standard machinery vibration analysis practice.
- Trend-rate observations are from Midwest CNC Services field-service work across the 2023 to 2025 period.

## When to bring this work to us

If your handheld readings have crossed into Zone B or higher, or if your trend shows a clear upward rate of change, the cheapest first step is a field diagnostic visit. We bring more sensitive instrumentation, do frequency analysis, and can usually tell the source within an hour.

[Get a quote](/get-a-quote/) with the machine model, your three-axis readings, and the trend over the last 6 months if you have it.
