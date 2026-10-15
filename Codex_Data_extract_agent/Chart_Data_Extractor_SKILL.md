---
name: chart-data-extractor
description: "Digitize PDF datasheet XY curves at source-supported resolution and build an Excel handoff for downstream SPICE model generation, with specifications, conditions, pins, provenance, uncertainty, fitting selections, and validation guidance. Use for datasheet graph extraction or modeling-workbook requests."
---

# PDF datasheet to modeling workbook

Produce one self-contained `.xlsx` workbook from the supplied PDF. Keep this
file as the only maintained instruction source; task-specific Python helpers,
rendered inspection images, and tests are temporary. Excel is the only generated
deliverable. Do not generate a SPICE model, simulator netlist, external report,
images, charts, formulas, or macros in the deliverable. Dense samples describe
the printed curve, not additional measured data or manufacturer accuracy.

## Downstream use with the datasheet

The downstream model generator may receive both this workbook and the original
PDF. Record that source-access expectation in Handoff when confirmed by the user;
for the MCP6L01 handoff it is confirmed. Keep the workbook independently usable
for numerical data, units, conditions, quality and fitting selections. PDF access
does not remove the need for those structured records.

Instruct the downstream tool to match the supplied PDF's SHA256 and revision to
Handoff, then use Metadata/Specifications/Pins/Test_Circuits source references to
check the relevant pages, figures, tables, footnotes and visually drawn topology.
Use the PDF as the source for published statements and the workbook as the
traceable digitization, normalization and fitting interface. If a transcription
or interpretation disagrees with the PDF, record a source-cited correction and
its affected IDs; preserve the original extraction and source disagreements.
Do not assume that PDF access resolves details the datasheet never specifies.
Keep missing curve regions blank and label downstream model assumptions
separately from extracted evidence. Confirm the selected device/package and
physical pin mapping before defining a simulator interface. Keep validation
holdouts and source uncertainty in use even when the PDF is available.

## Scope and source review

Obtain the PDF path, selected device/package, optional graph selections and
destination from the request. Pages mean physical PDF pages starting at 1. For
a modeling handoff, scan the complete datasheet even when only some graphs were
selected. Without graph selections include all relevant performance graphs, in
figure order. Ask only for a materially ambiguous graph/device or missing axis
calibration; record unspecified test details as unknown and continue.

Inventory every page for graphs, electrical/temperature tables, operating and
stress limits, equations, circuits, pins, and behavioral guidance. Retain the
datasheet title, revision/date, page count, SHA256 hash, and scan dispositions in
Handoff. Include package-specific thermal data for the selected device; exclude
mechanical dimensions and unrelated administrative content. Shared family
electrical evidence may apply to the selected device but variant-specific pins
must not be substituted. Verify tables, footnotes, package diagrams, and circuit
connections against rendered source pages. PDF text order does not establish
topology. Do not infer component values or graph test circuits from appearance.

Identify each selected plot, axes, units, legend, condition labels, and figure.
Match titles using normalized whitespace/case; inspect the surrounding page to
confirm the crop. Resolve multiple matches or unidentified selections before
finalizing. An identified but unextractable graph still receives its own
header-only numerical sheet, Metadata/Quality entries, and explicit failure.
Existing verified extraction workbooks may be reused after checking their source,
units, conditions, and gaps. Preserve the prior outputs without modification.

## Conditions and source interpretation

Resolve each field independently: series label > graph note > applicable table
or section default. Explicit sweeps and test purposes override incompatible
defaults. Do not apply DC midpoint output bias to a pulse-response trace as a
constant instantaneous output, or RL=10 kΩ as the short-circuit fixture. Store
source and resolution status for every condition: numeric, swept, relational,
unknown, not_applicable, or conflict. Keep expressions such as `VL = VDD/2` as
expressions; do not freeze them at one value when supply is swept. Store load
reference node alongside resistance. Mark inferred mappings and missing stimulus
amplitude/edge timing/feedback values explicitly. Graph defaults apply only to
the fields they state; a figure used for most tests is not proof of every setup.

