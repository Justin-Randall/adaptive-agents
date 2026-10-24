#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cygpath -u "$(git rev-parse --show-toplevel)")"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

FAKE_REPO="$TMP_ROOT/repo with spaces"
FAKE_HOME="$TMP_ROOT/codex home"
FAKE_BIN="$TMP_ROOT/bin"
INSTALLER="$FAKE_REPO/scripts/install-codex.sh"
CONFIG_HELPER="$FAKE_REPO/scripts/codex_config.py"
PASSES=0
FAILURES=0

pass() { PASSES=$((PASSES + 1)); echo "PASS: $1"; }
fail() { FAILURES=$((FAILURES + 1)); echo "FAIL: $1"; }

mkdir -p "$FAKE_REPO/scripts" "$FAKE_HOME" "$FAKE_BIN"
cp "$REPO_ROOT/scripts/install-codex.sh" "$INSTALLER"
cp "$REPO_ROOT/scripts/codex_config.py" "$CONFIG_HELPER"
printf '# Adaptive Agents test fixture\n' > "$FAKE_REPO/AGENTS.md"
printf '# Test index\n' > "$FAKE_REPO/INDEX.md"

run_installer() {
  CODEX_HOME="$1" HOME="$TMP_ROOT/home" USERPROFILE="$TMP_ROOT/windows-home" \
    bash "$INSTALLER" "${@:2}"
}

echo "=== Test 1: Fresh install creates the global symlink and narrow permission grant ==="
mkdir -p "$FAKE_HOME/fresh"
printf 'approval_policy = "on-request"\n' > "$FAKE_HOME/fresh/config.toml"
if run_installer "$FAKE_HOME/fresh" > "$TMP_ROOT/fresh.out" 2>&1; then
  if [[ -L "$FAKE_HOME/fresh/AGENTS.md" ]] &&
     [[ "$(readlink -f "$FAKE_HOME/fresh/AGENTS.md")" == "$(readlink -f "$FAKE_REPO/AGENTS.md")" ]]; then
    pass "fresh install links the canonical AGENTS.md"
  else
    fail "fresh install did not create a symlink to the canonical AGENTS.md"
  fi
  if python - "$FAKE_HOME/fresh/config.toml" "$FAKE_REPO" <<'PY'
import sys
import tomllib
from pathlib import Path

config = tomllib.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
repo = Path(sys.argv[2]).resolve().as_posix()
assert config["approval_policy"] == "on-request"
roots = config["sandbox_workspace_write"]["writable_roots"]
assert roots == [repo], roots
PY
  then
    pass "fresh install grants only the repository and preserves approval policy"
  else
    fail "fresh install config is invalid or changed unrelated policy"
  fi
else
  fail "fresh install failed: $(cat "$TMP_ROOT/fresh.out")"
fi

if python "$CONFIG_HELPER" --config "$FAKE_HOME/fresh/config.toml" --repo-root "$FAKE_REPO" --check --global-instructions "$FAKE_HOME/fresh/AGENTS.md" >/dev/null 2>&1; then
  pass "health-check contract accepts the canonical entrypoint and repository grant"
else
  fail "health-check contract rejected a valid Codex install"
fi

echo "=== Test 2: Dry-run previews without writing ==="
mkdir -p "$FAKE_HOME/dry-run"
if run_installer "$FAKE_HOME/dry-run" --dry-run > "$TMP_ROOT/dry-run.out" 2>&1 &&
   [[ ! -e "$FAKE_HOME/dry-run/AGENTS.md" ]] &&
   [[ ! -e "$FAKE_HOME/dry-run/config.toml" ]] &&
   grep -q "dry-run" "$TMP_ROOT/dry-run.out"; then
  pass "dry-run previews actions and leaves the Codex home unchanged"
else
  fail "dry-run wrote files or omitted its preview"
fi

echo "=== Test 3: Rerun is byte-stable ==="
cp "$FAKE_HOME/fresh/config.toml" "$TMP_ROOT/config.before"
run_installer "$FAKE_HOME/fresh" > "$TMP_ROOT/rerun.out" 2>&1
if cmp -s "$TMP_ROOT/config.before" "$FAKE_HOME/fresh/config.toml" &&
   [[ "$(readlink -f "$FAKE_HOME/fresh/AGENTS.md")" == "$(readlink -f "$FAKE_REPO/AGENTS.md")" ]]; then
  pass "rerun leaves config byte-stable and retains the canonical symlink"
else
  fail "rerun changed Codex config or the canonical symlink"
fi

