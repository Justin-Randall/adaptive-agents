# Retrospective: Broadcast versus work queue semantics

- Date: 2026-07-17
- Status: Promoted
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

- Status: Promoted
- Decision: Promoted to new playbook
- Rationale: Evidence-backed, reusable diagnostic procedure; the broadcast/work-queue distinction and two-consumer verification map to a focused playbook.

## Promotion Links

- [Event delivery diagnostics](../../playbooks/event-delivery-diagnostics.md)
