#!/usr/bin/env bash
# scripts/session-start/check-upgrade.sh
#
# Checks whether the Adaptive Agents repository has new upstream commits
# that the user has not already declined. If so, emits a --- PROMPT section
# with instructions for the model to ask the user.
#
# Refusal file: ~/.cache/adaptive-agents/refused-upgrade-hash
#   Written by the agent when the user declines. If the remote HEAD hash
#   matches the refusal file, this probe exits silently. When the remote
#   advances to a new commit, the hash changes and the user is re-prompted.
set -euo pipefail

CACHE_DIR="${HOME}/.cache/adaptive-agents"
REFUSAL_FILE="${CACHE_DIR}/refused-upgrade-hash"

# Validate cache directory exists before trying to read the refusal file.
# The agent creates this directory when it writes the hash on user decline.
if [[ ! -d "$CACHE_DIR" ]]; then
  CACHE_VALID=0
else
  CACHE_VALID=1
fi

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

detect_repo_root() {
  # Derive from this script's location: scripts/session-start/ -> repo root
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
  if [[ -f "$script_dir/AGENTS.md" && -f "$script_dir/INDEX.md" ]]; then
    echo "$script_dir"
    return 0
  fi
  return 1
}

main() {
  local repo_root
  repo_root="$(detect_repo_root)" || return 0

  # Fetch remote refs without modifying local state.
  GIT_TERMINAL_PROMPT=0 git -C "$repo_root" fetch origin --prune 2>/dev/null || return 0

  # Determine default branch
  local remote_branch="origin/main"
  if ! git -C "$repo_root" rev-parse --verify "$remote_branch" >/dev/null 2>&1; then
    local default
    default="$(git -C "$repo_root" remote show origin 2>/dev/null | sed -n 's/^  HEAD branch: //p')" || true
    if [[ -n "$default" ]]; then
      remote_branch="origin/$default"
    else
      return 0
    fi
  fi

  # Get remote HEAD hash for refusal comparison
  local remote_hash
  remote_hash="$(git -C "$repo_root" rev-parse --short "$remote_branch" 2>/dev/null)" || return 0

  # Check refusal file (only if cache directory exists)
  if [[ "$CACHE_VALID" -eq 1 && -f "$REFUSAL_FILE" ]]; then
    local refused_hash
    refused_hash="$(cat "$REFUSAL_FILE" 2>/dev/null)" || true
    if [[ "$refused_hash" == "$remote_hash" ]]; then
      return 0
    fi
  fi

  # Count new commits
  local count
  count="$(git -C "$repo_root" rev-list --count "HEAD..$remote_branch" 2>/dev/null)" || return 0

  if [[ "$count" -gt 0 ]]; then
    local changelog
    changelog="$(git -C "$repo_root" log --oneline "HEAD..$remote_branch" 2>/dev/null)" || changelog=""

    cat <<OUTPUT

--- PROMPT
The Adaptive Agents repository has $count new commits. Ask the user if they would like to upgrade now.

--- CHANGELOG
If the user asks what has changed, show these recent commits:
  $(echo "$changelog" | sed 's/^/  /')

--- ON APPROVE
Run these steps ONLY when the user approves:
  1. git -C "$repo_root" pull --ff-only origin main
  2. bash "$repo_root/scripts/install.sh"

OUTPUT
  fi
}

main "$@"
