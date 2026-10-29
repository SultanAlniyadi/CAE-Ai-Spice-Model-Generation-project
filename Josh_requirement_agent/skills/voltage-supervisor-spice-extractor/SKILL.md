---
name: voltage-supervisor-spice-extractor
description: >
  Extract voltage-supervisor / reset-IC parameters for a behavioral SPICE model, organized into
  four functional stages (threshold comparator, timing/delay, output driver, supply), with modeling
  techniques mapping each stage to SPICE elements. Normally invoked by the spice-extract skill after
  it detects a supervisor datasheet; can also be run directly on a supervisor datasheet.
---

# Voltage Supervisor Behavioral SPICE Model — Parameter Extractor

## Purpose
Extract the electrical parameters needed to build a **behavioral SPICE subcircuit model** of a voltage
supervisor (voltage detector / reset IC).

A behavioral model represents the supervisor as a network of controlled comparators, voltage sources,
timing elements, and output drivers. It does NOT require transistor-level data.

The four functional stages of a standard behavioral voltage supervisor model are:

| Stage | What it models | Key parameters needed |
|---|---|---|
| 1. Threshold comparator | Threshold voltage, hysteresis, temperature drift | Vth+, Vth−, Vhys, dVth/dT |
| 2. Timing / delay | Assert / deassert delay, power-on reset time | td_assert, td_deassert, tPOR |
| 3. Output driver | Logic levels, drive current, leakage | Voh, Vol, Iol, Ioh, Ileak |
| 4. Supply model | Operating range, quiescent current, threshold on VCC | Vcc_min, Vcc_max, Iq |

---

## Instructions

