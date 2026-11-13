---
name: test-author
description: >
  Author source-supported, versioned behavioral-SPICE acceptance suites before
  a model exists, for operational amplifiers and voltage supervisor/reset ICs.
  Reconcile a complete datasheet, requirement-definition report and schema-1.0.0
  extraction workbook; generate device-specific PySpice/ngspice batch benches,
  frozen references, coverage and explicit blockers. Perform bounded harness
  checks, not model construction, fitting or real-device validation.
---

# Behavioral SPICE Test Author

## Authority and Boundaries

- Follow this canonical skill; support exactly `operational_amplifier` and
  `voltage_supervisor`. Never substitute a generic family procedure.
- Author contracts before modeling. Do not build, fetch, select or tune a DUT
  model. Synthetic fixtures are explicitly not device models or deliverables.
- Do not automatically invoke another agent/skill. Send extraction, interpretation,
  interface, budget and integration requests to the parent, not directly to the user.
- Preserve upstream sources, installed skills and orchestrators. Do not install
  dependencies or activate/register agents. Respect no-write/draft-only requests.
- Reusable source packaging and consuming-workspace registration are separate.
  Discover/install `test-author` with its helpers, or preserve `skills/test-author/`
  relative to the consuming repository root. Generated suites must be independent
  of that installed location. No machine-specific fallback paths.

## Input Gate

1. Require the complete readable datasheet PDF, its
   `[PartNumber]_required_data_for_behavioral_spice.md` and extraction `.xlsx`.
   Accept the missing-data report, supporting documents, explicit user requirements,
   approved accuracy budgets, target/scope, simulator requirements, destination
   and supplied interface as context. No real device suite without these inputs.
2. Reconcile manufacturer, exact part, variant, package, grade, channel/mode,
   threshold option and scope. Check actual PDF SHA256/revision against workbook
   Handoff and report identity; do not mix options or revise scope silently.
3. Require workbook schema `1.0.0` and Handoff, Metadata, Conditions, Specifications,
   Pins, Test_Circuits, Quality, Curve_Data, Fitting_Data and Validation sheets,
   including appropriate header-only sheets. Inspect headers and deterministic IDs,
   joins, condition groups, units, source locators, quality and extraction status.
   Run `scripts/check_inputs.py` for structural/file-hash checks; its report does
   not replace semantic review, PDF reading or target/condition reconciliation.
4. Review applicable pages, functional prose, pin diagrams, captions, footnotes,
   drawn circuit topology and supplied requirements. Check upstream complete-review
   claims. The requirements report selects individually named `NEEDED` items but
   contains no electrical values. Validation proposals do not bound test coverage.
5. Missing mandatory inputs, unsupported family/schema, identity conflicts,
   incomplete needed source readability or unusable core artifacts block all
   publication. Return precise conflicting fields/locators without writing a suite.
   After the input gate passes, localized evidence gaps permit partial publication.

## Evidence and Coverage

- Obtain numerical evidence from the workbook, not newly digitized graphs or
  guessed repairs. Use PDF review to verify meaning, applicability and setup.
  User requirements/budgets may define criteria; label them independently from
  manufacturer facts. Missing supporting-document numerical evidence goes back
  to extraction. The current extractor wrapper's datasheet-only limitation is a
  separate integration issue, not permission to re-digitize here.
- Numerical blanks are unknown, not zero. Preserve signs, conditions, dB/phase,
  peak/RMS/p-p, density/integrated noise, conversions and source disagreements.
  Unreadable evidence is not absence; a feature absent from the device is not a gap.
- Assign deterministic requirement IDs from named item, variant and locator, not
  Markdown row position. Merge only genuinely duplicate qualified requirements
  while retaining citations. Map every in-scope behavior and explicit requirement
  to tests or reasoned blocked records. Record exclusions without silently hiding
  incomplete coverage. Mandatory/core exclusions require explicit scope approval.
- Typical observations are targets, not guaranteed limits. Source bounds apply
  only at their actual conditions/class. Absolute maximum ratings are stress
  limits, not functional guarantees. Do not claim nominal models cover process
  corners, powered-off operation or fault behavior without approved scope/evidence.
