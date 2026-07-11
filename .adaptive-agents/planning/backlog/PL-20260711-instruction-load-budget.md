# PL-20260711: Instruction Load Budget

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Implement a deterministic inventory and CI gate for the repository files an agent must read when following the canonical `AGENTS.md` route. Report their source size and rough token cost, warn at 80% utilization, and reject required-read profiles above the 65,536 estimated-token high-water mark.

## Problem Spec

Adaptive Agents routes models through entrypoints, indexes, global instructions, project instructions, and task-specific guidance, but the mandatory context cost is not measured. Without a reproducible inventory that distinguishes unconditional reads from task-conditional reads, future commit gates could enforce arbitrary limits or miss routing changes that materially increase the model's instruction burden. A deterministic source measurement and stable rough token heuristic are sufficient for detecting instruction bloat; model-specific tokenizer precision is not required.

Markdown links and prose do not encode enough semantics for CI to infer whether a target is mandatory, conditional, or merely informational. `AGENTS.md` and routed instructions remain authoritative, but automation needs a reviewed machine-readable route manifest derived from those documents. The manifest is an auditable measurement model, not a competing instruction source.

## Proposed CI Contract

### Required Deliverables

Use these paths unless activation-time repository evidence requires an explicitly documented change:

| Path | Purpose |
| --- | --- |
| `instruction-load-routes.json` | Human-reviewed route manifest: profiles, required files, reasons, and limits. |
| `instruction-load-baseline.json` | Deterministically generated metrics and normalized SHA-256 hashes. |
| `schemas/instruction-load-routes.schema.json` | JSON Schema for the reviewed manifest. |
| `schemas/instruction-load-baseline.schema.json` | JSON Schema for generated baseline output. |
| `scripts/check-instruction-load-budget.py` | Python 3 standard-library-only CLI implementing report, check, and baseline update modes. |
| `scripts/test-instruction-load-budget.py` | Isolated Python tests using temporary fixture repositories. |
| `.github/workflows/instruction-load-budget.yml` | CI job that runs focused tests and then the non-mutating budget check. |

Also add the script, tests, schemas, manifest, baseline, and workflow to repository health or required-path checks where appropriate. Document the developer commands in `README.md` without presenting branch protection as repository-controlled automation.

Do not add third-party runtime dependencies merely to count text or validate these small JSON documents. If full JSON Schema validation would require a dependency, implement the required structural checks directly in the script and keep the schemas as reviewed contracts.

### Source Of Truth And Route Semantics

Canonical Markdown remains authoritative. The route manifest records the reviewed interpretation needed by automation; it must never contain instruction text or become another agent entrypoint.

During implementation, trace imperative routing language from `AGENTS.md` and classify an edge as required only when the source tells the agent to read, load, follow, or apply the target for that profile. Do not include a file merely because it is linked, listed as available, described as a reference, or reachable from an index.

Use these classifications consistently:

- `always`: required in every session represented by the profile.
- `profile`: required whenever that named profile applies.
- `conditional`: required only when its explicit trigger applies; place it in a separate representative profile.
- `optional`: discoverable or useful but not counted in any required-read total.

Every counted manifest entry must include `path`, `classification`, and a short `reason` naming the authoritative routing source and trigger. Paths are repository-relative POSIX paths, case-sensitive, and may not contain `..`, backslashes, drive prefixes, URI schemes, or glob syntax.

CI cannot prove the meaning of arbitrary prose. Detect route drift honestly by storing normalized SHA-256 hashes for every counted file, including route-owning entrypoints. Any counted-file content change makes the baseline stale and requires an explicit `--update-baseline` diff for review. Reviewers remain responsible for confirming that manifest classifications still match the authoritative wording.

### Route Profiles

Measure named profiles rather than one misleading repository-wide total. At minimum, establish:

