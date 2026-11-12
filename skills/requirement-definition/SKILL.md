---
name: requirement-definition
description: >
  Tag individual source-referenced parameters and behaviors needed to build a
  behavioral ngspice model
  from a complete operational-amplifier or voltage-supervisor/reset-IC PDF.
  Inventory every figure and table as a locator, distinguish needed from unneeded
  named information, describe ngspice-aware modeling techniques, and report
  genuinely absent
  required information separately. Do not extract device values. Use for
  /requirement-definition.
---

# Behavioral SPICE Requirement Definition

## Scope and Source Review

This is a selection and handoff, not data extraction. Identify the information
needed for a pin-level behavioral ngspice subcircuit using supported controlled
sources, loading, clamps, states and timing. Do not make a netlist, fit or
simulate a model, make a workbook, or claim verified behavior.

1. Require a complete, readable datasheet PDF. Read every page, including all
   figures, tables, captions, footnotes, functional descriptions, pin definitions
   and operating constraints. Pasted text or excerpts may clarify a request but
   are not a substitute for the PDF. If pages or sources cannot be inspected well
   enough to inventory them and select the part accurately, return a blocker to
   the parent without writing either report. Do not treat unreadable information
   as absent.
2. Identify the manufacturer, PDF identity/revision, exact selected part,
   variant, package, grade, channel or threshold option, and requested scope.
   Record reviewed-page coverage. Do not mix variant options, channels, grades,
   test configurations or different limit classes. If the selection or family
   cannot be resolved from the source and request, return a blocker to the parent.
3. Detect the family from functional description, pins and characteristics:
   operational amplifier or voltage supervisor/reset IC. Follow only the
   corresponding conditional procedure below. Return unsupported families to
   the parent without inventing a generic procedure.
4. Respect the requested analyses and pin-level behaviors. When no scope is
   supplied, explicitly mark provisional nominal DC/AC/transient coverage as a
   `SCOPE ASSUMPTION`, not a datasheet fact. Include noise or temperature needs
   only where requested or relevant to the stated scope; note the fidelity cost
   of omitting them without inventing a requirement for an absent feature.
5. Before writing, verify that the PDF can support a complete source inventory
   and that both destination filenames are available. Return missing/inaccessible
   PDF, incomplete coverage, unresolved selection, and output conflicts to the
   parent, not directly to the user. Write neither report when blocked.

## Tagging and Evidence Rules

For the selected part and scope, register **every figure and table** in the PDF,
including packaging, stress, other-variant and otherwise irrelevant sources. Use
the PDF's own page and figure/table identifier (or a descriptive locator if it
has no identifier). Order the single inventory by page, then source identifier.
Sources are locators, **not** the unit of the needed/not-needed decision. Within
each source, tag every distinct named parameter, curve/series, timing event,
pin fact, functional behavior or other information item relevant to deciding
the handoff; split mixed sources into separately named items. Do not replace
parameter names with "electrical characteristics," "whole table," or "all
curves." For unrelated administrative or mechanical material, name the actual
category of information excluded rather than inventing electrical parameters.
Give each item a tag, short reason and route:

| Parameter tag | Meaning and route |
|---|---|
| `NEEDED` | This named item applies to the selected part and scope; route to Information Needed for downstream extraction. It was **not** extracted here. |
| `NOT NEEDED` | This named item is inapplicable to this part or outside the requested modeling scope; route to Information Not Needed with a specific reason. |

For example, an electrical table may have propagation delay tagged `NEEDED`
and a separately named input-low voltage tagged `NOT NEEDED` **only if** that
input threshold is genuinely irrelevant to the selected part and requested
behavior. This example is not a rule that either parameter is always needed or
unneeded: for a supervisor with a manual-reset input, its input-low voltage may
be needed to define input recognition. Decide independently for each parameter.
Different rows/curves/variants/conditions may need distinct tags even when they
share a source. If the same parameter appears in multiple sources, cite each
applicable source without treating duplicates as different modeling requirements.

Use non-numeric qualifiers such as selected variant, channel, direction, limit
class, pin, state, test-condition *type*, and applicable footnote. Do not copy
test conditions, limits, points, or plotted coordinates. Identify relevant
prose, pin definitions, functional operating constraints and notes as named
information needs with page/section locators. Record irrelevant prose only when
it explains an exclusion; do not treat pin functions or functional operating
limits as automatically irrelevant.

`NOT SPECIFIED` is reserved for required, applicable named information genuinely
absent after the **complete** PDF review. Put it only in the missing-data
report. A graph with the needed curve present is available for downstream
extraction even if no table gives the information; tag its named curve `NEEDED`
in the main report. A missing parameter for a selected variant may still be
absent even if another variant has it. An unreadable source or ambiguous part is a blocker,
not `NOT SPECIFIED`. A feature absent from the part or omitted from scope
does not create a missing-data entry.

