#!/usr/bin/env bash
set -euo pipefail

# install-vscode.sh
#
# Installs Adaptive Agents user-wide guidance for VS Code Chat / GitHub Copilot.
#
# This script:
#   - detects the Adaptive Agents repository root
#   - creates vscode/user-wide.instructions.md
#   - updates VS Code user settings.json
#   - adds this repository's vscode/ directory to chat.instructionsFilesLocations
#   - grants read access to the repository root via github.copilot.chat.additionalReadAccessPaths
#   - enables applying instruction files
#   - preserves existing settings where possible
#   - creates a timestamped backup before modifying settings.json
#
# It does not:
#   - modify project repositories
#   - copy Adaptive Agents files into other repositories
#   - store secrets
#   - require the repository to live at a fixed path

usage() {
  cat <<EOF
Usage:
  ./scripts/install-vscode.sh [options]

Options:
  --dry-run            Show what would change without writing files.
  --settings PATH      Use an explicit VS Code settings.json path.
  --code-flavor NAME   VS Code flavor: code, insiders, codium. Default: code.
  -h, --help           Show this help.

Examples:
  ./scripts/install-vscode.sh
  ./scripts/install-vscode.sh --dry-run
  ./scripts/install-vscode.sh --code-flavor insiders
  ./scripts/install-vscode.sh --settings "\$APPDATA/Code/User/settings.json"
EOF
}

DRY_RUN=0
EXPLICIT_SETTINGS_PATH=""
CODE_FLAVOR="code"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --settings)
      EXPLICIT_SETTINGS_PATH="${2:-}"
      if [[ -z "$EXPLICIT_SETTINGS_PATH" ]]; then
        echo "ERROR: --settings requires a path." >&2
        exit 1
      fi
      shift 2
      ;;
    --code-flavor)
      CODE_FLAVOR="${2:-}"
      if [[ -z "$CODE_FLAVOR" ]]; then
        echo "ERROR: --code-flavor requires a value." >&2
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

to_unix_path() {
  local p="$1"

  if command_exists cygpath; then
    cygpath -u "$p" 2>/dev/null || printf '%s\n' "$p"
  else
    printf '%s\n' "$p"
  fi
}

to_vscode_setting_path() {
  local p="$1"

  # VS Code settings are safest with forward slashes, even on Windows.
  if command_exists cygpath; then
    cygpath -m "$p" 2>/dev/null || printf '%s\n' "$p"
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

detect_settings_path() {
  if [[ -n "$EXPLICIT_SETTINGS_PATH" ]]; then
    to_unix_path "$EXPLICIT_SETTINGS_PATH"
    return
  fi

  local uname_s
  uname_s="$(uname -s 2>/dev/null || echo unknown)"

  case "$CODE_FLAVOR" in
    code)
      case "$uname_s" in
        MINGW*|MSYS*|CYGWIN*)
          if [[ -n "${APPDATA:-}" ]]; then
            to_unix_path "$APPDATA/Code/User/settings.json"
          else
            echo "ERROR: APPDATA is not set; use --settings PATH." >&2
            exit 1
          fi
          ;;
        Darwin*)
          printf '%s\n' "$HOME/Library/Application Support/Code/User/settings.json"
          ;;
        *)
          printf '%s\n' "$HOME/.config/Code/User/settings.json"
          ;;
      esac
      ;;
    insiders)
      case "$uname_s" in
        MINGW*|MSYS*|CYGWIN*)
          if [[ -n "${APPDATA:-}" ]]; then
            to_unix_path "$APPDATA/Code - Insiders/User/settings.json"
          else
            echo "ERROR: APPDATA is not set; use --settings PATH." >&2
            exit 1
          fi
          ;;
        Darwin*)
          printf '%s\n' "$HOME/Library/Application Support/Code - Insiders/User/settings.json"
          ;;
        *)
          printf '%s\n' "$HOME/.config/Code - Insiders/User/settings.json"
          ;;
      esac
      ;;
    codium)
      case "$uname_s" in
        MINGW*|MSYS*|CYGWIN*)
          if [[ -n "${APPDATA:-}" ]]; then
            to_unix_path "$APPDATA/VSCodium/User/settings.json"
          else
            echo "ERROR: APPDATA is not set; use --settings PATH." >&2
            exit 1
          fi
          ;;
        Darwin*)
          printf '%s\n' "$HOME/Library/Application Support/VSCodium/User/settings.json"
          ;;
        *)
          printf '%s\n' "$HOME/.config/VSCodium/User/settings.json"
          ;;
      esac
      ;;
    *)
      echo "ERROR: Unsupported --code-flavor '$CODE_FLAVOR'. Use code, insiders, or codium." >&2
      exit 1
      ;;
  esac
}

