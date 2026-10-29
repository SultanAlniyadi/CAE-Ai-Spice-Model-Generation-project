---
name: opamp-spice-extractor
description: >
  Extract operational-amplifier parameters for a behavioral SPICE model, organized into five
  functional stages (input error, gain/frequency response, slew/output, CMRR/PSRR, noise), with
  modeling techniques mapping each stage to SPICE elements. Normally invoked by the spice-extract
  skill after it detects an op-amp datasheet; can also be run directly on an op-amp datasheet.
---

# Op-Amp Behavioral SPICE Model — Parameter Extractor

## Purpose
Extract the electrical parameters needed to build a **behavioral SPICE subcircuit model** of an op-amp.
A behavioral model represents the op-amp as a network of controlled sources, resistors, capacitors, and
clamps — one stage per functional block. It does NOT require transistor-level data.

The five functional stages of a standard behavioral op-amp model are:

| Stage | What it models | Key parameters needed |
|---|---|---|
| 1. Input stage | Offset, bias current, input impedance, CM range | Vos, Ib, Ios, Rin_diff, Rin_cm, Cin, VCMR |
| 2. Gain / frequency | Open-loop gain, bandwidth, stability | Aol, GBWP, PM, pole/zero locations |
| 3. Slew / output | Output swing, slew rate, drive current | SR, Voh, Vol, Isc, Ro |
| 4. CMRR / PSRR | Supply and common-mode rejection | CMRR(DC), PSRR(DC), frequency roll-off of each |
| 5. Noise | Input-referred noise floor | en, in, 1/f corner fc |

---

## Instructions

### Step 1 — Identify the part
Record:
- Part number, manufacturer, datasheet revision
- Op-amp topology: voltage-feedback (VFB) or current-feedback (CFB)
- Input type: CMOS, bipolar, JFET — determines expected Ib magnitude
- Rail-to-rail: input only / output only / both — affects VICR clamping and output stage
- Number of amplifiers per package (single / dual / quad) — model covers one amplifier

---

### Step 2 — Extract Stage 1 parameters: Input

| Parameter | Symbol | Unit | Used in behavioral model |
|---|---|---|---|
| Input offset voltage | Vos | mV | DC voltage source in series with one input |
| Vos temperature drift | dVos/dT | µV/°C | Temperature coefficient on Vos source |
| Input bias current (+) | IB+ | pA or nA | Current source from IN+ to ground |
| Input bias current (−) | IB− | pA or nA | Current source from IN− to ground |
| Input offset current | Ios | pA or nA | Difference between IB+ and IB− |
| Differential input resistance | Rin_diff | Ω | Resistor between IN+ and IN− |
| Common-mode input resistance | Rin_cm | Ω | Resistors from each input to ground (×2) |
| Input capacitance (differential) | Cin_diff | pF | Capacitor across differential inputs |
| Input capacitance (common-mode) | Cin_cm | pF | Capacitors from each input to ground (×2) |
| CM input voltage range (min) | VCMR_low | V | Lower clamp voltage on CM input path |
| CM input voltage range (max) | VCMR_high | V | Upper clamp voltage on CM input path |

---

### Step 3 — Extract Stage 2 parameters: Gain and frequency response

| Parameter | Symbol | Unit | Used in behavioral model |
|---|---|---|---|
| DC open-loop gain | Aol | dB or V/V | Gain of error amplifier VCVS |
| Gain-bandwidth product | GBWP | MHz | Dominant pole: fp1 = GBWP / Aol_lin |
| Unity-gain bandwidth | fu | MHz | Cross-check: should equal GBWP for VFB |
| Phase margin at unity gain | PM | ° | If PM < 90°, sets second-pole frequency: fp2 derived from PM and GBWP |
| Open-loop gain at key frequencies | Aol(f) | dB | Pole/zero network values (read from Bode plot if not tabulated) |

**Derived values to compute and record:**
- Dominant pole: `fp1 = GBWP / Aol_linear` (Hz)
- If PM is known and < 90°: second pole `fp2 ≈ GBWP × tan(90° − PM)`
- Record both as they directly set capacitor values in the gain stage

---

### Step 4 — Extract Stage 3 parameters: Output stage