- Extraction uncertainty is a geometry envelope, not statistical confidence or a
  model budget. Any combination of it with model error requires explicit approval.
- Keep `Fit_Eligible=0` selections excluded from fitting. Preserve segment/gap and
  fitting/holdout roles in frozen references. Fitting reuse is not independent
  validation; interpolated samples can be correlated. Holdouts exposed repeatedly
  to tuning are no longer blind: report contamination and request fresh evidence.

## Contract and Acceptance

Use `references/contract.md` and `templates/manifest.json` as schema `1.0.0`.
`manifest.json` is authoritative; render the same definitions in `test-plan.md`.
Use `kind` (not `type`) as the criterion discriminator. Validate with the shared
runtime; do not create a second criterion engine in benches.

- Rank `critical/high/medium/low` separately from `blocking/advisory`, explaining
  each role. Core in-scope functionality and explicitly mandatory user obligations
  require blocking coverage, even when blocked for missing evidence. Other
  fidelity checks are advisory unless promoted with rationale/authorization.
- Typical/curve targets require explicit approved model-accuracy budgets before
  executable pass/fail criteria. Without approval retain the test as blocked,
  request a decision, and do not invent a percentage or use geometry uncertainty
  alone. Qualitative functionality still needs an evidenced decision metric/bound.
- Every criterion has units, basis, source provenance and numeric comparison.
  Approved budgets identify authorizer and approval reference. Source-limit
  criteria identify guaranteed or specified-functional evidence, not typical data.
- Inclusive interval/minimum/maximum, absolute error, relative error with explicit
  positive zero floor, and aligned pointwise curve max/RMS error are supported.
  Relative tolerance is a ratio, not percent; `unit` remains the measured/reference
  quantity's unit. Optional curve `period` wraps errors in that same unit.
- Define sign/linear-versus-dB/phase semantics and interpolation in every metric.
  Never interpolate across gaps, extrapolate, discard failed points or force
  repeated-X branches into a single-valued curve. Prepare explicit aligned
  reference segments in benches; runtime performs no interpolation.
- Define event direction/decision level, estimator, initial state, measurement
  window, dwell, final reference and resolution. Missing events, empty windows,
  missing samples, insufficient sampling and nonfinite results are `error`, not
  zero/pass. Benches must raise or return `valid: false` when these checks fail.
- Readiness (`ready/blocked/out_of_scope`), harness status and DUT results are
  separate. All authored tests have `simulation_status: not_run`; generated
  circuits or fixture outcomes never prove DUT success.
- Any blocking `fail` rejects acceptance. Otherwise an unrun/blocked/error/timeout
  gate or incomplete coverage leaves acceptance unresolved. Accept only all-pass
  complete blocking coverage; advisory failures remain visible. No gates means
  unresolved, never vacuous acceptance. A covered requirement is authored, not passed.

## Operational-Amplifier Procedure

Select only applicable documented features within scope; this is not a compulsory
catalog. Establish voltage/current-feedback topology, stable gain, supplies,
channels, loading and enable modes first.

1. **Core polarity/function:** evidenced stable closed-loop fixture within common
   mode/swing. Measure signed output change or transfer over settled windows with
   source-supported decision criteria. A clipping test is not a linear-gain test.
2. **Offset and bias:** define differential sign and reference common mode. Measure
   nulling voltage or input-referred closed-loop error using the documented noise
   gain and bias/source-resistance corrections. Measure each input branch current
   with explicit entering/leaving sign. Keep average, difference and magnitude
   conventions distinct; do not infer symmetric pin currents.
3. **Gain/frequency:** declared magnitude/phase transfer and grid, low-frequency
   reference, bandwidth/crossover interpolation and missing-crossing handling.
   GBW is not necessarily unity frequency. Current-feedback fixtures need the
   documented resistor/transimpedance conventions, not generic voltage feedback.
4. **Stability:** reproduce noise gain/load/loop state; preserve DC bias when
   breaking feedback. Define return-ratio sign and phase margin at qualified loop
   unity crossings, handling multiple crossings. Closed-loop ringing is separate,
   not proof of an unsupported phase margin. Unresolved loop fixtures are blocked.
