#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/install-codex.sh [--dry-run]

Install canonical Adaptive Agents guidance and a repository-scoped Codex
workspace-write grant for local ChatGPT Codex clients.
EOF
}

DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

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
CONFIG="$CODEX_DIR/config.toml"
GLOBAL="$CODEX_DIR/AGENTS.md"
OVERRIDE="$CODEX_DIR/AGENTS.override.md"

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

"$PYTHON" "$SCRIPT_DIR/codex_config.py" --config "$CONFIG" --repo-root "$REPO_ROOT" --global-instructions "$GLOBAL"
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[dry-run] Would write a redirect at $GLOBAL to $REPO_ROOT/AGENTS.md"
  echo "[dry-run] Would grant workspace-write access to $REPO_ROOT"
  exit 0
fi

mkdir -p "$CODEX_DIR"
if [[ ! -e "$GLOBAL" && ! -L "$GLOBAL" ]]; then
  "$PYTHON" "$SCRIPT_DIR/codex_config.py" --config "$CONFIG" --repo-root "$REPO_ROOT" \
    --global-instructions "$GLOBAL" --install-instructions
  CREATED_ENTRYPOINT=1
else
  CREATED_ENTRYPOINT=0
fi
if ! "$PYTHON" "$SCRIPT_DIR/codex_config.py" --config "$CONFIG" --repo-root "$REPO_ROOT" --apply; then
  if [[ "$CREATED_ENTRYPOINT" -eq 1 ]]; then rm -f -- "$GLOBAL"; fi
  exit 1
fi
echo "Codex integration installed for this shared local Codex home: $CODEX_DIR"
