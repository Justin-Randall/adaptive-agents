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

Autonomous trigger policy:

- Agents should create or propose sanitized `Captured` retrospectives when concrete session evidence shows a recurring lesson, repeated correction, reusable workaround, preference, guidance drift, successful workflow, or validation/checker failure.
- Autonomous capture stops at `Captured`; triage, promotion, and durable guidance edits remain user-approved.

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
- run [check-adaptive-agents.sh](../scripts/check-adaptive-agents.sh) after applying the approved patch when available
- if the checker fails, return failures to the user for approval, adjustment, or denial instead of auto-fixing
- validate the completed edit slice once
- stop and report when no requested work remains

Dogfood check:

- Use a triage response that proposes a small patch.
- Approve the patch and run [apply-approved-promotion.patch.prompt.md](../prompts/apply-approved-promotion.patch.prompt.md).
- Confirm it applies only the approved files and stops after one validation pass.
- Confirm it runs the checker after applying the approved patch and surfaces any failures as the next user decision point.
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

Candidate artifact:

- `prompts/review-promotion-candidates.prompt.md`

Expected behavior:

- summarize candidate lessons
- suggest likely durable targets
- identify already-covered lessons
- propose next actions for user approval
- avoid patches or file edits
- keep reports sanitized for source-controlled retrospectives

Dogfood check:

- Generate a report from the inbox.
- Confirm [2026-07-09-stale-project-readme.md](../retrospectives/inbox/2026-07-09-stale-project-readme.md) is evaluated as a candidate without editing `README.md` or durable guidance.
- Use it to choose the next manual promotion.

Dogfood result:

- Successful: the promotion-candidates flow identified the stale README retrospective as a useful manual triage target.
- Boundary check: the first approved patch was reverted after discussion, then a revised approved patch promoted the lesson to [coding.instructions.md](../instructions/coding.instructions.md) instead of applying the initial target blindly.
- Follow-up: because the promotion-candidates prompt is now user-facing, [README.md](../README.md) should list it with the other prompt workflows.

### 6.5. Guided Review Session

Combine inbox review, candidate selection, triage recommendation, and optional patch proposal into one prompt that stops at the user decision boundary.

Candidate artifact:

- `prompts/review-retrospective-session.prompt.md`

Expected behavior:

- select one `Captured` or `Deferred` retrospective, unless the user provides a path
- check existing durable guidance before recommending changes
- recommend exactly one decision: `Deferred`, `Rejected`, `Promoted to existing guidance`, or `Promote with proposed patch`
- include a proposed patch only when promotion or retrospective status updates are recommended
- stop by asking the user to approve, adjust, deny, or defer
- do not edit files or apply patches

Dogfood check:

- Run [review-retrospective-session.prompt.md](../prompts/review-retrospective-session.prompt.md) against the current inbox.
- Confirm it selects a concrete candidate and stops before applying changes.
- If the user approves a patch, hand off to [apply-approved-promotion.patch.prompt.md](../prompts/apply-approved-promotion.patch.prompt.md), then confirm the checker runs after application.

Dogfood result:

- Successful boundary: the prompt selected [2026-07-09-submodule-push-order-and-recursion.md](../retrospectives/inbox/2026-07-09-submodule-push-order-and-recursion.md), proposed a patch, and stopped for the user's decision instead of applying changes.
- User decision: the recommendation was deferred, and the retrospective status update was denied because the lesson needs more detailed treatment later.
- Prompt hardening: the prompt now surfaces explicit retrospective rationale that calls for more validation before promotion, avoids treating a deferred user decision as approval to change retrospective status, and uses apply-patch style patch headers for new and existing files.

### 7. Deterministic Repository Checks

Add a read-only script for structural repository health checks.

Candidate artifact:

- `scripts/check-adaptive-agents.sh`

Expected behavior:

- validate required root files and guidance directories
- validate prompt frontmatter and routing from [INDEX.md](../INDEX.md) and [README.md](../README.md)
- validate retrospective status values and promotion links
- flag blocked private/raw link patterns in checked-in retrospectives
- validate local Markdown links resolve
- detect guidance Markdown files that are not reachable from [INDEX.md](../INDEX.md) through local Markdown links

Dogfood result:

- Successful: [check-adaptive-agents.sh](../scripts/check-adaptive-agents.sh) ran against the current repository with `0 failure(s), 0 warning(s)`.
- Repair made during dogfood: the Python heredoc invocation was changed to an argv-array resolver so `python3`, `python`, and `py -3` work without shell parsing errors.
- Output hardening: concise default mode now reports only the final summary, while `--verbose` preserves detailed `PASS` output for debugging.
- Graph hardening: the checker now detects disconnected guidance Markdown nodes that are not reachable from [INDEX.md](../INDEX.md).
- Boundary check: the checker is read-only and made no repository edits during validation.

## Next Step

Dogfood [review-retrospective-session.prompt.md](../prompts/review-retrospective-session.prompt.md) again against a note that explicitly asks for more evidence and confirm it recommends `Deferred` rather than promotion.
