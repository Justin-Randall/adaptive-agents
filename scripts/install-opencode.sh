#!/usr/bin/env bash
set -euo pipefail

# install-opencode.sh
#
# Installs Adaptive Agents user-wide guidance for OpenCode-compatible editors.
#
# This script:
#   - detects the Adaptive Agents repository root
#   - creates or updates the OpenCode global configuration with instructions
#     pointing to Adaptive Agents files
#   - installs a global AGENTS.md so OpenCode always knows about Adaptive Agents
#   - installs custom slash commands to OpenCode's global commands directory
#   - creates a timestamped backup before modifying any config file
#
# It does not:
#   - modify VS Code settings or any other editor configuration
#   - modify project repositories
#   - copy Adaptive Agents files into other repositories
#   - store secrets
#   - require the repository to live at a fixed path

usage() {
  cat <<EOF
Usage:
  ./scripts/install-opencode.sh [options]

Options:
  --dry-run              Show what would change without writing files.
  --opencode-config PATH Use an explicit OpenCode config file path.
  --skip-commands        Skip installing custom slash commands.
  -h, --help             Show this help.

Examples:
  ./scripts/install-opencode.sh
  ./scripts/install-opencode.sh --dry-run
  ./scripts/install-opencode.sh --opencode-config ~/custom-opencode.json
  ./scripts/install-opencode.sh --skip-commands
EOF
}

DRY_RUN=0
EXPLICIT_CONFIG_PATH=""
SKIP_COMMANDS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --opencode-config)
      EXPLICIT_CONFIG_PATH="${2:-}"
      if [[ -z "$EXPLICIT_CONFIG_PATH" ]]; then
        echo "ERROR: --opencode-config requires a path." >&2
        exit 1
      fi
      shift 2
      ;;
    --skip-commands)
      SKIP_COMMANDS=1
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

to_unix_path() {
  local p="$1"
  if command_exists cygpath; then
    cygpath -u "$p" 2>/dev/null || printf '%s\n' "$p"
  else
    printf '%s\n' "$p"
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

find_python() {
  if python3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
    return 0
  fi

  if python --version >/dev/null 2>&1; then
    PYTHON_CMD=(python)
    return 0
  fi

  if py -3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
    return 0
  fi

  return 1
}

# ---------------------------------------------------------------------------
# Detect OpenCode config paths
# ---------------------------------------------------------------------------

detect_opencode_config_path() {
  if [[ -n "$EXPLICIT_CONFIG_PATH" ]]; then
    to_unix_path "$EXPLICIT_CONFIG_PATH"
    return
  fi

  local opencode_config_env
  opencode_config_env="${OPENCODE_CONFIG:-}"
  if [[ -n "$opencode_config_env" ]]; then
    to_unix_path "$opencode_config_env"
    return
  fi

  local uname_s
  uname_s="$(uname -s 2>/dev/null || echo unknown)"
  local config_dir

  case "$uname_s" in
    Darwin*)
      config_dir="$HOME/Library/Application Support/opencode"
      ;;
    *)
      # Standard OpenCode global config path: ~/.config/opencode/
      # Works on Linux, Windows (Git Bash, WSL), and other Unix-like systems.
      config_dir="$HOME/.config/opencode"
      ;;
  esac

  # OpenCode supports both .json and .jsonc. Prefer existing file if found.
  if [[ -f "$config_dir/opencode.jsonc" ]]; then
    printf '%s\n' "$config_dir/opencode.jsonc"
  elif [[ -f "$config_dir/opencode.json" ]]; then
    printf '%s\n' "$config_dir/opencode.json"
  else
    # Neither exists yet — default to .json
    printf '%s\n' "$config_dir/opencode.json"
  fi
}

detect_opencode_commands_dir() {
  local config_path="$1"
  # Commands directory typically lives alongside the config or under the config dir root
  local config_dir
  config_dir="$(dirname "$config_path")"
  printf '%s\n' "$config_dir/commands"
}

detect_opencode_agents_path() {
  local config_path="$1"
  local config_dir
  config_dir="$(dirname "$config_path")"
  printf '%s\n' "$config_dir/AGENTS.md"
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

  local config_path
  config_path="$(detect_opencode_config_path)"
  local config_dir
  config_dir="$(dirname "$config_path")"
  local commands_dir
  commands_dir="$(detect_opencode_commands_dir "$config_path")"
  local agents_path
  agents_path="$(detect_opencode_agents_path "$config_path")"

  echo "Adaptive Agents repository: $repo_root"
  echo "OpenCode config:            $config_path"
  echo "OpenCode commands:          $commands_dir"

  if command_exists opencode; then
    echo "OpenCode CLI:               $(command -v opencode)"
  else
    echo "OpenCode CLI:               not detected (install from https://opencode.ai)"
  fi
  echo

  # -----------------------------------------------------------------------
  # Step 1: Create or update OpenCode global config
  # -----------------------------------------------------------------------
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] Would create/update: $config_path"
    echo "[dry-run] Would set instructions array with paths under: $repo_root"
  else
    mkdir -p "$config_dir"

    local backup_path=""
    if [[ -f "$config_path" ]]; then
      backup_path="${config_path}.adaptive-agents.$(date +%Y%m%d-%H%M%S).bak"
      cp "$config_path" "$backup_path"
      echo "Backup written: $backup_path"
    fi

    if ! find_python; then
      echo "ERROR: Python is required to safely update OpenCode config." >&2
      echo "Install Python, or set OPENCODE_CONFIG and update the file manually." >&2
      echo "Expected instructions entry:" >&2
      echo "  \"$repo_root/AGENTS.md\"" >&2
      exit 1
    fi

    "${PYTHON_CMD[@]}" - "$config_path" "$repo_root" <<'PY'
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
repo_root = sys.argv[2]