Separate typical observations, population evidence, representative-part curves,
operating limits, and absolute maximum stress ratings. Preserve ± sign/magnitude
semantics, inequalities, footnotes and not-tested status by value column. Stress
ratings do not guarantee functional behavior or authorize destructive fitting.
Keep conflicting statements as separate records with a shared Quality link and
explain the preferred evidence; never silently average or overwrite them.
External protection, bypass, guard rings, and output-isolation resistors remain
external application recommendations, not inferred internal device components.

## Tools and source inspection

Use Python with `pymupdf`, `numpy`, `Pillow`, and `openpyxl`; `scipy` is useful
for image components and curve refinement. Inspect available dependencies first.
If one is missing, use an equivalent installed library or install only what is
needed subject to the environment's permissions. Never silently replace the
requested workbook with a text table.

Prefer vector geometry from `page.get_drawings(extended=True)` when the actual
data curves are vectors. A vector grid surrounding a bitmap curve is not a
vector source. Inspect `page.get_image_info()` and a rendered crop to determine
the representation of each series. Mixed sources may require both methods.

Keep PDF coordinates, crop offsets, page rotation, and render scaling explicit.
Use a common coordinate frame for text, paths, clipping, and calibration. Apply
the page rotation/derotation transformation when comparing displayed images with
unrotated PDF coordinates. Render previews with `annots=False` so annotations
cannot become data. Inspection crops may include labels; trace only the plot area.

## Axis calibration

For each axis, record at least two labeled tick centers and their numeric values.
Confirm the scale with intermediate labels where available; two endpoints alone
cannot distinguish linear from logarithmic scale. Use visible scale markings or
ask when the scale remains ambiguous. Parse scientific notation, powers of ten,
SI prefixes, negative numbers, and units explicitly. Keep numeric values and
headers in the same units; do not multiply an `mA` column by 1,000 accidentally.

Let `p` be the coordinate along the axis in the common source frame, `v` its data
value, and `T(v) = v` for linear axes or `log10(v)` for logarithmic axes. Fit:

```text
T(v) = a*p + b
linear: v = a*p + b
logarithmic: v = 10**(a*p + b)
```

Fit across reliable ticks, then check residuals against their visible positional
uncertainty. The sign of `a` handles reversed axes and the usual downward PDF
Y coordinates. Do not force the origin to zero or assume the plot border is a
labeled endpoint. Derive the visible domain from the calibrated plot boundaries.
Logarithmic labels must be positive; a zero tick is incompatible with that model.
Broken axes, incompatible tick fits, or missing calibration require clarification
or an explicit extraction failure. For graphs with two Y axes, associate each
series with the labeled axis or ask when the association is unclear.

## Trace the curves

### Vector source

- Identify data strokes using position, color, width, dash pattern, legend
  examples, and nearby curve labels. Remove axes, gridlines, legend strokes,
  text outlines, fills, and unrelated drawings from the data candidate set.
  Respect active PDF clipping; exclude portions hidden by clipping or overlays.
- Preserve the actual path commands. For straight segments, evaluate the
  segment. For cubic Bezier segments, solve intersections with each requested
  X coordinate or flatten adaptively to within 0.25 reference pixels, then
  interpolate only between adjacent vertices of the same visible path.
  Control points are not points on the curve.
- Identify subpath boundaries even if several subpaths share one drawing record.
  Preserve breaks; do not join unrelated endpoints. Maintain series identity
  through crossings using path continuity and legend attributes. If hidden paths
  cannot be distinguished from visible data, leave that region unresolved.
- A continuous path with a PDF dash style supplies the underlying curve geometry.
  Sample it when series identity is clear. Independently drawn dash fragments do
  not establish the missing geometry between fragments.

### Raster source

- Determine the image's native dimensions and placement transform, then measure
  effective native pixel size along each plot axis. Use the original embedded
  image when practical; render a registered crop when the graph spans images or
  mixes image and vector content. Account for image masks and opaque overlays.
