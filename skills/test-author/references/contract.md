# Suite Contract 1.0.0

This is the shared authoring/runtime contract, not device-specific evidence.
The runtime validates structure; the author must verify physical meaning,
numerical conditions, source joins, fixture design and coverage against inputs.

## Manifest

`schema_version` is `1.0.0`. `suite_id` and `suite_version` are nonempty strings.
`family` is `operational_amplifier` or `voltage_supervisor`.

| Field | Contract |
|---|---|
| target | Object with part, variant, package, grade, channel, scope. Part and scope are nonempty. Other fields explicitly identify the selection or unknown/not-applicable status. |
| sources | Nonempty list of id, kind, sha256, revision, locator. Source IDs are unique; hashes identify actual original bytes. Include approvals as sources when cited. |
| interface_file | Portable suite-relative path, normally interface.json. |
| simulator | backend = ngspice_batch, required_features list, positive finite timeout_s (default policy 60). Unknown optional features block execution until an approved probe/extension exists. |
| requirements | Nonempty list of unique id, description, source_refs, mandatory boolean, core boolean. |
| coverage | Exactly one record per requirement: requirement_id, test_ids, disposition, reason. Disposition is covered, blocked or out_of_scope. Covered requires all related tests ready; mixed readiness is blocked coverage. Exclusions require scope_approval with by/reference. |
| tests | Nonempty list described below. Each test appears in coverage for each referenced requirement. In-scope mandatory/core coverage has at least one blocking test. |
| hashes | Exact immutable inventory path -> lowercase SHA256, excluding only root manifest.json. Empty before sealing; never reseal during fitting. |
| assumptions | List of explicitly authorized/labeled authoring assumptions. Not facts. |
| blockers | List of global unresolved prerequisites; any entry prevents DUT acceptance. Individual evidence gaps belong in test prerequisites and blocked coverage instead. |
| harness_validation | status = not_run/pass/fail/blocked, evidence_files list. Records mechanics only. A pass requires evidence; static checks do not prove real DUT correctness. |

Source references are objects with `source_id` and nonempty `locator`, optionally
`entity_ids`, `condition_group_ids`, `circuit_ids`, `quality_ids` as lists of stable
text IDs. Workbook joins are checked before generating these references; runtime
checks source IDs but cannot resolve workbook entities from hashes alone.

## Tests

Each test has these required fields:

```text
id, requirement_ids, description, behavior, applicability, priority,
acceptance_role, role_reason, readiness, prerequisites, analysis, conditions,
stimulus, fixture, metric, criterion, source_refs, reference_files,
evidence_role, bench, timeout_s, simulation_status
```

- ID: portable alphanumeric/underscore/hyphen identifier, unique ignoring case.
- Priority: critical/high/medium/low. Acceptance role: blocking/advisory, with rationale.
- Readiness: ready/blocked/out_of_scope. Blocked records list precise prerequisites.
- Analysis: op/dc/ac/tran/noise. Conditions/stimulus/fixture are nonempty objects
  for ready tests; encode every relevant bias, source setting, load and connectivity.
- Metric: name, unit, definition (nonempty text), window and resolution (explicit
  nonempty definitions/settings). Bench code must check declared sample/window/
  event/dwell/refinement constraints. Runtime cannot infer this from prose.
- Criterion: supported comparison below; null allowed for blocked/excluded tests.
- Source references: nonempty list. Reference files: existing suite-relative paths.
- Evidence role: fitting/holdout/functional/target. Typical target source-limit
  comparisons are prohibited. Do not imply fitting evidence is blind validation.
- Bench: existing `.py` under benches/ for ready tests, otherwise may be null.
- Timeout: positive finite seconds for the full build/simulate/measure sequence;
  cleanup/preflight/reporting have separate bounded overhead. Simulator stage
  also respects simulator.timeout_s. Default policy is 60, not a device limit.
- Simulation status: always not_run in authored immutable manifest.

## Criterion

All criteria have `kind`, `unit`, `basis`, `provenance` (source references).
Basis is `source_limits` with `evidence_class: guaranteed|specified_functional`,
or `approved_budget` with `approval: {by, reference}`. Do not use a typical curve
as a guaranteed source limit. Unit equals the measured/reference quantity unit;
convert explicitly before evaluation. An approved relative tolerance is a ratio.

| Kind | Fields and inclusive comparison |
|---|---|
| interval | min, max; min <= measured <= max |
| minimum | min; measured >= min |
| maximum | max; measured <= max |
| absolute_error | reference, tolerance >= 0; abs(measured-reference) <= tolerance |
| relative_error | reference, tolerance >= 0, zero_floor > 0 in reference units; abs(error)/max(abs(reference),zero_floor) <= tolerance |
| curve_error | nonempty aligned reference list, tolerance >= 0, reduction max/rms, optional positive period or null. Compare all aligned points; wrapped signed error = (error+period/2) % period - period/2. RMS is sqrt(mean(error squared)). |

Numbers must be finite, not booleans. Missing/nonfinite samples or absent events
are errors. No interpolation, masking, extrapolation or implicit unit conversion
occurs in the evaluator. Benches supply explicitly aligned segmented values and
check evidence geometry. Store approval for any uncertainty/budget combination.

## Interface and Bench API

`interface.json`: subcircuit (portable SPICE name), terminals (ordered nonempty
list of name, role, pin_ids, channel), status proposed/accepted, source_refs.
Accepted status additionally requires approval by/reference. Terminal names are
case-insensitively unique; physical package order is not logical SPICE order.
The self-contained model must declare this name and ordered terminal names.

Each trusted bench exports `build_deck(model_path: Path, interface: dict,
test: dict) -> str` and `measure(run_dir: Path, test: dict) -> dict`.
Measurements return value or values, unit, optional valid/diagnostics. Valid must
be true for all required samples; use exceptions/valid=false for invalid windows.
Returned measurements must be finite JSON-serializable values.

Construct DUT circuits with PySpice, include the supplied self-contained model
and instantiate the accepted ordered terminals. The runtime checks inclusion
and instance presence as a minimal guard; this does not prove correct wiring or
that a metric observes the DUT. Review against the manifest and exercise each
measurement on known-result traces. Do not use the synthetic divider template
as a DUT bench. The template refuses non-fixture calls.

Run exports to separate per-test directories, never into the immutable suite.
Python bench execution is isolated and timed out but trusted, not sandboxed.
Model `.include`/`.inc` dependencies are unsupported; `.lib` sections are not
supported by this minimal self-contained-model contract. Request an extension
instead of silently dropping dependencies. PATH or an explicit ngspice executable
is accepted; record the actual version log and required features.

## Publication and Results

Copy runtime.py and run_suite.py into each suite; dependency constraints in
templates/requirements.txt are a starting point, not proof of installed support.
Every file (including instructions/harness evidence/helpers) is hashed except
the root manifest. Avoid symlinks, caches, duplicate case paths and Windows device
names. Stage exclusively, seal once, validate, publish without collision. Parent
retains the manifest SHA256 independently. Do not modify any frozen file in tuning.

Results live outside the suite in unique run directories. Results JSON records
suite version, manifest/model hashes, dependency versions/logs, preflight blockers,
integrity errors and per-test status. Execution exits 0 for accepted, 1 for
unresolved/rejected, 2 for invalid invocation/contract. Blocking failures reject;
otherwise missing gate passes, coverage/global blockers or integrity changes leave
acceptance unresolved. Advisory failures remain reported. Fixture/harness results
never establish DUT acceptance. No blocking gates means unresolved.
