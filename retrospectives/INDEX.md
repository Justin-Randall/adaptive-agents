# Retrospectives

Routing index for the retrospectives system. Each sibling directory holds notes of a single status.

| Directory | Status | Count | Purpose |
| --- | --- | --- | --- |
| [inbox/](inbox/) | Captured | 12 | Notes awaiting initial triage |
| [promoted/](promoted/) | Promoted | 13 | Lessons applied to durable guidance |
| [deferred/](deferred/) | Deferred | 1 | Triaged, set aside for re-evaluation |
| [rejected/](rejected/) | Rejected | 0 | Considered and declined |
| [resolved/](resolved/) | Resolved | 1 | Problem addressed and verified without broader promotion |

## Workflow

1. Capture a note in [inbox/](inbox/) using [inbox/template.md](inbox/template.md).
2. Use [adaptation-cycle.md](../playbooks/adaptation-cycle.md) to decide whether to promote.
3. After triage or verification, move the note to the matching sibling directory and update its status.
4. A verified implementation may move a note to [resolved/](resolved/) with resolution evidence. Use [promoted/](promoted/) when durable guidance was also adopted.
5. See [promoted/INDEX.md](promoted/INDEX.md), [deferred/INDEX.md](deferred/INDEX.md), [rejected/INDEX.md](rejected/INDEX.md), and [resolved/INDEX.md](resolved/INDEX.md) for directory indexes.
6. The [checker](../scripts/check-adaptive-agents.sh) validates the status-directory invariant.
