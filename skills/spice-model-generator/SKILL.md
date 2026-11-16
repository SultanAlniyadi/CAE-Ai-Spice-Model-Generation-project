---
name: spice-model-generator
description: >
  Generate an ngspice behavioral .SUBCKT from a reconciled requirement report,
  schema-1.0.0 extraction workbook, architecture recommendation and accepted
  test-author interface. Fit only eligible evidence and verify the DUT against
  the frozen, versioned acceptance suite without changing its tests or references.
---

# Behavioral SPICE Model Generator

## Authority and inputs

This skill implements only `operational_amplifier` and `voltage_supervisor` from
an existing, selected architecture. A recommendation is not permission to
change the accepted interface or the suite. Do not infer the manufacturer's
internal schematic from a behavioral equivalent. Do not install dependencies,
invoke other agents automatically, or modify the requirement report, workbook,
selector handoff, datasheet, test-author agent/skill, suite, or orchestrator.
Return conflicts, extraction requests and approvals to the parent. Respect
draft-only/no-write requests. This portable skill does not register the agent.

Require explicit paths to the complete readable PDF, its selected
`*_required_data_for_behavioral_spice.md` report, extraction `.xlsx`, and the
frozen suite root containing `manifest.json`, `interface.json`, `run_suite.py`,
`runtime.py`, benches and references. Require the selector's structured handoff
(it can be supplied as a parent message rather than a file), selected scope,
the suite manifest SHA256 retained independently by the parent/test author,
and external output destinations or an approved writable output parent. Never
substitute a different PDF/suite based on a plausible filename. The optional
missing-data report provides context, not numerical model inputs. If the
selector handoff or pinned hash is unavailable, request it before modeling.

## Reconciliation gate: no output before resolution

1. Read the complete input metadata, not just filenames. Compute the SHA256 of
   the actual supplied PDF bytes. Match it to workbook `Handoff` PDF hash and
   revision, selector `source.sha256`/revision and the PDF-kind entry in manifest
   `sources`. Verify the requirement report's PDF identity/revision and its hash
   when present; if the report omits a hash, resolve its recorded PDF path to
   the supplied PDF bytes and compare their SHA256, as well as revision. A path
   that cannot be resolved/verified is not a hash check. Missing/ambiguous source
   identity is a blocker, not permission to assume it matches. Record the actual
   hashes and each source locator. Never treat a workbook/suite file hash as the
   PDF hash.
2. Reconcile manufacturer, exact part, variant, package, grade, channel/mode,
   threshold option, family and scope across report, workbook Handoff and
   applicable Pins/Specifications/Metadata, selector target/scope and manifest
   `target`/`family`/source records. Resolve a selector's family-wide `parts` or
   `packages` list to the *same* selected member, not merely any member. Keep
   `unknown`, blank and documented not-applicable distinct; request confirmation
   when a selection-critical field cannot be proved. Check source-referenced
   pin IDs and mapping in `interface.json` against applicable workbook `Pins`.
3. Require workbook schema `1.0.0` and sheets `Handoff`, `Metadata`, `Conditions`,
   `Specifications`, `Pins`, `Test_Circuits`, `Quality`, `Curve_Data`,
   `Fitting_Data`, `Validation`, with the documented headers even if header-only.
   Inspect IDs, joins, condition groups, units, sources, variant applicability,
   statuses and quality flags; reject broken/ambiguous joins or unusable values.
   The report's individually named `NEEDED` items must be traceable to applicable
   workbook evidence and to suite requirements/coverage, or be explicitly
   documented as an evidence blocker or parent-approved out-of-scope exclusion.
   Block essential missing evidence rather than converting blanks to zero or
   silently dropping a behavior. Check that selector `status`, recommended
   architecture, ngspice compatibility path and essential data actually cover
   mandatory in-scope behaviors. An unsupported/conditional essential feature
   requires an approved implementation path or a blocker, not an invented fallback.
4. Inspect the versioned manifest, acceptance roles/coverage, referenced benches
   and reference files, and accepted interface approval. A `proposed` interface
   cannot be used for DUT acceptance; ask the parent for an approved new suite
   version, not an in-place edit. Treat suite contents as trusted executable
   Python and model/deck files as executable simulator input; review as needed.
   The structural runner cannot prove PDF semantics or bench wiring, so check
   relevant conditions and applicability independently. Report any global suite
   blocker or mandatory/core blocked coverage without pretending it can pass.

For *any* conflicting part/variant/package/PDF hash, report both values and
locators to the parent and stop before generating a model or log. If other
essential input gates fail, return precise blockers before output. Never guess
or silently overwrite an existing destination.

## Frozen suite integrity

From the supplied suite, before model generation, run its exported copy of the
runner (not the development template), using absolute paths where possible:

```powershell
python -B <suite>/run_suite.py validate --suite <suite>
```

