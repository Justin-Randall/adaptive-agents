---
name: bootstrap-project-layer
description: "Use when: bootstrapping an Adaptive Agents Project Layer in the current project or directory, adding project-specific agent guidance, or initializing indexed active and backlog planning."
---

# Bootstrap Project Layer

Use this skill only when Adaptive Agents is already installed and the user asks to create a project-specific Project Layer.

## Boundaries

- Create only `.adaptive-agents/` plus the explicitly approved Git exclusion entry.
- Do not create or merge root `AGENTS.md`, editor settings, or other project integration files.
- Treat an existing Project Layer as project-owned authored content. Never replace it from the canonical template.
- Preview all planned files and exclusion changes before invoking the setup script.

## Interview

1. Identify the target project root or directory and inspect existing project instructions, planning documents, and Git state.
2. Explain that installed user-wide Adaptive Agents guidance discovers `.adaptive-agents/INDEX.md` automatically.
3. Propose a project name, project-specific instructions, and any clearly warranted project-specific skills supported by inspected project evidence. Ask the user to approve or adjust them; do not copy existing authoritative guidance merely to centralize it.
4. Ask for the initial active work. It may be backlog-derived or direct exploratory, debugging, maintenance, or implementation work. Propose a `PL-YYYYMMDD` ID (or legacy `PL-YYYYMMDDTHHMMSSZ`, `PL-####`), title, objective, scope, and acceptance criteria.
5. Ask the user to choose one persistence mode:
   - `tracked`: available to commit and share with the repository;
   - `local-exclude`: add `/.adaptive-agents/` to `.git/info/exclude` for this clone only;
   - `gitignore`: add `/.adaptive-agents/` to the repository's `.gitignore`.
6. Show the exact bootstrap command and a concise change preview. Wait for explicit approval.

## Apply

After approval, run:

```bash
bash scripts/bootstrap-project-layer.sh \
  --target "<project-root>" \
  --project-name "<project-name>" \
  --active-plan-id "PL-$(date -u +%Y%m%d)" \
  --active-title "<active-plan-title>" \
  --persistence "<tracked|local-exclude|gitignore>"
```

Then edit only the newly generated Project Layer fields the user approved, preserving the template's routing and link invariants. Run the generated validator after those edits.

## Existing Layer

If `.adaptive-agents/` already exists:

1. Run its validator.
2. Report its template version and current active plan.
3. Do not run bootstrap as an upgrade mechanism.
4. Route structural template updates through the Project Layer upgrade workflow when available.