- Render at 300 DPI initially, increasing resolution only when PDF content
  benefits. Upscaling an embedded image does not add source detail. If the
  raster placement or native resolution cannot be established, use the current
  rendered pixels as a conservative limit and report that limitation.
- Separate curve strokes by color/intensity, dash pattern, and continuity. Mask
  labels and classify gridlines without deleting data at intersections. Estimate
  the center of each stroke, retaining its width as positional uncertainty.
- Trace connected neighborhoods along the curve, using previous direction and
  series attributes to distinguish crossings. Do not select a brightest/darkest
  pixel independently in every column. Unresolvable overlaps, occlusion, and
  missing fragments become gaps.
- Interpolate between adjacent points on a reliably traced connected stroke.
  Bridge the whitespace of a raster dash pattern only when repeated dash
  spacing, matching endpoints, and local continuity establish the same curve;
  disclose those intervals as dash interpolation. Otherwise leave them blank.
  Do not fit an assumed mathematical model to fill missing curve portions.

### Discrete and multi-valued data

Unconnected scatter plots retain only visibly drawn marker centers. Do not
generate intermediate samples, trend lines, or an assumed connecting curve.
Use separate X/Y column pairs for series with different X coordinates. Preserve
repeated X values as separate rows; deduplicate only the same source marker or
the same path intersection counted twice at a shared segment endpoint.

If a connected curve has several distinct Y values at an X (a loop or vertical
segment), use separate X/Y pairs with repeated X rows for isolated intersections,
or ordered traced vertices for a continuous vertical segment. Report that this
graph uses a path-preserving layout instead of a common single-valued X grid.
For graphs mixing scatter and connected curves, keep all series on the same
worksheet using separate pairs so discrete points are not resampled.

## Automatic sampling and precision

For ordinary single-valued connected curves, all series share one X column.
Choose spacing in source coordinates before converting back to data units:

1. For vector curves, one reference pixel is `72 / 300` PDF points. The minimum
   X spacing for a series is the larger of this pixel size and its stroke width
   along X, transformed into the chosen coordinate frame. Use the transformed
   pixel and stroke dimensions if tracing in render coordinates.
2. For raster curves, the minimum spacing is the larger of one effective native
   image pixel along X and the estimated stroke width along X. If rendering
   undersamples the source, use the larger rendered pixel size too.
3. For multiple or mixed-source series, use the largest series minimum as the
   common spacing. Never use a sharper curve to claim finer resolution for a
   coarser curve. Report which source limits the grid.
4. For visible plot width `W` and minimum spacing `s`, set
   `n = floor(W / s)`. With `n >= 1`, use `n + 1` positions including both plot
   boundaries, with interval `W / n >= s`. With `n < 1`, the source cannot
   support a dense grid; report this and retain only distinct resolvable points.
5. Convert the positions through the X calibration, ordering rows by increasing
   numeric X. This gives equal X increments for linear axes and equal X ratios
   for logarithmic axes. Keep the grid regular; do not append arbitrary extrema
   or points that create smaller intervals. Instead check that a reconstructed
   curve preserves extrema within source uncertainty; report unresolved features.

Evaluate each series at each grid position using its traced geometry. Within
each series, do not extrapolate outside its visible extent. Use `None` for low
confidence, ambiguous identity, missing geometry, or unsupported intersections.
Track why and where values are missing, independently of the workbook cells.
A blank is not zero. Never convert NaN or infinity into a numeric result.

Estimate positional uncertainty from native pixels, stroke width, and calibration
residuals. Propagate both X and Y uncertainty; a steep slope can make Y uncertain
even when the Y stroke is thin. For a log axis, transform the uncertainty bounds
back to data units rather than using a constant additive tolerance.

Round data to a useful decimal/significant-digit scale consistent with uncertainty.
Grid spacing is not the value uncertainty: coarse ticks can support intermediate
values when the curve and calibration are clear. Retain enough X digits for
distinct samples and a regular grid; use Excel display formats where necessary
and report X uncertainty so those digits do not imply unsupported accuracy.

