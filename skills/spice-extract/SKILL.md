---
name: spice-extract
description: >
  Extract the parameters needed to build a behavioral SPICE subcircuit model from an
  operational-amplifier or voltage-supervisor / reset-IC datasheet. Detects the component
  type, routes to the matching extractor skill, and writes a needed/not-needed requirements
  document (with modeling techniques) plus a separate missing-data report. Use this for
  /spice-extract or any request to turn a datasheet into SPICE-model parameters.
---

# SPICE Behavioral Model Parameter Extractor

## Purpose
Entry point for extracting parameters from an op-amp or voltage supervisor datasheet to build
a **behavioral SPICE subcircuit model**.

A behavioral SPICE model represents a component as functional stages (controlled sources, clamps,
timing elements). It does NOT need transistor-level data. This skill extracts exactly the parameters
required — no more.

Supported component types: **operational amplifiers**, **voltage supervisors / reset ICs**.

## Trigger
User runs `/spice-extract` or says "extract SPICE parameters from this datasheet".

---

## Step 1 — Get the datasheet

Ask the user for the PDF path if not already provided. Read the full PDF.

```
Please provide the path to the datasheet PDF (e.g. C:\path\to\Part_DS.pdf)
```

---

## Step 2 — Detect component type

Read the first two pages plus the electrical characteristics section heading. Determine:

- **Op-amp** — keywords: operational amplifier, op-amp, input offset voltage, gain-bandwidth, slew rate
- **Voltage supervisor** — keywords: voltage supervisor, voltage detector, reset IC, threshold voltage, power-on reset, watchdog

If ambiguous, ask: "Is this an op-amp or a voltage supervisor / reset IC?"

---

## Step 3 — Route to component-specific extractor

- Op-amp → invoke the `opamp-spice-extractor` skill and follow all of its steps
- Voltage supervisor → invoke the `voltage-supervisor-spice-extractor` skill and follow all of its steps

Carry out every extraction step from the chosen skill completely before proceeding.

---

## Step 4 — Write the two output documents

Following the chosen component skill, write TWO markdown files in the current working directory:

1. `[PartNumber]_behavioral_spice.md` — the main document, exactly two sections:
   - **Section 1 — Information Needed for the Behavioral Model**: every parameter the datasheet
     provides, with a Source column. This includes tabulated values (Source = "Table"), derived
     values (Source = "Derived"), AND graph-only values (Source = "Fig X (graph)"). Graph-only data
     is still in the datasheet, so read the approximate value from the graph and include it here.
     Sort the rows by Source — `Table` first, then `Derived`, then `Fig X (graph)` — keeping stage
     order within each group.
   - **Section 2 — Information Not Needed for the Behavioral Model**: datasheet content present
     for this part that a behavioral model ignores (packaging, thermal, ESD, pinout, ordering,
     layout, application circuits, etc.).
   - **Modeling Techniques**: how each stage's parameters map to SPICE elements (from the
     component skill's final step), cited against this part's actual values.

2. `[PartNumber]_missing_data.md` — the gaps: ONLY parameters needed for the behavioral model that
   are genuinely absent (NOT SPECIFIED) from this datasheet, with severity and workaround. Do NOT
   list graph-only parameters here — those belong in Section 1 of the main document.

Filter everything to THIS specific part number. Do not include generic parameters that do not
apply to the detected part.

---

## Step 5 — Report results to the user

After both markdown files are written, summarise:

1. Part number and component type
2. Count of parameters needed-and-found vs. missing
3. Highest severity gap (CRITICAL / HIGH / MEDIUM / LOW)
4. Path to the main document: `[PartNumber]_behavioral_spice.md`
5. Path to the missing-data document: `[PartNumber]_missing_data.md`
6. Top 1–3 recommended actions to resolve the most important gaps

---

## Legend

**Source column values in Section 1:**
- `Table` — value found in the electrical characteristics table
- `Derived` — computed from other parameters; formula shown
- `Fig X (graph)` — value read from a datasheet graph; note the figure number

**Status in the missing-data document:**
- `NOT SPECIFIED` — absent from the datasheet entirely (the only status that belongs here)

**Severity in the missing-data document:**
- `CRITICAL` — behavioral model cannot produce a valid result without this
- `HIGH` — simulation gives wrong results; must resolve before use
- `MEDIUM` — acceptable for first pass; resolve before design verification
- `LOW` — second-order effect; approximation is fine
