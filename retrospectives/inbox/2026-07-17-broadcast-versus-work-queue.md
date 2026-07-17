# Retrospective: Broadcast versus work queue semantics

- Date: 2026-07-17
- Status: Captured
- Scope: User-wide
- Session or task: Diagnosing unreliable live updates in a multi-client event stream

## Observation

When several clients must receive the same event, a shared destructive queue models competing workers rather than broadcast subscribers. Debugging focused too long on producer timing, debounce behavior, and transport mechanics even after evidence showed that events were produced correctly and multiple consumers were active.

## Evidence

Native file notifications fired, paths normalized correctly, debounce completed, and events entered the shared queue. The stream endpoint also accepted multiple simultaneous connections, but each queued event could be removed by only one connection. A minimal two-consumer check demonstrated that one publication reached exactly one consumer. Replacing the shared queue with one queue per subscriber made one event reach every connected client, and a two-client browser test verified that both rendered views updated after one file change.

## Impact

Confusing work distribution with event broadcast creates nondeterministic behavior that can appear to be a timing, filesystem, or network defect. Future diagnosis should compare the concurrency primitive's delivery semantics with the system contract before tuning timing or adding polling. Multi-subscriber behavior should be verified with at least two concurrent consumers, because a single-client test cannot distinguish work-queue delivery from broadcast.

## Scope Decision

- Candidate: User-wide
- Rationale: The distinction between competing-consumer queues and broadcast delivery applies across unrelated event-driven systems, including server-sent events, WebSockets, notifications, and in-process pub/sub.
- Project Layer considered: The immediate symptom occurred in one project, but the diagnostic lesson and concurrency-model distinction are technology- and project-independent.

## Proposed User-Wide Target

- `instructions/`
- `playbooks/`

## Promotion Decision

- Status: Captured
- Decision: Await triage before proposing durable guidance.
- Rationale: The observation is evidence-backed and reusable, but capture does not establish whether it belongs in default diagnostic instructions or a focused event-delivery playbook.

## Promotion Links

- None yet.

---

*After triage, move this note to `promoted/`, `deferred/`, or `rejected/` and update its status and promotion links.*
