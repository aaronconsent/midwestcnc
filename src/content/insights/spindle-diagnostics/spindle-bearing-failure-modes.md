---
title: "Spindle Bearing Failure Modes: Cage, Race, Ball, Retainer"
slug: "spindle-bearing-failure-modes"
pillar: "spindle-diagnostics"
target_query: "spindle bearing failure modes"
description: "Four spindle bearing failure modes — cage, race, ball, and seal — each with a distinct visual signature on the bench. What each pattern says about how the bearing died."
author: "Ken — Midwest CNC Services"
date: "2026-05-27"
signal_signature: "four failure mode categories; race spalling; cage fatigue; brinelling; seal intrusion"
---

## Key Takeaways

- Spindle bearings fail in four broad categories: cage failures, race failures, ball or roller failures, and seal failures. Each has a distinct visual signature on the bench.
- Race spalling is the most common failure mode we see on Mazak, Haas, and Okuma rebuilds. It almost always points to lubrication breakdown or chip ingress.
- Cage fatigue runs second. Pocket wear or pocket cracks usually mean the bearing ran past its design RPM or under load it wasn't sized for.
- True brinelling (impact damage) and false brinelling (idle-period vibration wear) look alike but mean different things. Confusing them sends a quote the wrong way.
- A spindle making noise for less than 30 days is almost always recoverable. Past 90 days, the inner race usually has worn into the shaft. Rebuild scope grows quickly from there.

When a spindle comes apart on our bench, the first thing we look at is which part of the bearing shows the primary damage. Most spindles arrive with more than one thing wrong. But there is almost always one initiating failure that started the cascade. This piece walks the four failure mode categories we see on Mazak, Haas, Okuma, and DMG Mori spindles. What each looks like. What each tells you about how the bearing died.

## The four failure mode categories

Bearing failures fall into four categories. Each category is named for where the damage starts. The cage holds the rolling elements in place. The races are the inner and outer grooves the elements run in. The rolling elements are the balls or rollers themselves. The seals are the lip or labyrinth retainers that keep contaminants out and lubricant in.

Each part fails for different reasons. Each leaves different visual marks. Symptoms outside the spindle can look the same.

When we run the [vibration symptom decoder](/insights/spindle-diagnostics/diagnose-cnc-spindle-vibration/) from outside the machine, we are mostly sorting bearing failure from balance or tooling problems. Once the spindle is on the bench, the question shifts. It is no longer "is the bearing bad." It is "which part of the bearing failed first, and why."

## Race failures: spalling, smearing, and bluing

Race failures account for about half of the bearing rebuilds in our shop log. The most common subtype is race spalling. Small chips of material flake out of the raceway surface. The pock marks grow over time.

Spalling is fatigue damage. The lubricant film thins. Metal touches metal. Microstructural fatigue takes over. Each rolling element passes the same spot tens of millions of times during a normal service life. The cumulative load eventually pops a chip out of the race surface.

Two less common race failures are useful tell-tales. Smearing shows up as a slicked, polished band on the raceway. It means the rolling elements were skidding under high load instead of rolling cleanly. Bluing shows up as a heat-discoloration band across the race. It means local overheating from lubrication breakdown under load.

When we see race spalling, the rebuild scope depends on whether the damage reached the inner race. Outer-race spalling alone is a clean rebuild. Replace the bearing set. Verify the housing bore. Reassemble. Inner-race spalling on the shaft side means the shaft itself may need attention. That moves the job into the higher cost range covered in [the rebuild-vs-replace economics](/insights/spindle-diagnostics/rebuild-vs-replace-spindle-economics/) piece.

## Cage failures: fatigue, pocket wear, and pocket cracks

Cage fatigue runs second in our failure-mode log. The cage holds the rolling elements at the correct spacing around the race. When it fails, the elements bunch up or skid against each other. The bearing degrades fast from there.

Visible signs include pocket wear, where the windows that hold each ball or roller get elongated. Pocket cracks, where small fissures radiate from a pocket edge. Or outright cage breakage.

Cage failures almost always indicate the bearing ran past its design RPM ceiling or under load it wasn't sized for. We see this most often on machines retrofit with higher-RPM spindles without matching the bearing specification. Or on production work that exceeded the original duty-cycle math.