## Workbook interface (schema 1.0.0)

Default destination: `<PDF stem>_<selected device>_model_input.xlsx` in the
directory containing this file (MCP6L01 uses `_MCP6L01_model_input.xlsx`). Resolve
explicit relative paths against the working directory. Use exclusive creation
and `_2`, `_3`, etc. for collisions, including explicit destinations. Save using
openpyxl, reopen, and remove only an incomplete file created by this run if saving
fails. Existing workbooks/reports remain preserved.

Create one numerical sheet per graph, in selection/figure order, plus exactly
these structured sheets. Reserve their names before sanitizing graph titles.
All sheets have one header row and ordinary text/numeric cells; no notes blocks,
merged headers, charts, images, formulas or macros. Freeze/filter headers and
use readable widths. Numerical graph sheets contain original headers/data only.
When reusing a workbook, inspect and remove inherited charts/images from the new
copy; an earlier report is not proof that those objects are absent. Keep the
source workbook unchanged and disclose any mismatch in Quality.
Connected curves share X unless multi-valued; scatter/path layouts use separate
X/Y pairs and blank padding. Keep original graph units. Sanitize `[]:*?/\`,
controls and apostrophes; cap names at 31 characters and suffix duplicates
case-insensitively. Do not use the reserved Excel name History.

Use the following columns as a minimum schema; add explicit explanatory fields
where source semantics need them. IDs are text and deterministic by source
figure/series or specification row. Do not use row numbers as IDs. A condition
group joins all Conditions records for an entity. References must resolve.

| Sheet | Required record and fields |
|---|---|
| Handoff | Record_ID, Category, Key, Value_Text, Value_Number, Units, Source, Status. Device/packages, revision/hash, schema, inventory, coverage, limitations, usage, normalization/weight semantics, scan results and verification results. |
| Metadata | Curve_ID, Graph_ID, Source_Page, Source_Figure, Source_Title, Graph_Sheet, X_Column, Y_Column, Series_Label, X_Quantity, Y_Quantity, X/Y_Original_Unit, X/Y_Normalized_Unit, X/Y_Normalization_Factor, X/Y_Axis_Scale, Extraction_Method, Layout, Sampling, Condition_Group_ID, Quality_ID, Modeling_Role, Evidence_Class, Sign_Convention, Extraction_Status. |
| Conditions | Condition_ID, Condition_Group_ID, Entity_Type, Entity_ID, Field, Value, Min, Max, Unit, Normalized_Value/Min/Max, Normalized_Unit, Expression, Status, Resolution, Source_Page, Source_Reference, Notes. One row per field, including unknowns. |
| Specifications | Parameter_ID, Category, Parameter, Symbol, Minimum, Typical, Maximum, Original_Unit, Normalized_Minimum/Typical/Maximum, Normalized_Unit, Minimum/Typical/Maximum_Status, Sign_Convention, Value_Text, Condition_Group_ID, Footnotes, Applicability, Package, Source_Page/Reference, Quality_ID, Modeling_Use. Split composite impedance into linked parallel R/C records. |
| Pins | Pin_ID, Device, Package, Physical_Pin, Symbol, Logical_Role, Channel, Source_Page, Source_Reference, Verification_Status. Physical order is not a subcircuit interface. |
| Test_Circuits | Record_ID, Circuit_ID, Record_Type, Name, Component_Type, Value, Unit, Normalized_Value/Unit, Node_1, Node_2, Expression, Measurement, Scope, Status, Source_Page/Reference, Unresolved_Details. Separate components, DUT mappings, equations and missing setup details. |
| Quality | Quality_ID, Entity_Type/ID, Category, Status, Source_Page/Reference, X_Min/Max, X_Unit, Segment_ID, X/Y_Uncertainty, Uncertainty_Unit, Basis, Description. Include per-curve calibration/geometry, gaps/clipping/overlap, unknown setups and source conflicts. |
| Curve_Data | Point_ID, Curve_ID, Point_Order, Segment_ID, X_Original, Y_Original, X_Normalized, Y_Normalized, X/Y_Original_Unit, X/Y_Normalized_Unit, X/Y_Uncertainty_Original, X/Y_Uncertainty_Normalized, Value_Status, Extraction_Evaluation, Quality_ID, Source_Sheet, Source_X_Cell, Source_Y_Cell. Include explicit gap/padding rows with blank numeric values; readable segment IDs never continue across a missing region. |
| Fitting_Data | Fit_Point_ID, Curve_ID, Point_ID, Segment_ID, X_Normalized, Y_Normalized, Suggested_Weight, Role, Fit_Eligible, Selection_Reason, Segment_Start/End, Reduction_Method, Quality_ID. Point_ID must reference Curve_Data; held-out selections remain labeled/excluded from fitting. |
| Validation | Test_ID, Entity_Type/ID, Role, Condition_Group_ID, Circuit_ID, Stimulus, Measured_Response, Comparison_Method, Tolerance_Basis, Tolerance_Value, Tolerance_Unit, Setup_Status, Missing_Prerequisites, Source_Page/Reference, Simulation_Status. Suggestions are not completed simulations. |

Missing numeric values are empty cells, never zeros, NaN or strings. Status
columns distinguish unknown conditions, omitted/unreadable values, padding,
clipping/overlap, and extraction failures. Include a source and Quality link for
every curve, including fully readable ones. Record curve segment boundaries,
sampling interval/log ratio or path layout, uncertainty and unresolved ranges
inside Excel so it can be used independently of this conversation.

## Normalization, uncertainty and fitting

Preserve original units and add normalized values in structured sheets: V, A,
s, Hz, Ω, F and V/s; temperature remains explicitly °C. Keep voltage p-p
distinct from peak/RMS, current magnitudes distinct from signed currents, gain/
rejection in dB, phase in degrees. Noise density is amplitude density V/√Hz
or A/√Hz, not power spectral density. Examples: µA×1e-6→A; µs×1e-6→s;
nV/√Hz×1e-9→V/√Hz; V/µs×1e6→V/s; mV/mA×1→Ω. Do not convert dB or phase
without an explicit downstream transformation. Retain repeated X observations.

Estimate X/Y positional uncertainty from stroke/native pixel width, axis
calibration residuals and verified tracing agreement, then propagate through
the calibration. Include rounding and local slope effects. For logarithmic
axes transform bounds back to data units; additive constants are inappropriate.
Label this a geometry envelope, not a standard deviation. Record whether points
are direct path vertices/markers, interpolated along visible geometry, or disclosed
dash interpolation. Never infer missing portions from a fitting model.

Build Fitting_Data from each readable segment independently. Simplify in source
axis space (log10 for log axes), checking reconstructed values at all retained
full-data coordinates against local extraction uncertainty. Preserve segment
endpoints, extrema, knees, transitions and repeated X. Keep path/scatter points
when reduction would destroy multi-valued geometry. Never bridge missing ranges.
Retain the full extraction in Curve_Data. Suggested numerical weights normalize
to 1 within each curve so resampling does not increase its total influence.
They are not statistical confidence; downstream curve/behavior weights remain a
separate choice. Holdout points may have normalized comparison weights but must
have Fit_Eligible=0 and an explicit validation role.

Suggest gain/phase, DC characteristics, noise, slew and output limits as fitting
constraints. Default small/large pulse responses and phase-reversal demonstrations
to validation holdouts; input traces are validation stimuli. For every proposed
test specify matching conditions, stimulus, response, comparison and tolerance
basis (local extraction envelope or applicable source limits). Typical values
without bounds are targets, not pass/fail tolerances. Mark incomplete setups
and unsigned/unknown conventions explicitly. Keep instructions simulator-neutral;
record ngspice only as a tentative future target. Simulation_Status is
not_run; do not claim a model or simulation has been validated.

## MCP6L01 reference interpretation

For DS20002140D, scan all 42 physical pages and include all 17 Figures 2-1–2-17
on pages 7–9. Scope pins/thermal data to MCP6L01 SC70 and SOT-23. Verify pins
1 VOUT, 2 VSS, 3 VIN+, 4 VIN−, 5 VDD on both page 1 and Table 3-1 page 11.
Pages 3–4 contain DC/AC/temperature tables. Table 1-1 min/max footnote says
"For design guidance only; not tested." Keep it distinct from typical values.
Use table IB=2 pA at25°C as preferred nominal evidence while preserving page14
Section4.6's 1 pA narrative in a conflict record. ZCM/ZDIFF are 10^13 Ω parallel
5/2 pF, not the concatenated PDF-text numbers. θJA is331°C/W SC70 and256°C/W
SOT-23. Preserve stress ratings separately from the1.8–6 V operating range.

Figure2-3 requires separate path pairs/repeated X. Figures2-1–2-3 are
representative-part offset observations, not nominal population specifications;
Figure2-4 is one wafer lot. Figure2-7 is below-rail input conduction through
ESD protection, separate from normal IB. Figure2-8 uses distinct gain/phase
Y axes. Figure2-13's mV/mA ratio normalizes to Ω. Figure2-14's source voltage
ticks are V with20 mV/div; a prior extraction may use mV if labeled consistently.
Figures2-10,2-14,2-15 are validation holdouts by default.

Visually verify page5 Figure1-1: both RG/RF=100kΩ; positive RG VP→VIN+,
positive RF VIN+→VDD/2, upper CF6.8pF VIN+→GND; negative RG VM→VIN−,
negative RF VIN−→VOUT, lower CF6.8pF VIN−→VOUT; CB1/CB2=100nF/1µF
VDD→GND; RL10kΩ VOUT→VL, CL60pF VOUT→GND. Equation1-1 states
GDM=RF/RG; VCM=(VP+VDD/2)/2; VOST=VIN−−VIN+;
VOUT=VDD/2+(VP−VM)+VOST*(1+GDM). VCM is not(VP+VM)/2;
VOST includes temperature/CMRR/PSRR/AOL effects. The printed mV definition
requires consistent units before using the equation numerically.

Include pages13–15 guidance: common-mode stage transition near VDD−1.1 V,
typical rail extension±0.3 V,35mV output headroom under stated load, input
protection and external D1/D2/resistors, external RISO for large CL (example
>100pF atG+1), and bypass/PCB leakage recommendations. The suggested4% overshoot
is RISO tuning guidance, not a guaranteed DUT limit. Preserve the Bessel example's
printed100Hz claim with11.3/20.5kΩ and100/68pF; its component-derived natural
frequency is about12.7kHz, so flag a source discrepancy instead of correcting it.
Other-variant unused-amplifier circuits are excluded. Page15's existing model
was tested in PSpice; compatibility and operation outside specs are not assured.
Do not fetch/install it as part of extraction.

## Embedded helpers

Copy into a temporary script when useful. Add source-specific tracing and
table construction; no permanent helper dependency is required.

```python
import math
import re
from pathlib import Path

