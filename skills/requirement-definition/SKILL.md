---
name: requirement-definition
description: >
  Extract evidence-backed behavioral SPICE model requirements from operational-amplifier
  or voltage-supervisor/reset-IC datasheets. Identify the family, extract applicable
  functional-stage parameters, and write needed/not-needed requirements with modeling
  techniques plus a separate missing-data report. Use for /requirement-definition.
---

# Behavioral SPICE Requirement Definition

## Scope and Source Review

Extract parameters and write Markdown reports only. Do not generate a SPICE model,
fit a model, run simulations, or claim verified model behavior. Behavioral stages
use controlled sources, impedance elements, clamps, state, and timing rather than
transistor-level internal data.

1. Use the supplied PDF path or pasted datasheet text, selected part/package/grade,
   modeling objective, and destination. Read the full accessible source, including
   tables, figures, footnotes, functional descriptions, and pin definitions.
2. Record manufacturer, exact part/variant, revision/date, source path, package,
   pin functions, supply configuration, and applicable conditions. Do not mix
   threshold options, channels, grades, test loads, or typical and guaranteed limits.
3. Identify the family from functional description, pins, and characteristics:
   op-amp (offset, open-loop gain, bandwidth, slew) or supervisor/reset IC
   (voltage detection, reset threshold, delays, watchdog). Execute only the matching
   conditional procedure below, not both.
4. Return missing/inaccessible source, unresolved part selection, ambiguous family,
   or unsupported family to the parent as a precise blocker. Do not ask the user
   directly or guess. For partial pasted text, report the coverage limitation;
   do not claim a parameter is absent from the full datasheet without reviewing it.
5. Filter requirements to this part and the requested analyses. If no objective is
   supplied, explicitly label a provisional nominal pin-level DC/AC/transient scope
   as a scope assumption, not as device evidence. Include noise or temperature
   requirements when relevant; identify omissions and their fidelity limits.

## Evidence Rules

| Status | Meaning and routing |
|---|---|
| EXTRACTED | Explicit table/text specification; main report with table/page or text/page citation |
| GRAPH ONLY | Available only in a figure; main report with figure/page, conditions, approximate read and uncertainty |
| DERIVED | Computed from supported source values; main report with formula, units, input citations and applicability limits |
| NOT SPECIFIED | Required applicable value genuinely absent after full source review; missing-data report only |

Preserve min/typ/max separately, units, temperature, supply, load, frequency,
direction, polarity, and test configuration. Typical values are not guarantees.
Do not fabricate precision for graph reads. If a graph is unreadable, keep the
GRAPH ONLY item in the main report with value unresolved and return the reading
blocker; it is not datasheet-absent. Do not count unresolved readings as extracted.

Keep unknowns unknown. Do not supply generic typical defaults, infer zero from
silence, or treat absolute-maximum stress ratings as functional operating ranges,
threshold tolerances, drive-current limits, or model targets. User-authorized model
assumptions must be separately labeled `USER-AUTHORIZED MODEL ASSUMPTION` in the
modeling discussion with authorization, rationale and limitations; they are not
one of the four evidence statuses and do not remove a NOT SPECIFIED gap.

## Conditional Procedure: Operational Amplifier

### Identification

Record voltage-feedback (VFB) versus current-feedback (CFB), CMOS/bipolar/JFET
input type if documented, rail-to-rail input/output claims and their conditions,
amplifier count, pin mapping, shutdown/enable if present, and supply operating
range/current. Specify whether the requirements cover one channel or the package.
Do not infer bias currents or rail behavior from process/topology names alone.

### Stage 1: Input

| Parameters | Units | Behavioral use |
|---|---|---|
| Vos; dVos/dT | V; V/degC | Series input offset source and supported temperature dependence |
| IB+, IB-, Ios and temperature dependence | A | Input current sources; retain sign/reference conventions |
| Rin_diff, Rin_cm | ohm | Differential/common-mode loading with documented per-pin definitions |
| Cin_diff, Cin_cm | F | Input capacitive loading with documented per-pin definitions |
| VCMR_low, VCMR_high | V | Valid common-mode range and supported out-of-range behavior |

