---
title: "Belt-Driven vs. Integral-Motor Spindles: Failure Differences"
slug: "belt-vs-integral-motor-spindles"
pillar: "spindle-diagnostics"
target_query: "belt driven vs integral spindle"
description: "Belt-driven spindles and integral-motor spindles fail in different ways and demand different rebuild paths. Failure-mode frequencies, repair scope, and what each drive type tells you before you call us."
author: "Ken — Midwest CNC Services"
date: "2026-05-27"
signal_signature: "belt-driven spindle; integral-motor cartridge; motor winding; coupling alignment; belt slip"
---

## Key Takeaways

- Belt-driven and integral-motor spindles are different machines under the hood. Belt-driven uses an external motor with a belt-and-pulley to the spindle shaft. Integral-motor cartridge designs put the motor windings inside the spindle housing.
- Belt-driven spindles fail mostly at the bearings. Roughly 80 percent of belt-driven rebuilds we see are bearing-related. The motor itself rarely needs work because it lives outside the spindle.
- Integral-motor spindles fail at the bearings AND at the motor. About 65 percent are bearing failures; another 15 percent involve motor winding damage. The remaining 20 percent are mixed or other.
- The rebuild path is different. Belt-driven rebuilds are usually a clean bearing-set swap on the spindle alone. Integral-motor rebuilds often involve the motor stator, the rotor, or the cooling jacket, in addition to the bearings.
- Cost difference is meaningful. A typical belt-driven rebuild on a production VMC lands $4,500 to $7,500. A comparable integral-motor cartridge rebuild lands $9,000 to $14,000, and replacement cartridges run $18,000 to $45,000 depending on the platform.

When a spindle is on the bench for diagnosis, the first question we ask is which drive type we have. Belt-driven? Or integral-motor cartridge? The two designs fail at different rates in different places. They take different rebuild paths. The cost ranges are different. The same symptom on the shop's end can lead to very different repair quotes. This piece walks the differences.

## The two designs in 200 words

A belt-driven spindle uses an external motor mounted to the headstock. A belt connects the motor pulley to a pulley on the spindle shaft. The motor sits outside the housing. Bearings inside the housing support the shaft. The work happens at the front of the shaft.

An integral-motor spindle works differently. The motor rotor lives on the spindle shaft itself. The motor windings live inside the spindle housing. The whole thing is one cartridge. No belt. No pulleys. No external motor. The spindle is its own motor.

Belt-driven designs are most common on lower-RPM mill spindles, production lathes, and older platforms. Integral-motor designs are most common on higher-RPM mill spindles and modern multitasking platforms. The [Mazak Integrex](/repairs/mazak-cnc-machine-repair/integrex/) and [DMG Mori NTX](/repairs/dmg-mori-cnc-machine-repair/ntx/) are common examples. Grinding spindles also use integral-motor designs.

## Failure-mode frequencies, belt-driven

Belt-driven failures concentrate on the bearing side. About 80 percent of belt-driven rebuilds come in for bearing damage of some kind. The [bearing failure modes piece](/insights/spindle-diagnostics/spindle-bearing-failure-modes/) covers what each kind looks like.

The other 20 percent breaks down like this. Belt-related issues account for about 10 percent. Belt slip. Belt wear. Broken belt. Pulley wear. Coupling alignment problems between the motor and the spindle pulley account for about 5 percent. The last 5 percent is mixed. Drawbar issues. Seal failures. Other.

The motor itself rarely needs rebuild work. The motor lives outside the spindle housing. It is its own serviceable unit. When a motor on a belt-driven machine fails, the motor gets replaced. The spindle does not have to come apart.

## Failure-mode frequencies, integral-motor

Integral-motor failures are more distributed. About 65 percent are bearing-related. Another 15 percent involve the motor windings or the rotor. The rest is mixed. Cooling jacket failures. Encoder issues. Sensor problems. Combination failures where two or three things went wrong at once.

Motor failures on integral-motor spindles are the diagnostic challenge. The motor winding lives inside the spindle housing. Heat affects it. Vibration affects it. Contamination affects it. When the windings fail, the spindle has to come apart for the motor work. The bearings come out at the same time. The rebuild scope expands.