import numpy as np
from openpyxl import load_workbook


def fit_axis(positions, values, logarithmic=False):
    p, v = np.asarray(positions, float), np.asarray(values, float)
    if (p.ndim != 1 or v.ndim != 1 or p.size != v.size or p.size < 2
            or not np.all(np.isfinite(p)) or not np.all(np.isfinite(v))
            or np.unique(p).size < 2):
        raise ValueError("Need at least two distinct, finite tick positions")
    if logarithmic and np.any(v <= 0):
        raise ValueError("Log-axis ticks must be positive")
    t = np.log10(v) if logarithmic else v
    if np.unique(t).size < 2:
        raise ValueError("Tick values must establish a nonconstant axis")
    a, b = np.linalg.lstsq(np.column_stack((p, np.ones_like(p))), t,
                             rcond=None)[0]
    if not math.isfinite(a) or not math.isfinite(b) or a == 0:
        raise ValueError("Degenerate axis calibration")
    # Inspect these source-coordinate residuals; scale confirmation is separate.
    residuals = (t - (a * p + b)) / a
    return float(a), float(b), residuals


def axis_values(positions, a, b, logarithmic=False):
    t = a * np.asarray(positions, float) + b
    return np.power(10.0, t) if logarithmic else t


def regular_positions(left, right, minimum_spacing):
    if not all(math.isfinite(v) for v in (left, right, minimum_spacing)):
        raise ValueError("Grid inputs must be finite")
    if right <= left or minimum_spacing <= 0:
        raise ValueError("Need a positive plot width and spacing")
    intervals = math.floor((right - left) / minimum_spacing)
    if intervals < 1:
        raise ValueError("Plot is narrower than one resolvable interval")
    return np.linspace(left, right, intervals + 1)


