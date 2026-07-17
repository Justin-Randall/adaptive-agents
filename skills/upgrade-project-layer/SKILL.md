---
name: upgrade-project-layer
description: "Use when: comparing or upgrading an existing Adaptive Agents Project Layer to a newer canonical template without overwriting project-owned guidance or plans."
---

# Upgrade Project Layer

Project Layers are project-owned copies of a versioned canonical template. Upgrade through review, not replacement.

## Inspect

1. Confirm `.adaptive-agents/project-layer.json` and `.adaptive-agents/INDEX.md` exist.
2. Run the installed Project Layer validator.
3. Run the read-only comparison:

```bash
bash scripts/inspect-project-layer-upgrade.sh --target "<project-root>"
```

4. Read only the reported missing or changed canonical files and the nearby project-owned files needed to understand conflicts.

## Propose

1. Separate structural template improvements from intentional project customization.
2. Preserve active plans, working memory, backlog items, closed packets, project instructions, and project skills unless the user explicitly asks to change them.
3. Propose a focused patch containing exact repository-relative paths.
4. Explain any content that cannot be merged mechanically.
5. When retrospective sibling directories (`promoted/`, `deferred/`, `rejected/`) are missing, run the migration script instead of proposing manual file-by-file patches:

```bash
bash scripts/migrate-project-layer-retrospectives.sh --target "<project-root>"
```

The script is idempotent, preserves all notes, and handles the full conversion including INDEX.md creation.
6. Stop and ask the user to approve, adjust, or deny the patch.

## Apply

After explicit approval:

1. Apply only the approved patch.
2. If the patch includes retrospective directory conversion, run the migration script:

```bash
bash scripts/migrate-project-layer-retrospectives.sh --target "<project-root>"
```
3. Update `.adaptive-agents/project-layer.json` to the canonical template version only when all approved structural changes for that version are present.
4. Run `.adaptive-agents/scripts/check-project-layer.sh`.
5. Report preserved customizations and any intentionally deferred template differences.

Never recopy the canonical template over an existing Project Layer or treat project-only paths as obsolete by default.