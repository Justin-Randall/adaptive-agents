#!/usr/bin/env bash
set -euo pipefail

PASSES=0
FAILURES=0

pass() {
  PASSES=$((PASSES + 1))
  printf 'PASS: %s\n' "$1"
}

fail() {
  FAILURES=$((FAILURES + 1))
  printf 'FAIL: %s\n' "$1"
}

find_python() {
  if python3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
  elif python --version >/dev/null 2>&1; then
    PYTHON_CMD=(python)
  elif py -3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
  else
    return 1
  fi
}

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_ROOT_NORM="${REPO_ROOT//\\//}"
INSTALLER="$REPO_ROOT/scripts/install-vscode.sh"

if ! find_python; then
  echo "ERROR: Python is required to run these tests." >&2
  exit 1
fi

TMP_ROOT="$(mktemp -d -p "$REPO_ROOT")"
trap 'rm -rf "$TMP_ROOT"' EXIT
TEST_HOME="$TMP_ROOT/home"
mkdir -p "$TEST_HOME"

run_installer() {
  local settings_path="$1"
  local version_output="$2"
  shift 2
  HOME="$TEST_HOME" ADAPTIVE_AGENTS_VSCODE_VERSION_OUTPUT="$version_output" \
    bash "$INSTALLER" --settings "$settings_path" "$@"
}

json_check() {
  local path="$1"
  local expression="$2"
  "${PYTHON_CMD[@]}" - "$path" "$REPO_ROOT_NORM" <<PY
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
repo = sys.argv[2]
raise SystemExit(0 if ($expression) else 1)
PY
}

HOOK_PATH="$TEST_HOME/.copilot/hooks/adaptive-agents.json"

# A fresh supported install writes one hook and only the continuing read grant.
T1="$TMP_ROOT/fresh/settings.json"
T1_OUTPUT="$(run_installer "$T1" '1.129.0')"
if json_check "$HOOK_PATH" 'list(data.get("hooks", {})) == ["SessionStart"] and len(data["hooks"]["SessionStart"]) == 1 and data["hooks"]["SessionStart"][0]["type"] == "command" and "vscode-session-start.py" in data["hooks"]["SessionStart"][0]["command"] and "bash" not in data["hooks"]["SessionStart"][0]["command"]'; then
  pass "supported install writes one Adaptive Agents SessionStart hook"
else
  fail "supported install writes one Adaptive Agents SessionStart hook"
fi
HOOK_COMMAND="$("${PYTHON_CMD[@]}" -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["hooks"]["SessionStart"][0]["command"])' "$HOOK_PATH")"
if [[ "$HOOK_COMMAND" == "py -3 \"$REPO_ROOT_NORM/scripts/vscode-session-start.py\"" ]] && printf '{"hookEventName":"SessionStart"}\n' | eval "$HOOK_COMMAND" >/dev/null; then
  pass "installed hook command executes the adapter directly with Windows Python"
else
  fail "installed hook command executes the adapter directly with Windows Python"
fi
if json_check "$T1" 'data == {"github.copilot.chat.additionalReadAccessPaths": [repo]}'; then
  pass "fresh settings contain only the external read grant"
else
  fail "fresh settings contain only the external read grant"
fi
if [[ "$T1_OUTPUT" == *"deterministic SessionStart hook"* && "$T1_OUTPUT" != *"terminal.autoApprove"* ]]; then
  pass "completion output reports hook-native setup without terminal approval"
else
  fail "completion output reports hook-native setup without terminal approval"
fi

# Migration removes only installer-owned legacy entries.
T2="$TMP_ROOT/migration/settings.json"
mkdir -p "$(dirname "$T2")"
cat > "$T2" <<EOF
{
  "editor.fontSize": 15,
  "chat.instructionsFilesLocations": {
    "$REPO_ROOT_NORM/vscode": true,
    "C:/user/instructions": true
  },
  "chat.includeApplyingInstructions": false,
  "chat.includeReferencedInstructions": true,
  "github.copilot.chat.additionalReadAccessFolders": ["$REPO_ROOT_NORM"],
  "github.copilot.chat.additionalReadAccessPaths": ["C:/existing/read/path"],
  "chat.tools.terminal.autoApprove": {
    "git status": true,
    "rm": false,
    "/^bash\\\\ \"C:/old/adaptive-agents/scripts/session\\\\-start\\\\.sh\"$/": {
      "approve": true,
      "matchCommandLine": true
    },
    "/^user exact command$/": {
      "approve": true,
      "matchCommandLine": true
    }
  }
}
EOF
run_installer "$T2" 'Version: 1.130.2 (stable)' >/dev/null
if json_check "$T2" 'data["chat.instructionsFilesLocations"] == {"C:/user/instructions": True} and data["chat.tools.terminal.autoApprove"] == {"git status": True, "rm": False, "/^user exact command$/": {"approve": True, "matchCommandLine": True}}'; then
  pass "migration removes only Adaptive Agents bootstrap registration and approval"
else
  fail "migration removes only Adaptive Agents bootstrap registration and approval"
fi
if json_check "$T2" 'data["chat.includeApplyingInstructions"] is False and data["chat.includeReferencedInstructions"] is True and data["editor.fontSize"] == 15'; then
  pass "migration preserves generic and unrelated user settings"
else
  fail "migration preserves generic and unrelated user settings"
