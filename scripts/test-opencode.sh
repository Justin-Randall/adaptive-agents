#!/usr/bin/env bash
set -euo pipefail

# test-opencode.sh
#
# Automated dogfood test for the OpenCode installer integration.
#
# Validates all automated claims without requiring a real OpenCode session:
#   1. Config generation — installer creates valid JSON with correct instructions
#   2. Instruction paths resolve — every path points to an actual file
#   3. Idempotency — running the installer twice produces identical config
#   4. Command deployment — command files land with valid YAML frontmatter
#   5. README check — OpenCode installation is documented
#
# Runs in a temporary, isolated directory. Exit code 0 = all pass, 1 = failures.

usage() {
  cat <<EOF
Usage:
  bash scripts/test-opencode.sh [options]

Options:
  --installer PATH   Path to install-opencode.sh. Default: scripts/install-opencode.sh
  -h, --help         Show this help.
EOF
}

INSTALLER_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --installer)
      INSTALLER_PATH="${2:-}"
      if [[ -z "$INSTALLER_PATH" ]]; then
        echo "ERROR: --installer requires a path." >&2
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

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# Normalize repo root to match installer output format (C:/Users/... not /c/Users/...)
ROOT_FS="$REPO_ROOT"
case "$ROOT_FS" in
  /[a-z]/*)
    letter="$(printf '%s' "${ROOT_FS:1:1}" | tr '[:lower:]' '[:upper:]')"
    ROOT_FS="$letter:${ROOT_FS:2}"
    ;;
esac

if [[ -z "$INSTALLER_PATH" ]]; then
  INSTALLER_PATH="$SCRIPT_DIR/install-opencode.sh"
fi

if [[ ! -f "$INSTALLER_PATH" ]]; then
  echo "FAIL: Installer not found: $INSTALLER_PATH"
  exit 1
fi

# ---------------------------------------------------------------------------
# Find Python
# ---------------------------------------------------------------------------

PYTHON_CMD=()
find_python() {
  if python --version >/dev/null 2>&1; then
    PYTHON_CMD=(python)
    return 0
  fi
  if python3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
    return 0
  fi
  if py -3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
    return 0
  fi
  return 1
}
if ! find_python; then
  echo "FAIL: Python is required for config validation tests."
  exit 1
fi

# ---------------------------------------------------------------------------
# Create temp directory (Windows-visible path)
# ---------------------------------------------------------------------------

detect_temp_dir() {
  local uname_s
  uname_s="$(uname -s 2>/dev/null || echo unknown)"

  case "$uname_s" in
    MINGW*|MSYS*|CYGWIN*)
      # Use LOCALAPPDATA\Temp so Windows Python can see the path
      if [[ -n "${LOCALAPPDATA:-}" ]]; then
        mktemp -d -p "$LOCALAPPDATA/Temp" 2>/dev/null
      elif [[ -n "${TMPDIR:-}" ]]; then
        mktemp -d -p "$TMPDIR" 2>/dev/null
      else
        mktemp -d
      fi
      ;;
    *)
      mktemp -d
      ;;
  esac
}

# Create a temporary, isolated home-like directory for testing
TEST_DIR="$(detect_temp_dir)"

# Convert to forward slashes so Python string escapes (e.g., \U in C:\Users) are not triggered
TEST_DIR="${TEST_DIR//\\//}"
trap 'rm -rf "$TEST_DIR"' EXIT

PASSES=0
FAILURES=0

pass() {
  PASSES=$((PASSES + 1))
  printf '  PASS: %s\n' "$1"
}

fail() {
  FAILURES=$((FAILURES + 1))
  printf '  FAIL: %s\n' "$1"
}

# ---------------------------------------------------------------------------
# 1. Config generation test
# ---------------------------------------------------------------------------
printf '=== Test 1: Config generation ===\n'

TEST_CONFIG="$TEST_DIR/opencode.json"
TEST_COMMANDS="$TEST_DIR/commands"

bash "$INSTALLER_PATH" \
  --opencode-config "$TEST_CONFIG" \
  > /dev/null 2>&1

if [[ ! -f "$TEST_CONFIG" ]]; then
  fail "Config file was not created at $TEST_CONFIG"
else
  pass "Config file created"
fi

# Validate JSON
if "${PYTHON_CMD[@]}" -c "import json; json.load(open('$TEST_CONFIG'))" 2>/dev/null; then
  pass "Config file is valid JSON"
else
  fail "Config file is not valid JSON"
fi

# Check sentinel marker file (separate from config to avoid OpenCode schema rejection)
TEST_MARKER="$(dirname "$TEST_CONFIG")/.adaptive-agents-installed"
if [[ -f "$TEST_MARKER" ]]; then
  pass "Sentinel marker file .adaptive-agents-installed is present"
else
  fail "Sentinel marker file .adaptive-agents-installed is missing"
fi

# Check expected instructions
if "${PYTHON_CMD[@]}" -c "
import json
c = json.load(open('$TEST_CONFIG'))
expected = [
    '${ROOT_FS}/AGENTS.md',
    '${ROOT_FS}/INDEX.md',
    '${ROOT_FS}/instructions/global.instructions.md',
    '${ROOT_FS}/instructions/*.instructions.md',
]
actual = c.get('instructions', [])
for e in expected:
    assert e in actual, f'Missing instruction: {e}'
" 2>/dev/null; then
  pass "Instructions array contains all expected entries"
else
  fail "Instructions array missing expected entries"
fi

# Check global AGENTS.md was installed
TEST_AGENTS="$(dirname "$TEST_CONFIG")/AGENTS.md"
if [[ -f "$TEST_AGENTS" ]]; then
  pass "Global AGENTS.md installed"
  if grep -q "ADAPTIVE_AGENTS_GLOBAL_LOADED" "$TEST_AGENTS"; then
    pass "Global AGENTS.md contains sentinel response"
  else
    fail "Global AGENTS.md missing sentinel response"
  fi
  if grep -q "${ROOT_FS}" "$TEST_AGENTS"; then
    pass "Global AGENTS.md contains resolved repo path"
  else
    fail "Global AGENTS.md missing resolved repo path"
  fi
else
  fail "Global AGENTS.md not installed"
fi

echo

# ---------------------------------------------------------------------------
# 2. Instruction paths resolve test
# ---------------------------------------------------------------------------
printf '=== Test 2: Instruction paths resolve ===\n'

# Check that non-glob instructions point to real files
"${PYTHON_CMD[@]}" -c "
import json, os, glob

c = json.load(open('$TEST_CONFIG'))
for entry in c.get('instructions', []):
    if '*' in entry:
        matches = glob.glob(entry)
        assert len(matches) >= 1, f'Glob pattern matches no files: {entry}'
    else:
        assert os.path.exists(entry), f'Path does not exist: {entry}'
" 2>/dev/null && pass "All instruction paths resolve to actual files" \
  || fail "Some instruction paths do not resolve"

echo

# ---------------------------------------------------------------------------
# 3. Idempotency test
# ---------------------------------------------------------------------------
printf '=== Test 3: Idempotency ===\n'

# Run installer again with same args
# Save config after first run
cp "$TEST_CONFIG" "$TEST_DIR/config-after-first-run.json"

bash "$INSTALLER_PATH" \
  --opencode-config "$TEST_CONFIG" \
  --skip-commands \
  > /dev/null 2>&1

if "${PYTHON_CMD[@]}" -c "
import json
c1 = json.load(open('$TEST_DIR/config-after-first-run.json'))
c2 = json.load(open('$TEST_CONFIG'))
assert c1 == c2, 'Configs differ between runs'
" 2>/dev/null; then
  pass "Installer is idempotent — config identical after two runs"
else
  fail "Installer is not idempotent — config differs between runs"
fi

echo

# ---------------------------------------------------------------------------
# 4. Command deployment test
# ---------------------------------------------------------------------------
printf '=== Test 4: Command deployment ===\n'

# Re-run installer without --skip-commands and with an explicit commands dir
TEST_CONFIG2="$TEST_DIR/config2.json"
TEST_COMMANDS2="$TEST_DIR/commands2"

bash "$INSTALLER_PATH" \
  --opencode-config "$TEST_CONFIG2" \
  > /dev/null 2>&1

# The installer writes commands dir alongside the config
# We need to find where commands were installed. The installer
# uses the config dir + "/commands". Let's check.
EXPECTED_COMMANDS_DIR="$(dirname "$TEST_CONFIG2")/commands"

expected_commands=(
  "capture-retrospective.md"
  "triage-retrospective.md"
  "review-retrospective-inbox.md"
  "review-promotion-candidates.md"
  "apply-approved-promotion.md"
  "check-adaptive-agents.md"
)

all_found=true
for cmd in "${expected_commands[@]}"; do
  if [[ -f "$EXPECTED_COMMANDS_DIR/$cmd" ]]; then
    pass "Command file installed: $cmd"
  else
    fail "Command file missing: $cmd"
    all_found=false
  fi
done

# Validate YAML frontmatter on each command file
for cmd_file in "$EXPECTED_COMMANDS_DIR"/*.md; do
  if [[ -f "$cmd_file" ]]; then
    if head -1 "$cmd_file" | grep -q '^---$'; then
      pass "$(basename "$cmd_file") has valid YAML frontmatter opening"
    else
      fail "$(basename "$cmd_file") is missing YAML frontmatter"
    fi
  fi
done

echo

# ---------------------------------------------------------------------------
# 5. README check
# ---------------------------------------------------------------------------
printf '=== Test 5: README documentation ===\n'

README_PATH="$REPO_ROOT/README.md"
if [[ ! -f "$README_PATH" ]]; then
  fail "README.md not found at $README_PATH"
else
  if grep -q 'Install OpenCode' "$README_PATH" 2>/dev/null; then
    pass "README.md contains OpenCode installation section"
  else
    fail "README.md is missing OpenCode installation section"
  fi
fi

echo

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
printf '=== Results: %d passed, %d failed ===\n' "$PASSES" "$FAILURES"

if [[ "$FAILURES" -gt 0 ]]; then
  exit 1
fi
exit 0
