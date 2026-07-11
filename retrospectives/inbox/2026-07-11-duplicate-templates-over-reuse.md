# 2026-07-11: Duplicate Templates Instead of Reusing Existing Files

- Status: Captured
- Scope: User-wide
- Captured: 2026-07-11

## Observation

During the Claude Code installer implementation, I created a separate `claude/` directory with template rule files (`claude/rules/global-instructions.md`, `coding-standards.md`, `boundary-rules.md`) and hook scripts. These templates duplicated content already present in `instructions/*.instructions.md` — they were thin wrappers saying "load instructions from X" rather than pointing tools at the existing files directly.

I also embedded the `ADAPTIVE_AGENTS_GLOBAL_LOADED` sentinel inline in tool-specific templates (cursorrules, windsurfrules, GEMINI.md templates) instead of having all tools discover it from the single source in `AGENTS.md`.

## Impact

- Redundant template files that must be maintained and kept in sync with source instruction files
- Wasted time creating, reviewing, and removing the duplicate directory
- Tool-specific configs that hardcode the sentinel instead of delegating to AGENTS.md
- Health checker initially validated the wrong file for the sentinel

## Root Cause

Defaulting to "create new template files" rather than "look at what already exists and point the tool at it." The existing `instructions/` directory and `AGENTS.md` were the canonical sources — the installer's job is to tell each tool where to find those files, not to duplicate their content.

## Recommendation

When building a new tool installer:
1. First look at existing files that already contain the information the tool needs
2. Prefer delegation (tool config → reference existing file) over duplication (copy content into tool-specific template)
3. Config content should be minimal: just enough to locate and load the canonical Adaptive Agents files
4. Sentinels, operating rules, and instructions live in one place — the installer tells tools where that place is

Before creating any new file in the Adaptive Agents repo, ask: does this information already exist somewhere? If yes, the installer should reference it, not duplicate it.

## Evidence

- `claude/` directory created with 6 files, then removed — all content already existed in `instructions/`
- 7 backlog items had the sentinel inline in their installer templates — all had to be corrected to reference AGENTS.md instead
- Health checker initially validated CLAUDE.md for the sentinel instead of AGENTS.md
- The installer now generates rules dynamically from `instructions/*.instructions.md` instead of copying templates