def normalize_path(p: str) -> str:
    """Convert to forward-slash form for portability."""
    return p.replace("\\", "/")


def strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments while preserving string literals."""
    result = []
    i = 0
    n = len(text)
    in_string = False
    escape = False
    in_line_comment = False
    in_block_comment = False

    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if in_line_comment:
            if c in "\r\n":
                in_line_comment = False
                result.append(c)
            i += 1
            continue

        if in_block_comment:
            if c == "*" and nxt == "/":
                in_block_comment = False
                i += 2
            else:
                if c in "\r\n":
                    result.append(c)
                i += 1
            continue

        if in_string:
            result.append(c)
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_string = False
            i += 1
            continue

        if c == '"':
            in_string = True
            result.append(c)
            i += 1
            continue

        if c == "/" and nxt == "/":
            in_line_comment = True
            i += 2
            continue

        if c == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            continue

        result.append(c)
        i += 1

    return "".join(result)


def remove_trailing_commas(text: str) -> str:
    """Remove trailing commas before ] or } while preserving string literals."""
    result = []
    i = 0
    n = len(text)
    in_string = False
    escape = False
    while i < n:
        c = text[i]
        if in_string:
            result.append(c)
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            result.append(c)
            i += 1
            continue
        if c == ",":
            j = i + 1
            while j < n and text[j].isspace():
                j += 1
            if j < n and text[j] in "}]":
                i += 1
                continue
        result.append(c)
        i += 1
    return "".join(result)


def clean_jsonc(text: str) -> str:
    """Strip comments and trailing commas for safe JSON parsing."""
    return remove_trailing_commas(strip_jsonc(text))


norm_root = normalize_path(repo_root)
expected_instructions = [
    f"{norm_root}/AGENTS.md",
    f"{norm_root}/INDEX.md",
    f"{norm_root}/instructions/global.instructions.md",
    f"{norm_root}/instructions/*.instructions.md",
]

if config_path.exists():
    raw = config_path.read_text(encoding="utf-8").strip()
    if raw:
        try:
            config = json.loads(clean_jsonc(raw))
        except json.JSONDecodeError:
            config = {}
    else:
        config = {}
else:
    config = {}

if not isinstance(config, dict):
    config = {}

# Merge instructions array
existing = config.get("instructions", [])
if not isinstance(existing, list):
    existing = [existing]

for entry in expected_instructions:
    if entry not in existing:
        existing.append(entry)

config["instructions"] = existing

# Sentinel marker
# Write a separate marker file so OpenCode's schema validation never sees it
marker_path = config_path.with_name(".adaptive-agents-installed")
marker_path.write_text(f"adaptive-agents-installed {norm_root}\n", encoding="utf-8")

config_path.write_text(
    json.dumps(config, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
PY
    echo "OpenCode config updated: $config_path"
  fi
  echo

  # -----------------------------------------------------------------------
  # Step 2: Install custom slash commands
  # -----------------------------------------------------------------------
  if [[ "$SKIP_COMMANDS" -eq 1 ]]; then
    echo "Skipping command installation (--skip-commands)."
  else
    local src_commands_dir="$repo_root/opencode/commands"
    if [[ -d "$src_commands_dir" ]]; then
      if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] Would copy $src_commands_dir/*.md → $commands_dir/"
      else
        mkdir -p "$commands_dir"
        local cmd_file
        for cmd_file in "$src_commands_dir"/*.md; do
          if [[ -f "$cmd_file" ]]; then
            cp "$cmd_file" "$commands_dir/"
            echo "Installed command: $(basename "$cmd_file")"
          fi
        done
      fi
    else
      echo "WARNING: Source commands directory not found: $src_commands_dir" >&2
    fi
  fi
  echo

  # -----------------------------------------------------------------------
  # Step 3: Install global AGENTS.md
  # -----------------------------------------------------------------------
  local src_agents="$repo_root/opencode/AGENTS.md"
  if [[ -f "$src_agents" ]]; then
    if [[ "$DRY_RUN" -eq 1 ]]; then
      echo "[dry-run] Would install global rules: $src_agents → $agents_path"
    else
      mkdir -p "$(dirname "$agents_path")"
      # Substitute REPO_ROOT placeholder with actual path
      sed "s|<REPO_ROOT>|$repo_root|g" "$src_agents" > "$agents_path"
      echo "Global rules installed: $agents_path"
    fi
  else
    echo "WARNING: Source AGENTS.md not found: $src_agents" >&2
  fi
  echo

  # -----------------------------------------------------------------------
  # Summary
  # -----------------------------------------------------------------------
  if command_exists opencode; then
    echo "OpenCode is installed. Start a session and ask:"
    echo "  \"Are Adaptive Agents active?\""
    echo "You should see: ADAPTIVE_AGENTS_GLOBAL_LOADED"
  else
    echo "OpenCode CLI is not detected. Install it from https://opencode.ai"
    echo "After installation, run this script again or start opencode in any project."
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo
    echo "[dry-run] No files were modified."
  fi
}

main
