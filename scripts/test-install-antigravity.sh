#!/usr/bin/env bash
set -euo pipefail

# test-install-antigravity.sh
#
# Automated tests for the Antigravity 2.0 desktop app installer.
#
# Tests what can be tested without the actual app installed:
#   1. Dry-run — no files modified
#   2. Prerequisite check — fails with actionable error when app not found
#   3. Fresh install — GEMINI.md imports AGENTS.md via @ syntax
#   4. Idempotency — rerun produces byte-identical output
#   5. User content preservation — pre-existing prose survives
#   6. User-file preservation — non-installer files untouched
#   7. README check — references install-antigravity.sh
#
# Runs in a temporary, isolated directory. Exit code 0 = all pass, 1 = failures.

usage() {
  cat <<EOF
Usage:
  bash scripts/test-install-antigravity.sh [options]

Options:
  --installer PATH   Path to install-antigravity.sh. Default: scripts/install-antigravity.sh
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
  INSTALLER_PATH="$SCRIPT_DIR/install-antigravity.sh"
fi

if [[ ! -f "$INSTALLER_PATH" ]]; then
  echo "FAIL: Installer not found: $INSTALLER_PATH"
  exit 1
fi

PASSES=0
FAILURES=0

pass() { PASSES=$((PASSES + 1)); echo "  PASS: $1"; }
fail() { FAILURES=$((FAILURES + 1)); echo "  FAIL: $1"; }

# Find a working Python 3 interpreter for JSON validation
find_python3() {
  local candidates=(python3 python py)
  local c
  for c in "${candidates[@]}"; do
    if "$c" --version >/dev/null 2>&1; then
      PYTHON3="$c"
      return 0
    fi
  done
  echo "ERROR: Python 3 is required for JSON validation in tests." >&2
  exit 1
}
find_python3

# ---------------------------------------------------------------------------
# Create temp home directory to isolate the test
# ---------------------------------------------------------------------------
create_temp_dir() {
  "$PYTHON3" -c "import tempfile; print(tempfile.mkdtemp())" 2>/dev/null ||
  mktemp -d 2>/dev/null ||
  mktemp -d -t 'antigravity-test-XXXX' 2>/dev/null ||
  { echo "ERROR: cannot create temp directory" >&2; exit 1; }
}
TEST_HOME="$(create_temp_dir)"
export HOME="$TEST_HOME"
export USERPROFILE="$TEST_HOME"

# Mock the Antigravity 2.0 desktop app by creating a dummy executable in a
# common install path within the temp home.  We use LOCALAPPDATA since the
# installer checks that first on Windows (the most likely platform).
MOCK_APP_DIR="$TEST_HOME/appdata/Programs/Antigravity"
mkdir -p "$MOCK_APP_DIR"
touch "$MOCK_APP_DIR/Antigravity.exe"
export LOCALAPPDATA="$TEST_HOME/appdata"

cleanup() {
  rm -rf "$TEST_HOME"
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Test 1: Prerequisite check — fails with actionable error when app not found
# ---------------------------------------------------------------------------
echo "=== Test 1: Prerequisite check ==="
# Hide the mock to test the failure path
mv "$MOCK_APP_DIR/Antigravity.exe" "$MOCK_APP_DIR/Antigravity.exe.hidden"

if bash "$INSTALLER_PATH" > "$TEST_HOME/install-output.txt" 2>&1; then
  fail "Installer succeeded despite app not being detected"
else
  if grep -qi "antigravity.*not.*installed\|download" "$TEST_HOME/install-output.txt" 2>/dev/null; then
    pass "Installer rejected missing app with actionable error"
  else
    fail "Installer rejection output lacks actionable guidance"
  fi
fi

mv "$MOCK_APP_DIR/Antigravity.exe.hidden" "$MOCK_APP_DIR/Antigravity.exe"

# ---------------------------------------------------------------------------
# Test 2: Dry-run creates no files
# ---------------------------------------------------------------------------
echo
echo "=== Test 2: Dry-run creates no files ==="
bash "$INSTALLER_PATH" --dry-run > /dev/null 2>&1

if [[ ! -f "$TEST_HOME/.gemini/GEMINI.md" ]]; then
  pass "Dry-run left no files behind"
else
  fail "Dry-run created files unexpectedly"
fi

# ---------------------------------------------------------------------------
# Test 3: Fresh install creates native import and permission grant
# ---------------------------------------------------------------------------
echo
echo "=== Test 3: Fresh install ==="
bash "$INSTALLER_PATH" > /dev/null 2>&1

if [[ -f "$TEST_HOME/.gemini/GEMINI.md" ]]; then
  pass "GEMINI.md created"
else
  fail "GEMINI.md not created"
fi

if grep -q "^#==ADAPTIVE_AGENTS_START==" "$TEST_HOME/.gemini/GEMINI.md" 2>/dev/null; then
  pass "GEMINI.md has ADAPTIVE_AGENTS_START marker"
else
  fail "GEMINI.md missing ADAPTIVE_AGENTS_START marker"
fi

if grep -q "^#==ADAPTIVE_AGENTS_END==" "$TEST_HOME/.gemini/GEMINI.md" 2>/dev/null; then
  pass "GEMINI.md has ADAPTIVE_AGENTS_END marker"
else
  fail "GEMINI.md missing ADAPTIVE_AGENTS_END marker"
fi

if grep -Fxq "@$INSTALL_REPO_ROOT/AGENTS.md" "$TEST_HOME/.gemini/GEMINI.md" 2>/dev/null; then
  pass "GEMINI.md has a native absolute AGENTS.md import"
else
  fail "GEMINI.md missing native absolute AGENTS.md import"
fi

echo "  (Part B requires one-time dialog — not testable in isolation)"

# ---------------------------------------------------------------------------
# Test 4: Idempotency — re-run produces same result
# ---------------------------------------------------------------------------
echo
echo "=== Test 4: Idempotency ==="
cp "$TEST_HOME/.gemini/GEMINI.md" "$TEST_HOME/GEMINI.md.before"
bash "$INSTALLER_PATH" > /dev/null 2>&1

SECTION_COUNT=$(grep -c "^#==ADAPTIVE_AGENTS_START==" "$TEST_HOME/.gemini/GEMINI.md" 2>/dev/null || true)
if [[ "$SECTION_COUNT" -eq 1 ]]; then
  pass "GEMINI.md has exactly one Adaptive Agents section (no duplication)"
else
  fail "GEMINI.md has $SECTION_COUNT sections (expected 1)"
fi

if cmp -s "$TEST_HOME/GEMINI.md.before" "$TEST_HOME/.gemini/GEMINI.md"; then
  pass "Re-run leaves GEMINI.md unchanged"
else
  fail "Re-run changed GEMINI.md"
fi

# ---------------------------------------------------------------------------
# Test 5: User content preservation — pre-existing prose is kept
# ---------------------------------------------------------------------------
echo
echo "=== Test 5: User content preservation ==="
cat > "$TEST_HOME/.gemini/GEMINI.md" <<'EOF'
# Personal Preferences

I like concise answers and example code.

EOF

bash "$INSTALLER_PATH" > /dev/null 2>&1

if grep -q "Personal Preferences" "$TEST_HOME/.gemini/GEMINI.md"; then
  pass "Existing user content preserved in GEMINI.md"
else
  fail "Existing user content lost from GEMINI.md"
fi

if grep -q "^#==ADAPTIVE_AGENTS_START==" "$TEST_HOME/.gemini/GEMINI.md"; then
  pass "User GEMINI.md still has Adaptive Agents section after re-install"
else
  fail "User GEMINI.md missing Adaptive Agents section after re-install"
fi

if grep -q "^@$INSTALL_REPO_ROOT/AGENTS.md$" "$TEST_HOME/.gemini/GEMINI.md"; then
  pass "AGENTS.md import present alongside user content"
else
  fail "AGENTS.md import missing alongside user content"
fi

# ---------------------------------------------------------------------------
# Test 6: User-file preservation — non-installer files are never deleted
# ---------------------------------------------------------------------------
echo
echo "=== Test 6: User-file preservation ==="
echo "# User-authored file" > "$TEST_HOME/.gemini/user-guidelines.md"

bash "$INSTALLER_PATH" > /dev/null 2>&1

if [[ -f "$TEST_HOME/.gemini/user-guidelines.md" ]]; then
  pass "Non-installer file preserved"
else
  fail "Non-installer file was deleted"
fi

# ---------------------------------------------------------------------------
# Test 7: README check
# ---------------------------------------------------------------------------
echo
echo "=== Test 7: README check ==="
README="$REPO_ROOT/README.md"
if [[ -f "$README" ]]; then
  if grep -q "install-antigravity.sh" "$README" 2>/dev/null; then
    pass "README references install-antigravity.sh"
  else
    fail "README missing install-antigravity.sh reference"
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
