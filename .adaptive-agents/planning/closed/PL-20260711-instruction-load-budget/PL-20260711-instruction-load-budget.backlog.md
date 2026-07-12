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

The active memory path is intentionally explicit in the manifest. When active work changes, update that path and regenerate the baseline in the same reviewed change. Do not implement globbing, parse Markdown to discover it automatically, or "find the first `*.memory.md`". When `ACTIVE.md` starts with `# No Active Plan`, omit active memory from `adaptive_agents_planned_change`; `ACTIVE.md` itself remains counted. When an active work unit exists, the manifest must name its exact linked memory path, and validation fails if that file is missing.

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
```
