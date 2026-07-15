#!/usr/bin/env bash
set -euo pipefail

# install-antigravity.sh
#
# Installs Adaptive Agents user-wide guidance for Google Antigravity 2.0.
#
# Architecture (two parts, user scope — see .adaptive-agents/planning):
#   1. Single entry point: one `@` import line in the global
#      ~/.gemini/GEMINI.md loading the canonical repository AGENTS.md
#      content at session start. AGENTS.md -> INDEX.md -> instructions/
#      fan-out handles routing. The global context file is loaded
#      automatically in every Antigravity 2.0 session (shares the
#      Gemini CLI global context system).
#   2. Project-based access grant: The user creates an Antigravity
#      Project that includes the Adaptive Agents repo folder, and/or
#      adjusts the Project security preset in Settings for cross-project
#      read/write access. This step is UI-based and cannot be scripted.
#
# Official documentation (verified 2026-07-12):
#   https://antigravity.google/docs/getting-started     — Projects, security presets
#   https://antigravity.google/docs/features            — Scoped permissions
#   https://antigravity.google/docs/cli/best-practices  — Workspace GEMINI.md/AGENTS.md
#   https://antigravity.google/docs/plugins             — Global plugin directory
#
# Prerequisites:
#   - Google Antigravity 2.0 must be installed.
#
# It does not:
#   - copy or generate guidance content (the repository is the source of truth)
#   - modify provider, model, or unrelated settings
#   - modify other repositories
#   - store secrets

usage() {
  cat <<EOF
Usage:
  ./scripts/install-antigravity.sh [options]

Options:
  --dry-run              Show what would change without writing files.
  -h, --help             Show this help.

Examples:
  ./scripts/install-antigravity.sh
  ./scripts/install-antigravity.sh --dry-run
EOF
}

DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

detect_repo_root() {
  if command_exists git && git rev-parse --show-toplevel >/dev/null 2>&1; then
    git rev-parse --show-toplevel
    return
  fi

  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "$script_dir/.." && pwd
}

# Detect the Antigravity 2.0 desktop app on common platforms.
detect_antigravity_app() {
  # Windows
  if [[ -n "${LOCALAPPDATA:-}" ]] && [[ -f "$LOCALAPPDATA/Programs/Antigravity/Antigravity.exe" ]]; then
    printf '%s\n' "$LOCALAPPDATA/Programs/Antigravity/Antigravity.exe"
    return 0
  fi
  if [[ -n "${PROGRAMFILES:-}" ]] && [[ -f "$PROGRAMFILES/Antigravity/Antigravity.exe" ]]; then
    printf '%s\n' "$PROGRAMFILES/Antigravity/Antigravity.exe"
    return 0
  fi
  if [[ -n "${PROGRAMFILES_X86:-}" ]] && [[ -f "$PROGRAMFILES_X86/Antigravity/Antigravity.exe" ]]; then
    printf '%s\n' "$PROGRAMFILES_X86/Antigravity/Antigravity.exe"
    return 0
  fi

  # macOS
  if [[ -d "/Applications/Antigravity.app" ]]; then
    printf '%s\n' "/Applications/Antigravity.app"
    return 0
  fi

  # Linux — check common paths
  if [[ -f "/opt/antigravity/antigravity" ]]; then
    printf '%s\n' "/opt/antigravity/antigravity"
    return 0
  fi
  if command_exists antigravity; then
    command -v antigravity
    return 0
  fi

  return 1
}

# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