echo "=== Test 3b: Duplicate existing grants are not expanded ==="
mkdir -p "$FAKE_HOME/duplicate-grant"
repo_root_toml="$(python -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve().as_posix())' "$FAKE_REPO")"
printf '[sandbox_workspace_write]\nwritable_roots = ["%s", "%s"]\n' "$repo_root_toml" "$repo_root_toml" > "$FAKE_HOME/duplicate-grant/config.toml"
cp "$FAKE_HOME/duplicate-grant/config.toml" "$TMP_ROOT/duplicate.before"
if run_installer "$FAKE_HOME/duplicate-grant" > "$TMP_ROOT/duplicate.out" 2>&1 &&
   cmp -s "$TMP_ROOT/duplicate.before" "$FAKE_HOME/duplicate-grant/config.toml"; then
  pass "pre-existing duplicate grants are left byte-stable without adding another entry"
else
  fail "installer expanded or rewrote pre-existing duplicate grants"
fi

echo "=== Test 4: Existing permission roots and comments are preserved ==="
mkdir -p "$FAKE_HOME/existing-grant"
cat > "$FAKE_HOME/existing-grant/config.toml" <<'EOF'
model = "test-model"
approval_policy = "on-request"

[sandbox_workspace_write]
# Keep the user's extra writable path.
writable_roots = [
  "C:/existing/path", # Retain this user's existing root.
]
network_access = false
EOF
if run_installer "$FAKE_HOME/existing-grant" > "$TMP_ROOT/existing-grant.out" 2>&1 &&
   python - "$FAKE_HOME/existing-grant/config.toml" "$FAKE_REPO" <<'PY'
import sys
import tomllib
from pathlib import Path

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
config = tomllib.loads(raw)
roots = config["sandbox_workspace_write"]["writable_roots"]
repo = Path(sys.argv[2]).resolve().as_posix()
assert roots == ["C:/existing/path", repo], roots
assert config["model"] == "test-model"
assert config["approval_policy"] == "on-request"
assert config["sandbox_workspace_write"]["network_access"] is False
assert "# Keep the user's extra writable path." in raw
assert "# Retain this user's existing root." in raw
PY
then
  pass "existing permission values, comments, and unrelated keys survive"
else
  fail "existing config merge failed or lost user values"
fi

echo "=== Test 5: Existing user instruction files are preserved and block install ==="
for file_name in AGENTS.md AGENTS.override.md; do
  test_home="$FAKE_HOME/user-file-$file_name"
  mkdir -p "$test_home"
  printf 'user-authored guidance\n' > "$test_home/$file_name"
  if run_installer "$test_home" > "$TMP_ROOT/user-file.out" 2>&1; then
    fail "installer replaced or ignored existing $file_name"
  elif [[ "$(cat "$test_home/$file_name")" == "user-authored guidance" ]] &&
       [[ ! -e "$test_home/config.toml" ]]; then
    pass "existing $file_name is preserved and install stops before config changes"
  else
    fail "installer changed Codex config after detecting existing $file_name"
  fi
done

echo "=== Test 6: Unsupported permission profiles fail without mutation ==="
mkdir -p "$FAKE_HOME/custom-profile"
cat > "$FAKE_HOME/custom-profile/config.toml" <<'EOF'
default_permissions = "custom"
approval_policy = "on-request"

[permissions.custom]
extends = ":workspace"
EOF
cp "$FAKE_HOME/custom-profile/config.toml" "$TMP_ROOT/profile.before"
if run_installer "$FAKE_HOME/custom-profile" > "$TMP_ROOT/profile.out" 2>&1; then
  fail "installer silently changed or ignored the active custom permission profile"
elif cmp -s "$TMP_ROOT/profile.before" "$FAKE_HOME/custom-profile/config.toml" &&
     [[ ! -e "$FAKE_HOME/custom-profile/AGENTS.md" ]]; then
  pass "custom profile is preserved and rejected before any install mutation"
else
  fail "custom profile conflict caused partial changes"
fi

echo "=== Test 7: Read-only sandbox fails without mutation ==="
mkdir -p "$FAKE_HOME/read-only"
printf 'sandbox_mode = "read-only"\n' > "$FAKE_HOME/read-only/config.toml"
cp "$FAKE_HOME/read-only/config.toml" "$TMP_ROOT/read-only.before"
if run_installer "$FAKE_HOME/read-only" > "$TMP_ROOT/read-only.out" 2>&1; then
  fail "installer changed or ignored read-only sandbox mode"