Never transcribe, approximate, derive, calculate, digitize, or report any
device-specific electrical or graph values. Never supply numeric formulas,
sample values, replacement numbers, numeric test conditions, or simulator
validation claims. Figure/table IDs, page numbers, part/package/revision
identifiers, parameter and condition names, and report counts are locators,
not modeling data. Do not convert stress ratings into functional limits, infer
zero or symmetry from silence, or assert a characteristic from a technology
label. Separately label authorized modeling assumptions with their origin and
limitations; they do not change a `NOT SPECIFIED` item into PDF evidence.

## Conditional Procedure: Operational Amplifier

### Identification

Tag documented feedback topology (voltage or current feedback), input
technology, rail-to-rail claims and qualifiers, amplifier count, pin mapping,
shutdown or enable behavior if present, and functional supply configuration.
Specify whether the requested behavior is for one selected channel or the
whole package. Do not infer input currents or rail behavior from topology or
process claims alone; exclude other-channel sources only if they cannot inform
the selected channel.

### Input Stage

Look for input offset and drift, input bias and offset currents with sign and
reference conventions, differential/common-mode resistance and capacitance
with pin definitions, common-mode operating range, and documented behavior
outside it. Tag input crossover, phase reversal, protection and overload
behavior only where stated or needed. A range limit does not prove a hard clamp
or phase reversal; an unsigned current difference does not define each pin's
current direction. Identify relevant curves and conditions by name, not values.

### Gain and Frequency Stage

Look for open-loop gain, gain-bandwidth or unity-gain response, phase margin
with noise gain and load qualifiers, stable-gain restrictions, open-loop
gain/phase plots, and load-dependent stability evidence. Name the source
information a downstream builder would need to choose pole/zero behavior:
low-frequency gain, actual loop crossover and phase behavior, feedback topology,
compensation and test configuration. A simple dominant-pole or two-pole
approximation is only a conditional modeling technique; do not infer a pole
    from phase margin alone, equate unity frequency with gain-bandwidth without
support, or force voltage-feedback assumptions onto current-feedback parts.
For current feedback, look for transimpedance and feedback-resistor-dependent
response instead. Flag unsupported pole shaping as a fidelity limit or, if
required information is absent, a missing-data entry; do not compute poles.

### Slew and Output Stage

Look for directional slew behavior, output swing or rail headroom by load,
source/sink functional drive capability, output impedance with frequency and
loop-state qualifiers, settling/overload recovery and capacitive-load behavior
when relevant. Source/sink asymmetry and supply/load conditions matter. A
short-circuit test does not establish a guaranteed linear drive limit. If a
downstream slew-limited stage is proposed, name its scaling and dynamic-state
evidence needs; do not calculate an internal charging current. Distinguish
open-loop output resistance from load regulation near saturation. Neither a
gain/bandwidth/input-capacitance combination nor a headroom slope establishes
open-loop output resistance without architectural evidence.

### Common-Mode and Supply Rejection Stage

Look for common-mode and supply rejection, frequency-dependent rejection,
positive/negative supply distinctions, measurement definitions and reference
conditions. Rejection falling with frequency implies increasing error coupling;
do not propose shaping that instead improves rejection at high frequency.
List the transfer and sign/phase evidence needed for an input-referred error
stage. Do not calculate error amplitudes or corner frequencies.

### Noise Stage (when relevant)

Look for input voltage/current noise density, low-frequency noise, spectral
curves, flicker behavior, bandwidth/measurement qualifiers and source-impedance
context. Spectral density is not a transient amplitude and peak-to-peak noise
does not by itself specify RMS behavior. Name the noise spectrum and simulator
noise-source support needed downstream, without reading curve points or
deriving a flicker corner. Do not presume a particular behavioral source
supports noise in the target simulator.

### Op-Amp Modeling Techniques and Gaps

Map applicable input sources/loading, finite-gain controlled sources, dynamic
response shaping, slew limiting, load-dependent clamps or current limiting,
rejection error injection and noise shaping to **named source inputs**. Prefer
ngspice core controlled sources and explicit R/C dynamic stages where suitable;
do not suggest a generic E-source `LAPLACE` element. `s_xfer` requires XSPICE
and is only a conditional option if the target build and analyses support it.
For noise distinguish ngspice `.noise`-recognized elements from deterministic
behavioral or transient noise sources; do not assume they are interchangeable.
Describe dependencies, ngspice support, fidelity limits, and stages blocked for
lack of evidence, without values or implementation equations. Temperature behavior
and enable states need source support. Convergence aids are implementation
choices, not datasheet characteristics.