def sheet_name(title, ordinal, used_names):
    base = re.sub(r"[\x00-\x1f\x7f\[\]:*?/\\]", "_", title).strip()
    base = base.strip("'").strip() or f"Graph {ordinal}"
    if base.casefold() == "history":
        base = "History graph"
    candidate, suffix_number = base[:31].rstrip(" '"), 2
    while candidate.casefold() in used_names:
        suffix = f" ({suffix_number})"
        candidate = base[:31 - len(suffix)] + suffix
        suffix_number += 1
    used_names.add(candidate.casefold())
    return candidate


def save_unique(workbook, destination):
    destination = Path(destination)
    if destination.suffix.lower() != ".xlsx":
        raise ValueError("Workbook destination must have an .xlsx extension")
    number = 1
    while True:
        candidate = (destination if number == 1 else destination.with_name(
            f"{destination.stem}_{number}.xlsx"))
        try:
            stream = candidate.open("xb")
        except FileExistsError:
            number += 1
            continue
        try:
            with stream:
                workbook.save(stream)
            check = load_workbook(candidate, read_only=True, data_only=True)
            try:
                if check.sheetnames != workbook.sheetnames:
                    raise ValueError("Saved worksheet names/order differ")
            finally:
                check.close()
        except Exception:
            candidate.unlink(missing_ok=True)
            raise
        return candidate
