# Project Retrospective Inbox

This inbox stores project-owned observations before they become durable Project Layer guidance.

Project context may be retained when it is appropriate for this layer's source-control policy. Never include secrets, credentials, private client data, or raw sensitive output.

## Workflow

1. Create `YYYY-MM-DD-short-title.md` from [template.md](template.md).
2. Decide scope before selecting a target type.
3. Use `Project Layer` for behavior intended only here.
4. Use `User-wide` when the lesson applies across projects — this flags it for promotion to the Adaptive Agents repository.
5. Use `Undetermined` when evidence is insufficient; keep the note local by default.
6. Set `Status: Captured` until an approved triage decision changes it.
7. Promote only through an explicit proposed patch and user approval.

Do not copy a project retrospective into user-wide Adaptive Agents. Escalation requires a separate sanitized proposal supported by cross-project intent or evidence.

## Captured Notes

- [Fabricated timestamp IDs](2026-07-10-fabricated-timestamp-ids.md) — Promoted: agent fabricated a UTC timestamp instead of running `date -u`. Added as rule 8 to `instructions/global.instructions.md`.
