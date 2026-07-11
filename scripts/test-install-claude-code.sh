#!/usr/bin/env bash
set -euo pipefail

# test-install-claude-code.sh
#
# Automated dogfood test for the Claude Code installer integration.
#
# Validates all automated claims without requiring a real Claude Code session:
#   1. Config generation — CLAUDE.md imports the canonical AGENTS.md
#   2. Settings merge — repository access is added without losing user settings
#   3. Idempotency — rerunning produces byte-for-byte identical managed files
#   4. Dry-run — no files are modified
#   5. README check — Claude Code installation is documented
#
# Runs in a temporary, isolated directory. Exit code 0 = all pass, 1 = failures.

usage() {
  cat <<EOF
Usage:
  bash scripts/test-install-claude-code.sh [options]

Options:
  --installer PATH   Path to install-claude-code.sh. Default: scripts/install-claude-code.sh
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
INSTALL_REPO_ROOT="$(git -C "$REPO_ROOT" rev-parse --show-toplevel 2>/dev/null || printf '%s' "$REPO_ROOT")"

if [[ -z "$INSTALLER_PATH" ]]; then
  INSTALLER_PATH="$SCRIPT_DIR/install-claude-code.sh"
fi

if [[ ! -f "$INSTALLER_PATH" ]]; then
  echo "FAIL: Installer not found: $INSTALLER_PATH"
  exit 1
fi

PASSES=0
FAILURES=0

pass() { PASSES=$((PASSES + 1)); echo "  PASS: $1"; }
fail() { FAILURES=$((FAILURES + 1)); echo "  FAIL: $1"; }

# ---------------------------------------------------------------------------
# Create temp home directory to isolate the test
# ---------------------------------------------------------------------------
create_temp_dir() {
  python -c "import tempfile; print(tempfile.mkdtemp())" 2>/dev/null ||
  mktemp -d 2>/dev/null ||
  mktemp -d -t 'claude-test-XXXX' 2>/dev/null ||
  { echo "ERROR: cannot create temp directory" >&2; exit 1; }
}
TEST_HOME="$(create_temp_dir)"
export HOME="$TEST_HOME"
export USERPROFILE="$TEST_HOME"

cleanup() {
  rm -rf "$TEST_HOME"
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

echo "=== Test 1: Dry-run creates no files ==="
bash "$INSTALLER_PATH" --dry-run > /dev/null 2>&1

if [[ ! -f "$TEST_HOME/.claude/CLAUDE.md" ]] && [[ ! -f "$TEST_HOME/.claude/settings.json" ]]; then
  pass "Dry-run left no files behind"
else
  fail "Dry-run created files unexpectedly"
fi

echo
echo "=== Test 2: First install creates native import and access grant ==="
mkdir -p "$TEST_HOME/.claude"
cat > "$TEST_HOME/.claude/settings.json" <<'JSON'
{
  "theme": "light",
  "permissions": {
    "allow": [
      "Read"
    ],
    "additionalDirectories": [
      "C:/existing/directory"
    ]
  }
}
JSON

bash "$INSTALLER_PATH" > /dev/null 2>&1

if [[ -f "$TEST_HOME/.claude/CLAUDE.md" ]]; then
  pass "CLAUDE.md created"
else
  fail "CLAUDE.md not created"
fi

if grep -q "^#==ADAPTIVE_AGENTS_START==" "$TEST_HOME/.claude/CLAUDE.md" 2>/dev/null; then
  pass "CLAUDE.md has ADAPTIVE_AGENTS_START marker"
else
  fail "CLAUDE.md missing ADAPTIVE_AGENTS_START marker"
fi

if grep -q "^#==ADAPTIVE_AGENTS_END==" "$TEST_HOME/.claude/CLAUDE.md" 2>/dev/null; then
  pass "CLAUDE.md has ADAPTIVE_AGENTS_END marker"
else
  fail "CLAUDE.md missing ADAPTIVE_AGENTS_END marker"
fi

if grep -Fxq "@$INSTALL_REPO_ROOT/AGENTS.md" "$TEST_HOME/.claude/CLAUDE.md" 2>/dev/null; then
  pass "CLAUDE.md has a native absolute AGENTS.md import"
else
  fail "CLAUDE.md missing native absolute AGENTS.md import"
fi

if python - "$TEST_HOME/.claude/settings.json" "$INSTALL_REPO_ROOT" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as settings_file:
    settings = json.load(settings_file)

directories = settings["permissions"]["additionalDirectories"]
assert settings["theme"] == "light"
assert settings["permissions"]["allow"] == ["Read"]
assert "C:/existing/directory" in directories
assert directories.count(sys.argv[2]) == 1
PY
then
  pass "Settings merge preserves user values and grants repository access"
else
  fail "Settings merge changed user values or omitted repository access"
fi

echo
echo "=== Test 3: Idempotency — re-run produces same result ==="
cp "$TEST_HOME/.claude/CLAUDE.md" "$TEST_HOME/CLAUDE.md.before"
cp "$TEST_HOME/.claude/settings.json" "$TEST_HOME/settings.json.before"
bash "$INSTALLER_PATH" > /dev/null 2>&1

SECTION_COUNT=$(grep -c "^#==ADAPTIVE_AGENTS_START==" "$TEST_HOME/.claude/CLAUDE.md" 2>/dev/null || true)
if [[ "$SECTION_COUNT" -eq 1 ]]; then
  pass "CLAUDE.md has exactly one Adaptive Agents section (no duplication)"
else
  fail "CLAUDE.md has $SECTION_COUNT sections (expected 1)"
fi

if cmp -s "$TEST_HOME/CLAUDE.md.before" "$TEST_HOME/.claude/CLAUDE.md" &&
   cmp -s "$TEST_HOME/settings.json.before" "$TEST_HOME/.claude/settings.json"; then
  pass "Re-run leaves CLAUDE.md and settings.json unchanged"
else
  fail "Re-run changed CLAUDE.md or settings.json"
fi

echo
echo "=== Test 4: README has Claude Code section ==="
README="$REPO_ROOT/README.md"
if [[ -f "$README" ]]; then
  if grep -q "install-claude-code.sh" "$README" 2>/dev/null; then
    pass "README references install-claude-code.sh"
  else
    fail "README missing install-claude-code.sh reference"
  fi

  if grep -q "Claude Code" "$README" 2>/dev/null; then
    pass "README has Claude Code section"
  else
    fail "README missing Claude Code section"
  fi
else
  fail "README not found"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo
echo "=== Results: $PASSES passed, $FAILURES failed ==="

if [[ "$FAILURES" -gt 0 ]]; then
  exit 1
fi
