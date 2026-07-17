#!/usr/bin/env bash
set -euo pipefail

# Installs deterministic Adaptive Agents SessionStart integration for VS Code 1.129+.

usage() {
  cat <<EOF
Usage:
  ./scripts/install-vscode.sh [options]

Options:
  --dry-run            Show what would change without writing files.
  --settings PATH      Use an explicit VS Code settings.json path.
  --code-flavor NAME   VS Code flavor: code, insiders, codium. Default: code.
  -h, --help           Show this help.
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
  if command_exists cygpath; then
    cygpath -u "$1" 2>/dev/null || printf '%s\n' "$1"
  else
    printf '%s\n' "$1"
  fi
}

to_vscode_path() {
  if command_exists cygpath; then
    cygpath -m "$1" 2>/dev/null || printf '%s\n' "$1"
  else
    printf '%s\n' "$1"
  fi
}

detect_repo_root() {
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local candidate="$script_dir/.."
  if [[ -f "$candidate/AGENTS.md" && -f "$candidate/INDEX.md" ]]; then
    cd "$candidate" && pwd
    return
  fi
  echo "ERROR: Could not determine Adaptive Agents repository root." >&2
  exit 1
}

detect_settings_path() {
  if [[ -n "$EXPLICIT_SETTINGS_PATH" ]]; then
    to_unix_path "$EXPLICIT_SETTINGS_PATH"
    return
  fi

  local uname_s
  uname_s="$(uname -s 2>/dev/null || echo unknown)"
  local product_dir=""
  case "$CODE_FLAVOR" in
    code) product_dir="Code" ;;
    insiders) product_dir="Code - Insiders" ;;
    codium) product_dir="VSCodium" ;;
    *)
      echo "ERROR: Unsupported --code-flavor '$CODE_FLAVOR'. Use code, insiders, or codium." >&2
      exit 1
      ;;
  esac

  case "$uname_s" in
    MINGW*|MSYS*|CYGWIN*)
      if [[ -z "${APPDATA:-}" ]]; then
        echo "ERROR: APPDATA is not set; use --settings PATH." >&2
        exit 1
      fi
      to_unix_path "$APPDATA/$product_dir/User/settings.json"
      ;;
    Darwin*) printf '%s\n' "$HOME/Library/Application Support/$product_dir/User/settings.json" ;;
    *) printf '%s\n' "$HOME/.config/$product_dir/User/settings.json" ;;
  esac
}

find_python_command() {
  local uname_s
  uname_s="$(uname -s 2>/dev/null || echo unknown)"
  if [[ "$uname_s" == MINGW* || "$uname_s" == MSYS* || "$uname_s" == CYGWIN* ]] && py -3 -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
    HOOK_PYTHON_COMMAND="py -3"
  elif python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
    HOOK_PYTHON_COMMAND="python3"
  elif python -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' >/dev/null 2>&1; then
    PYTHON_CMD=(python)
    HOOK_PYTHON_COMMAND="python"
  elif py -3 -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
    HOOK_PYTHON_COMMAND="py -3"
  else
    echo "ERROR: Python 3.11 or newer is required for VS Code integration." >&2
    return 1
  fi
}