Assign missing-information priority based on requested scope: frequency
response may be CRITICAL for AC; gain, input error, common-mode range, slew,
swing and rejection may be HIGH when their behavior matters. Input loading,
output resistance, rejection roll-off, drift and noise importance depends on
the analyses. Ask for manufacturer evidence or characterization rather than
defaults; do not create gaps for unrequested noise or temperature fidelity.

## Conditional Procedure: Voltage Supervisor / Reset IC

### Identification

Tag selected threshold options and channels, sense and supply pins, fixed or
adjustable configuration, reset output topology/polarity, truth table, and
documented manual reset, watchdog and enable features. Name per-channel
requirements and combined-reset logic only where applicable. Crossing
direction is not the same as assert/deassert: use the device's actual truth
table instead of assuming polarity or event mapping.

### Threshold Comparator Stage

Look for rising/falling thresholds, hysteresis and convention, threshold
accuracy and drift, sense reference, and adjustable-device divider/loading
information. Tag only rows/curves and footnotes for the selected option and
channels. A single threshold does not establish an unreported crossing, zero
hysteresis or symmetry. If both crossings or a documented convention are
required to model behavior, identify those inputs for downstream analysis;
do not derive a threshold. A hysteretic comparator needs ngspice-supported
state and initialization, not an unevidenced algebraic latch. Temperature
and tolerance sweeps depend on functional evidence.

### Timing and Delay Stage

Look for assertion and release timing, startup/power-on reset behavior, glitch
rejection, overdrive and ramp-rate dependence, programmable timing,
retriggering and initial-state definitions. Keep distinct timing events
distinct; do not add delays that describe the same event. A timer or event-
based approach needs documented paths and initial conditions. Name timer
relationship evidence without calculating RC values, delays or trip levels.
An arbitrary simulator initialization does not establish startup fidelity.
Prefer a core ngspice analog state/timing realization where evidence supports
one; XSPICE event or hysteresis code models are conditional on an enabled build.

### Output Driver Stage

Look for output-state voltage under load, functional source/sink behavior,
off-state leakage, output capacitance where relevant, low-supply reset validity,
output-supply behavior and power-down state. For open-drain outputs an external
pull-up establishes the high state; do not require a driven high-state
specification. A logic-level test current is not proof of a current limit.
For downstream finite-impedance drivers, distinguish load-point behavior from
functional limits; do not calculate on-resistance or assume symmetric drive.

### Supply and Sense Stage

Look for functional supply operating range, supply current by state and
conditions, documented low-supply validity behavior, sense pin loading and
leakage. Supply operating minimum does not by itself define reset validity or
an internal comparator threshold. Gate the proposed behavior only as the
functional description supports it; do not invent a secondary comparator or
use absolute-maximum stress ratings as functional targets.

### Optional Manual Reset and Watchdog

If manual reset is absent from the selected part, omit its requirements, gaps
and techniques. If present, look for pin polarity, logic-level bounds or
directional crossing evidence, documented hysteresis, pull-up, minimum pulse,
debounce/filtering, propagation and release interaction. Logic-level bounds
do not prove exact comparator crossings. Name the inputs needed for reset
logic without making up thresholds.

If watchdog is absent from the selected part, omit its requirements, gaps and
techniques. If present, look for watchdog timeout/reset pulse, valid input
levels and edges, windowing where applicable, startup delay, enable behavior,
retrigger rules and reset interactions. A retriggerable timer or windowed state
machine must follow the documented input rules, not run unconditionally.
Sources dedicated to an absent feature are still inventoried with their named
information tagged `NOT NEEDED`.

### Supervisor Modeling Techniques and Gaps

Map evidenced thresholds/state, separate delays and startup behavior, output
polarity/driver, supply behavior and only present manual reset/watchdog
functions to candidate techniques and named inputs. Note dependencies,
ngspice state/timing support, fidelity limits and evidence-blocked stages.
Do not assume a generic event scheduler, native digital state machine, or
cross-dialect behavioral syntax works in core ngspice; distinguish analog
state/capacitor/switch paths from XSPICE-dependent event code models.
Convergence smoothing cannot replace documented glitch or timing behavior.
Never mix threshold options across variants.

Missing decision thresholds may be CRITICAL for requested reset behavior;
crossings, timing, driver levels and low-supply behavior may be HIGH. Drift,
loading, leakage and supply current priority follows the scope. Manual reset
and watchdog evidence is important only when those features exist and matter
to the analysis. Seek functional data or measurements rather than defaulting
to unstated hysteresis, pull-up or drive behavior.

## Report Contract

Write both Markdown reports in the caller's destination, or the current
working directory if none was specified. Check for **either** existing output
before writing; on any collision return an overwrite blocker to the parent
without writing or replacing either file. Do not migrate old artifacts. Use
the exact selected part in filename-safe form and report any normalization.