fi
if json_check "$T2" '"github.copilot.chat.additionalReadAccessFolders" not in data and data["github.copilot.chat.additionalReadAccessPaths"] == ["C:/existing/read/path", repo]'; then
  pass "migration retains the canonical read grant and removes obsolete key"
else
  fail "migration retains the canonical read grant and removes obsolete key"
fi

# Rerunning is byte-stable for both managed files.
cp "$T2" "$TMP_ROOT/settings-before.json"
cp "$HOOK_PATH" "$TMP_ROOT/hook-before.json"
run_installer "$T2" '1.129.0' >/dev/null
if cmp -s "$T2" "$TMP_ROOT/settings-before.json" && cmp -s "$HOOK_PATH" "$TMP_ROOT/hook-before.json"; then
  pass "supported rerun is byte-stable"
else
  fail "supported rerun is byte-stable"
fi

# Disabled hooks block installation without any mutation.
T3="$TMP_ROOT/disabled/settings.json"
mkdir -p "$(dirname "$T3")"
printf '{"chat.useHooks":false}\n' > "$T3"
rm -f "$HOOK_PATH"
if run_installer "$T3" '1.129.0' >"$TMP_ROOT/disabled.out" 2>&1; then
  fail "explicitly disabled hooks block installation"
elif [[ ! -e "$HOOK_PATH" ]] && json_check "$T3" 'data == {"chat.useHooks": False}' && grep -Fq 'chat.useHooks is false' "$TMP_ROOT/disabled.out"; then
  pass "explicitly disabled hooks block installation without mutation"
else
  fail "explicitly disabled hooks block installation without mutation"
fi

# Unsupported and malformed versions fail before creating settings or hooks.
for version in '1.128.9' 'not-a-version'; do
  case_name="${version//[^A-Za-z0-9]/-}"
  settings="$TMP_ROOT/$case_name/settings.json"
  rm -f "$HOOK_PATH"
  if run_installer "$settings" "$version" >"$TMP_ROOT/$case_name.out" 2>&1; then
    fail "version $version is rejected"
  elif [[ ! -e "$settings" && ! -e "$HOOK_PATH" ]] && grep -Fq '1.129.0 or newer' "$TMP_ROOT/$case_name.out"; then
    pass "version $version is rejected before mutation"
  else
    fail "version $version is rejected before mutation"
  fi
done

# Dry-run reports capability and leaves both targets untouched.
T4="$TMP_ROOT/dry-run/settings.json"
mkdir -p "$(dirname "$T4")"
printf '{"editor.wordWrap":"on"}\n' > "$T4"
cp "$T4" "$TMP_ROOT/dry-run-before.json"
rm -f "$HOOK_PATH"
T4_OUTPUT="$(run_installer "$T4" '1.129.0-insider' --dry-run)"
if cmp -s "$T4" "$TMP_ROOT/dry-run-before.json" && [[ ! -e "$HOOK_PATH" ]] && [[ "$T4_OUTPUT" == *"Would install deterministic SessionStart hook"* ]]; then
  pass "dry-run accepts version suffixes and performs no mutation"
else
  fail "dry-run accepts version suffixes and performs no mutation"
fi

# A copied installation removes only a recognized generated legacy bootstrap.
COPIED_REPO="$TMP_ROOT/copied-repo"
mkdir -p "$COPIED_REPO/scripts" "$COPIED_REPO/vscode"
cp "$INSTALLER" "$COPIED_REPO/scripts/install-vscode.sh"
cp "$REPO_ROOT/scripts/vscode-session-start.py" "$COPIED_REPO/scripts/"
touch "$COPIED_REPO/AGENTS.md" "$COPIED_REPO/INDEX.md"
printf '# User-Wide Adaptive Agent Bootstrap\n' > "$COPIED_REPO/vscode/user-wide.instructions.md"
COPIED_SETTINGS="$TMP_ROOT/copied/settings.json"
HOME="$TEST_HOME" ADAPTIVE_AGENTS_VSCODE_VERSION_OUTPUT='1.129.0' bash "$COPIED_REPO/scripts/install-vscode.sh" --settings "$COPIED_SETTINGS" >/dev/null
if [[ ! -e "$COPIED_REPO/vscode/user-wide.instructions.md" ]]; then
  pass "migration removes a recognized generated bootstrap file"
else
  fail "migration removes a recognized generated bootstrap file"
fi

mkdir -p "$COPIED_REPO/vscode"
printf '# User-owned instructions\n' > "$COPIED_REPO/vscode/user-wide.instructions.md"
HOME="$TEST_HOME" ADAPTIVE_AGENTS_VSCODE_VERSION_OUTPUT='1.129.0' bash "$COPIED_REPO/scripts/install-vscode.sh" --settings "$COPIED_SETTINGS" >"$TMP_ROOT/copied-user.out" 2>&1
if [[ -f "$COPIED_REPO/vscode/user-wide.instructions.md" ]] && grep -Fq 'Preserving unrecognized file' "$TMP_ROOT/copied-user.out"; then
  pass "migration preserves an unrecognized file at the legacy path"
else
  fail "migration preserves an unrecognized file at the legacy path"
fi

printf '\nVS Code hook installer tests: %d passed, %d failure(s).\n' "$PASSES" "$FAILURES"
[[ "$FAILURES" -eq 0 ]]