Require exit code 0 and `status: valid`. Compare returned `manifest_sha256`
with the parent's independently pinned 64-hex hash; also independently hash
`manifest.json` and compare. `validate` checks the exact frozen file inventory
against `manifest.hashes` except the root manifest itself. A successful
self-consistent validation alone is not independent approval. If hashes differ,
files are missing or the suite is invalid, stop and report; never call `seal`,
rewrite hashes, change tests, criteria, benches, references or interface.
Record suite ID/version, pinned hash and interface status. Repeat validation and
pinned comparison immediately before each DUT suite invocation, and check the
returned results hashes and inventory again afterward. Keep models, scratch
fitting data, logs, results and Python caches outside the suite.

## Build the model from evidence

- Set `.SUBCKT <interface.subcircuit> <terminal 1> ... <terminal N>` in the exact
  ordered, case-insensitively matching `interface.json` terminal-name list; end
  with `.ENDS <interface.subcircuit>`. This is logical SPICE order, not physical
  package order. Match each terminal's role, `pin_ids`, channel, NC/exposed-pad
  applicability and shared rails to the verified selected package. Do not remove
  terminals merely because a stage does not use them.
- Implement the selector's primary architecture and only applicable supporting
  methods. For an op amp, derive input polarity/bias/common-mode behavior,
  gain/compensation or slew dynamics, output limits/loading, supply behavior and
  enabled states **only where** relevant source evidence exists. For a supervisor,
  derive applicable sense/threshold direction, hysteresis state, timing/startup,
  manual/watchdog behavior and push-pull/open-drain driver **only where** evidenced.
  Unidentified states, optional functions, noise or limits are not free model
  parameters. If an essential stage cannot be built, stop/request evidence.
- Parameterize from applicable `Specifications`, `Conditions`, `Test_Circuits`,
  `Pins`, `Metadata`/`Quality` and fit-eligible `Curve_Data` joined through
  `Fitting_Data`. Check conditions, limit class (typical versus guaranteed),
  source region, direction, sign, reference state, load and normalized units.
  Trace each numeric model parameter to workbook row/curve/condition IDs in the
  work log. Use workbook values and conditions only: no guessed operating point,
  invented pole, resistance, delay, clamp, smoothing constant or numeric corner.
  If implementation needs an unsourced number, request extraction/approved
  evidence through the parent; approval alone is not a fabricated datasheet fact.
  Do not extrapolate across unreadable spans or reuse other variants' values.
- Prefer verified core ngspice R/C/L, supported dependent/behavioral sources and
  analog state/switch realizations when the selector's primary path is core.
  Check installed ngspice syntax, version and build before optional XSPICE or
  version-dependent elements; the selector's documented path is not a runtime
  check. No unsupported cross-dialect `LAPLACE` E source, unverified XSPICE
  `s_xfer`/`pwl`, or assumed .noise contribution from deterministic B sources.
  The resulting `.lib` must be self-contained: no `.include`, `.inc`, `.lib`
  directives/sections or external model assets (the runner rejects them). Run
  a bounded parse/operating-point or analysis-specific smoke circuit against
  the actual installed ngspice binary, recording results separately; no fixture
  or smoke result counts as DUT acceptance. Do not code bench-specific answers.

Write a unique `.lib` path outside the suite; do not overwrite a prior model.
Its leading SPICE comment header (`*`) must state exact selected part, variant
and package, generation date with timezone, architecture and supporting methods,
source suite ID/version and pinned manifest SHA256, plus model scope/traceability
to the workbook. The `.lib` filename extension does not authorize `.lib` section
syntax. Compute the model SHA256 only after its bytes are finalized; preserve
that candidate unchanged during suite execution.

## Fitting and iteration budget

At most **10 candidate iterations total**, including the initial model and every
subsequent parameter revision. Maintain an external ledger of candidate number,
parameter IDs/values/units, fit-only evidence IDs, objective and outcome. Only
`Fitting_Data` rows with `Role=fitting` AND `Fit_Eligible=1`, verified applicable
`Curve_Data`/conditions and source-supported specification constraints may drive
parameter adjustment. A specified/typical workbook value can initialize a fixed
parameter where applicable; distinguish it from a fitted observation. Do not use
`Fit_Eligible=0`, `holdout`, workbook `Validation`, frozen references, or any suite
test result to select parameters, weights or model structure. Honor per-segment
gaps, repeated X, source status and units; suggested weights have only their
documented meaning, not confidence or a new model-accuracy budget. Fit under
source-supported or independently approved fitting objectives only; do not
derive a tolerance from digitization geometry or a suite criterion. Stop early
when those objectives and numerical stability are met, or no justified update
remains; at iteration 10 stop regardless. Record unmet or undefined targets,
non-identifiable parameters and convergence limits. Never relabel fit reuse as
independent validation.

