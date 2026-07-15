#!/usr/bin/env bash
set -euo pipefail

# test-opencode.sh
#
# Automated tests for scripts/install-opencode.sh (single-entrypoint rework).
#
# Validates against isolated temp directories; never touches the real
# OpenCode configuration:
#   1. Fresh install: entry point + trust grant + marker
#   2. Legacy migration: redundant layers removed, user content preserved
#   3. User-authored AGENTS.md is never deleted
#   4. Idempotency: rerun is byte-for-byte stable, no duplicate backups
#   5. Dry-run writes nothing
#   6. %APPDATA%/opencode legacy artifacts are cleaned up
#   7. README documents the OpenCode installation path
#
# Exit code 0 = all pass, 1 = any failure.

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

command_exists() {
  command -v "$1" >/dev/null 2>&1
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

detect_repo_root() {
  if command_exists git && git rev-parse --show-toplevel >/dev/null 2>&1; then
    git rev-parse --show-toplevel
    return
  fi
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "$script_dir/.." && pwd
}

REPO_ROOT="$(detect_repo_root)"
REPO_ROOT_NORM="${REPO_ROOT//\\//}"
INSTALLER="$REPO_ROOT/scripts/install-opencode.sh"

if ! find_python; then
  echo "ERROR: Python is required to run these tests." >&2
  exit 1
fi

TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

# Run the installer against an isolated config path and isolated APPDATA so
# the user's real configuration is never touched.
run_installer() {
  local config_path="$1"
  local appdata_dir="$2"
  shift 2
  env APPDATA="$appdata_dir" OPENCODE_CONFIG="" \
    bash "$INSTALLER" --opencode-config "$config_path" "$@"
}

# JSON assertion helper: exits 0 when the Python expression evaluates truthy.
json_check() {
  local config_path="$1"
  local expression="$2"
  "${PYTHON_CMD[@]}" - "$config_path" "$REPO_ROOT_NORM" <<PY
import json, sys
config = json.load(open(sys.argv[1], encoding="utf-8"))
repo = sys.argv[2]
result = ($expression)
raise SystemExit(0 if result else 1)
PY
}

LEGACY_COMMANDS=(
  apply-approved-promotion.md
  capture-retrospective.md
  check-adaptive-agents.md
  review-promotion-candidates.md
  review-retrospective-inbox.md
  triage-retrospective.md
)

seed_legacy_layers() {
  local dir="$1"
  mkdir -p "$dir/commands"

  cat > "$dir/opencode.jsonc" <<EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "provider": {
    "custom": {
      "name": "Preserved Provider"
    }
  },
  "instructions": [
    "$REPO_ROOT_NORM/AGENTS.md",
    "$REPO_ROOT_NORM/INDEX.md",
    "$REPO_ROOT_NORM/instructions/global.instructions.md",
    "$REPO_ROOT_NORM/instructions/*.instructions.md",
    "~/my-own-instructions.md"
  ]
}
EOF

  cat > "$dir/AGENTS.md" <<'EOF'
# Adaptive Agents — OpenCode Global Rules

Legacy generated copy that duplicates the sentinel.
EOF

  local cmd
  for cmd in "${LEGACY_COMMANDS[@]}"; do
    printf -- '---\ndescription: legacy\n---\nlegacy body\n' > "$dir/commands/$cmd"
  done
  printf -- '---\ndescription: mine\n---\nuser body\n' > "$dir/commands/user-command.md"
}

# ---------------------------------------------------------------------------
# Test 1: Fresh install — entry point + trust grant + marker
# ---------------------------------------------------------------------------
T1="$TMP_ROOT/t1"
mkdir -p "$T1/appdata"
run_installer "$T1/config/opencode.json" "$T1/appdata" >/dev/null

if [[ -f "$T1/config/opencode.json" ]]; then
  pass "fresh install creates config file"
else
  fail "fresh install creates config file"
fi

if json_check "$T1/config/opencode.json" 'config.get("instructions") == [f"{repo}/AGENTS.md"]'; then
  pass "fresh install: instructions is exactly the single canonical AGENTS.md entry"
else
  fail "fresh install: instructions is exactly the single canonical AGENTS.md entry"
fi

if json_check "$T1/config/opencode.json" 'config.get("permission", {}).get("external_directory", {}).get(f"{repo}/**") == "allow"'; then
  pass "fresh install: external_directory grant marks the repository allow"
else
  fail "fresh install: external_directory grant marks the repository allow"
fi

if json_check "$T1/config/opencode.json" 'config.get("$schema") == "https://opencode.ai/config.json"'; then
  pass "fresh install: \$schema is set"
else
  fail "fresh install: \$schema is set"
fi

if [[ -f "$T1/config/.adaptive-agents-installed" ]]; then
  pass "fresh install: idempotency marker written"
else
  fail "fresh install: idempotency marker written"
fi

# ---------------------------------------------------------------------------
# Test 2: Legacy migration — redundant layers removed, user content preserved
# ---------------------------------------------------------------------------
T2="$TMP_ROOT/t2"
mkdir -p "$T2/config" "$T2/appdata"
seed_legacy_layers "$T2/config"
run_installer "$T2/config/opencode.jsonc" "$T2/appdata" >/dev/null

if json_check "$T2/config/opencode.jsonc" 'sorted(config.get("instructions", [])) == sorted([f"{repo}/AGENTS.md", "~/my-own-instructions.md"])'; then
  pass "migration: legacy instructions entries removed, canonical + user entries kept"
