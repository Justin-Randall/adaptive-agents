# Retrospectives

Routing index for the retrospectives system. Each sibling directory holds notes of a single status.

| Directory | Status | Count | Purpose |
| --- | --- | --- | --- |
| [inbox/](inbox/) | Captured | 10 | Notes awaiting initial triage |
| [promoted/](promoted/) | Promoted | 13 | Lessons applied to durable guidance |
| [deferred/](deferred/) | Deferred | 1 | Triaged, set aside for re-evaluation |
| [rejected/](rejected/) | Rejected | 0 | Considered and declined |

## Workflow

1. Capture a note in [inbox/](inbox/) using [inbox/template.md](inbox/template.md).
2. Use [adaptation-cycle.md](../playbooks/adaptation-cycle.md) to decide whether to promote.
3. After triage, move the note to the matching sibling directory and update its status.
4. See [promoted/INDEX.md](promoted/INDEX.md), [deferred/INDEX.md](deferred/INDEX.md), [rejected/INDEX.md](rejected/INDEX.md) for directory indexes.
5. The [checker](../scripts/check-adaptive-agents.sh) validates the status-directory invariant.