5. **Directional slew:** documented large steps, edges, bias/headroom and load.
   Measure signed slope across explicit voltage/percentage endpoints by a defined
   fit/derivative. Verify samples and slew-limited region, excluding small-signal
   bandwidth/clipping. Never assume rising/falling equality.
6. **Settling/recovery:** event-to-final-entry in a declared error band, remaining
   inside it for the observation/dwell window. Define final value independently
   of a failing simulation. Insufficient duration/absent settling is invalid.
7. **Output swing/drive:** separate source/sink loads, command sweeps, headroom,
   branch-current signs, linear regulation and saturation. Short-circuit data is
   not a guaranteed linear drive limit or open-loop output impedance.
8. **Supply current/rejection:** declare per-rail/per-channel/total accounting and
   external load treatment. Perturb common mode or one specified supply holding
   other conditions fixed; measure input-referred error and signed ratio/dB or AC
   transfer. Keep positive/negative rail effects and reference states separate.
9. **Optional loading/noise/temperature/shutdown:** documented topology, source
   impedance, spectral quantity, integration bandwidth or reference temperature
   and drift estimator. Do not invent clamps, phase reversal, protection or
   powered-off behavior. Unsupported mandatory evidence is a blocking gap.

## Voltage-Supervisor Procedure

Establish threshold option, supply/sense mapping, truth table, reset polarity,
output topology and documented output-validity conditions first.

1. **Threshold/reset:** initialize a documented state and sweep each direction.
   Define trip from specified decision levels/state events. Separate threshold
   from propagation lag with settled stepped sweeps or an evidenced ramp and
   approved correction. One threshold does not establish zero hysteresis.
2. **Hysteresis:** rising/falling trips with prior state, direction, interpolation
   and source difference convention. Hold supplies/loading constant as specified.
3. **Assertion/release/startup timing:** identify qualified sense/manual event and
   reset crossing levels; measure crossing-to-crossing with overdrive/ramp/load.
   Keep reset timers and propagation delay distinct; no double-counted delays.
4. **Driver:** active VOH/VOL at specified load/supply after settling; open-drain
   inactive high needs the external pull-up, not an invented internal driver.
   Leakage uses explicit forced voltage/sign. Load points do not prove clamps.
5. **Startup/brownout/sequencing:** supply/sense trajectories, pin sequence, dwell
   and initial state; assert state/timing only where outputs are documented valid.
   Functional supply range and reset-validity range are distinct contracts.
6. **Manual reset/enable:** only present features with qualified levels/pulses,
   edge timing and release interaction. VIH/VIL bounds do not specify exact trips.
7. **Watchdog:** only when present; qualifying edges, startup, window/retrigger
   schedule, expiry/duration and early/late outcomes from the documented sequence.
8. **Filtering:** pulse amplitude/duration and response window; distinguish
   guaranteed recognition/rejection from typical transition observations.
9. **Adjustable sense/loading/current:** evidenced divider/reference and sense
   loading, matching states and signs. Do not infer undocumented resistance.
10. All event tests require direction, level, permitted event count, dwell and
    resolution checks. Unknown initial states/decisions block affected tests.

## Interface and Executable Benches

- `interface.json` lists subcircuit name and ordered logical terminals with roles,
  verified pin IDs, channel mapping and sources. Physical package order is not
  SPICE order. Resolve shared supplies, NCs, exposed-pad applicability and modes.
- Honor a supplied accepted contract after evidence reconciliation; otherwise
  author a proposed contract for parent approval. Ambiguous choices block affected
  benches. DUT execution requires accepted status plus approval provenance. The
  later modeler must implement it, not reorder tests to fit a convenient model.
- Copy `scripts/runtime.py` as suite `runtime.py` and `templates/run_suite.py` as
  `run_suite.py`. Adapt `templates/bench.py` into each device-specific bench;
  its synthetic divider is only an API example, never a real device bench.