Do not assign individual IB+ and IB- signs from an unsigned Ios alone. Record any
input crossover, phase reversal, protection, or overload behavior actually stated.
A range limit alone does not prove hard clamping or phase reversal.

### Stage 2: Gain and Frequency

Extract DC Aol (dB or V/V), GBWP and unity-gain frequency fu (Hz), phase margin PM
(degrees) at the stated noise gain/load, minimum stable gain, open-loop gain/phase
versus frequency, and supported poles/zeros or load-stability conditions.

Convert `Aol_linear = 10^(Aol_dB/20)`. For approximately dominant-pole VFB response,
`fp1 approximately GBWP/Aol_linear` (Hz) is a DERIVED approximation, not a universal
rule. GBWP and fu need not coincide for compensated/non-unity-stable or CFB parts.
For a two-pole VFB approximation with first-pole phase near -90 degrees at the
actual unity loop crossover fcross, `fp2 approximately fcross*tan(PM)` for
`0 < PM < 90 degrees`. State the assumed two-pole/no-zero response and actual
test conditions. Do not use `GBWP*tan(90 degrees - PM)` or infer a single pole
solely from PM = 90 degrees. CFB requires source-supported transimpedance and
feedback-resistor response; do not force VFB derivations onto it. If prerequisites
are absent, leave pole locations unresolved and document the gap.

### Stage 3: Slew and Output

Extract rising/falling SR (V/s), Voh/Vol or rail headroom versus load (V), source/sink
short-circuit currents (A), functional drive limits, output impedance versus
frequency and open-/closed-loop conditions (ohm), settling/overload recovery when
relevant, and load capacitance conditions.

Use slew charging/discharging currents with `I_slew = SR*C_slew` only with the
model's internal-to-output scaling stated. Output clamps and current limiting
must retain supply/load dependence and source/sink asymmetry. A short-circuit
test is not necessarily a guaranteed linear drive capability.

Require direct evidence for open-loop output resistance Ro. The expression
`Aol_linear/(2*pi*GBWP*Cin_diff)` has resistance units but no justified general
relationship to output resistance; do not use it. A headroom-versus-current slope
may yield a local incremental saturation/load-regulation resistance
`abs(delta Vout/delta Iout)` under matched conditions, not open-loop Ro. Label it
accordingly and do not substitute it for Ro without an evidenced architecture.

### Stage 4: CMRR and PSRR

Extract DC CMRR/PSRR (dB), frequency response and -3 dB rejection corners (Hz),
positive/negative supply distinctions, measurement definitions and reference
conditions. Input-referred error magnitude is `Vcm/10^(CMRR/20)` or
`Vripple/10^(PSRR/20)` when those definitions apply; sign/phase may be unknown.
Rejection decreasing with frequency means error coupling increases: do not put
an unqualified low-pass pole on error coupling and thereby improve rejection.
Recommend source-supported pole/zero shaping with finite high-frequency bounds.

### Stage 5: Noise

Extract voltage-noise white density en (V/sqrt(Hz)), current-noise density in
(A/sqrt(Hz)), 0.1-10 Hz voltage noise (V peak-to-peak), frequency plots and flicker
corner fc (Hz). Under the white-plus-1/f density approximation,
`en_total = en*sqrt(1+fc/f)` and the sqrt(2)-times-white-floor crossing identifies
fc; cite the graph and approximation. Peak-to-peak noise is not directly RMS
without statistical/bandwidth assumptions. Spectral density is not a time-domain
noise amplitude. State simulator noise-source/build support requirements rather
than assuming a generic B-source or VNSE exists. Source-impedance current noise
becomes comparable around `abs(Zsource) = en/in` under compatible conditions.

### Op-Amp Modeling Guidance and Gaps

