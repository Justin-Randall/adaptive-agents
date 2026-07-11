#!/usr/bin/env bash
set -euo pipefail

# install-claude-code.sh
#
# Installs Adaptive Agents user-wide guidance for Claude Code.
#
# This script:
#   - detects the Adaptive Agents repository root
#   - creates or updates ~/.claude/CLAUDE.md with a native AGENTS.md import
#   - grants Claude Code access to the Adaptive Agents repository
#
# It does not:
#   - modify project .claude/ configuration
#   - modify provider config, model selection, or unrelated permissions
#   - copy Adaptive Agents files into other repositories
#   - store secrets
#   - require the repository to live at a fixed path

usage() {
  cat <<EOF
Usage:
  ./scripts/install-claude-code.sh [options]

Options:
  --dry-run              Show what would change without writing files.
  -h, --help             Show this help.

Examples:
  ./scripts/install-claude-code.sh
  ./scripts/install-claude-code.sh --dry-run
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

find_python() {
  if command_exists python3 && python3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
  elif command_exists python && python --version >/dev/null 2>&1; then
    PYTHON_CMD=(python)
  elif command_exists py && py -3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
  else
    return 1
  fi
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

  local claude_dir="$HOME/.claude"
  local settings_path="$claude_dir/settings.json"

  echo "Adaptive Agents repository: $repo_root"
  echo "Claude Code config dir:     $claude_dir"

  if command_exists claude; then
    echo "Claude Code CLI:            $(command -v claude)"
  else
    echo "Claude Code CLI:            not detected"
  fi
  echo

  # -----------------------------------------------------------------------
  # Create or update ~/.claude/CLAUDE.md
  # -----------------------------------------------------------------------
  local claude_md_path="$claude_dir/CLAUDE.md"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] Would create/update: $claude_md_path"
  else
    mkdir -p "$claude_dir"

    local section_content

    section_content=$(cat <<EOF
#==ADAPTIVE_AGENTS_START==

@$repo_root/AGENTS.md

#==ADAPTIVE_AGENTS_END==
EOF
)

    if [[ -f "$claude_md_path" ]]; then
      # Use grep -q inside conditionals (exempt from set -e) so we don't
      # silently exit when markers are absent.
      if grep -q "^#==ADAPTIVE_AGENTS_START==" "$claude_md_path" 2>/dev/null &&
         grep -q "^#==ADAPTIVE_AGENTS_END==" "$claude_md_path" 2>/dev/null; then
        # Both markers present — replace content between them.
        local start_line end_line
        start_line=$(grep -n "^#==ADAPTIVE_AGENTS_START==" "$claude_md_path" | head -1 | cut -d: -f1)
        end_line=$(grep -n "^#==ADAPTIVE_AGENTS_END==" "$claude_md_path" | head -1 | cut -d: -f1)
        {
          [[ "$start_line" -gt 1 ]] && head -n "$((start_line - 1))" "$claude_md_path"
          echo "$section_content"
          tail -n +"$((end_line + 1))" "$claude_md_path"
        } > "$claude_md_path.tmp"
        mv "$claude_md_path.tmp" "$claude_md_path"
        echo "Updated existing section in: $claude_md_path"
      else
        # No markers (or only START) — append section
        echo "" >> "$claude_md_path"
        echo "$section_content" >> "$claude_md_path"
        echo "Appended section to: $claude_md_path"
      fi
    else
      echo "$section_content" > "$claude_md_path"
      echo "Created: $claude_md_path"
    fi
  fi
  echo

  # -----------------------------------------------------------------------
  # Grant access to routed Adaptive Agents files outside the working tree
  # -----------------------------------------------------------------------
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] Would ensure permissions.additionalDirectories contains: $repo_root"
  else
    if ! find_python; then
      echo "ERROR: Python is required to safely update settings.json." >&2
      exit 1
    fi

    "${PYTHON_CMD[@]}" - "$settings_path" "$repo_root" <<'PY'
import json
import sys
from pathlib import Path

settings_path = Path(sys.argv[1])
repo_root = sys.argv[2]

if settings_path.exists():
    raw = settings_path.read_text(encoding="utf-8").strip()
    settings = json.loads(raw) if raw else {}
else:
    settings = {}

if not isinstance(settings, dict):
    raise ValueError("settings.json must contain a JSON object")

permissions = settings.setdefault("permissions", {})
if not isinstance(permissions, dict):
    raise ValueError("settings.json permissions must be a JSON object")

additional_directories = permissions.setdefault("additionalDirectories", [])
if not isinstance(additional_directories, list):
    raise ValueError("permissions.additionalDirectories must be a JSON array")

if repo_root not in additional_directories:
    additional_directories.append(repo_root)

updated = json.dumps(settings, indent=2, ensure_ascii=False) + "\n"
current = settings_path.read_text(encoding="utf-8") if settings_path.exists() else ""
if updated != current:
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(updated, encoding="utf-8")
    print(f"Granted repository access in: {settings_path}")
else:
    print(f"Repository access already configured in: {settings_path}")
PY
  fi
  echo

  # -----------------------------------------------------------------------
  # Summary
  # -----------------------------------------------------------------------
  if command_exists claude; then
    echo "Claude Code is installed. Start a session and ask:"
    echo "  \"Are Adaptive Agents active?\""
    echo "You should see: ADAPTIVE_AGENTS_GLOBAL_LOADED"
  else
    echo "Claude Code CLI is not detected. Install it from:"
    echo "  https://claude.ai/download"
    echo "After installation, run this script again."
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo
    echo "[dry-run] No files were modified."
  fi
}

main