write_user_wide_instructions() {
  local repo_root="$1"
  local out_file="$2"
  local repo_setting_path="$3"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] Would write: $out_file"
    return
  fi

  mkdir -p "$(dirname "$out_file")"

  cat > "$out_file" <<EOF
---
applyTo: "**"
---

# User-Wide Adaptive Agent Bootstrap

The user's canonical Adaptive Agents knowledgebase is located at:

\`$repo_setting_path\`

Apply these referenced Adaptive Agents instructions:

- [Adaptive Agents operating rules]($repo_setting_path/AGENTS.md)
- [Adaptive Agents routing index]($repo_setting_path/INDEX.md)
- [Global user-wide instructions]($repo_setting_path/instructions/global.instructions.md)

Before doing non-trivial coding work:

1. Treat the Adaptive Agents repository as user-wide guidance.
2. Follow the routing in the Adaptive Agents index to load only relevant checked-in instructions, skills, memories, prompts, agents, or playbooks.
3. Also read the Current project repository's own local instructions if they exist.
4. Check for \`.adaptive-agents/INDEX.md\`; when present, read its routed project instructions and active planning context after user-wide guidance.
5. Project-local instructions override Adaptive Agents guidance when they are more specific.
6. Do not create Adaptive Agents directories or files inside the Current project repository unless explicitly instructed or applying the user-approved Project Layer bootstrap workflow.
7. Do not copy \`skills/\`, \`memory/\`, \`retrospectives/\`, \`agents/\`, \`playbooks/\`, or \`schemas/\` into the Current project repository unless explicitly instructed.
8. If a durable user-wide lesson should be captured, propose or write it in the Adaptive Agents repository, not in the Current project repository.
9. If unsure whether a lesson is durable, create or propose a retrospective note rather than modifying permanent instructions.

The generated file is only a local bootstrap. Durable guidance belongs in checked-in Adaptive Agents repository files.
EOF
}

update_vscode_settings() {
  local settings_path="$1"
  local instructions_dir_setting_path="$2"
  local repo_root_path="$3"

  python_candidate_works() {
    local candidate="$1"
    eval "$candidate --version >/dev/null 2>&1"
  }

  local settings_dir
  settings_dir="$(dirname "$settings_path")"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] Would update VS Code settings: $settings_path"
    echo "[dry-run] Would set chat.instructionsFilesLocations['$instructions_dir_setting_path'] = true"
    echo "[dry-run] Would remove obsolete github.copilot.chat.additionalReadAccessFolders"
    echo "[dry-run] Would set github.copilot.chat.additionalReadAccessPaths += ['$repo_root_path']"
    echo "[dry-run] Would set chat.includeApplyingInstructions = true"
    echo "[dry-run] Would set chat.includeReferencedInstructions = true"
    return
  fi

  mkdir -p "$settings_dir"

  if [[ ! -f "$settings_path" ]]; then
    printf '{}\n' > "$settings_path"
  fi

  local backup_path
  backup_path="${settings_path}.adaptive-agents.$(date +%Y%m%d-%H%M%S).bak"
  cp "$settings_path" "$backup_path"

  if command_exists python3 && python_candidate_works "python3"; then
    PYTHON_BIN="python3"
  elif command_exists python && python_candidate_works "python"; then
    PYTHON_BIN="python"
  elif command_exists py && python_candidate_works "py -3"; then
    PYTHON_BIN="py -3"
  else
    echo "ERROR: Python is required to safely update VS Code settings.json." >&2
    echo "Detected Python launchers may be unavailable or misconfigured in this shell." >&2
    echo "A backup was not written because settings were not modified." >&2
    echo "Install Python, or update this setting manually:" >&2
    echo "  chat.instructionsFilesLocations['$instructions_dir_setting_path'] = true" >&2
    exit 1
  fi

  # shellcheck disable=SC2086
  $PYTHON_BIN - "$settings_path" "$instructions_dir_setting_path" "$repo_root_path" <<'PY'
import json
import sys
from pathlib import Path

settings_path = Path(sys.argv[1])
instructions_dir = sys.argv[2]
repo_root = sys.argv[3]


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


raw = settings_path.read_text(encoding="utf-8").strip()

if not raw:
    settings = {}
else:
    try:
        settings = json.loads(remove_trailing_commas(strip_jsonc(raw)))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Could not parse VS Code settings file: {settings_path}", file=sys.stderr)
        print(f"JSON error: {exc}", file=sys.stderr)
        print("No changes were written. Restore from the generated backup if needed.", file=sys.stderr)
        sys.exit(1)

if not isinstance(settings, dict):
    print("ERROR: VS Code settings root must be a JSON object.", file=sys.stderr)
    sys.exit(1)

locations = settings.get("chat.instructionsFilesLocations")
if locations is None:
    locations = {}
elif not isinstance(locations, dict):
    print("ERROR: Existing chat.instructionsFilesLocations is not an object.", file=sys.stderr)
    sys.exit(1)

locations[instructions_dir] = True
settings["chat.instructionsFilesLocations"] = locations

# Required for applyTo-based instruction files to be automatically included.
settings["chat.includeApplyingInstructions"] = True

# Helpful once instructions start linking to other Adaptive Agents files.
settings["chat.includeReferencedInstructions"] = True

# Remove the ineffective key generated by the initial implementation.
settings.pop("github.copilot.chat.additionalReadAccessFolders", None)

# Grant read access to the Adaptive Agents repository from any workspace.
additional_paths = settings.get("github.copilot.chat.additionalReadAccessPaths")
if additional_paths is None:
    additional_paths = []
elif not isinstance(additional_paths, list):
    print("ERROR: Existing github.copilot.chat.additionalReadAccessPaths is not an array.", file=sys.stderr)
    sys.exit(1)

if repo_root not in additional_paths:
    additional_paths.append(repo_root)
settings["github.copilot.chat.additionalReadAccessPaths"] = additional_paths

settings_path.write_text(
    json.dumps(settings, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
PY

  echo "Backup written: $backup_path"
}

main() {
  local repo_root
  repo_root="$(detect_repo_root)"

  if [[ ! -f "$repo_root/AGENTS.md" || ! -f "$repo_root/INDEX.md" ]]; then
    echo "ERROR: This does not look like the Adaptive Agents repository root." >&2
    echo "Expected to find AGENTS.md and INDEX.md in: $repo_root" >&2
    exit 1
  fi

  local repo_setting_path
  repo_setting_path="$(to_vscode_setting_path "$repo_root")"

  local vscode_dir="$repo_root/vscode"
  local instructions_file="$vscode_dir/user-wide.instructions.md"

  local vscode_dir_setting_path
  vscode_dir_setting_path="$(to_vscode_setting_path "$vscode_dir")"

  local settings_path
  settings_path="$(detect_settings_path)"

  echo "Adaptive Agents repository: $repo_root"
  echo "VS Code flavor: $CODE_FLAVOR"
  echo "VS Code settings: $settings_path"
  echo "VS Code instructions directory: $vscode_dir"

  write_user_wide_instructions "$repo_root" "$instructions_file" "$repo_setting_path"
  update_vscode_settings "$settings_path" "$vscode_dir_setting_path" "$repo_setting_path"

  echo
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "Dry run complete. No files were modified."
  else
    echo "VS Code setup complete."
    echo
    echo "Generated:"
    echo "  $instructions_file"
    echo
    echo "Updated:"
    echo "  $settings_path"
    echo "    - chat.instructionsFilesLocations + vscode/ directory"
    echo "    - github.copilot.chat.additionalReadAccessPaths + repo root"
    echo "    - chat.includeApplyingInstructions = true"
    echo "    - chat.includeReferencedInstructions = true"
    echo
    echo "Verification (fresh VS Code Chat session in an unrelated repository):"
    echo "  1. Sentinel:      \"Are Adaptive Agents active?\" -> ADAPTIVE_AGENTS_GLOBAL_LOADED"
    echo "  2. Content proof: \"What is in section 1 of the Adaptive Agents INDEX.md?\""
    echo "                    -> must describe the items listed from the repository"
    echo "  3. Write-back:    ask for a retrospective capture -> file appears in"
    echo "                    $repo_root/retrospectives/inbox/"
    echo "The sentinel alone is not proof; repeat across multiple fresh sessions."
  fi
}

main "$@"