Map input sources/loading, finite-gain controlled-source gain networks, RC poles,
slew limiting, load-dependent clamps/current limits, rejection error injection,
and noise shaping to this part's actual values. Temperature dependence and
enable states require evidence. Numerical convergence aids are implementation
choices, not extracted device parameters. Mark unsupported stages unpopulated.

Assess gaps against the requested scope: GBWP/response can be CRITICAL for AC;
Aol, offset/bias, VCMR, slew, swing/current limit and DC rejection are commonly
HIGH when those behaviors matter. Input loading, Ro, rejection roll-off,
temperature drift and flicker/current noise can be MEDIUM or HIGH depending on
the circuit; white noise is HIGH for noise analysis. Seek manufacturer data,
supported curves, or characterized measurements rather than inserting defaults.

## Conditional Procedure: Voltage Supervisor / Reset IC

### Identification

Record threshold channels and selected option, each sense/supply pin, fixed versus
adjustable thresholds, push-pull/open-drain/open-collector outputs, reset polarity,
truth table, MR presence, watchdog presence/type and enable controls. Extract
per-channel requirements and combined-reset logic. Do not equate rising/falling
threshold direction with assert/deassert: undervoltage normally asserts on a
falling crossing and releases on rising; use the actual device truth table.

### Stage 1: Threshold Comparator

Extract rising Vth_rise and falling Vth_fall (V), hysteresis Vhys (V), threshold
accuracy/min/typ/max (% or V), drift (ppm/degC or V/degC), sense reference and
divider/loading specifications for adjustable devices. Derive
`Vhys = Vth_rise - Vth_fall` only for matching conditions and channel definitions.
If one directional threshold and defined hysteresis are provided, derive the
other only using the stated hysteresis convention. A single threshold does not
establish hysteresis symmetry, zero hysteresis, or either unreported crossing.
Leave these unknown and report applicable gaps. Use a hysteretic comparator with
explicit state storage/initialization supported by the simulator; do not recommend
an algebraically self-referencing behavioral voltage source as a portable latch.
Temperature-dependent reference and tolerance sweeps require functional evidence.

### Stage 2: Timing and Delay

Extract assert delay td_assert, release delay td_deassert, POR hold time tPOR,
minimum pulse/glitch rejection, overdrive dependencies, startup/ramp-rate limits,
timer-programming relationships, retrigger behavior and timing conditions.
Do not add POR and release delays if the datasheet defines them as the same event.
RC timers/one-shots or behavioral event timing must match separate assert/release
paths and initial states. For an evidenced exponential timer,
`td = -R*C*ln(1 - Vtrip/Vfinal)` applies only for zero initial voltage charging
toward Vfinal; use the actual initial/final voltages otherwise. Initialization
must reflect documented startup behavior, not an arbitrary .ic claiming fidelity.

### Stage 3: Output Driver

Extract Vol at Iol, Voh at Ioh (push-pull only), functional source/sink limits,
off-state Ileak, Cout if relevant, low-supply reset-valid voltage, output supply
and power-down state. Voh/Ioh are not requirements for an open-drain high state;
the external pull-up sets it. Do not interpret a logic-level test current as a
current limit. `Vol/Iol` gives only an effective on-resistance approximation at
that operating point; a maximum Vol yields a bound, not a typical resistance.
Use finite output impedance, supported current limits and leakage in controlled
drivers or switches; push-pull source and sink resistances need separate evidence.

### Stage 4: Supply and Sense

Extract functional Vcc_min/Vcc_max, Iq versus supply/temperature/state, documented
internal logic-valid threshold if present, reset behavior below valid supply,
and Rin_sense/Cin_sense or input leakage for adjustable/sense pins. Supply
operating minimum need not equal reset-valid or internal comparator thresholds.
Gate state/driver behavior only according to documented power-down behavior;
do not invent a secondary comparator. Use supply current sources and sense
loading only where supported. Keep stress ratings out of functional targets.

### Optional MR and Watchdog

If MR is absent, omit MR requirements, gaps and techniques. If present, extract
polarity, VIL/VIH or actual directional thresholds, hysteresis if specified,
internal pull-up Rmr or current, minimum assert pulse tmr, debounce/filtering,
assert propagation and release interaction. Logic VIL/VIH bounds do not prove
precise comparator crossings. Map supported MR detection/filtering into reset logic.