- **Startup**: files that every session must load before routing a task.
- **Non-trivial coding**: startup plus default engineering instructions required for code changes.
- **Adaptive Agents planned change**: non-trivial coding plus this repository's mandatory Project Layer instructions and active planning context.
- **Consequential repository change**: the planned-change profile plus the architecture contract required for behavioral, structural, installer, schema, validator, or integration-boundary changes.
- **Canonical guidance update**: the planned-change profile plus the user-wide maintenance skill required when changing canonical guidance.
- **Task-conditional examples**: representative planning, retrospective, and installer workflows, reported separately from the unconditional budget.

Each profile declares ordered repository-relative paths and why each file is required. Shared files count once per profile even when multiple routing edges reach them. Missing files, duplicate paths, path escapes, and unclassified entries fail validation.

Start from this candidate inventory and verify every entry during activation. Do not silently add or remove paths:

| Profile | Candidate required files |
| --- | --- |
| `startup` | `AGENTS.md`, `INDEX.md` |
| `non_trivial_coding` | `startup` plus `instructions/global.instructions.md`, `instructions/repository-boundaries.instructions.md`, `instructions/coding.instructions.md`, `instructions/tdd.instructions.md`, `instructions/command-failure-pivot.instructions.md`, `instructions/temp-artifact-hygiene.instructions.md` |
| `adaptive_agents_planned_change` | `non_trivial_coding` plus `.adaptive-agents/INDEX.md`, `.adaptive-agents/instructions/INDEX.md`, `.adaptive-agents/instructions/project.instructions.md`, `.adaptive-agents/planning/INDEX.md`, `.adaptive-agents/planning/active/ACTIVE.md`, and the exact active work-unit memory linked from `ACTIVE.md` |
| `consequential_repository_change` | `adaptive_agents_planned_change` plus `.adaptive-agents/ARCHITECTURE.md` |
| `canonical_guidance_update` | `adaptive_agents_planned_change` plus `skills/update-adaptive-agents/SKILL.md` |
| `planning_workflow` | `adaptive_agents_planned_change` plus `.adaptive-agents/skills/manage-planning/SKILL.md` |
| `planning_closure` | `planning_workflow` plus `.adaptive-agents/playbooks/end-work.md` |
| `retrospective_workflow` | the applicable base profile plus the specifically routed retrospective skill, prompt, and playbook required by the requested retrospective operation |

Profiles may extend another profile in the manifest, but expansion must reject cycles and deduplicate by normalized path while preserving first-seen order. Store the expanded ordered file list in the baseline so reviewers can see exactly what CI counted.

Deduplication is per profile, not global: each expanded profile contains its own complete deduplicated file list and totals. A shared file therefore appears once in each profile that requires it. The baseline may repeat that file's metrics in multiple expanded profiles; do not create a separate global metric table unless the activated plan explicitly changes this contract.

The active memory path is intentionally explicit in the manifest. When active work changes, update that path and regenerate the baseline in the same reviewed change. Do not implement globbing, parse Markdown to discover it automatically, or “find the first `*.memory.md`”. When `ACTIVE.md` starts with `# No Active Plan`, omit active memory from `adaptive_agents_planned_change`; `ACTIVE.md` itself remains counted. When an active work unit exists, the manifest must name its exact linked memory path, and validation fails if that file is missing.

### Deterministic Metrics

Use a repository-owned Python script so results are identical across supported shells. Read each file as strict UTF-8, replace CRLF and lone CR with LF, and compute every metric from that normalized text. This prevents Git checkout settings from changing results on Windows. For each file and profile, report:

- normalized UTF-8 byte count
- Unicode character count
- deterministic word count using exactly `len(normalized_text.split())` on the complete Markdown source
- SHA-256 of normalized UTF-8 bytes
- estimated tokens using a documented, versioned conversion formula

Calculate a conservative deterministic estimate for each file and deduplicated profile:

```text
word_estimate = ceil(words * 1.5)
character_estimate = ceil(characters / 4)
estimated_tokens = max(word_estimate, character_estimate)
```

Round derived estimates upward and expose both component estimates and the versioned formula in human-readable and machine-readable output. This is deliberately a rough, model-neutral heuristic for detecting repository instruction bloat, not a prediction of any particular model's tokenizer. Revising the formula requires an explicit metric-version and baseline update.