The fix is rarely just "replace the cage." Cage damage usually brings secondary race damage with it. The fix is the full bearing set. The diagnostic conversation often expands. Is the machine being run within its design envelope?

## Ball and roller failures: contamination, thermal, and impact

The rolling elements themselves fail less often than the cage or race. But when they do, the cause is usually one of three things. Contamination. Thermal damage. Impact loading.

Contamination shows up as pitting on the ball surface. Small craters where a hard particle was crushed between ball and race. Thermal damage shows up as discoloration and out-of-round wear. Impact loading shows up as true brinelling. Distinct indentations at the position where the ball sat during a static-load event. Like a crash. Or a heavy tool drop into the spindle taper.

True brinelling is sometimes confused with false brinelling. The two look similar but mean different things. True brinelling shows isolated indentations matching ball positions at the instant of impact. False brinelling shows uniform wear bands across many balls. It is caused by small-amplitude vibration during long idle periods. Often during shipping. Or in machines that sat unused for months. The two failure modes call for different prevention. Crash investigation versus better idle-period vibration isolation.

## Seal failures: the contamination entry path

The fourth category is the one most often overlooked. The seal or labyrinth retainer keeps contaminants out and lubricant in. When it fails, the bearing usually has 200 to 800 hours of service life left before one of the other three failure modes takes over.

We see seal intrusion as the initiating cause behind much of the coolant-related spindle damage on horizontal machining centers and high-pressure-coolant verticals.

Common seal failures: dried-out elastomer lips that no longer wipe cleanly. Contact-seal wear marks where the spinning surface has cut a groove into the lip. Or a damaged seal from a prior service event where it was reinstalled in the wrong orientation. The visible sign is usually that the bearing cavity has darkened with contamination. Even when the seal itself looks intact at a glance.

A spindle with healthy bearings but a marginal seal is on borrowed time. Catching that during a preventive teardown is one of the higher-leverage things we do on a [Mazak spindle service](/spindle-grinding/mazak-spindle-repair/) or [Okuma spindle service](/spindle-grinding/okuma-spindle-repair/) visit.

## What each failure tells you about prior service

The failure mode often points back to how the spindle was run before we got it. Race spalling without seal damage usually means the lubrication system was the weak point. Wrong grease. Missed intervals. A failing pump.

Cage fatigue usually means duty cycle or RPM exceeded specification. Ball contamination usually points at a coolant intrusion event or a seal failure that wasn't caught in time. True brinelling means a crash or a heavy tool drop. False brinelling means the machine sat too long with poor vibration isolation.

These patterns are not a substitute for talking to the shop about machine history. But they are reliable enough that we include them in the bench report we send back with every [spindle rebuild](/spindle-grinding/).

## When the failure is recoverable, and when it isn't

Most bearing failures are recoverable through a rebuild. Replace the bearing set. Verify the housing bore and shaft fit. Reassemble. Verify runout and balance at sign-off. Recoverable cases are roughly 80 percent of what we see.

The non-recoverable cases share a pattern. The failure progressed long enough that the inner race wore into the shaft. Or the outer race wore into the housing bore. Once the shaft or bore is out of tolerance, the rebuild path narrows.

Either the shaft gets reground (possible on some platforms, not on integral-motor spindles). Or the housing gets sleeved (possible but adds cost and risk). Or the spindle becomes a replacement candidate rather than a rebuild candidate.

The single best preventive habit, across every brand we service, is to catch the failure at the first symptom. A spindle noisy for less than 30 days is almost always a clean rebuild. A spindle noisy for six months is almost always at least partly into the non-recoverable category.

## Sources & references

- Failure-mode terminology and visual descriptions follow standard bearing failure analysis literature from SKF, FAG, and NTN.
- Failure-mode frequencies are from the Midwest CNC Services rebuild log across 2023 to 2025.
- The 30-day threshold for clean-rebuild eligibility is approximate. Specific cases depend on the platform, the duty cycle, and which failure category is leading.

## When to bring this work to us

If you have taken a spindle out of service and are deciding whether to ship it in for a teardown, the failure mode you can see from outside is rarely enough to predict what we will find on the bench. The bench is where the four failure categories sort themselves out. The rebuild scope follows from that.

[Get a quote](/get-a-quote/) with the machine model, the symptoms you observed, and how long the spindle was making noise before it came out of service.