If watchdog is absent, omit its requirements, gaps and techniques. If present,
extract twdt, watchdog reset pulse width tw_reset, WDI valid levels/edges/pulse
width, window limits if applicable, startup delay, enable/disable behavior,
retrigger conditions and reset interactions. Recommend a retriggerable timer or
windowed state machine, not an unconditional oscillator that ignores WDI rules.

### Supervisor Modeling Guidance and Gaps

Map source-backed thresholds/state, independent delays/POR, polarity/output
driver, supply behavior and only present MR/watchdog functions to this part.
Parameterization across variants must not silently mix threshold options.
Convergence smoothing is a numerical implementation choice and must not replace
specified glitch or timing behavior. Identify simulator support for state/timing.

Missing decision thresholds are CRITICAL for reset detection; hysteresis/release
crossings, delays/POR, output levels and low-supply behavior are commonly HIGH
for reset analysis. Drift/accuracy, loading, current/leakage and Iq severity depend
on temperature, interface and power objectives. MR detection and watchdog timing
are HIGH when those functions are present and required. Obtain functional data
or measurements; do not default hysteresis, drift, pull-up, output headroom or
drive limits, and do not use absolute maxima as workarounds.

## Report Contract

Write both files in the caller's destination or current working directory. Check
existing outputs before writing; return an overwrite conflict to the parent rather
than silently replacing user files. Use the exact selected part in filename-safe
form and report any filename normalization.

`[PartNumber]_behavioral_spice.md` has identification/source/scope metadata followed
by exactly three top-level report sections (stage subsections may appear within them):

1. `## Information Needed for the Behavioral Model`
2. `## Information Not Needed for the Behavioral Model`
3. `## Modeling Techniques`

Section 1 includes all applicable EXTRACTED, DERIVED and GRAPH ONLY requirements:

| Parameter | Symbol | Min | Typ / Approx | Max | Unit | Conditions | Stage / Use | Status | Source / Formula / Uncertainty |
|---|---|---|---|---|---|---|---|---|---|

Sort by source: Table (and explicit text specifications) first, Derived next,
Fig X (graph) last; retain stage order within each group. Cite table/text page,
figure/page or derivation inputs. Graph-only values belong here, never in the
missing-data report. Do not label a max-only value as typical.

Section 2 lists only present but irrelevant content with reasons: packaging,
ordering, soldering, thermal/process/ESD/stress data or application/layout details
not used in the selected behavioral scope. Pin functions, functional operating
limits and application-derived functional evidence are not categorically irrelevant.

Section 3 maps each applicable stage to recommended SPICE elements and actual
extracted values/citations, qualifications and simulator support. Identify which
techniques cannot yet be populated, fidelity omissions, and separately labeled
user-authorized assumptions. Do not generate a netlist or claim simulation.

`[PartNumber]_missing_data.md` contains ONLY applicable required NOT SPECIFIED
parameters genuinely absent from the reviewed datasheet:

| Missing Parameter | Status | Stage | Behavior / Analysis Affected | Severity | Workaround / Evidence Needed |
|---|---|---|---|---|---|

Use CRITICAL (core requested behavior cannot be represented), HIGH (materially
misleading results), MEDIUM (limited first-pass fidelity), LOW (secondary effect
for the stated scope). Severity is scope-dependent, not a device fact. Workarounds
request manufacturer evidence, measurements or parent approval of an explicitly
unverified assumption; never invent a replacement value. If no applicable data
is missing, explicitly state that. Reading blockers are reported separately to
the parent, not disguised as NOT SPECIFIED.

## Return to Parent

After writing both reports, return part/family and scope, found versus missing
counts (distinguishing unresolved graph reads), highest gap severity or none,
both file paths, source coverage/read blockers, and up to three prioritized
actions to obtain missing evidence. Do not claim successful full extraction when
a material source/selection blocker remains.