detect_vscode_version() {
  local output="${ADAPTIVE_AGENTS_VSCODE_VERSION_OUTPUT:-}"
  local cli=""
  case "$CODE_FLAVOR" in
    code) cli="code" ;;
    insiders) cli="code-insiders" ;;
    codium) cli="codium" ;;
    *)
      echo "ERROR: Unsupported --code-flavor '$CODE_FLAVOR'. Use code, insiders, or codium." >&2
      return 1
      ;;
  esac

  if [[ -z "$output" ]]; then
    if ! command_exists "$cli" || ! output="$($cli --version 2>&1)"; then
      echo "ERROR: Could not determine the $CODE_FLAVOR version." >&2
      echo "Adaptive Agents requires VS Code 1.129.0 or newer." >&2
      echo "Verify with: $cli --version" >&2
      return 1
    fi
  fi
  if [[ ! "$output" =~ ([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
    echo "ERROR: Could not parse the $CODE_FLAVOR version from: $output" >&2
    echo "Adaptive Agents requires VS Code 1.129.0 or newer." >&2
    echo "Verify with: $cli --version" >&2
    return 1
  fi

  local major="${BASH_REMATCH[1]}"
  local minor="${BASH_REMATCH[2]}"
  VSCODE_VERSION="$major.$minor.${BASH_REMATCH[3]}"
  if (( major < 1 || (major == 1 && minor < 129) )); then
    echo "ERROR: Detected $CODE_FLAVOR version $VSCODE_VERSION." >&2
    echo "Adaptive Agents requires VS Code 1.129.0 or newer." >&2
    return 1
  fi
}

update_settings() {
  local mode="$1"
  local settings_path="$2"
  local repo_root="$3"
  local legacy_vscode_dir="$4"

  "${PYTHON_CMD[@]}" - "$mode" "$settings_path" "$repo_root" "$legacy_vscode_dir" <<'PY'
import json
import re
import sys
from pathlib import Path

mode, settings_name, repo_root, legacy_vscode_dir = sys.argv[1:]
settings_path = Path(settings_name)


def strip_jsonc(text):
    result = []
    index = 0
    in_string = False
    escaped = False
    line_comment = False
    block_comment = False
    while index < len(text):
        character = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if character in "\r\n":
                line_comment = False
                result.append(character)
            index += 1
            continue
        if block_comment:
            if character == "*" and following == "/":
                block_comment = False
                index += 2
            else:
                if character in "\r\n":
                    result.append(character)
                index += 1
            continue
        if in_string:
            result.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if character == '"':
            in_string = True
            result.append(character)
            index += 1
            continue
        if character == "/" and following == "/":
            line_comment = True
            index += 2
            continue
        if character == "/" and following == "*":
            block_comment = True
            index += 2
            continue
        result.append(character)
        index += 1
    return "".join(result)


try:
    raw = settings_path.read_text(encoding="utf-8") if settings_path.is_file() else "{}"
    settings = json.loads(re.sub(r",\s*([}\]])", r"\1", strip_jsonc(raw)))
except (json.JSONDecodeError, OSError) as error:
    print(f"ERROR: Could not parse VS Code settings file: {settings_path}: {error}", file=sys.stderr)
    raise SystemExit(1)

if not isinstance(settings, dict):
    print("ERROR: VS Code settings root must be a JSON object.", file=sys.stderr)
    raise SystemExit(1)
if settings.get("chat.useHooks") is False:
    print("ERROR: chat.useHooks is false; enable hooks before installing Adaptive Agents.", file=sys.stderr)
    raise SystemExit(1)
if mode == "preflight":
    raise SystemExit(0)

locations = settings.get("chat.instructionsFilesLocations")
if locations is not None:
    if not isinstance(locations, dict):
        print("ERROR: Existing chat.instructionsFilesLocations is not an object.", file=sys.stderr)
        raise SystemExit(1)
    locations.pop(legacy_vscode_dir, None)
    if not locations:
        settings.pop("chat.instructionsFilesLocations", None)

settings.pop("github.copilot.chat.additionalReadAccessFolders", None)
additional_paths = settings.get("github.copilot.chat.additionalReadAccessPaths", [])
if not isinstance(additional_paths, list):
    print("ERROR: Existing github.copilot.chat.additionalReadAccessPaths is not an array.", file=sys.stderr)
    raise SystemExit(1)
if repo_root not in additional_paths:
    additional_paths.append(repo_root)
settings["github.copilot.chat.additionalReadAccessPaths"] = additional_paths

approval_value = {"approve": True, "matchCommandLine": True}
terminal_approvals = settings.get("chat.tools.terminal.autoApprove")
if terminal_approvals is not None:
    if not isinstance(terminal_approvals, dict):
        print("ERROR: Existing chat.tools.terminal.autoApprove is not an object.", file=sys.stderr)
        raise SystemExit(1)
    for pattern, value in list(terminal_approvals.items()):
        generated = (
            value == approval_value
            and pattern.startswith('/^bash\\ "')
            and pattern.endswith('/scripts/session\\-start\\.sh"$/')
        )
        if generated:
            del terminal_approvals[pattern]
    if not terminal_approvals:
        settings.pop("chat.tools.terminal.autoApprove", None)

settings_path.parent.mkdir(parents=True, exist_ok=True)
settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY
}

write_hook() {
  local hook_path="$1"
  local adapter_path="$2"
  local adapter_setting_path="$3"
  if [[ ! -f "$adapter_path" ]]; then
    echo "ERROR: SessionStart adapter is missing: $adapter_path" >&2
    return 1
  fi
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] Would install deterministic SessionStart hook: $hook_path"
    return
  fi

  "${PYTHON_CMD[@]}" - "$hook_path" "$HOOK_PYTHON_COMMAND \"$adapter_setting_path\"" <<'PY'
import json
import sys
from pathlib import Path

hook_path = Path(sys.argv[1])
payload = {
    "hooks": {
        "SessionStart": [
            {"type": "command", "command": sys.argv[2], "timeout": 30}
        ]
    }
}
hook_path.parent.mkdir(parents=True, exist_ok=True)
hook_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
json.loads(hook_path.read_text(encoding="utf-8"))
PY
}

remove_legacy_bootstrap() {
  local legacy_file="$1"
  if [[ ! -f "$legacy_file" ]]; then
    return
  fi
  if ! grep -Fq '# User-Wide Adaptive Agent Bootstrap' "$legacy_file"; then
    echo "WARNING: Preserving unrecognized file at legacy bootstrap path: $legacy_file" >&2
    return
  fi
  rm "$legacy_file"
  rmdir "$(dirname "$legacy_file")" 2>/dev/null || :
}

main() {
  local repo_root
  repo_root="$(detect_repo_root)"
  local repo_setting_path
  repo_setting_path="$(to_vscode_path "$repo_root")"
  local settings_path
  settings_path="$(detect_settings_path)"
  local legacy_vscode_dir
  legacy_vscode_dir="$(to_vscode_path "$repo_root/vscode")"
  local hook_path="$HOME/.copilot/hooks/adaptive-agents.json"
  local adapter_path="$repo_root/scripts/vscode-session-start.py"
  local adapter_setting_path
  adapter_setting_path="$(to_vscode_path "$adapter_path")"

  find_python_command
  detect_vscode_version
  update_settings preflight "$settings_path" "$repo_setting_path" "$legacy_vscode_dir"

  echo "Adaptive Agents repository: $repo_root"
  echo "VS Code flavor: $CODE_FLAVOR"
  echo "VS Code version: $VSCODE_VERSION"
  echo "VS Code settings: $settings_path"

  write_hook "$hook_path" "$adapter_path" "$adapter_setting_path"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[dry-run] Would retain github.copilot.chat.additionalReadAccessPaths + repo root"
    echo "[dry-run] Would remove installer-owned legacy VS Code bootstrap settings"
    echo "Dry run complete. No files were modified."
    return
  fi

  if [[ -f "$settings_path" ]]; then
    cp "$settings_path" "${settings_path}.adaptive-agents.$(date +%Y%m%d-%H%M%S).bak"
  fi
  update_settings apply "$settings_path" "$repo_setting_path" "$legacy_vscode_dir"
  remove_legacy_bootstrap "$repo_root/vscode/user-wide.instructions.md"

  echo
  echo "VS Code setup complete with deterministic SessionStart hook."
  echo "Installed: $hook_path"
  echo "Session status: $HOME/.cache/adaptive-agents/vscode-session-start-status.json"
  echo "Updated: $settings_path"
  echo "  - github.copilot.chat.additionalReadAccessPaths + repo root"
  echo "  - removed installer-owned legacy bootstrap settings"
}

main "$@"