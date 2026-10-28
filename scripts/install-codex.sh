#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/install-codex.sh [--dry-run | --check]

Install canonical Adaptive Agents guidance and a repository-scoped Codex
workspace-write grant plus the managed Total Recall runtime for local
ChatGPT Codex clients.
EOF
}

DRY_RUN=0
CHECK_ONLY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --check) CHECK_ONLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done
if [[ "$DRY_RUN" -eq 1 && "$CHECK_ONLY" -eq 1 ]]; then
  echo "ERROR: --dry-run and --check cannot be combined." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
if command -v cygpath >/dev/null 2>&1; then
  REPO_ROOT="$(cygpath -u "$REPO_ROOT")"
fi
if [[ -n "${CODEX_HOME:-}" ]]; then
  CODEX_DIR="$CODEX_HOME"
  if command -v cygpath >/dev/null 2>&1 && [[ "$CODEX_DIR" == [A-Za-z]:* ]]; then
    CODEX_DIR="$(cygpath -u "$CODEX_DIR")"
  fi
elif [[ "${OS:-}" == "Windows_NT" || "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* ]]; then
  if command -v cygpath >/dev/null 2>&1; then
    CODEX_DIR="$(cygpath -u "${USERPROFILE:?USERPROFILE is required on Windows}")/.codex"
  else
    echo "ERROR: cygpath is required to resolve the native Windows Codex home." >&2
    exit 1
  fi
else
  CODEX_DIR="${HOME:?HOME is required}/.codex"
fi
if [[ "${OS:-}" == "Windows_NT" || "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* ]]; then
  ADAPTIVE_HOME="${USERPROFILE:?USERPROFILE is required on Windows}"
  if command -v cygpath >/dev/null 2>&1; then
    ADAPTIVE_HOME="$(cygpath -u "$ADAPTIVE_HOME")"
  else
    echo "ERROR: cygpath is required to resolve the native Windows user home." >&2
    exit 1
  fi
else
  ADAPTIVE_HOME="${HOME:?HOME is required}"
fi
CONFIG="$CODEX_DIR/config.toml"
GLOBAL="$CODEX_DIR/AGENTS.md"
OVERRIDE="$CODEX_DIR/AGENTS.override.md"
HOOKS="$CODEX_DIR/hooks.json"
SESSION_ROOT="$ADAPTIVE_HOME/.adaptive-agents/sessions/codex"
RUNTIME_ROOT="$ADAPTIVE_HOME/.adaptive-agents/codex/total-recall"

if [[ -e "$OVERRIDE" || -L "$OVERRIDE" ]]; then
  echo "ERROR: $OVERRIDE takes precedence over AGENTS.md. Preserve it and resolve the Codex global-instructions conflict manually." >&2
  exit 1
fi
PYTHON=""
for candidate in python3 python py; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import tomllib' >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done
if [[ -z "$PYTHON" ]]; then
  echo "ERROR: Python 3.11 or newer (with tomllib) is required to safely merge Codex config.toml." >&2
  exit 1
fi
PYTHON_EXECUTABLE="$("$PYTHON" -c 'import sys; print(sys.executable)')"

"$PYTHON" "$SCRIPT_DIR/codex_config.py" --config "$CONFIG" --repo-root "$REPO_ROOT" \
  --session-root "$SESSION_ROOT" --global-instructions "$GLOBAL"
"$PYTHON" "$SCRIPT_DIR/codex_hooks_config.py" --config "$HOOKS" \
  --script "$RUNTIME_ROOT/launcher.py" --python "$PYTHON_EXECUTABLE" --toml-config "$CONFIG"
RUNTIME_PLAN="$("$PYTHON" "$SCRIPT_DIR/codex_total_recall_installer.py" --runtime-root "$RUNTIME_ROOT" \
  --adapter-source "$SCRIPT_DIR/codex_total_recall.py" \
  --launcher-source "$SCRIPT_DIR/codex_total_recall_launcher.py" \
  --python-executable "$PYTHON_EXECUTABLE" --adaptive-agents-root "$REPO_ROOT")"

if [[ "$CHECK_ONLY" -eq 1 ]]; then
  "$PYTHON" "$SCRIPT_DIR/codex_config.py" --config "$CONFIG" --repo-root "$REPO_ROOT" \
    --session-root "$SESSION_ROOT" --check --global-instructions "$GLOBAL"
  "$PYTHON" "$SCRIPT_DIR/codex_hooks_config.py" --config "$HOOKS" \
    --script "$RUNTIME_ROOT/launcher.py" --python "$PYTHON_EXECUTABLE" \
    --toml-config "$CONFIG" --check
  "$PYTHON" "$SCRIPT_DIR/codex_total_recall_installer.py" --runtime-root "$RUNTIME_ROOT" \
    --adapter-source "$SCRIPT_DIR/codex_total_recall.py" \
    --launcher-source "$SCRIPT_DIR/codex_total_recall_launcher.py" \
    --python-executable "$PYTHON_EXECUTABLE" --adaptive-agents-root "$REPO_ROOT" --check
  echo "Codex Total Recall installation is healthy."
  exit 0
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[dry-run] Would write a redirect at $GLOBAL to $REPO_ROOT/AGENTS.md"
  echo "[dry-run] Would grant workspace-write access to $REPO_ROOT and $SESSION_ROOT"
  echo "[dry-run] $RUNTIME_PLAN"
  echo "[dry-run] Would install Total Recall hooks at $HOOKS"
  exit 0
fi

BACKUP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-install-backup.XXXXXX")"
ROLLBACK_ENABLED=0
snapshot_file() {
  local key="$1"
  local path="$2"
  if [[ -e "$path" || -L "$path" ]]; then
    cp -a -- "$path" "$BACKUP_DIR/$key"
    printf 'present\n' > "$BACKUP_DIR/$key.state"
  else
    printf 'absent\n' > "$BACKUP_DIR/$key.state"
  fi
}
restore_file() {
  local key="$1"
  local path="$2"
  if [[ "$(cat "$BACKUP_DIR/$key.state")" == "present" ]]; then
    rm -f -- "$path"
    mkdir -p "$(dirname "$path")"
    cp -a -- "$BACKUP_DIR/$key" "$path"
  else
    rm -f -- "$path"
  fi
}
finish_install() {
  local status="$?"
  if [[ "$status" -ne 0 && "$ROLLBACK_ENABLED" -eq 1 ]]; then
    restore_file codex-config "$CONFIG"
    restore_file global-instructions "$GLOBAL"
    restore_file hooks "$HOOKS"
    restore_file runtime-active "$RUNTIME_ROOT/active.json"
    restore_file runtime-launcher "$RUNTIME_ROOT/launcher.py"
  fi
  rm -rf -- "$BACKUP_DIR"
  exit "$status"
}
trap finish_install EXIT
snapshot_file codex-config "$CONFIG"
snapshot_file global-instructions "$GLOBAL"
snapshot_file hooks "$HOOKS"
snapshot_file runtime-active "$RUNTIME_ROOT/active.json"
snapshot_file runtime-launcher "$RUNTIME_ROOT/launcher.py"
ROLLBACK_ENABLED=1

"$PYTHON" "$SCRIPT_DIR/codex_total_recall_installer.py" --runtime-root "$RUNTIME_ROOT" \
  --adapter-source "$SCRIPT_DIR/codex_total_recall.py" \
  --launcher-source "$SCRIPT_DIR/codex_total_recall_launcher.py" \
  --python-executable "$PYTHON_EXECUTABLE" --adaptive-agents-root "$REPO_ROOT" --apply
if [[ ! -e "$GLOBAL" && ! -L "$GLOBAL" ]]; then
  "$PYTHON" "$SCRIPT_DIR/codex_config.py" --config "$CONFIG" --repo-root "$REPO_ROOT" \
    --global-instructions "$GLOBAL" --install-instructions
fi
"$PYTHON" "$SCRIPT_DIR/codex_config.py" --config "$CONFIG" --repo-root "$REPO_ROOT" \
  --session-root "$SESSION_ROOT" --apply
"$PYTHON" "$SCRIPT_DIR/codex_hooks_config.py" --config "$HOOKS" \
  --script "$RUNTIME_ROOT/launcher.py" --python "$PYTHON_EXECUTABLE" \
  --toml-config "$CONFIG" --apply
"$PYTHON" "$SCRIPT_DIR/codex_config.py" --config "$CONFIG" --repo-root "$REPO_ROOT" \
  --session-root "$SESSION_ROOT" --check --global-instructions "$GLOBAL"
"$PYTHON" "$SCRIPT_DIR/codex_hooks_config.py" --config "$HOOKS" \
  --script "$RUNTIME_ROOT/launcher.py" --python "$PYTHON_EXECUTABLE" \
  --toml-config "$CONFIG" --check
"$PYTHON" "$SCRIPT_DIR/codex_total_recall_installer.py" --runtime-root "$RUNTIME_ROOT" \
  --adapter-source "$SCRIPT_DIR/codex_total_recall.py" \
  --launcher-source "$SCRIPT_DIR/codex_total_recall_launcher.py" \
  --python-executable "$PYTHON_EXECUTABLE" --adaptive-agents-root "$REPO_ROOT" --check
ROLLBACK_ENABLED=0
trap - EXIT
rm -rf -- "$BACKUP_DIR"
echo "Codex integration installed for this shared local Codex home: $CODEX_DIR"