### Step 1 — Identify the part
Record:
- Part number, manufacturer, datasheet revision
- Number of threshold channels (single / dual / multi-voltage)
- Output type: push-pull (CMOS) or open-drain
- Reset polarity: active-low reset (RESET#) or active-high (RESET)
- Manual reset (MR) pin present: yes / no
- Watchdog timer present: yes / no

---

### Step 2 — Extract Stage 1 parameters: Threshold comparator

| Parameter | Symbol | Unit | Used in behavioral model |
|---|---|---|---|
| Rising threshold voltage (assert) | Vth+ | V | Upper comparator reference |
| Falling threshold voltage (deassert) | Vth− | V | Lower comparator reference |
| Hysteresis voltage | Vhys | mV | Difference: Vth+ − Vth− |
| Threshold temperature coefficient | dVth/dT | ppm/°C or mV/°C | Temperature-dependent voltage source on reference |
| Threshold accuracy at 25 °C | ΔVth | % or mV | Sets tolerances on comparator reference voltage |

**Note:** If the datasheet specifies only one threshold (e.g., "VRST = 2.93 V"), assume symmetric hysteresis unless Vhys is listed separately.

---

### Step 3 — Extract Stage 2 parameters: Timing and delay

| Parameter | Symbol | Unit | Used in behavioral model |
|---|---|---|---|
| Reset assert delay (VCC falling through Vth) | td_assert | µs or ms | Delay element in assert path: R×C or behavioral delay |
| Reset deassert delay (VCC rising through Vth) | td_deassert | µs or ms | Delay element in deassert path |
| Power-on reset time | tPOR | ms | One-shot timer on initial VCC ramp; sets minimum reset hold time |
| Minimum VCC ramp rate required | dV/dt_min | V/ms | If specified, sets flag — model needs VCC ramp-rate check logic |
| Watchdog timeout period | twdt | ms | Oscillator period in watchdog stage (if present) |
| Watchdog reset pulse width | tw_reset | µs | Duration of reset output pulse on watchdog trip |

---

### Step 4 — Extract Stage 3 parameters: Output driver

| Parameter | Symbol | Unit | Used in behavioral model |
|---|---|---|---|
| Output high voltage | Voh | V | Upper level of push-pull output VCVS (CMOS output only) |
| Output low voltage | Vol | V | Lower level of output VCVS / open-drain saturation level |
| Output sink current | Iol | mA | Current-limit element in sink direction |
| Output source current | Ioh | mA | Current-limit element in source direction (push-pull only) |
| Output leakage current | Ileak | µA | Leakage current source when output is in high-impedance state |
| Output capacitance | Cout | pF | Shunt capacitor at output node (if specified) |

---

### Step 5 — Extract Stage 4 parameters: Supply model

| Parameter | Symbol | Unit | Used in behavioral model |
|---|---|---|---|
| Minimum operating VCC | Vcc_min | V | Lower enable threshold on VCC supply port |
| Maximum operating VCC | Vcc_max | V | Upper limit on VCC supply port |
| Quiescent current | Iq | µA | Current source drawn from VCC in steady state |
| VCC threshold for internal logic | Vcc_th_int | V | If part monitors its own supply, sets secondary internal comparator |
| Sense pin input resistance | Rin_sense | kΩ | Resistor to ground at sense input (for adjustable-threshold parts) |
| Sense pin capacitance | Cin_sense | pF | Shunt capacitor at sense input |

---

### Step 6 — Manual reset pin (if present)

| Parameter | Symbol | Unit | Used in behavioral model |
|---|---|---|---|
| MR threshold voltage (assert) | Vmr+ | V | Comparator threshold on MR input pin |
| MR threshold voltage (deassert) | Vmr− | V | Lower comparator threshold on MR input |
| MR input pull-up resistance | Rmr | kΩ | Internal pull-up on MR pin modeled as resistor to VCC |
| MR minimum assert pulse width | tmr | µs | Minimum pulse filter / debounce delay on MR path |

---

### Step 7 — Flag missing and graph-only data

For each parameter above, mark its status:
- **EXTRACTED** — value found in electrical characteristics table
- **GRAPH ONLY** — value exists only in a graph; manual read required; note which figure
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
Manufacturer / Datasheet Rev / Date / Output type / Polarity / Channels

## Section 1 — Information Needed for the Behavioral Model
(Every parameter the datasheet provides — tabulated, derived, or read from a graph.)

| Parameter | Symbol | Value (Typ) | Unit | Stage | Used In | Source |
|---|---|---|---|---|---|---|
[Threshold, timing, output-driver, supply, and MR-pin parameters: EXTRACTED, DERIVED, or GRAPH ONLY]

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
(Threshold → Timing → Output → Supply → MR pin).

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
| Vth+ (rising threshold) | Stage 1 | Comparator has no assert threshold; model cannot flag undervoltage | CRITICAL | Must be specified; no meaningful model is possible |
| Vth− (falling threshold) | Stage 1 | Deassert behaviour undefined; model either latches or uses wrong release point | HIGH | Use Vth+ − Vhys if Vhys is known |
| Vhys | Stage 1 | Comparator has no hysteresis; output may chatter on noisy supply; reset simulation unreliable | HIGH | If not specified, model as zero and note; real devices often have 20–100 mV typ |
| dVth/dT | Stage 1 | Threshold fixed at 25 °C; temperature-corner reset margin analysis invalid | MEDIUM | Use ±50 ppm/°C as a typical CMOS estimate |
| Threshold accuracy ΔVth | Stage 1 | Tolerances absent; worst-case reset margin cannot be verified | MEDIUM | Use min/max Vth from absolute ratings table if available |
| td_assert | Stage 2 | Comparator trips instantly; glitch filtering and propagation delays absent | HIGH | Use typical value; real latency prevents false resets on supply transients |
| td_deassert | Stage 2 | Reset releases instantly; microcontroller may receive reset before VCC is stable | HIGH | Use typical value; tPOR often subsumes this |
| tPOR | Stage 2 | No power-on hold time; reset may release before downstream circuits are ready | HIGH | Use typical value; critical for microcontroller applications |
| Vol | Stage 3 | Output low voltage is zero; pull-down drive to microcontroller RESET pin too optimistic | HIGH | Use max Vol at specified Iol; affects logic interface reliability |
| Voh | Stage 3 | Push-pull output high level unknown; high-state assertion incorrect (CMOS outputs) | HIGH | Use Vcc − 0.1 V typ as estimate for CMOS push-pull |
| Iol | Stage 3 | Output current unlimited; bus loading and Vol verification cannot be confirmed | MEDIUM | Set from abs-max output current; use to cap sink current source |
| Ileak | Stage 3 | Open-drain high state is lossless; leakage into pullup network absent | LOW | Use typical max; significant only with high-value pull-up resistors |
| Iq | Stage 4 | No supply current drawn; power budget simulation incorrect | MEDIUM | Use typical value from supply current spec |
| Vcc_min | Stage 4 | Model operates below real power-down threshold; brownout behaviour wrong | HIGH | Must be set from abs-max ratings; model shuts down below Vcc_min |
| Rin_sense / Cin_sense | Stage 4 | No input loading on adjustable-threshold divider; threshold seen by IC differs from designed value | MEDIUM | For adjustable parts: use Rin_sense to correct divider ratio |
| Vmr thresholds | MR pin | MR pin has no detection window; manual reset initiation cannot be simulated | HIGH | Use VIL/VIH of logic family as estimate if not specified |
| Rmr (internal pull-up) | MR pin | MR pin floats; simulation with passive pull-up resistor network incorrect | MEDIUM | Use 100 kΩ as a typical pull-up estimate |
| twdt | Watchdog | Watchdog timer period unknown; watchdog test simulations cannot be timed | HIGH | Must be specified; no watchdog model is meaningful without period |

**Severity key:**
- CRITICAL — behavioral model cannot function without this parameter
- HIGH — simulation gives wrong or misleading results; resolve before use
- MEDIUM — first-pass acceptable; resolve before final verification
- LOW — second-order effect; acceptable approximation in most cases

---

### Step 10 — Append the Modeling Techniques reference

After the tables, add a `## Modeling Techniques` section to `[PartNumber]_behavioral_spice.md`
that tells the model builder HOW to turn each stage's parameters into SPICE elements. Include only
the stages that apply to this part (e.g. drop Watchdog / MR-pin rows if absent).

```
## Modeling Techniques (behavioral, SPICE-portable)

### Stage 1 — Threshold comparator
- Core element: behavioral source with built-in hysteresis.
  B1 det 0 V = (V(sense) > {Vth_hi}) ? 1 : (V(sense) < {Vth_lo}) ? 0 : V(det)
  The self-reference on V(det) latches state and gives hysteresis Vhys = Vth+ − Vth−.
- Alternative: ideal comparator primitive + resistive positive-feedback divider to set Vhys.
- Reference: internal bandgap is a DC source; add linear tempco from dVth/dT over TEMP.
- Adjustable-threshold parts: add Rin_sense / Cin_sense so the divider the comparator sees
  matches the real pin loading.

### Stage 2 — Timing / delay
- Reset assert/deassert delay: charge an RC when the comparator trips; a second comparator fires
  when the cap crosses a reference. td = R·C·ln(...). Separate charge/discharge paths model
  assert and deassert delays independently.
- Power-on reset (tPOR): one-shot / monostable that holds reset asserted for a fixed interval
  after VCC becomes valid. Put .ic on the timer cap to avoid power-on race conditions.
- Watchdog (if present): relaxation oscillator (comparator + RC) with period = twdt; a WDI edge
  resets the ramp, a timeout drives a reset pulse of width tw_reset.

### Stage 3 — Output driver
- Push-pull (CMOS): VCVS switching between Voh and Vol in series with Rout ≈ Vol/Iol to respect
  the drive-current limits.
- Open-drain: voltage-controlled switch (SW) to ground, on-resistance = Vol/Iol, plus a leakage
  current source Ileak in the off state (high level through external pull-up is not lossless).
- Polarity (active-low RESET# vs active-high): a logic inversion feeding the driver.

### Stage 4 — Supply model
- Self-powered behavior: gate the comparator and driver with (V(vcc) > {Vcc_min}) so outputs go
  to their defined power-down state as VCC collapses.
- Quiescent current: a current (or G) source drawing Iq from VCC; make it VCC/temp-dependent only
  if a graph provides that.

### Cross-cutting
- State/latch: self-referencing B-sources (or a behavioral SR latch) hold reset state between events.
- Parameterize Vth, Vhys, td, tPOR, Iq in a .param block so one subcircuit covers a threshold family.
- Convergence: give comparators finite gain/slew and small RC smoothing instead of ideal steps.
- Fidelity tiers: minimum model = comparator + hysteresis + fixed reset delay + output driver;
  add tempco, VCC-ramp-rate checks, and watchdog only if the simulation needs them.
```

Map the techniques to the actual extracted values (e.g. cite this part's Vth+, Vth−, td, tPOR).
For any stage whose parameters were missing, note which technique cannot be populated yet.
