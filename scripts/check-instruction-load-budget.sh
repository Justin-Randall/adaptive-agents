#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' >/dev/null 2>&1; then
  PYTHON_CMD=(python3)
elif python -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' >/dev/null 2>&1; then
  PYTHON_CMD=(python)
elif py -3 -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' >/dev/null 2>&1; then
  PYTHON_CMD=(py -3)
else
  printf 'ERROR: Python 3.11 or newer is required.\n' >&2
  exit 1
fi

exec "${PYTHON_CMD[@]}" "$SCRIPT_DIR/check-instruction-load-budget.py" "$@"