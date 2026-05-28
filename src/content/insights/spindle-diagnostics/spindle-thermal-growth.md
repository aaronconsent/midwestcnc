---
title: "Spindle Thermal Growth: Drift, Compensation, and Faults"
slug: "spindle-thermal-growth"
pillar: "spindle-diagnostics"
target_query: "cnc spindle thermal growth"
description: "How CNC spindles grow with temperature, why compensation usually catches it, and how to tell when the thermal pattern itself is the early signal of a bearing problem."
author: "Ken — Midwest CNC Services"
date: "2026-05-27"
signal_signature: "thermal growth coefficient; thermal compensation; spindle nose extension; soak time; thermal sensor"
---

## Key Takeaways

- Most CNC spindles grow between 5 and 25 microns per degree Celsius of warm-up rise. That growth is real and measurable. It is also normal and predictable on a healthy machine.
- Modern Mazak Smooth, Okuma OSP, and Heidenhain TNC controls compensate for thermal growth automatically using a thermal sensor in the headstock. The compensation works well when the sensor is reading correctly.
- Thermal growth becomes a diagnostic problem in two cases. Either the compensation system has failed (sensor drift, parameter loss), or the spindle is growing in a pattern the compensation cannot account for (bearing damage shifting the geometry as it warms).
- The cleanest test is a 30-minute soak time observation. A healthy spindle grows on a predictable curve that flattens by minute 25. A failing spindle either grows faster, grows farther, or shows a curve that does not flatten.
- A thermal pattern that survived 5 years and suddenly changed is almost always the early signal of a bearing or preload problem. Catching it in the first month of the change saves the spindle.

Spindle thermal growth is one of those topics where the textbook description is mostly accurate, the control compensation usually works, and the diagnostic question rarely comes up — until it does. When it does, the thermal pattern is often the earliest reliable signal that something is changing inside the spindle. This piece walks the normal behavior, how compensation handles it, and the two diagnostic patterns that point at a real problem.

## Why spindles grow

Heat comes from the bearings, the motor (on integral-motor spindles), and the cutting work itself. The heat soaks into the spindle nose, the shaft, and the housing. Each part has its own thermal growth coefficient. The geometry shifts by a few microns per degree Celsius as the spindle warms up.

The shift matters for production work because micron-level dimensional changes on a milled part are well within the tolerance window most shops are trying to hold. A spindle that has grown 30 microns axially during warm-up has moved the cutting Z position by 30 microns. On a finishing pass at tight tolerance, that is the difference between in-spec and out-of-spec.

The numbers vary by platform. A typical [Mazak production VMC](/repairs/mazak-cnc-machine-repair/) grows roughly 15 to 25 microns axially during the first 20 minutes of warm-up. A [Haas VF-series](/repairs/haas-cnc-machine-repair/vf-series/) grows in a similar range. Multitasking platforms and grinding spindles often grow less because they were designed with tighter thermal control.

## How control compensation handles it

Modern CNC controls compensate for thermal growth through a measurement loop. A thermal sensor in the headstock reads the spindle temperature. The control applies a growth model — usually a linear or piecewise-linear function — to convert the temperature change into an axis offset. The offset is applied to the Z (or other axis) position before each move.

The compensation is usually invisible to the operator. It runs in the background. The part comes out in spec even though the spindle has physically grown during the operation.

When the compensation works, you do not notice it. When it fails, you notice fast. Parts start drifting out of spec partway through a run. The drift correlates with how long the spindle has been running, not with anything the program did differently.

## Compensation failures vs bearing failures

The diagnostic question is which is happening. The two failures produce similar symptoms — dimensional drift over the course of a run — but they have different fixes.

**Compensation failure.** The sensor has drifted, the parameter has been lost, or the cabling to the sensor has failed. The spindle is growing normally, but the control is no longer correcting for it. The fix is in the control: replace the sensor, restore the parameter, or repair the cabling.

**Bearing-driven thermal failure.** The bearings themselves are running hotter than they should, or are growing in a pattern that the compensation model does not account for. The spindle has changed thermal behavior because something inside it has changed. The fix is a bench rebuild covered in the [bearing failure modes piece](/insights/spindle-diagnostics/spindle-bearing-failure-modes/).

Telling the two apart is the practical purpose of the soak-time test.

## The 30-minute soak test

The test is simple. Power up the spindle. Indicate the spindle nose extension against a precision reference. Run the spindle at a representative production RPM. Record the indicator reading every 2 minutes for 30 minutes.

A healthy spindle produces a smooth curve. The growth rate is highest in the first 5 minutes, slows through minute 10, and flattens by minute 20 to 25. The total growth is usually 15 to 30 microns axially on a typical production VMC.

A spindle with compensation failure produces the same curve. The growth is normal. The control just is not compensating for it. The diagnostic confirms by running a test cut and checking dimensional drift against the recorded growth curve.

A spindle with bearing-driven thermal failure produces a different curve. Growth rate stays elevated past minute 10. Total growth exceeds the normal range by enough to notice. Or the curve has a kink — flat for a while, then climbing again, suggesting two different thermal sources reaching equilibrium at different rates.

## What the kink in the curve usually means

We see the kinked curve enough to call it out specifically. The first growth phase is the spindle housing warming up. That part is normal. The second phase, the kink at minute 15 or 20, is usually a bearing that is running hotter than it should. The bearing reaches its own thermal steady state later than the housing does, and the result is a growth pattern with two distinct phases.

The single best diagnostic for this is comparing the current curve against the curve the same machine produced when it was newer. Most shops do not have a baseline curve. That is why we recommend recording one any time we do a [Mazak spindle rebuild](/spindle-grinding/mazak-spindle-repair/) or [Okuma spindle rebuild](/spindle-grinding/okuma-spindle-repair/). The post-rebuild curve becomes the reference for everything after.

## When the thermal pattern changes

The most useful single signal is a thermal pattern that changed. The spindle has run for 5 years with a known soak-time curve. Last month, the curve shifted. The growth rate is higher. The flat zone arrives later. The dimensional drift on long production runs has become noticeable for the first time.

Almost every time we have seen this pattern, the spindle was in early bearing or preload failure. The bearings were not yet making audible noise. The runout had not yet climbed past the [end-of-life threshold described in the runout measurement piece](/insights/spindle-diagnostics/spindle-runout-measurement/). But the thermal behavior had changed, and the thermal behavior was the early signal.

The fix at that stage is usually a clean bench rebuild. The kind described in [the rebuild-vs-replace economics piece](/insights/spindle-diagnostics/rebuild-vs-replace-spindle-economics/). Catching it before the bearings progress saves the spindle.

## Sources & references

- Thermal growth coefficients follow standard machine-tool thermal behavior literature, plus our measurements on production-class spindles in the 2023 to 2025 service log.
- The 30-minute soak-time test is a practical working procedure derived from ISO 230-3 thermal performance test standards.
- The 15-25 micron range is approximate. Specific numbers vary by platform, machine size, and ambient conditions.

## When to bring this work to us

If your dimensional drift on long production runs has changed, or if your thermal compensation seems to have stopped working, the cheapest first step is a soak-time test run by your operators with a dial indicator. If the curve looks abnormal compared to what you remember, the next step is a field diagnostic visit.

[Get a quote](/get-a-quote/) with the machine model, the dimensional drift numbers you have measured, and the soak-time curve if you have recorded one.
