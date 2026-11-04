#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

fail() { echo "FAIL: $1" >&2; exit 1; }
pass() { echo "PASS: $1"; }

for installer in install.sh install-claude-code.sh install-opencode.sh install-vscode.sh; do
  if bash "$REPO_ROOT/scripts/$installer" --dry-run --check >"$TMP_ROOT/conflict.out" 2>&1; then
    fail "$installer rejects --dry-run with --check"
  fi
  grep -Fq "cannot be combined" "$TMP_ROOT/conflict.out" || fail "$installer reports the check/dry-run conflict"
  pass "$installer rejects --dry-run with --check"
done

CLAUDE_HOME="$TMP_ROOT/claude-home"
mkdir -p "$CLAUDE_HOME/.claude"
printf '#==ADAPTIVE_AGENTS_START==\n@%s/AGENTS.md\n#==ADAPTIVE_AGENTS_END==\n' "$REPO_ROOT" > "$CLAUDE_HOME/.claude/CLAUDE.md"
printf '{"permissions":{"additionalDirectories":["%s"]}}\n' "$REPO_ROOT" > "$CLAUDE_HOME/.claude/settings.json"
HOME="$CLAUDE_HOME" bash "$REPO_ROOT/scripts/install-claude-code.sh" --check >"$TMP_ROOT/claude.out" || fail "Claude structured check"
grep -Fq 'PASS: Claude Code entrypoint' "$TMP_ROOT/claude.out" || fail "Claude structured check output"
pass "Claude structured check accepts the managed entrypoint and grant"

OPEN_CONFIG="$TMP_ROOT/opencode.json"
printf '{"instructions":["%s/AGENTS.md"],"permission":{"external_directory":{"%s/**":"allow"}}}\n' "$REPO_ROOT" "$REPO_ROOT" > "$OPEN_CONFIG"
HOME="$TMP_ROOT/opencode-home" bash "$REPO_ROOT/scripts/install-opencode.sh" --opencode-config "$OPEN_CONFIG" --check >"$TMP_ROOT/opencode.out" || fail "OpenCode structured check"
grep -Fq 'PASS: OpenCode configuration' "$TMP_ROOT/opencode.out" || fail "OpenCode structured check output"
pass "OpenCode structured check accepts the managed entrypoint and grant"

echo "Installer check-mode tests: all passed."