| Parameter | Symbol | Unit | Used in behavioral model |
|---|---|---|---|
| Output voltage swing high | Voh | V | Upper clamp on output VCVS |
| Output voltage swing low | Vol | V | Lower clamp on output VCVS |
| Output short-circuit current (source) | Isc+ | mA | Positive current-limit element at output |
| Output short-circuit current (sink) | Isc− | mA | Negative current-limit element at output |
| Slew rate (rising) | SR+ | V/µs | Charging current for slew-rate capacitor: I_slew = SR × C_slew |
| Slew rate (falling) | SR− | V/µs | Discharging current for slew-rate capacitor |
| Open-loop output resistance | Ro | Ω | Series resistor between gain stage and output pin |

**Note on Ro:** Often not tabulated. Estimate from output-headroom-vs-current graph (slope = Ro), or calculate Ro ≈ Aol_lin / (2π × GBWP × Cin_diff).

---

### Step 5 — Extract Stage 4 parameters: CMRR and PSRR

| Parameter | Symbol | Unit | Used in behavioral model |
|---|---|---|---|
| Common-mode rejection ratio (DC) | CMRR_DC | dB | Gain of CM-to-differential error source: Vcm_err = Vcm / 10^(CMRR/20) |
| CMRR frequency at −3 dB | f_cmrr | Hz | Pole in CMRR network (read from CMRR vs. frequency graph) |
| Power supply rejection ratio (DC) | PSRR_DC | dB | Gain of supply-to-input error source: Vps_err = Vripple / 10^(PSRR/20) |
| PSRR+ frequency at −3 dB | f_psrr+ | Hz | Pole in positive-supply PSRR network |
| PSRR− frequency at −3 dB | f_psrr− | Hz | Pole in negative-supply PSRR network |

---

### Step 6 — Extract Stage 5 parameters: Noise

| Parameter | Symbol | Unit | Used in behavioral model |
|---|---|---|---|
| Voltage noise density (white floor) | en | nV/√Hz | White noise source at input (typically specified at 1 kHz or 10 kHz) |
| Voltage noise (0.1–10 Hz, 1/f band) | en_1f | µVp-p | Cross-check for 1/f noise level |
| Current noise density | in | pA/√Hz or fA/√Hz | Current noise source at each input |
| 1/f voltage noise corner | fc | Hz | Flicker noise corner: en_total = en × √(1 + fc/f) |

**Note on fc:** Almost never tabulated. Read from voltage noise density graph as the frequency where the noise density is √2 × (white floor value).

---

### Step 7 — Flag missing and graph-only data

For each parameter above, mark its status:
- **EXTRACTED** — value found in electrical characteristics table
- **GRAPH ONLY** — value exists but only in a graph; manual read required; note which figure
- **NOT SPECIFIED** — not present anywhere in the datasheet
- **DERIVED** — computed from other extracted values (show formula)

---

### Step 8 — Produce the main output document (two sections)

Generate `[PartNumber]_behavioral_spice.md`. Keep it simple — exactly two sections, filtered
to THIS part number only. Section 1 lists every parameter the datasheet provides. Section 2 lists
datasheet content that is NOT needed for a behavioral model.

**Routing rule — where each parameter goes:**
- **EXTRACTED** (tabulated value) → Section 1, Source = "Table"
- **DERIVED** (computed from other params) → Section 1, Source = "Derived"
- **GRAPH ONLY** (value exists in a graph) → Section 1, Source = "Fig X (graph)" — the data IS in
  the datasheet, so read the approximate value from the graph and include it here. It is NOT missing.
- **NOT SPECIFIED** (absent from the datasheet entirely) → missing-data document (Step 9) only

```
# Behavioral SPICE Model — [Part Number]
Manufacturer / Datasheet Rev / Date / Topology / Input type / Rail-to-rail

## Section 1 — Information Needed for the Behavioral Model
(Every parameter the datasheet provides — tabulated, derived, or read from a graph.)

| Parameter | Symbol | Value (Typ) | Unit | Stage | Used In | Source |
|---|---|---|---|---|---|---|
[Input, gain/frequency, output, CMRR/PSRR, noise parameters that were EXTRACTED, DERIVED, or GRAPH ONLY]
[Include derived fp1 / fp2 here]

## Section 2 — Information Not Needed for the Behavioral Model
(Datasheet content present for this part that a behavioral model ignores.)

| Datasheet Item | Why Not Needed for Behavioral Model |
|---|---|
[e.g. package / thermal resistance, abs-max ESD / latch-up, pinout, ordering codes,
PCB layout guidance, application circuits, moisture / soldering, die/process data]
```

