---
title: "Spindle Taper Damage: When It Can Be Salvaged"
slug: "spindle-taper-damage"
pillar: "spindle-diagnostics"
target_query: "damaged cnc spindle taper"
description: "When a damaged spindle taper can be reground and when it cannot. BT vs HSK vs Capto regrindability, the depth-and-pattern call, and what salvageability actually costs."
author: "Ken — Midwest CNC Services"
date: "2026-05-27"
signal_signature: "BT taper; HSK taper; Capto taper; regrind; taper face"
---

## Key Takeaways

- BT, HSK, and Capto tapers have very different regrindability. A BT taper with light damage is almost always salvageable. An HSK taper with the same damage is sometimes salvageable. A Capto taper rarely is.
- The depth of the damage is the first thing we measure. Surface marks under 0.001 inch deep usually regrind cleanly. Damage past 0.003 inch starts to push the taper out of geometry tolerance even after a regrind.
- The pattern of the damage matters as much as the depth. A small isolated mark is easier to recover than a wide pattern spread across the contact face.
- A taper that has lost its draw-in geometry — where the holder no longer pulls fully against the face — is past the point a regrind can fix. The spindle nose itself needs replacement at that point.
- The cost split is roughly 4-to-1. A clean taper regrind on a BT-style spindle typically runs $1,200 to $3,000. A full spindle-nose replacement runs $8,000 to $14,000 once you include the work of pressing out and reseating the shaft.

A damaged spindle taper is one of the few things on a CNC machine where the decision is almost binary. The taper is either inside the geometry the holder needs, or it is not. Surface marks that look bad can sometimes regrind into a clean usable taper. Tapers that look only mildly damaged sometimes turn out to have shifted geometry that no regrind will restore. This piece walks how we sort the two, on BT, HSK, and Capto interfaces.

## What a spindle taper actually does

The taper is the precision conical bore in the front of the spindle. The tool holder seats into it. Two surfaces matter. The taper itself, which centers the holder. And the face, which the holder draws against to set axial position. The combination is what keeps a tool concentric and rigid against cutting load.

Damage to either surface reduces the connection's stiffness, its concentricity, or both. The result on the part is some combination of poor surface finish, chatter, dimensional drift, and tool life that drops below normal. The [vibration symptom decoder](/insights/spindle-diagnostics/diagnose-cnc-spindle-vibration/) and the [runout measurement procedure](/insights/spindle-diagnostics/spindle-runout-measurement/) usually catch taper damage as runout that does not respond to a tooling swap.

## BT taper damage and regrindability

BT tapers are the most forgiving of the three common interfaces. The 7-in-24 cone is shallow enough that mild surface damage can be reground without losing the geometry the holder needs.

We see three damage patterns on BT tapers. A small isolated mark, usually from a chip or hard particle that got pulled into the taper. A circumferential rub, usually from a holder that was inserted at an angle. And generalized wear across the whole contact face, usually from long service life on a high-cycle machine.

The first two are usually salvageable. A BT taper with a surface mark under 0.001 inch deep, in one isolated location, will regrind cleanly. The cost is in the $1,200 to $2,500 range for the regrind itself, sometimes higher if the spindle has to be pulled and shipped. The third pattern — generalized wear — is harder to call. It depends on whether the wear has shifted the cone geometry or just thinned the surface uniformly.

## HSK taper damage

HSK is a hollow shank interface with a face contact. Damage to the cone is recoverable in some cases. Damage to the face contact is much harder.

The HSK design draws the holder hard against the spindle face, which loads both the cone and the face simultaneously. The face is where most of the rigidity comes from. When that face wears or gets dented, the holder no longer makes full contact, and the rigidity drops faster than the cone alone would explain.

