---
title: "Spindle Preload Loss: Symptoms and Diagnostic Procedure"
slug: "spindle-preload-loss"
pillar: "spindle-diagnostics"
target_query: "spindle preload loss"
description: "Spindle preload loss looks like bearing damage on most diagnostics but the fix is different. The load-vs-runout decision tree, what preload loss feels like, and why it is often the easier rebuild."
author: "Ken — Midwest CNC Services"
date: "2026-05-27"
signal_signature: "preload loss; angular contact bearing; preload spacer; load-vs-runout; preload spring stack"
---

## Key Takeaways

- Preload loss is the gradual loss of axial force holding the spindle bearing set. It looks like bearing damage on most external diagnostics. The underlying fix is different.
- The classic preload-loss signal is loud cold, quiet warm. The spindle sounds rough on cold start. It then quiets down once thermal expansion has closed the gap.
- The load-vs-runout decision tree separates preload loss from bearing damage in under 1 hour. Preload loss shows runout that improves under axial load. Bearing damage does not.
- Most CNC spindles use 1 of 3 preload mechanisms: a precision spacer, a spring stack, or hydraulic preload. Each fails differently and each is restored differently.
- A clean preload restoration is usually the cheaper rebuild. The bearing races are often still healthy. The fix is restoring axial force, not replacing the bearings.

Preload loss is one of the spindle failure modes that is easiest to misdiagnose. It produces symptoms identical to bearing damage on most external diagnostics. Vibration goes up. Runout climbs. Surface finish degrades. The shop sees those symptoms and assumes bearings. A bench teardown then sometimes reveals bearings that are still healthy. The preload was the problem, not the bearings. This piece walks the symptoms, the diagnostic procedure, and the 3 preload mechanisms we restore on Mazak, Haas, Okuma, and DMG Mori spindles.

## What preload actually is

Angular contact bearings need a specific axial load to work right. The load presses the rolling elements against the race at a defined contact angle. That gives the bearing its load capacity and its stiffness. Without preload, the bearing can rotate. But it does not have its design stiffness. It does not have its design load capacity.

Spindle bearings come from the factory preloaded. The preload is set during initial assembly. It is held by one of three mechanisms through the spindle's service life. Over time, preload can degrade. The reasons depend on the mechanism.

When preload drops below the design value, the bearing acts erratically. Stiffness varies with temperature and load. Vibration goes up. Runout climbs. The symptoms look like a bearing failure. But the actual bearing races may still be in good condition.

## The classic loud-cold-quiet-warm signal

The most distinctive preload-loss signal is a noise pattern that varies with temperature. The spindle sounds rough on cold start. As it warms up, the noise reduces. By the time the machine has reached operating temperature, the spindle sounds normal again.

The mechanism is thermal expansion. When the spindle is cold, the gap between the bearing components is at its widest. The preload, if reduced, is at its weakest. The bearing rattles within that gap and produces audible noise. As the spindle warms, the components expand. The gap closes. The contact force increases. The noise drops.

This pattern is distinct from bearing damage, where the noise either stays constant with temperature or gets worse as the spindle warms. The [cold-start noise piece](/insights/spindle-diagnostics/cold-start-spindle-noise/) covers the timing of normal cold-start behavior versus what preload loss looks like over the warm-up curve.

If your spindle has the loud-cold-quiet-warm pattern that returns each morning, preload is the most likely cause.

## The load-vs-runout decision tree

The diagnostic procedure that separates preload loss from bearing damage uses [runout measurements](/insights/spindle-diagnostics/spindle-runout-measurement/) under two conditions.

**Condition 1: runout under no axial load.** Indicate the spindle nose with a known-good test bar. Run the spindle at low RPM. Record the runout.

**Condition 2: runout under axial load.** Apply a known axial force to the spindle. Most often we use a lightly loaded drawbar, but a calibrated axial force application works too. Re-indicate. Record the new runout.

A healthy bearing produces similar runout in both conditions. A damaged bearing produces poor runout in both. Preload loss produces a specific pattern: high runout under no load, lower runout under axial load. The axial load is temporarily restoring what the preload mechanism should be providing continuously.

When we see that pattern on the bench, the diagnostic conversation shifts to preload restoration rather than bearing replacement. The cost and lead-time picture changes accordingly.

## Three preload mechanisms

**Precision spacer preload.** A precisely-machined spacer sits between the bearings. The spacer length determines the preload. This mechanism is common on production VMC spindles. It is the most stable over time. When it fails, the failure is usually catastrophic. A crash event. A contamination event. A manufacturing defect. Otherwise it does not degrade gradually.

**Spring stack preload.** A stack of disc springs or coil springs applies the axial force. This is common on integral-motor cartridges and on some grinding spindles. Spring stacks fatigue with cycling. Similar to the [Belleville stacks in drawbars](/insights/spindle-diagnostics/spindle-drawbar-diagnostics/). The preload decreases gradually as the spring constants drop. We see this most often on machines past 12 years of production duty.

**Hydraulic preload.** A hydraulic mechanism continuously applies axial force. Sometimes with closed-loop control. This is the most active preload type. It is common on high-end multitasking platforms. Also on some precision grinding spindles. When the hydraulic system fails — leaks, pump failures, sensor drift — preload drops fast. The diagnostic is usually obvious. The hydraulic system has its own alarms.

The mechanism your spindle uses determines what we look at on the bench and what the restoration costs.

## What restoration involves

For a precision-spacer spindle, restoration means measuring the existing spacer. We determine what spacer length would restore the design preload. We install a new spacer. The bench work is straightforward once we have the spacer. The bearing set normally stays. Unless it has been damaged by the loss of preload.

For a spring-stack spindle, restoration means replacing the spring stack with a fresh set. The new stack restores the design preload. As with the spacer case, the bearings stay if they are still healthy.

For a hydraulic-preload spindle, restoration is usually a repair of the hydraulic system. Not a bench rebuild. The bearings normally do not need attention.

In all three cases, the rebuild path is much cheaper than a full bearing set replacement. We cover the cost difference in [the rebuild-vs-replace economics piece](/insights/spindle-diagnostics/rebuild-vs-replace-spindle-economics/). When the diagnostic isolates preload loss instead of bearing damage, the savings can be 40 to 60 percent.

## Why this matters for shops

The reason this matters is the misdiagnosis cost. A shop that sees vibration, runout climb, and noise sometimes goes directly to a bearing rebuild quote. If the actual cause was preload loss, the bearing rebuild is overscope for the problem. The shop pays for bearings that did not need replacement.

We diagnose before quoting whenever the symptoms are consistent with preload loss. The diagnostic adds an hour to the process. It can save thousands of dollars on the rebuild.

For shops planning rebuilds against the [spindle-rebuild lead-time](/insights/spindle-diagnostics/spindle-rebuild-lead-time/) calendar, knowing whether the work is preload restoration versus full bearing replacement also affects the lead time estimate. Preload work is usually on the fast lane of that timeline.

## Sources & references

- Preload mechanism descriptions follow standard bearing-system design literature.
- The load-vs-runout decision tree is a working procedure we use at the bench. It is derived from standard spindle metrology practice.
- Failure-rate observations by mechanism type are from Midwest CNC Services rebuild log across the 2023 to 2025 period.

## When to bring this work to us

If your spindle has the loud-cold-quiet-warm pattern, or if your runout under load is materially different from your runout without load, preload is the likely cause. The fix is usually cheaper and faster than a full bearing rebuild.

[Get a quote](/get-a-quote/) with the machine model, the symptoms you are seeing, and whether the noise pattern changes with warm-up.
