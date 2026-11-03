# Requirement Definition Consolidation Plan

## Goal and Scope

Consolidate op-amp and voltage-supervisor behavioral parameter extraction into one skill and subagent named `requirement-definition`, with a registered `/requirement-definition` command. Ensure every in-scope agent except `ruthless-orchestrator` is a subagent. Do not inspect for changes to or modify `agents/ruthless-orchestrator.md`.

Use `skills/requirement-definition/SKILL.md` as the single canonical skill. Rename `agents/spice-model-extractor.md` to `agents/requirement-definition.md`, set its agent identity to `requirement-definition`, and declare `mode: subagent`, preserving its description and required tools. Add `.mplab-ai/command/requirement-definition.md` as a thin command wrapper that delegates to this subagent rather than duplicating its workflow. Remove the obsolete `skills/spice-extract/`, `skills/opamp-spice-extractor/`, and `skills/voltage-supervisor-spice-extractor/` directories; do not leave compatibility stubs.

## Implementation

1. Rename the existing entry skill directory to `skills/requirement-definition/` and make its `SKILL.md` the sole complete extraction workflow. Retain shared source review, part identification, output, missing-data, and reporting requirements, and incorporate the full specialist content as mutually exclusive conditional procedures:
   - Op-amp: part/topology identification; input; gain/frequency; slew/output; CMRR/PSRR; noise; associated extraction, derived-value, and modeling-technique guidance.
   - Voltage supervisor/reset IC: channel/output/polarity identification; threshold; timing; output driver; supply; optional MR/watchdog; associated extraction and modeling-technique guidance.
2. Define one consistent report contract: `[PartNumber]_behavioral_spice.md` with three explicit sections (information needed, information not needed, modeling techniques) and `[PartNumber]_missing_data.md` for required parameters genuinely absent from the datasheet. Preserve source attribution/order, graph-only values in the main report, and part-specific filtering. Replace the contradictory “exactly two sections” wording.
3. Preserve the evidence statuses `EXTRACTED`, `GRAPH ONLY`, `DERIVED`, and `NOT SPECIFIED`. Remove unsupported typical-value defaults and assumptions presented as device facts, and prohibit using absolute-maximum stress ratings as functional operating/model targets. Keep absent values unknown; a user-authorized model assumption must be identified separately from datasheet evidence. A single threshold does not establish hysteresis symmetry.
4. Review the op-amp output-resistance estimation formula and applicability during consolidation; retain it only if technically justified and dimensionally valid, otherwise require source evidence or leave the value unspecified.
5. Rename `agents/spice-model-extractor.md` to `agents/requirement-definition.md`, update its frontmatter identity/name and description to `requirement-definition`, and add `mode: subagent`. Have it load only `requirement-definition`, reference the project skill location accurately, and return missing-input or ambiguity blockers to its parent. Preserve required tool access and both report deliverables. Remove references to deleted skill/agent names.
6. Add `.mplab-ai/command/requirement-definition.md` using the project's command format. Keep it as a thin entry point that passes the user's request and datasheet context to the `requirement-definition` subagent; do not duplicate extraction rules in the command.
7. Delete the old `skills/spice-extract/`, `skills/opamp-spice-extractor/`, and `skills/voltage-supervisor-spice-extractor/` paths after the unified skill is in place. Leave chart extraction, technique selection, and their agents unchanged except for any concrete broken cross-reference discovered during implementation.

## Validation

- Verify each in-scope agent except `ruthless-orchestrator` declares `mode: subagent`; leave `agents/ruthless-orchestrator.md` entirely untouched.
- Check the renamed agent and skill identity/frontmatter, required tools, reports, parent-directed blockers, and command routing are consistent.
- Search project files for stale `spice-model-extractor`, `spice-extract`, `opamp-spice-extractor`, `voltage-supervisor-spice-extractor`, and `/spice-extract` references, excluding unrelated product-family names where context warrants.
- Validate `.mplab-ai/command/requirement-definition.md` against the project command-file conventions and confirm it delegates to the agent without copying its workflow.
- Check the unified skill has valid frontmatter, covers both component families and conditional features, has no contradictory output contract, and preserves the source/status rules.
- Check representative cases: a single threshold with hysteresis unspecified, a value stated only as an absolute maximum, an ambiguous component family, a missing/inaccessible datasheet, and optional MR/watchdog features absent. Unknowns remain unknown, irrelevant stages are omitted, and a subagent returns blockers to its parent.
- Confirm all three old skill directories and the old agent path are absent, the new command/agent/skill are present, and chart-data extraction / technique-selection workflows are unchanged.

## Risks and Boundaries

- The unified worker must use the repository's `mode: subagent` convention while preserving its needed tools; the command is only an entry point and does not become another agent.
- A missing datasheet value may still be used as a user-authorized modeling assumption, but it must not be represented as manufacturer evidence or used to claim verified device behavior.
- The unified skill performs parameter extraction and report generation only; it does not generate or validate a SPICE model or run simulations.