elif cmp -s "$TMP_ROOT/read-only.before" "$FAKE_HOME/read-only/config.toml" &&
     [[ ! -e "$FAKE_HOME/read-only/AGENTS.md" ]]; then
  pass "read-only mode is preserved and rejected before any install mutation"
else
  fail "read-only conflict caused partial changes"
fi

echo "=== Test 8: Invalid TOML fails without mutation ==="
mkdir -p "$FAKE_HOME/invalid"
printf '[sandbox_workspace_write\nwritable_roots = [\n' > "$FAKE_HOME/invalid/config.toml"
cp "$FAKE_HOME/invalid/config.toml" "$TMP_ROOT/invalid.before"
if run_installer "$FAKE_HOME/invalid" > "$TMP_ROOT/invalid.out" 2>&1; then
  fail "installer accepted malformed TOML"
elif cmp -s "$TMP_ROOT/invalid.before" "$FAKE_HOME/invalid/config.toml" &&
     [[ ! -e "$FAKE_HOME/invalid/AGENTS.md" ]]; then
  pass "malformed TOML is preserved and rejected before any install mutation"
else
  fail "malformed TOML conflict caused partial changes"
fi

echo "=== Test 9: Health check rejects missing grants and non-canonical entrypoints ==="
mkdir -p "$FAKE_HOME/health-missing-grant" "$FAKE_HOME/health-wrong-entry"
python - "$FAKE_REPO/AGENTS.md" "$FAKE_HOME/health-missing-grant/AGENTS.md" <<'PY'
import os
import sys
os.symlink(sys.argv[1], sys.argv[2])
PY
printf '[sandbox_workspace_write]\nwritable_roots = []\n' > "$FAKE_HOME/health-missing-grant/config.toml"
if python "$CONFIG_HELPER" --config "$FAKE_HOME/health-missing-grant/config.toml" --repo-root "$FAKE_REPO" --check --global-instructions "$FAKE_HOME/health-missing-grant/AGENTS.md" >/dev/null 2>&1; then
  fail "health check accepted a missing repository permission grant"
else
  pass "health check rejects a missing repository permission grant"
fi
python - "$FAKE_HOME/user-other-AGENTS.md" "$FAKE_HOME/health-wrong-entry/AGENTS.md" <<'PY'
import os
import sys
from pathlib import Path
Path(sys.argv[1]).write_text("user guidance\n", encoding="utf-8")
os.symlink(sys.argv[1], sys.argv[2])
PY
printf '[sandbox_workspace_write]\nwritable_roots = [%s]\n' "$(python -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve().as_posix())' "$FAKE_REPO")" > "$FAKE_HOME/health-wrong-entry/config.toml"
if python "$CONFIG_HELPER" --config "$FAKE_HOME/health-wrong-entry/config.toml" --repo-root "$FAKE_REPO" --check --global-instructions "$FAKE_HOME/health-wrong-entry/AGENTS.md" >/dev/null 2>&1; then
  fail "health check accepted a non-canonical global entrypoint"
else
  pass "health check rejects a non-canonical global entrypoint"
fi

echo "=== Test 10: Platform default Codex home is resolved without CODEX_HOME ==="
if command -v cygpath >/dev/null 2>&1; then
  DEFAULT_PROFILE="$TMP_ROOT/windows profile"
  mkdir -p "$DEFAULT_PROFILE"
  expected_home="$(cygpath -u "$DEFAULT_PROFILE")/.codex"
  if env -u CODEX_HOME USERPROFILE="$DEFAULT_PROFILE" HOME="$TMP_ROOT/ignored-home" bash "$INSTALLER" --dry-run > "$TMP_ROOT/windows-default.out" 2>&1 &&
     grep -Fq "$expected_home" "$TMP_ROOT/windows-default.out"; then
    pass "native Windows default resolves from USERPROFILE"
  else
    fail "native Windows default did not resolve from USERPROFILE"
  fi
else
  DEFAULT_HOME="$TMP_ROOT/unix home"
  mkdir -p "$DEFAULT_HOME"
  if env -u CODEX_HOME HOME="$DEFAULT_HOME" USERPROFILE="$TMP_ROOT/ignored-windows-home" bash "$INSTALLER" --dry-run > "$TMP_ROOT/unix-default.out" 2>&1 &&
     grep -Fq "$DEFAULT_HOME/.codex" "$TMP_ROOT/unix-default.out"; then
    pass "Unix and WSL default resolves from HOME"
  else
    fail "Unix default did not resolve from HOME"
  fi
fi

echo
echo "=== Results: $PASSES passed, $FAILURES failed ==="
if [[ "$FAILURES" -gt 0 ]]; then exit 1; fi