For graph-read rows, give the best approximate value and name the figure in the Source column so
the reader knows a manual read confirmed it. Only NOT SPECIFIED parameters are excluded here.

**Sort Section 1 by the Source column** so firm data is scanned first: all `Table` rows first,
then `Derived`, then `Fig X (graph)` rows last. Within each Source group, keep stage order
(Input → Gain → Output → CMRR → PSRR → Noise → Supply).

---

### Step 9 — Produce the separate missing-data document

Generate `[PartNumber]_missing_data.md` listing ONLY parameters that are needed for the behavioral
model but are genuinely absent from the datasheet (status NOT SPECIFIED). GRAPH ONLY parameters do
NOT belong here — they go in Section 1 of the main document.

If every needed parameter is available (tabulated or from a graph), state that no required data is
missing and list any graph-only items only as a reminder that they need a manual read.

```
# Missing Data for Behavioral SPICE Model — [Part Number]

| Missing Parameter | Stage Affected | Model Behaviour Without It | Severity | Workaround |
|---|---|---|---|---|
```

Only include rows for parameters that are NOT fully extracted. Use this reference:

| Missing Parameter | Stage Affected | Model Behaviour Without It | Severity | Workaround |
|---|---|---|---|---|
| Vos | Stage 1 | No DC input error; precision and high-gain DC analysis invalid | HIGH | Use typ value; add ±max sweep for worst-case |
| Vos drift (dVos/dT) | Stage 1 | Offset fixed at all temperatures; temp-corner DC analysis wrong | MEDIUM | Use ±2 µV/°C for CMOS; ±10 µV/°C for bipolar as estimate |
| Ib / Ios | Stage 1 | No input leakage; transimpedance, photodiode, and high-Z source circuits optimistic | HIGH | Use typ value; model as current source at each input |
| Rin_diff / Rin_cm | Stage 1 | Input loading absent; gain error in high-source-impedance circuits missed | LOW–MEDIUM | Use 10¹³ Ω for CMOS (often negligible); verify if Rs > 100 MΩ |
| Cin_diff / Cin_cm | Stage 1 | High-frequency input loading absent; bandwidth of high-Z source circuits overestimated | MEDIUM | Use typ pF; add as input capacitors in model |
| VCMR limits | Stage 1 | Model never clips at input rail; phase reversal / distortion at CM extremes absent | HIGH | Set clamp voltages from VCMR spec; essential for rail-to-rail parts |
| Aol (DC gain) | Stage 2 | Loop gain wrong; closed-loop accuracy, distortion, and gain error all incorrect | HIGH | Must be specified; derive fp1 only after Aol is known |
| GBWP | Stage 2 | Dominant pole fp1 unknown; entire AC frequency response wrong | CRITICAL | Cannot build a valid frequency-response stage without GBWP |
| Phase margin (PM) | Stage 2 | Second pole absent; model appears unconditionally stable; overshoot/ringing wrong | HIGH | Use PM to derive fp2; default to single-pole only if PM = 90° confirmed |
| Bode plot data | Stage 2 | Multi-pole / zero behaviour missed; stability with real feedback networks wrong | MEDIUM | Read from graph; compare against single-pole model as sanity check |
| SR+ / SR− | Stage 3 | No slew limiting; large-signal transients appear faster than reality | HIGH | Must set slew cap and current independently from GBWP |
| Voh / Vol | Stage 3 | Output swings beyond rails; large-signal and clipping simulations invalid | HIGH | Use headroom spec; set upper and lower output clamps |
| Isc | Stage 3 | Unlimited output current; load drive and short-circuit protection tests unrealistic | HIGH | Set current limit from Isc typ; note source vs. sink asymmetry if present |
| Ro | Stage 3 | Zero output impedance; closed-loop Zout and load regulation optimistic | MEDIUM | Estimate from output swing vs. current graph slope or formula |
| CMRR_DC | Stage 4 | Full CM signal passes to output; differential amp circuits show false rejection | HIGH | Set CM error gain = 1/10^(CMRR_dB/20) |
| CMRR frequency roll-off | Stage 4 | CMRR treated as flat at all frequencies; high-frequency CM rejection overestimated | MEDIUM | Read f_cmrr from graph; add first-order pole to CMRR network |
| PSRR_DC | Stage 4 | Supply ripple couples directly to output with no attenuation | HIGH | Set PS error gain = 1/10^(PSRR_dB/20) |
| PSRR frequency roll-off | Stage 4 | PSRR treated as flat; high-frequency supply noise underestimated at output | MEDIUM | Read f_psrr from graph; add pole; note PSRR+ ≠ PSRR− |
| en (white noise) | Stage 5 | Output noise floor is zero; any noise simulation is meaningless | HIGH | Must use datasheet en; scale VNSE source as en × √BW |
| in (current noise) | Stage 5 | Noise from source impedance absent; SNR for high-Z sources overestimated | MEDIUM | Use fA/√Hz typ; significant only when Rs > en/in |
| fc (1/f corner) | Stage 5 | Flat noise assumed to DC; low-frequency / audio / sensor simulations optimistic | MEDIUM | Read from noise density graph; set flicker noise corner in model |

