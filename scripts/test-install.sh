#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TMP_ROOT="$(mktemp -d -p "$REPO_ROOT")"
trap 'rm -rf "$TMP_ROOT"' EXIT

FAKE_REPO="$TMP_ROOT/repo"
FAKE_HOME="$TMP_ROOT/home"
FAKE_BIN="$TMP_ROOT/bin"
TEST_LOG="$TMP_ROOT/installers.log"
mkdir -p "$FAKE_REPO/scripts" "$FAKE_HOME/.claude" "$FAKE_BIN"
touch "$FAKE_REPO/AGENTS.md" "$FAKE_REPO/INDEX.md" "$FAKE_HOME/.claude/settings.json"
cp "$REPO_ROOT/scripts/install.sh" "$FAKE_REPO/scripts/install.sh"

cat > "$FAKE_REPO/scripts/install-claude-code.sh" <<'EOF'
#!/usr/bin/env bash
printf 'claude\n' >> "$TEST_LOG"
exit 7
EOF

cat > "$FAKE_REPO/scripts/install-vscode.sh" <<'EOF'
#!/usr/bin/env bash
printf 'vscode\n' >> "$TEST_LOG"
exit 0
EOF

cat > "$FAKE_BIN/code" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
chmod +x "$FAKE_BIN/code"

set +e
OUTPUT="$(HOME="$FAKE_HOME" PATH="$FAKE_BIN:/usr/bin:/bin" LOCALAPPDATA="" PROGRAMFILES="" PROGRAMFILES_X86="" TEST_LOG="$TEST_LOG" bash "$FAKE_REPO/scripts/install.sh" 2>&1)"
STATUS=$?
set -e

if [[ "$STATUS" -eq 0 ]]; then
  echo "FAIL: umbrella installer returned success despite a failed integration"
  exit 1
fi
if [[ "$(cat "$TEST_LOG")" != $'claude\nvscode' ]]; then
  echo "FAIL: umbrella installer did not continue after the first failure"
  printf '%s\n' "$OUTPUT"
  exit 1
fi
if [[ "$OUTPUT" != *"Failed integrations:"* || "$OUTPUT" != *"install-claude-code.sh"* ]]; then
  echo "FAIL: umbrella installer did not summarize the failed integration"
  printf '%s\n' "$OUTPUT"
  exit 1
fi

echo "PASS: umbrella installer continues after failures and returns aggregate failure"