else
  fail "migration: legacy instructions entries removed, canonical + user entries kept"
fi

if json_check "$T2/config/opencode.jsonc" 'config.get("provider", {}).get("custom", {}).get("name") == "Preserved Provider"'; then
  pass "migration: unrelated config keys preserved"
else
  fail "migration: unrelated config keys preserved"
fi

if [[ ! -f "$T2/config/AGENTS.md" ]]; then
  pass "migration: legacy AGENTS.md copy removed"
else
  fail "migration: legacy AGENTS.md copy removed"
fi

LEGACY_LEFT=0
for cmd in "${LEGACY_COMMANDS[@]}"; do
  [[ -f "$T2/config/commands/$cmd" ]] && LEGACY_LEFT=1
done
if [[ "$LEGACY_LEFT" -eq 0 ]]; then
  pass "migration: legacy command files removed"
else
  fail "migration: legacy command files removed"
fi

if [[ -f "$T2/config/commands/user-command.md" ]]; then
  pass "migration: user-authored command preserved"
else
  fail "migration: user-authored command preserved"
fi

# ---------------------------------------------------------------------------
# Test 3: User-authored AGENTS.md is never deleted
# ---------------------------------------------------------------------------
T3="$TMP_ROOT/t3"
mkdir -p "$T3/config" "$T3/appdata"
printf '# My own global rules\n\ndo not delete\n' > "$T3/config/AGENTS.md"
run_installer "$T3/config/opencode.json" "$T3/appdata" >/dev/null

if [[ -f "$T3/config/AGENTS.md" ]] && grep -q "do not delete" "$T3/config/AGENTS.md"; then
  pass "user-authored AGENTS.md left untouched"
else
  fail "user-authored AGENTS.md left untouched"
fi

# ---------------------------------------------------------------------------
# Test 4: Idempotency — rerun byte-for-byte stable, no duplicate backups
# ---------------------------------------------------------------------------
T4="$TMP_ROOT/t4"
mkdir -p "$T4/config" "$T4/appdata"
seed_legacy_layers "$T4/config"
run_installer "$T4/config/opencode.jsonc" "$T4/appdata" >/dev/null
cp "$T4/config/opencode.jsonc" "$T4/after-first-run.jsonc"
BACKUPS_AFTER_FIRST="$(ls "$T4/config"/*.bak 2>/dev/null | wc -l)"
sleep 1
run_installer "$T4/config/opencode.jsonc" "$T4/appdata" >/dev/null
BACKUPS_AFTER_SECOND="$(ls "$T4/config"/*.bak 2>/dev/null | wc -l)"

if cmp -s "$T4/config/opencode.jsonc" "$T4/after-first-run.jsonc"; then
  pass "idempotency: rerun leaves config byte-for-byte unchanged"
else
  fail "idempotency: rerun leaves config byte-for-byte unchanged"
fi

if [[ "$BACKUPS_AFTER_FIRST" == "$BACKUPS_AFTER_SECOND" ]]; then
  pass "idempotency: rerun creates no additional backups"
else
  fail "idempotency: rerun creates no additional backups"
fi

# ---------------------------------------------------------------------------
# Test 5: Dry-run writes nothing
# ---------------------------------------------------------------------------
T5="$TMP_ROOT/t5"
mkdir -p "$T5/config" "$T5/appdata"
seed_legacy_layers "$T5/config"
BEFORE_STATE="$(cd "$T5" && find . -type f | sort; cat "$T5/config/opencode.jsonc")"
run_installer "$T5/config/opencode.jsonc" "$T5/appdata" --dry-run >/dev/null
AFTER_STATE="$(cd "$T5" && find . -type f | sort; cat "$T5/config/opencode.jsonc")"

if [[ "$BEFORE_STATE" == "$AFTER_STATE" ]]; then
  pass "dry-run: no files created, modified, or removed"
else
  fail "dry-run: no files created, modified, or removed"
fi

# ---------------------------------------------------------------------------
# Test 6: %APPDATA%/opencode legacy artifacts cleaned up
# ---------------------------------------------------------------------------
T6="$TMP_ROOT/t6"
mkdir -p "$T6/appdata/opencode/commands" "$T6/config"
cat > "$T6/appdata/opencode/opencode.json" <<EOF
{
  "instructions": [
    "$REPO_ROOT_NORM/AGENTS.md",
    "$REPO_ROOT_NORM/INDEX.md",
    "$REPO_ROOT_NORM/instructions/global.instructions.md",
    "$REPO_ROOT_NORM/instructions/*.instructions.md"
  ],
  "_adaptive_agents_installed": true
}
EOF
for cmd in "${LEGACY_COMMANDS[@]}"; do
  printf 'legacy\n' > "$T6/appdata/opencode/commands/$cmd"
done
run_installer "$T6/config/opencode.json" "$T6/appdata" >/dev/null

if [[ ! -d "$T6/appdata/opencode" ]]; then
  pass "appdata cleanup: fully-legacy APPDATA opencode directory removed"
else
  fail "appdata cleanup: fully-legacy APPDATA opencode directory removed"
fi

# ---------------------------------------------------------------------------
# Test 7: README documents the OpenCode installation path
# ---------------------------------------------------------------------------
if grep -q "install-opencode.sh" "$REPO_ROOT/README.md"; then
  pass "README documents the OpenCode installer"
else
  fail "README documents the OpenCode installer"
fi

printf '\ntest-opencode: %d passed, %d failed.\n' "$PASSES" "$FAILURES"
[[ "$FAILURES" -eq 0 ]]