**Severity key:**
- CRITICAL — behavioral model cannot represent the correct AC response without this
- HIGH — simulation gives wrong results; do not sign off without resolving
- MEDIUM — first-pass acceptable; resolve before final design verification
- LOW — second-order effect; acceptable approximation in most cases

---

### Step 10 — Append the Modeling Techniques reference

After the tables, add a `## Modeling Techniques` section to `[PartNumber]_behavioral_spice.md`
that tells the model builder HOW to turn each stage's parameters into SPICE elements. This is the
classic multi-stage macro-model approach (Boyle-style), simplified to behavioral primitives.

```
## Modeling Techniques (behavioral, SPICE-portable)

### Stage 1 — Input error block
- Offset: DC source Vos in series with one input; add a tempco from dVos/dT over TEMP.
- Bias/offset current: current sources IB+ and IB− from each input to ground; make them
  temperature-dependent if IB rises with TEMP (CMOS parts).
- Input impedance: Rin_diff across the inputs, Rin_cm from each input to ground, with Cin in
  parallel. For CMOS, Rin is often 10^13 Ω and negligible except with very high source impedance.
- Common-mode range: clamp the CM input path at VCMR_low / VCMR_high so the model clips at the
  input rail (essential for rail-to-rail parts; prevents false linear behavior past the rails).

### Stage 2 — Gain / frequency response
- Error amplifier: a VCVS (or G-source into a node) with gain = AOL_linear sensing (IN+ − IN−).
- Dominant pole: RC on the gain node set to fp1 = GBWP / AOL_linear.
- Second pole: only if PM < 90°; add a second RC at fp2 ≈ GBWP·tan(90° − PM). If PM = 90°,
  a single pole is sufficient and no second pole is modeled.
- Read extra poles/zeros from the Bode plot only when stability with real feedback matters.

### Stage 3 — Slew / output block
- Slew limiter: limit the current charging the dominant-pole cap so dV/dt is capped at SR
  (I_slew = SR · C_pole). Separate source/sink limits if SR+ ≠ SR−.
- Output swing: clamp the output VCVS at Voh / Vol (rail headroom).
- Output current limit: cap source/sink current at Isc.
- Output resistance: series Ro between the gain stage and the output pin; estimate from the
  output-headroom-vs-current graph if not tabulated.

### Stage 4 — CMRR / PSRR networks
- CMRR: inject a CM-dependent error into the input, gain = 1/10^(CMRR_dB/20). Add a pole at
  f_cmrr so rejection rolls off with frequency instead of staying flat.
- PSRR: inject a supply-ripple-dependent error, gain = 1/10^(PSRR_dB/20), with poles at
  f_psrr. Model PSRR+ and PSRR− separately when they differ.

### Stage 5 — Noise model
- White floor: input-referred voltage-noise source set to en (VNSE / behavioral noise).
- 1/f: shape the source with corner fc so density follows en·√(1 + fc/f).
- Current noise: in sources at each input; significant only when Rs > en/in.

### Cross-cutting
- Parameterize Vos, AOL, GBWP, SR, Voh/Vol in a .param block so one subcircuit covers a family.
- Convergence: use finite (not infinite) gains and small series/shunt R-C to aid DC convergence.
- Fidelity tiers: minimum model = offset + single-pole gain + slew + output clamp; add CMRR/PSRR
  roll-off, 1/f noise, and temperature effects only when the simulation needs them.
```

Map the techniques to this part's actual extracted values (cite its AOL, GBWP, PM, SR, Voh/Vol).
For any stage whose parameters were missing, note which technique cannot be populated yet.