```

## Verification and delivery

Compare source-registered reconstructions at off-grid positions, bends/extrema,
crossings, dashed portions and clipping boundaries. Reopen Excel and verify:
all selected graph sheets/order/headers/data preserved; stable IDs unique and
joins resolve; finite numeric cells and actual blanks; Conditions/Quality/roles/
sources for every curve; specification value-column status/footnotes and pins
match rendered sources; conversions and fitting error bounds; per-curve weight
sums; no holdout accidentally eligible; no formulas/charts/images/macros.
Record performed verification and its practical limits in Handoff. Do not claim
new digitization if the curves were reused from a verified prior workbook.

When revising the skill, validate YAML frontmatter/name/description, compile and
exercise embedded helpers, and check for missing references/unfinished scaffold.
Use a temporary SKILL.md wrapper for directory validators; do not install it.
Test source-aware calibration/sampling with synthetic nonlinear/coarse-grid/log/
reversed/crossing/dashed/raster/scatter sources where extraction mechanics change.
For handoff changes test clipped/missing ranges, repeated X, source conflicts,
conditional defaults, conversions, fitting error/segments/weights and workbook
readback. Synthetic ground truth checks mechanics, not general extraction accuracy.
Run acceptance on a real datasheet when available and describe reuse accurately.

Verify protected outputs remain unchanged. Remove temporary scripts, crops,
JSON inventories and test workbooks created by this run, leaving only the revised
skill and delivered Excel. Return a clickable workbook link and concise counts,
verification result and material unresolved conditions. All detailed support
information belongs in Excel; do not generate an external completion report.