Cooling jacket failures on integral-motor spindles are an underrated cause. The jacket keeps the motor windings within their temperature limits. When it starts to leak, or the cooling flow gets restricted, the windings run hotter than they should. The windings then fail early.

## Rebuild path differences

The rebuild work is different between the two designs. The planning differs too.

**Belt-driven rebuild.** Remove the spindle. Pull the bearings. Inspect the shaft and housing. Replace the bearing set. Verify runout and balance. Reinstall. Verify belt alignment and tension at reinstall. Total bench time is usually 2 to 4 days. Cost is usually $4,500 to $7,500 on a production VMC.

**Integral-motor rebuild.** Remove the cartridge. Disassemble. Inspect the rotor and the stator windings. Inspect the cooling jacket. Inspect the bearings. Repair or replace whichever subsystem is damaged. Verify the assembly. Bench time is usually 5 to 10 days for a clean job. Longer if motor work is needed. Cost is usually $9,000 to $14,000 on a production VMC. Higher on multitasking platforms.

The second pattern is why we ask about the drive type before quoting. The same symptom can be a 4-day bench job or a 10-day one.

## When belt-driven becomes integral, and vice versa

A few platforms have offered both drive types across generations. Older [Mazak](/spindle-grinding/mazak-spindle-repair/) and [Haas](/spindle-grinding/haas-spindle-repair/) VMCs were mostly belt-driven. Newer generations shifted to integral-motor in higher-RPM configurations. Knowing which generation you have is part of the diagnostic conversation.

You can usually tell from outside. A belt-driven spindle has an external motor visible on or behind the headstock. There is usually an access panel that exposes the belt for service. An integral-motor spindle has no external motor on the spindle line. The spindle simply terminates at the rear without a separate motor housing.

If you cannot tell from external inspection, the machine documentation will say. Or the spindle parameter screen on a modern control will list the drive type.

## Diagnostic implications

The drive type affects how we interpret some of the standard diagnostic signals.

**Vibration.** Belt-driven vibration has extra sources. The belt itself. The motor itself. A worn pulley keyway can produce vibration that looks bearing-shaped on a meter. But it comes from the motor side. Integral-motor designs do not have this confounder. Vibration on an integral-motor spindle is almost always inside the cartridge.

**Thermal behavior.** Integral-motor spindles run hotter than belt-driven ones. The motor heat is generated inside the housing. The [thermal growth piece](/insights/spindle-diagnostics/spindle-thermal-growth/) covers the soak-time test. The expected total growth is higher on integral-motor designs.

**Noise patterns.** Belt-driven spindles can make a sound that scales with motor RPM. The sound is often belt-and-pulley noise, not bearing noise. Integral-motor designs do not have this source.

## Sources & references

- Drive type failure frequencies are from Midwest CNC Services rebuild log across the 2023 to 2025 period, separated by drive type.
- Bench time and cost ranges reflect actual rebuild jobs in that same period. Specific quotes vary by platform, generation, and the scope of any motor-side work that is needed.
- Drive type identification follows manufacturer documentation for the Mazak, Haas, Okuma, and DMG Mori platforms we service.

## A practical note on planning rebuilds

The drive type changes how shops should think about rebuild planning. A belt-driven spindle on a 12-year-old production VMC is usually a cheap rebuild. A bearing set replacement, some belt work, an alignment check. Total downtime is short. The decision to rebuild is straightforward.

An integral-motor cartridge on the same vintage of machine is a different conversation. The bearing rebuild is still possible. But the motor side of the cartridge ages too. The cooling jacket can degrade. The windings can develop insulation breakdown over thousands of hours. A "bearing rebuild" on an integral-motor that turns out to need motor work as well jumps in cost and lead time. We always inspect the motor side during an integral-motor rebuild for exactly this reason.

## When to bring this work to us

If a spindle problem has come up and you are not sure whether you have a belt-driven or integral-motor design, let us know the machine model when you call. We can usually tell from the model alone. The drive type changes both the diagnostic flow and the cost expectation.

[Get a quote](/get-a-quote/) with the machine model and the symptoms you are seeing. We will come back with a quote scoped to the drive type you actually have.