main() {
  local repo_root
  repo_root="$(detect_repo_root)"

  if [[ ! -f "$repo_root/AGENTS.md" || ! -f "$repo_root/INDEX.md" ]]; then
    echo "ERROR: This does not look like the Adaptive Agents repository root." >&2
    echo "Expected to find AGENTS.md and INDEX.md in: $repo_root" >&2
    exit 1
  fi

  # -----------------------------------------------------------------------
  # Prerequisite: Antigravity 2.0 desktop app must be installed
  # -----------------------------------------------------------------------
  local antigravity_path
  if antigravity_path="$(detect_antigravity_app)"; then
    echo "Google Antigravity 2.0 detected: $antigravity_path"
  else
    cat >&2 <<EOF
ERROR: Google Antigravity 2.0 is not installed.

The installer requires the Antigravity 2.0 desktop app. There is nothing
to integrate with if the app is not present.

Install Google Antigravity 2.0:
  https://antigravity.google/download

After installation, run this script again.
EOF
    exit 1
  fi

  local gemini_dir="$HOME/.gemini"
  local context_file="$gemini_dir/GEMINI.md"

  echo "Adaptive Agents repository: $repo_root"
  echo

  # -----------------------------------------------------------------------
  # Part A: Native entry point — ~/.gemini/GEMINI.md
  #
  # The Antigravity 2.0 desktop app shares the Gemini CLI global context
  # system. The global context file at ~/.gemini/GEMINI.md is consulted by
  # the agent on startup.  We write an @ import referencing the canonical
  # AGENTS.md so that AGENTS.md -> INDEX.md -> instructions/ fan-out
  # handles all routing.
  # -----------------------------------------------------------------------
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] Would create/update: $context_file"
  else
    mkdir -p "$gemini_dir"

    local section_content

    section_content=$(cat <<EOF
#==ADAPTIVE_AGENTS_START==

@$repo_root/AGENTS.md

#==ADAPTIVE_AGENTS_END==
EOF
)

    if [[ -f "$context_file" ]]; then
      if grep -q "^#==ADAPTIVE_AGENTS_START==" "$context_file" 2>/dev/null &&
         grep -q "^#==ADAPTIVE_AGENTS_END==" "$context_file" 2>/dev/null; then
        # Both markers present — replace content between them.
        local start_line end_line
        start_line=$(grep -n "^#==ADAPTIVE_AGENTS_START==" "$context_file" | head -1 | cut -d: -f1)
        end_line=$(grep -n "^#==ADAPTIVE_AGENTS_END==" "$context_file" | head -1 | cut -d: -f1)
        {
          [[ "$start_line" -gt 1 ]] && head -n "$((start_line - 1))" "$context_file"
          echo "$section_content"
          tail -n +"$((end_line + 1))" "$context_file"
        } > "$context_file.tmp"
        mv "$context_file.tmp" "$context_file"
        echo "Updated existing section in: $context_file"
      else
        # No markers — append section
        echo "" >> "$context_file"
        echo "$section_content" >> "$context_file"
        echo "Appended section to: $context_file"
      fi
    else
      echo "$section_content" > "$context_file"
      echo "Created: $context_file"
    fi
  fi
  echo

  # -----------------------------------------------------------------------
  # Part B: One-time permission dialog
  #
  # Antigravity 2.0 stores file-access permission grants in its own
  # internal binary storage that the installer cannot write to directly.
  # The first time you ask the agent about this repository, a dialog
  # will appear.  Select "Yes, and always allow" — the grant persists
  # permanently and you will never see the dialog again.
  #
  # See: https://antigravity.google/docs/permissions
  # -----------------------------------------------------------------------
  echo
  echo "=== Part B: First-run permission dialog ==="
  echo
  echo "The first time you ask the agent about this repository,"
  echo "you will see a permission dialog like this:"
  echo
  echo "  \"Allow read access to this path?\""
  echo "  $repo_root/AGENTS.md"
  echo
  echo "Select: \"Yes, and always allow\""
  echo
  echo "The grant persists permanently — you will never see it again."
  echo

  # -----------------------------------------------------------------------
  # Summary
  # -----------------------------------------------------------------------
  echo
  echo "Installation complete!"
  echo
  echo "Verification (fresh Antigravity 2.0 conversation in an unrelated Project):"
  echo "  1. Sentinel:      \"Are Adaptive Agents active?\" -> ADAPTIVE_AGENTS_GLOBAL_LOADED"
  echo "  2. Content proof: \"What is the current active plan?\""
  echo "                    -> must name the actual plan from the repository"
  echo "  3. Write-back:    ask for a retrospective capture -> file appears in"
  echo "                    $repo_root/retrospectives/inbox/"
  echo "The sentinel alone is not proof; repeat across multiple fresh sessions."
  echo "Intermittent loading is a failure, not a pass."
}

main
