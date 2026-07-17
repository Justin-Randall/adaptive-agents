#!/usr/bin/env bash
# session-start.sh
#
# Entry point for session-start probes. Iterates over scripts/session-start/*.sh
# in lexicographic order, runs each one, and collects all stdout.
#
# If any probe fails, emits a --- PROBE FAILURE section with the probe path,
# exit code, and stderr output so the model can inform the user and offer to
# create a backlog item.
#
# Always exits 0. Empty stdout means nothing to do. Non-empty stdout becomes
# instructions in context.
#
# Usage:
#   bash scripts/session-start.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROBES_DIR="$SCRIPT_DIR/session-start"

if [[ ! -d "$PROBES_DIR" ]]; then
  exit 0
fi

shopt -s nullglob
probes=("$PROBES_DIR"/*.sh)
shopt -u nullglob

if [[ ${#probes[@]} -eq 0 ]]; then
  exit 0
fi

# Run each probe in lexicographic order. Capture stdout and stderr separately.
# On failure, emit a diagnostic section for the model.
for probe in "${probes[@]}"; do
  if [[ ! -x "$probe" && ! -f "$probe" ]]; then
    continue
  fi

  stdout_file="$(mktemp)"
  stderr_file="$(mktemp)"
  exit_code=0
  bash "$probe" >"$stdout_file" 2>"$stderr_file" || exit_code=$?

  if [[ "$exit_code" -ne 0 ]]; then
    probe_stderr="$(cat "$stderr_file")"
    cat <<OUTPUT

--- PROBE FAILURE
A session-start probe failed. Inform the user and offer to create a backlog item.
Probe: ${probe}
Exit code: ${exit_code}
Stderr: ${probe_stderr:-no stderr output}

OUTPUT
  fi

  cat "$stdout_file"
  rm -f "$stdout_file" "$stderr_file"
done