Implement the arithmetic with integer operations so floating-point behavior cannot vary:

```text
word_estimate = (words * 3 + 1) // 2
character_estimate = (characters + 3) // 4
estimated_tokens = max(word_estimate, character_estimate)
```

Profile totals sum each deduplicated file's normalized bytes, characters, words, and both component token estimates, then calculate the profile `estimated_tokens` as the maximum of the two summed component estimates. Do not sum per-file maxima, because that produces a different and unnecessarily inflated result.

### High-Water Mark

Set **65,536 estimated tokens (64 Ki tokens)** as the hard high-water mark for every required-read profile. This limit applies to the deduplicated transitive set of repository files that the canonical route tells a model it **must** read for that profile; it does not count optional references, unrelated guidance, historical artifacts, or the entire repository.

At the initial `1.5` tokens-per-word factor, the word-only equivalent is at most **43,690 words**, but the character estimate may trigger the gate earlier. CI should warn at **52,429 estimated tokens** (80% of the high-water mark) and fail when `estimated_tokens > 65,536`. Exactly `65,536` passes.

The high-water mark is a compaction safeguard, not a target. Crossing it indicates that mandatory guidance or routing needs consolidation before more required context is added. Task-conditional files count only in profiles where their documented trigger makes them mandatory.

### Baseline Artifact

Commit a machine-readable baseline containing:

- schema and metric-algorithm versions
- route profiles and ordered paths
- per-file metrics
- deduplicated profile totals
- the token-estimation formula
- the 65,536-token high-water mark, warning level, and any stricter profile-specific limits or approved growth tolerances

The baseline must not contain timestamps, absolute paths, environment data, or nondeterministically ordered values. A separate Markdown or console report may summarize the same data for reviewers.

Use JSON with two-space indentation, stable object-key ordering, manifest profile order preserved, file order preserved after expansion, and exactly one trailing LF. The baseline is generated output; contributors change it only with `--update-baseline` and review its diff. The manifest is authored configuration and must never be rewritten by the script.

The manifest should have this minimum shape:

```json
{
    "schemaVersion": 1,
    "metricVersion": 1,
    "highWaterEstimatedTokens": 65536,
    "warningEstimatedTokens": 52429,
    "profiles": [
        {
            "name": "startup",
            "extends": [],
            "maxEstimatedTokens": 65536,
            "maxGrowthEstimatedTokens": null,
            "files": [
                {
                    "path": "AGENTS.md",
                    "classification": "always",
                    "reason": "Native user-wide entrypoint."
                }
            ]
        }
    ]
}
```

The generated baseline should repeat the schema and metric versions, limits, formula constants, expanded profiles, per-file normalized metrics and hashes, and profile totals. Do not copy `reason` text into generated metrics unless needed for readable reports.

`maxEstimatedTokens` is optional per profile and defaults to the top-level `highWaterEstimatedTokens`; it may only make the limit stricter. `maxGrowthEstimatedTokens` is optional and defaults to `null`, meaning no independent growth gate. When set, it is the maximum allowed increase from the committed baseline profile total. Store both settings in the authored manifest, never hardcode profile-specific exceptions in Python.

Increment `schemaVersion` when the manifest or baseline JSON structure changes. Increment `metricVersion` when normalization, word counting, hashing, profile aggregation, or token-estimation behavior changes. Either change requires explicit baseline regeneration and a reviewed diff.

### Script Interface

The implementation should provide one cross-platform entrypoint with behavior equivalent to:

```text
python scripts/check-instruction-load-budget.py --check
python scripts/check-instruction-load-budget.py --report
python scripts/check-instruction-load-budget.py --update-baseline
```