We can sometimes regrind an HSK taper with light cone damage if the face is still flat. We rarely regrind an HSK taper with face damage. The face geometry is what makes HSK work. Once it is gone, the spindle nose usually needs replacement. On a multitasking platform like an [Integrex](/repairs/mazak-cnc-machine-repair/integrex/) or a [DMG Mori NTX](/repairs/dmg-mori-cnc-machine-repair/ntx/), where HSK is common, that pushes the rebuild into the higher cost range described in [the rebuild-vs-replace economics](/insights/spindle-diagnostics/rebuild-vs-replace-spindle-economics/) piece.

## Capto taper damage

Capto is a polygonal taper, not a cone. The geometry that gives it its load capacity also makes it the least forgiving to regrind. The flat sections that the holder seats against are at specific angles. Once those angles shift, no amount of surface conditioning brings them back.

We rarely accept a Capto regrind job. The few times we have, it was because the damage was confined to a single flat and the geometry of the other flats was perfect. Even then, the result was marginal. Most Capto spindles with taper damage become spindle-nose replacement jobs rather than regrind jobs.

This is the practical reason Capto tapers are most often found on multitasking and live-tooling lathe spindles where the machine builder expected long service life and built in margin around taper protection. The interfaces are excellent when healthy. They are unforgiving when damaged.

## Reading the damage on the bench

When a spindle comes in with reported taper damage, the first measurements we take are these.

The taper face. Indicated against a master plug or a precision ring. The TIR tells us if the face is square to the spindle axis. Out of square means the spindle nose has shifted, not just the taper surface.

The taper bore at multiple depths. We indicate at the entry, the middle, and the deep end of the taper. Three uniform readings mean the taper has worn but kept its angle. Variable readings across the depth mean the angle has shifted, which is harder to fix.

The draw-in distance. A holder is inserted by hand and the position is measured. Then the drawbar is engaged. The change in position is the draw-in. A taper that has lost draw-in geometry pulls the holder in further than the original spec, which means the holder is bottoming on the face or losing contact with the cone before it should. That pattern usually means spindle-nose replacement.

## When regrind is the right call

Regrind wins when the damage is shallow, localized, and the geometry is still inside tolerance after the cut. On BT tapers, that covers most surface marks under 0.001 inch deep. On HSK, it covers cone-only damage with a clean face. On Capto, it almost never applies.

The cost-and-time picture for a regrind is friendly. The spindle does not have to be torn down all the way. The work is precision grinding against a master, and the verification is straightforward. Most regrind jobs we complete are back in the shop's hands inside two to three weeks.

## When replacement is the right call

Replacement wins when the geometry has shifted, when face damage is present on an HSK, when any meaningful damage is on a Capto, or when the regrind would push the taper outside the holder manufacturer's tolerance.

Replacement is expensive because it usually means pulling the shaft, replacing the spindle nose (or in some cases the full shaft assembly), and rebuilding the bearing stack along with it. The full bench rebuild is described in the [Mazak spindle service](/spindle-grinding/mazak-spindle-repair/) and [Okuma spindle service](/spindle-grinding/okuma-spindle-repair/) pages. Cost is usually in the $8,000 to $14,000 range on a typical VMC, higher on multitasking platforms.

## Sources & references

- Taper geometry tolerances follow the ISO and ANSI standards for BT, HSK, and Capto interfaces (we work to those tolerances at the bench without claiming a separate certification).
- Damage-depth thresholds and cost ranges reflect work in the Midwest CNC Services service log over the 2023 to 2025 period.
- The 0.001-inch and 0.003-inch thresholds are practical working numbers. Exact limits vary by taper size and by the holder system the shop uses.

## When to bring this work to us

If you suspect taper damage, the first step is the runout-trend conversation. Damage to the taper usually shows up in runout numbers before it shows up as visible marks. If the runout has climbed and the tool swap test does not bring it back, the taper is the likely cause.

[Get a quote](/get-a-quote/) with the machine model, the taper interface (BT, HSK, or Capto), the runout numbers you have measured, and any photo of the visible damage you can share.