Use the frozen acceptance suite on the final candidate, not as the fitting
optimizer. In particular a failed holdout may not trigger tuning on that
holdout: record rejection and request fresh evidence/authorized reauthoring
through the parent. If environmental troubleshooting warrants rerunning, use
the identical model SHA256 and pinned suite SHA256 in a fresh external results
directory, label the repeat and disclose that viewed holdouts are no longer
blind. If a suite change is necessary, request a *new* test-author suite version.

## DUT execution and results

Preflight Python 3.10+, PySpice availability/version, ngspice executable/version
and required build features without installing software. The unmodified runner
currently blocks any nonempty `simulator.required_features` pending a reviewed
runner extension/probe; do not claim a local feature probe makes it accept.
After the final model and renewed `validate`, execute the exported runner:

```powershell
python -B <suite>/run_suite.py run --suite <suite> --model <absolute-model.lib> --results <external-results-parent>
```

If needed pass `--ngspice <verified-executable>`. The external results parent
must not be inside the suite. The runner creates a unique `run-*` directory
containing `results.json`, per-test logs/decks/traces and `ngspice-version.log`.
Keep stdout/stderr and exit code. Exit 0 means runner accepted; 1 means runner
rejected or unresolved; 2 means invalid invocation/contract. A missing dependency
or required feature is a documented blocker, never a pass: if `run` can execute,
retain its external `results.json` with blocked statuses; if it cannot, record
all unrun tests and the exact reason in the log. Never change the suite to bypass
a block. Do not use harness/fixture evidence as DUT results.

Check `results.json` `manifest_sha256` against the pinned hash, `model_sha256`
against your finalized `.lib`, `suite_version` and `suite_id` against the
validated manifest; inspect `preflight_blockers`, `integrity_errors`, each
`results[]` status and the final `acceptance`. A hash or integrity mismatch is
unresolved and must be reported even if a test measurement passed. Use the
manifest's `criterion.kind` (never `type`) and the runner's evaluation; do not
re-evaluate acceptance with an invented comparison or relaxed tolerance.

## Model test log and acceptance

Produce a unique `model_test_log.md` or `.txt` beside the model or in another
external destination. Include the PDF/workbook/report/selector/suite/model
paths and identities, source suite version, manifest SHA256 and model SHA256;
Python, PySpice and actual ngspice versions (read the runner's version log;
write `missing` or `unknown` if unavailable); commands, validate outcome,
preflight/integrity errors, run-results path, actual iterations and fitting
decisions, and the final `accepted`, `rejected` or `unresolved` status. Disclose
limitations, approved exclusions, unsupported features, pending extraction or
approval, and whether a suite was actually run against the DUT.

Join every manifest test ID to its `results.json` entry; when execution never
started, treat each as unrun unless a known prerequisite blocks it. Tabulate
total, passed, failed, blocked, errored, unrun for each priority
`critical/high/medium/low` and each `blocking/advisory` role, including combined
priority-by-role breakdown and grand totals. Runner `timeout` counts as errored
with a separately shown timeout subtotal. `out_of_scope` remains excluded/unrun
with a separate subtotal, not a pass (include its scope approval). Missing
result entries are unrun. For each `fail`, give test ID, measured `value` or
computed curve error, criterion `kind`, reference and inclusive expected bound:
`interval` [min,max], `minimum` >= min, `maximum` <= max,
`absolute_error` |value-reference| <= tolerance, `relative_error`
|value-reference|/max(|reference|,zero_floor) <= tolerance, or `curve_error`
max/RMS aligned error <= tolerance (with optional period). For scalar error
criteria `value` is the measured scalar and `error` is the evaluated difference
(a dimensionless ratio for `relative_error`); for `curve_error` `value` is the
reduced aligned error and `measurement.values` contains the compared samples.
Preserve the criterion quantity unit and explicitly label dimensionless ratios;
do not mislabel a measured scalar as its error. For each `blocked` test give
its ID and runner `detail`, manifest `prerequisites` and global blockers as
applicable; report errors/timeouts/unrun reasons individually as well.

Accept **only** when the runner reports `accepted`, at least one in-scope
blocking gate exists and every such gate passed; no blocking gate may be
blocked, errored, timed out, failed or unrun. Require no blocked in-scope
coverage, suite-global blockers, preflight/integrity/hash errors or unresolved
source identity. Blocking `fail` rejects; otherwise any missing gate pass or
incomplete verification is `unresolved`. Advisory failures/errors remain
visible but do not themselves reject; out-of-scope tests do not pass. Do not
override the runner's `unresolved` or `rejected` with a more favorable status.

Return a brief parent handoff: `.lib`, log and external results paths (if
produced), suite/model hashes, iterations, final status, highest-priority
blocking failures, and precise extraction/approval requests. When the input
gate fails before model creation, return the conflict and locators without
fabricating a model, log or DUT test outcome.