- With no mode, print usage to stderr and exit `2`.
- Accept exactly one mode; incompatible or unknown arguments exit `2`.
- `--check` validates configuration, computes current metrics, compares the exact generated baseline with the committed baseline, applies limits, writes nothing, and exits nonzero on failure.
- `--report` validates configuration and prints current profile composition, per-file metrics, totals, utilization, and baseline deltas without modifying files.
- `--update-baseline` validates configuration, refuses to write if a profile exceeds the hard limit, and atomically rewrites only `instruction-load-baseline.json`; CI never invokes it. Write a temporary UTF-8 file in the baseline's directory, flush and close it, then call `os.replace(temp_path, baseline_path)` so replacement works on Windows and POSIX. Delete a leftover temporary file if replacement fails.
- Resolve the repository root from the script location rather than the caller's current directory. Optional test-only path overrides may be exposed through function parameters or explicit CLI arguments, not ambient environment variables.

Exit codes:

- `0`: success, including warning-only utilization.
- `1`: valid invocation but validation, drift, stale baseline, or budget failure.
- `2`: usage error.

Diagnostics must identify the profile, file, metric, baseline value, current value, delta, and applicable limit. The script must distinguish route drift from content growth so reviewers know whether instructions became broader or merely longer.

Print normal reports to stdout and actionable failures to stderr. Never print absolute paths in baseline output. Sort diagnostics by profile order and expanded file order.

### Gate Policy

Initial CI should fail when:

- a manifest path is missing, duplicated, absolute, or escapes the repository
- current routes and the reviewed manifest no longer satisfy the chosen routing contract
- generated baseline content differs from the checked-in baseline
- a profile's deterministic token estimate exceeds 65,536 or a stricter approved profile limit
- a profile exceeds an independently approved growth tolerance even when it remains below the high-water mark
- metric or schema versions change without an explicit baseline update

Any baseline difference fails `--check`, including a changed normalized hash whose aggregate counts happen to remain equal. A manifest change must be followed by an explicit baseline update. Warning-only utilization returns success but emits one stable `WARN:` line per affected profile.

Warn when a profile reaches 52,429 estimated tokens. Establish any stricter profile limits from measured current behavior, then tighten them only after dogfooding shows the profiles model actual required reads. No model-specific tokenizer validation is required for this gate.

## Verification Shape

Use `unittest` and temporary directories from the Python standard library. Tests must not mutate the real manifest, baseline, instructions, Git configuration, or user files.

At minimum, test:

1. documented word and character arithmetic, including zero and odd values
2. LF and CRLF inputs producing identical normalized metrics and hashes
3. profile inheritance preserving order and deduplicating shared files
4. inheritance-cycle rejection
5. duplicate, absolute, backslash, glob, URI, and escaping-path rejection
6. unknown classification and malformed manifest rejection
7. strict UTF-8 failure with an actionable file diagnostic
8. missing counted file failure
9. stale baseline after content growth
10. stale baseline after same-size content or route-source changes via SHA-256
11. `52,428` estimated tokens producing no warning and `52,429` producing a warning
12. exactly `65,536` estimated tokens passing and `65,537` failing
13. deterministic baseline output and exactly one trailing LF
14. `--report` and `--check` writing no files
15. `--update-baseline` atomically changing only the baseline
16. invocation from outside the repository root
17. no-active-plan omission of active memory and active-plan requirement for the exact manifest memory path
18. per-profile deduplication without cross-profile suppression
19. default, stricter, and invalid looser `maxEstimatedTokens` values
20. null and configured `maxGrowthEstimatedTokens` behavior

Generate exact warning and failure boundary fixtures programmatically from repeated normalized text; do not commit enormous static fixture files merely to reach 52,429 or 65,536 estimated tokens.

Run the focused tests and check on both Ubuntu and Windows runners using one maintained Python version supported by the repository. CI wiring calls tests first and `--check` second. Add the budget check to `scripts/check-adaptive-agents.sh` as a read-only health check, but avoid running the focused test suite twice in the same CI job.

Use Python 3.11 for the initial workflow and document Python 3.11 or newer as the supported runtime. The implementation may use only Python 3.11 standard-library APIs unless the activated plan explicitly revises this requirement.

GitHub Actions can provide a required status check for protected branches, but a workflow file cannot configure branch protection by itself. After the workflow lands, document the repository-owner step to mark the budget job as required. Do not add or modify local Git hooks; the gate protects merges, while developers may run `--check` before committing.

