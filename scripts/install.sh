#!/usr/bin/env bash
set -euo pipefail

# install.sh
#
# Umbrella installer for Adaptive Agents.
# Detects which AI coding tools are installed and runs the appropriate
# sub-installer for each.
#
# Usage:
#   ./scripts/install.sh [options]
#
# Options:
#   --dry-run     Show what would change without writing files.
#   --tool TOOL   Install only for a specific tool (claude, opencode, vscode).
#   -h, --help    Show this help.
#
# Examples:
#   ./scripts/install.sh
#   ./scripts/install.sh --dry-run
#   ./scripts/install.sh --tool claude

usage() {
  cat <<EOF
Usage:
  ./scripts/install.sh [options]

Options:
  --dry-run     Show what would change without writing files.
  --tool TOOL   Install only for a specific tool.
  -h, --help    Show this help.

Supported tools: claude, antigravity, opencode, vscode  ("antigravity" = Antigravity 2.0 desktop app; not the agy CLI)
EOF
}

DRY_RUN=0
TOOL_FILTER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --tool)
      TOOL_FILTER="${2:-}"
      if [[ -z "$TOOL_FILTER" ]]; then
        echo "ERROR: --tool requires a tool name." >&2
        exit 1
      fi
      shift 2
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

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

detect_repo_root() {
  # Derive from this script's own location (scripts/ -> repo root).
  # This works regardless of the current working directory.
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local candidate="$script_dir/.."
  if [[ -f "$candidate/AGENTS.md" && -f "$candidate/INDEX.md" ]]; then
    cd "$candidate" && pwd
    return
  fi
  # Fallback: git rev-parse (works when cwd is inside the repo).
  if command_exists git && git rev-parse --show-toplevel >/dev/null 2>&1; then
    local top
    top="$(git rev-parse --show-toplevel)"
    if [[ -f "$top/AGENTS.md" && -f "$top/INDEX.md" ]]; then
      echo "$top"
      return
    fi
  fi
  echo "ERROR: Could not determine Adaptive Agents repository root." >&2
  exit 1
}

REPO_ROOT="$(detect_repo_root)"

if [[ ! -f "$REPO_ROOT/AGENTS.md" || ! -f "$REPO_ROOT/INDEX.md" ]]; then
  echo "ERROR: This does not look like the Adaptive Agents repository root." >&2
  echo "Expected to find AGENTS.md and INDEX.md in: $REPO_ROOT" >&2
  exit 1
fi

echo "Adaptive Agents installer"
echo "Repository: $REPO_ROOT"
echo

SUB_INSTALLERS=()

# Claude Code
if [[ -z "$TOOL_FILTER" || "$TOOL_FILTER" == "claude" ]]; then
  if command_exists claude || [[ -f "$HOME/.claude/settings.json" ]]; then
    echo "  [detected] Claude Code"
    SUB_INSTALLERS+=("$REPO_ROOT/scripts/install-claude-code.sh")
  fi
fi

# OpenCode
if [[ -z "$TOOL_FILTER" || "$TOOL_FILTER" == "opencode" ]]; then
  if command_exists opencode || [[ -d "$HOME/.config/opencode" ]]; then
    echo "  [detected] OpenCode"
    SUB_INSTALLERS+=("$REPO_ROOT/scripts/install-opencode.sh")
  fi
fi

# Antigravity 2.0 (desktop app)
if [[ -z "$TOOL_FILTER" || "$TOOL_FILTER" == "antigravity" ]]; then
  detected=""
  if [[ -n "${LOCALAPPDATA:-}" ]] && [[ -f "$LOCALAPPDATA/Programs/Antigravity/Antigravity.exe" ]]; then
    detected=1
  elif [[ -n "${PROGRAMFILES:-}" ]] && [[ -f "$PROGRAMFILES/Antigravity/Antigravity.exe" ]]; then
    detected=1
  elif [[ -n "${PROGRAMFILES_X86:-}" ]] && [[ -f "$PROGRAMFILES_X86/Antigravity/Antigravity.exe" ]]; then
    detected=1
  elif [[ -d "/Applications/Antigravity.app" ]]; then
    detected=1
  fi
  if [[ -n "$detected" ]]; then
    echo "  [detected] Antigravity 2.0"
    SUB_INSTALLERS+=("$REPO_ROOT/scripts/install-antigravity.sh")
  fi
fi

# VS Code / GitHub Copilot
if [[ -z "$TOOL_FILTER" || "$TOOL_FILTER" == "vscode" ]]; then
  if command_exists code || [[ -n "${APPDATA:-}" && -d "$APPDATA/Code" ]]; then
    echo "  [detected] VS Code"
    SUB_INSTALLERS+=("$REPO_ROOT/scripts/install-vscode.sh")
  fi
fi

echo

if [[ ${#SUB_INSTALLERS[@]} -eq 0 ]]; then
  echo "No supported AI coding tools detected."
  echo
  echo "Supported tools:"
  echo "  Claude Code     — https://claude.ai/download"
  echo "  Antigravity 2.0 — https://antigravity.google/download"
  echo "  OpenCode        — https://opencode.ai"
  echo "  VS Code         — https://code.visualstudio.com"
  echo
  echo "Install a supported tool and re-run this script."
  exit 0
fi

FAILED_INSTALLERS=()

for installer in "${SUB_INSTALLERS[@]}"; do
  if [[ -f "$installer" ]]; then
    echo "Running: $installer"
    if [[ "$DRY_RUN" -eq 1 ]]; then
      if ! bash "$installer" --dry-run; then
        FAILED_INSTALLERS+=("$(basename "$installer")")
      fi
    else
      if ! bash "$installer"; then
        FAILED_INSTALLERS+=("$(basename "$installer")")
      fi
    fi
    echo
  else
    echo "WARNING: Installer not found: $installer" >&2
    FAILED_INSTALLERS+=("$(basename "$installer")")
  fi
done

if [[ ${#FAILED_INSTALLERS[@]} -gt 0 ]]; then
  echo "Failed integrations:" >&2
  printf '  - %s\n' "${FAILED_INSTALLERS[@]}" >&2
  exit 1
fi

echo "Done."
