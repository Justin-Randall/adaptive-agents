# PL-20261105: Improve Total Recall INDEX.md Maintenance

- Work Unit: PL-20261105-total-recall-index-maintenance
- Status: Closed — Completed (2026-11-06)
- Memory: [PL-20261105-total-recall-index-maintenance.memory.md](PL-20261105-total-recall-index-maintenance.memory.md)

## Progress

- [x] Activate focused INDEX.md maintenance work unit.
- [x] Inspect existing maintenance contract and implementation seams.
- [x] Add and verify the smallest effective guidance/test change.
- [x] Add a dedicated post-session maintenance handoff after the long-form treatment falsified the inline checkpoint.
- [x] Run deterministic handoff regression tests and a fresh long-form Copilot treatment.
- [x] Complete review and closure approval.

## Closure review

Implementation review found no outstanding fixes. Focused Total Recall tests passed 10/10, `git diff --check` found no substantive content issue, and the host-mode Project Layer validator passed with 0 failures. Two realistic long-form Copilot treatments produced concise, source-backed topic updates after the dedicated session-end maintenance handoff.

## Objective

Improve the likelihood and quality of model-authored `INDEX.md` topic and evidence updates in Total Recall sessions, without requiring exhaustive event coverage or introducing a separate retrieval engine.

## Problem Spec

Models in Codex and VS Code Copilot often preserve the ledger and answer questions successfully but omit useful semantic topic updates. Existing guidance intentionally makes indexing selective and non-blocking, but the trigger for a worthwhile update is too implicit. A three-turn, decision-rich Copilot treatment still produced no topic, so the inline completion checkpoint is an inadequate trigger by itself. The next fix is a distinct, bounded maintenance handoff at session end.

## Scope

- Inspect the current Total Recall root template, recovery guidance, maintenance contract, and relevant hook/runtime behavior.
- Define a concise, explicit maintenance checkpoint for meaningful subjects, decisions, constraints, and evidence relationships.
- Add focused validation or dogfood probes that distinguish useful semantic updates from routine activity and exhaustive indexing.
- Verify Codex behavior and assess whether the guidance is portable to Copilot without changing Copilot retrieval architecture.

Deferred: new retrieval engines, embeddings, cross-session memory, mandatory all-event coverage, and broad provider-specific redesign.

## Acceptance Criteria

1. The maintenance contract gives models a clear, low-cost trigger for updating an existing topic or adding one useful topic when warranted.
2. The contract explicitly permits no update when no reusable subject or relationship emerged.
3. Tests or bounded dogfood provide falsifiable evidence that meaningful updates improve without restoring exhaustive indexing pressure.
4. Source links remain evidence-backed and the root index remains concise.
5. Project-layer validation and focused checks pass, or any environment limitation is recorded with evidence.
6. The dedicated handoff either causes a valid topic in the long-form treatment or is falsified by a clean negative result; routine activity remains eligible for no update.

## Applicable Guidance

- `AGENTS.md`: preserve evidence, use narrow reversible changes, and follow repository boundaries.
- `planning-conventions.md`: keep the work unit bounded and test-first where implementation changes are made.
- `ARCHITECTURE.md`: keep the ledger authoritative and indexes as navigation.
- `skills/manage-planning/SKILL.md`: maintain active plan, memory, completion review, and validation evidence.

## Test Plan

- Write focused tests or fixtures first for the maintenance-trigger wording and validator behavior; confirm the expected failure before implementation.
- Run the focused checks against sessions containing a meaningful decision, routine activity, and a large event stream; verify useful routing, no routine noise, and no all-event gate.
- Run the project-layer validator and relevant Total Recall tests after the focused checks pass.
- Use the already-open VS Code workspace at `~/.adaptive-agents` as the dogfood source. Through VS Code Copilot Chat, use the computer-use skill to inspect existing session directories and select a bounded session whose ledger contains both meaningful decisions/evidence and routine events.
- Run a fresh Copilot question that requires a distinctive detail from the selected session, observe whether Copilot follows the session root's bounded source-retrieval instructions, and inspect the corresponding `INDEX.md` afterward for a concise topic/evidence update with valid source links.
- Repeat with one genuinely meaningful long-form slice and one routine-only slice. The meaningful conversation should span several turns, refine a subject, accumulate decisions or constraints, and create enough captured ledger material that a concise topic route improves navigation; the routine slice should remain below that threshold. Expect a useful new or revised topic only for the meaningful slice; do not require one topic per event.
- Compare the Copilot answer, source anchors, and index diff. Record whether the update was model-authored, semantically useful, concise, and evidence-backed; repeat on a second session when the first result is ambiguous.
- Record any UI, authentication, session-selection, or provider limitations rather than treating an inconclusive dogfood run as proof of success.
- Falsification rule: if the fresh long-form treatment completes after receiving the dedicated handoff and still leaves `INDEX.md` at its no-topics state, treat the hypothesis as disproved for that provider and record the limitation rather than claiming success.

## DRY Assessment

Not required for the initial documentation/contract slice; the work should modify the existing maintenance contract rather than add a parallel indexing mechanism. Reassess if runtime or validator logic is duplicated across providers.

