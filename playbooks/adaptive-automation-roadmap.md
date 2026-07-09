# Adaptive Automation Roadmap

Use this roadmap to make Adaptive Agents more automated without letting agents silently rewrite durable guidance.

Automation should start with reversible capture and reviewable proposals. Durable guidance changes should remain explicit until the capture and promotion workflow has been dogfooded successfully.

## Principles

- Automate mechanics before judgment.
- Capture first; promote only after triage.
- Prefer proposed patches over silent durable changes.
- Keep generated or local files disposable.
- Distinguish checked-in prompt source files from editor runtime discoverability; each prompt workflow needs an explicit invocation or installation path before it is considered ready.
- Use Markdown links for checked-in guidance references.
- Validate each completed automation slice once, then dogfood it before building the next layer.

## Layers

### 1. Assisted Capture

Create a prompt or skill that turns a session observation into a retrospective note.

Candidate artifacts:

- `prompts/capture-retrospective.prompt.md`
- or `skills/capture-retrospective/SKILL.md`

Expected behavior:

- create `retrospectives/inbox/YYYY-MM-DD-short-title.md`
- use [retrospectives/inbox/template.md](../retrospectives/inbox/template.md)
- set `Status: Captured`
- record observation, evidence, impact, and proposed durable target
- do not promote automatically

Dogfood check:

- Ask the agent to capture one real session lesson.
- Confirm it uses the filename convention.
- Confirm it does not edit durable guidance.
- Confirm the checked-in prompt has a clear VS Code invocation path, generated user-profile prompt, setup-script wiring, or documented manual test path.

### 2. Assisted Triage

Create a workflow that evaluates a captured retrospective and recommends what should happen next.

Candidate artifacts:

- `prompts/triage-retrospective.prompt.md`
- or an expanded [Update Adaptive Agents](../skills/update-adaptive-agents/SKILL.md) skill section

Expected decisions:

- `Deferred`
- `Rejected`
- `Promoted to existing guidance`
- `Promote with proposed patch`

Dogfood check:

- Triage a captured note that is already covered by existing guidance.
- Confirm the workflow links to existing durable guidance instead of duplicating rules.
- Confirm that if the workflow recommends updating the retrospective, it also returns a fenced `diff` patch for that update.
- Confirm it writes `No patch recommended.` only when no file update is recommended.

### 3. Approved Patch Application

Allow the agent to apply focused durable guidance edits after triage proposes a patch and the user explicitly approves it.

Candidate artifact:

- `prompts/apply-approved-promotion.patch.prompt.md`

Expected behavior:

- require explicit approval before editing
- re-read each target file before applying the patch
- apply only the approved patch
- edit the narrowest owning file
- update [INDEX.md](../INDEX.md) when discovery changes
- update the retrospective status and promotion links
- validate the completed edit slice once
- stop and report when no requested work remains

Dogfood check:

- Use a triage response that proposes a small patch.
- Approve the patch and run [apply-approved-promotion.patch.prompt.md](../prompts/apply-approved-promotion.patch.prompt.md).
- Confirm it applies only the approved files and stops after one validation pass.
- Confirm it refuses or asks for clarification when a patch hunk omits an explicit repository-relative `*** Update File:` path.

### 4. End-of-Session Capture Prompt

Add a manually invoked prompt for end-of-session learning capture.

Candidate artifact:

- `prompts/end-of-session-capture.prompt.md`

Expected behavior:

- ask whether there is a reusable lesson
- create a captured retrospective only when there is enough evidence
- avoid durable guidance edits during capture

Dogfood check:

- Run [end-of-session-capture.prompt.md](../prompts/end-of-session-capture.prompt.md) after a real session.
- Confirm it captures only concrete observations.

Dogfood result:

- Successful: an end-of-session review from another workspace created [2026-07-09-submodule-push-order-and-recursion.md](../retrospectives/inbox/2026-07-09-submodule-push-order-and-recursion.md) as a single `Captured` retrospective with concrete evidence and a bounded dogfood check.
- Boundary check: it did not promote the note or edit durable guidance.

### 5. Retrospective Queue Tooling

Add lightweight scripts or prompts to manage the inbox.

Candidate checks:

- list `Captured` notes
- list `Deferred` notes older than a chosen age
- validate `YYYY-MM-DD-short-title.md` filenames
- validate promotion links resolve
- validate statuses use the known set from [adaptation-cycle.md](adaptation-cycle.md)

Candidate artifact:

- `prompts/review-retrospective-inbox.prompt.md`

Dogfood check:

- Run [review-retrospective-inbox.prompt.md](../prompts/review-retrospective-inbox.prompt.md) after several retrospectives exist.
- Confirm it reports actionable status without changing guidance.

Dogfood result:

- Successful: a natural-language request to review the current retrospective inbox inferred the correct prompt behavior without using a slash command, and a less capable flash model still grouped the three notes by status.
- Follow-up hardening: keep report links repository-relative and avoid copied `vscode-file://` or `workbench.html` links.

### 6. Promotion Reports

Generate periodic review reports for captured and deferred notes.

Expected behavior:

- summarize candidate lessons
- suggest likely durable targets
- identify already-covered lessons
- propose next actions for user approval

Dogfood check:

- Generate a report from the inbox.
- Use it to choose the next manual promotion.

## Next Step

Build the promotion report slice, then dogfood it against the current retrospective inbox.