The workflow should:

- run on pull requests and pushes to `main`
- grant read-only repository contents permission
- use a fixed maintained Python version
- run `python scripts/test-instruction-load-budget.py` first
- run `python scripts/check-instruction-load-budget.py --check` second
- use jobs with stable IDs `test-ubuntu` and `test-windows` for platform coverage
- add one final job with ID and display name `instruction-load-budget`, `needs: [test-ubuntu, test-windows]`, and `if: always()`
- make the final job fail unless both needed jobs succeeded; this is the single status check branch protection requires

## Implementation Guardrails

- Do not crawl every Markdown link or count every file reachable from an index.
- Do not infer `must` semantics from headings, filenames, or directory membership.
- Do not copy instruction text into JSON.
- Do not use absolute paths, glob expansion, locale-sensitive word parsing, or platform-native line endings in generated output.
- Do not invoke a model API, tokenizer service, package manager, or network request.
- Do not update the baseline during `--check`, tests, repository health checks, or CI.
- Do not make warnings fail the process.
- Do not add a local Git hook or claim the workflow alone enables branch protection.
- Do not alter canonical instruction wording merely to make route parsing easier; the manifest records the reviewed interpretation.
- Do not suppress multiple failures after the first one when the script can safely report all actionable diagnostics in one run.

## Implementation Order

Follow this order to reduce ambiguity and preserve a falsifiable test loop:

1. Activate the plan and verify the candidate route inventory against current imperative wording.
2. Write fixture-based failing tests for normalization, profile expansion, and the 65,536 boundary.
3. Add the two schemas and reviewed route manifest.
4. Implement parsing, structural validation, path safety, normalization, metrics, and profile expansion.
5. Implement deterministic report and baseline serialization.
6. Implement `--check` and `--update-baseline`, including atomic replacement.
7. Generate and review the initial baseline from the verified manifest.
8. Add the focused script tests to CI on Ubuntu and Windows.
9. Add the non-mutating `--check` CI step and repository health integration.
10. Update README commands and document the external branch-protection step.
11. Run focused tests, the budget check, `scripts/check-adaptive-agents.sh`, and `git diff --check`.

## Acceptance Criteria

- [ ] A reviewer can trace every counted file to a documented mandatory routing source and profile trigger.
- [ ] Optional links and unrelated repository Markdown are excluded from required-read totals.
- [ ] Every manifest path exists, remains inside the repository, and decodes as strict UTF-8; active memory is omitted only for `# No Active Plan`.
- [ ] Manifest and baseline structures satisfy their checked-in schemas and equivalent built-in structural validation.
- [ ] Metrics and hashes are identical for equivalent LF and CRLF content.
- [ ] The committed baseline is byte-stable across repeated generation on Windows and Linux.
- [ ] Repeated baseline generation produces byte-identical output, including exactly one trailing LF.
- [ ] `--check` is read-only and rejects stale baselines, invalid routes, unsafe paths, and profiles above 65,536 estimated tokens.
- [ ] Warning utilization starts at 52,429 estimated tokens without failing the check.
- [ ] Exactly 65,536 estimated tokens passes; 65,537 fails.
- [ ] Focused tests exercise all required failure and boundary cases without touching real user configuration.
- [ ] Repository health invokes the budget check and remains read-only.
- [ ] CI runs focused tests before the gate and exposes one status check suitable for branch protection.
- [ ] README documents report, check, baseline-update, and branch-protection setup commands accurately.
- [ ] No model-specific tokenizer or third-party runtime package is required.

## Scope

Trace `AGENTS.md` and its mandatory routing edges for representative work contexts; classify unconditional and conditional reads; define and validate a reviewed route manifest; implement deterministic per-file and profile metrics; commit a reproducible baseline; add focused tests; and wire a non-mutating CI check with reviewer-actionable diagnostics.

Automatically rewriting baselines, model-specific token accounting, and measuring tool-added system prompts outside this repository are out of scope.