`[PartNumber]_required_data_for_behavioral_spice.md` starts with metadata:
selected part/family/variant/package/grade/channel, manufacturer, PDF path and
identity/revision (or not indicated), requested scope and explicitly labeled
scope assumptions, and complete reviewed-page coverage. Directly under that
metadata, include a **single chronological source inventory** of every figure
and table, including sources with no needed content. The inventory is not an
additional top-level report section. Each row is one named information item
(or one named category of non-model material); repeat a source locator for
multiple items. Use columns such as:

| Page and source ID | Named parameter / behavior / content | Parameter tag | Non-numeric qualifiers | Reason / route |
|---|---|---|---|---|

For mixed sources, put needed and unneeded parameters on separate rows. Name
each distinct electrical parameter, direction, timing event, curve or series
that has a different decision; retain variant, channel, condition type, limit
class and footnote qualifiers where applicable. Do not use `INCLUDE`, `PARTIAL`
or `EXCLUDE` as the decision for a source. Sources covering only other variants
still get one or more named `NOT NEEDED` rows with a selection reason. Group
purely mechanical or administrative content by named category if appropriate,
but do not collapse electrical parameters into a category. Relevant prose and
pin facts must also receive individual tags in the sections below (and may be
listed in the inventory if helpful). The inventory is an evidence coverage
index, not a substitute for the parameter-focused sections.
Avoid extra `##` headings in metadata and inventory. Follow with exactly
three top-level report sections, in this order:

1. `## Information Needed for the Behavioral Model`
2. `## Information Not Needed for the Behavioral Model`
3. `## Modeling Techniques`

In Information Needed, list every distinct `NEEDED` named parameter/behavior
by stage with source/page locators, applicable non-numeric qualifiers and the
reason it matters for the requested model. Tag needed prose, individual pin
facts, relevant footnotes and functional operating constraints by page/section
too. Explain that `NEEDED` means **extract downstream**, not extracted now.
A figure's needed curves stay here even if no table includes them. Order cited
sources by page and identifier within each stage where possible; the unified
inventory gives the authoritative PDF-wide source order.

In Information Not Needed, list every `NOT NEEDED` named item from the
inventory, with the same locator and a short scope/variant/function reason;
include parameter-level prose exclusions when relevant. Do not simply say
"unused rows" or "table excluded" where named electrical parameters exist.
Group irrelevant ordering, layout or administrative material by content type
when useful. Do not categorically exclude pin descriptions, operational limits
or application-derived functional evidence; first test relevance to this part
and scope. `NOT NEEDED` is not a synonym for `NOT SPECIFIED`.

In Modeling Techniques, identify **ngspice as the primary target** and map
applicable stages to qualitative behavioral techniques, named needed inputs
and page/figure/table references. For each technique state a plausible ngspice
implementation path (core subcircuit primitives such as supported controlled
sources, R/C state and switches where sufficient; otherwise a clearly
conditional XSPICE/build- or version-dependent path), required analyses,
dependencies, fidelity limitations and stage(s) blocked pending missing
evidence. Do not assume another SPICE dialect's `LAPLACE`, event, hysteresis,
lookup or noise syntax is native ngspice. If the target ngspice version/build
is unknown, do not promise XSPICE or optional features; flag version/build
and syntax verification for downstream implementation. If a core path cannot
cover requested behavior, mark the technique conditional or blocked rather
than pretending it works. Separately label authorized assumptions with origin
and limitations. Do not quote device values, give sample numbers or numeric
equations, include graph read-offs or derived results, make a netlist, or
claim a technique has been validated by simulation.

`[PartNumber]_missing_data.md` contains only applicable required information
that is `NOT SPECIFIED` after the full readable PDF review. Identify the
selected part and scope, then use a checklist such as:

| Missing named information | Status | Modeling stage | Affected behavior / analysis | Priority | Evidence needed / possible characterization |
|---|---|---|---|---|---|

Use `CRITICAL` when core requested behavior cannot be represented; `HIGH` for
material risk to requested results; `MEDIUM` for limited first-pass fidelity;
`LOW` for secondary effects. Priority is scope-dependent, not a device fact.
Request manufacturer evidence or characterization rather than replacement
numbers. Do not put present graph-only data, inapplicable features, or
unreadable material here. If nothing applicable is missing, say so explicitly.
Neither report contains copied electrical values or assumed numbers.

## Return to Parent

After writing both reports, return the selected part/family/scope, PDF page
coverage, figure/table source count and item totals by `NEEDED`/`NOT NEEDED`
(count distinct tagged items, noting repeated citations), number of
`NOT SPECIFIED` information needs, highest missing priority or none, both
report paths, and up to three prioritized evidence requests. If a complete
inventory, readable PDF, unambiguous part, or output paths are unavailable,
write neither report and return the precise blocker to the parent instead.