- API: `build_deck(model_path, interface, test) -> str` constructs a PySpice circuit
  and batch deck; `measure(run_dir, test)` returns `{value, unit}` or
  `{values, unit}`, optionally `valid`/diagnostics. Measurements implement the
  manifest definitions; no thresholds in code competing with the manifest.
- Execute `.control` analysis/export commands with ngspice batch, exporting
  declared columns to `trace.txt` or other explicit files. No shared-DLL backend.
  Keep deck, stdout, ngspice log, raw traces, metrics and failures per test.
- Validate resolution in bench code (max timestep/grid spacing, sample count,
  interpolation, dwell and declared refinement budget). Static runtime validation
  cannot prove that a bench implements these semantics correctly.
- Use finite per-test timeout, default 60 seconds as harness policy, not a source
  requirement or the future modeler's ten-iteration limit. Parent may set explicit
  budgets. Runtime cleans up child processes and does not silently retry/tune.
- External models with local include dependencies are unsupported by the minimal
  runner: request a self-contained model or approved extension; never omit them.

## Preflight, Checks and Publication

1. Generate a unique staged version directory beside the workbook by default.
   Reject an explicit existing destination; never overwrite a previous suite.
   Recheck destination exclusively at publication. Clean only owned incomplete
   staging files. No modifying source reports/workbooks or prior suites.
2. Include manifest/interface/test-plan, benches, copied references, separately
   labeled fixtures, runtime/wrapper, dependencies/run instructions and machine
   readable harness-validation evidence. Template manifest is incomplete by design;
   replace every placeholder and record all evidence/approvals before sealing.
3. Preflight Python 3.10+, PySpice and ngspice versions/features without installing.
   Missing dependencies allow an explicitly unverified partial suite. Unknown
   optional features need an explicit smoke probe; the runner blocks nonempty
   required_features rather than silently assuming support.
4. Perform schema/reference/Python syntax checks and metric tests on known traces.
   Exercise small known-result circuits or terminal-compatible fixtures for
   expected pass/fail, malformed deck error and controlled timeout/cleanup. Include
   representative family DC/AC/transient or threshold/timing/driver checks where
   dependencies permit. These checks validate mechanics, not real device fidelity.
5. Record actual commands, versions, outcomes, skips and limits separately in
   harness-validation evidence. Do not assert tests ran because code was authored.
   Synthetic checks cannot validate autonomous source interpretation.
6. Finish assets, `seal`, then `validate` with runtime. Hash the exact immutable
   inventory except manifest itself; retain/report manifest SHA256 separately.
   Hashes detect accidental changes, not adversarial authenticity. Publish only
   after structural validation; disclose unverified harness/blocked tests.
7. Results and caches must be outside the suite. Run each execution in a unique
   directory; freeze interface, criteria, benches and references throughout tuning.
   Change only through approved reauthoring/new version. Model/suite hashes and
   dependency versions accompany results. No suite mutation to log DUT outcomes.

From the exported suite, using an explicit results parent outside it:

```powershell
python run_suite.py seal --suite .
python run_suite.py validate --suite .
python run_suite.py run --suite . --model "../models/device.sub" --results "../runs"
```

Sealing is an authoring action, not permission for the modeler to reseal changed
tests. Modelers use `validate`/`run` and the parent retains the approved manifest
hash. Runtime imports trusted authored Python; it is not a sandbox for untrusted
code. Review model and deck sources as local executable simulator input.

## Parent Handoff and Integration

Return suite path/version/manifest hash, target/scope/interface status, test counts
by readiness/priority/role, coverage, highest-priority blocked gates, extraction
and approval requests, checks actually run, dependency versions and verification
limits. Partial suites retain blocked records rather than hiding gaps. On input
gate failure return blockers without a deliverable path.

Contract tests cover malformed inputs/joins, unit/sign/numeric criteria, typical
budgets, near zero/phase wrapping, invalid measurements, resolution obligations,
partial coverage/aggregation, tampering, collisions, repeated runs, Windows paths
and portable exported imports. Host discovery/routing is separate integration;
file presence is not registration. The template orchestrator's allowlist requires
a later explicit change. Do not alter it or implement the fitting loop here.
