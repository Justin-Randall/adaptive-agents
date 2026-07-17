#!/usr/bin/env bash
# migrate-project-layer-retrospectives.sh
#
# Converts a Project Layer's retrospective directory from the old flat-inbox
# layout (all statuses mixed in inbox/) to a sibling-directory layout where
# each note lives in the directory matching its status.
#
# Usage: bash scripts/migrate-project-layer-retrospectives.sh [project-layer-root]
#
# If project-layer-root is omitted, defaults to $PWD/.adaptive-agents

set -euo pipefail

LAYER_ROOT="${1:-$PWD/.adaptive-agents}"
RETRO_DIR="$LAYER_ROOT/retrospectives"
MOVED=0
CREATED=0

# Status-to-directory mapping
status_dir() {
  case "$1" in
    Promoted)  echo "promoted" ;;
    Deferred)  echo "deferred" ;;
    Rejected)  echo "rejected" ;;
    Captured)  echo "" ;;
    *)         echo "" ;;
  esac
}

if [[ ! -d "$RETRO_DIR/inbox" ]]; then
  echo "No retrospectives/inbox/ found at $RETRO_DIR — nothing to migrate."
  exit 0
fi

# Create sibling directories if missing
for dir in promoted deferred rejected; do
  if [[ ! -d "$RETRO_DIR/$dir" ]]; then
    mkdir -p "$RETRO_DIR/$dir"
    echo "Created $RETRO_DIR/$dir/"
    CREATED=$((CREATED + 1))
  fi
done

# Move notes whose status does not match Captured
shopt -s nullglob
for note in "$RETRO_DIR/inbox"/*.md; do
  basename="$(basename "$note")"
  case "$basename" in
    README.md|template.md|INDEX.md) continue ;;
  esac

  status="$(grep -Em1 '^- Status: ' "$note" | sed 's/^- Status: *//' || true)"
  target_dir="$(status_dir "$status")"

  if [[ -z "$target_dir" ]]; then
    # Captured or unknown — leave in inbox
    continue
  fi

  if [[ -f "$RETRO_DIR/$target_dir/$basename" ]]; then
    echo "Already exists at $RETRO_DIR/$target_dir/$basename — skipping"
    continue
  fi

  mv "$note" "$RETRO_DIR/$target_dir/$basename"
  echo "Moved $basename ($status) → $target_dir/"
  MOVED=$((MOVED + 1))
done
shopt -u nullglob

# Create retrospective routing INDEX.md if missing
INDEX_FILE="$RETRO_DIR/INDEX.md"
if [[ ! -f "$INDEX_FILE" ]]; then
  cat > "$INDEX_FILE" <<'INDEXEOF'
# Project Retrospectives

Project retrospectives capture learning whose intended behavior may be specific to this project.

| Directory | Status | Purpose |
| --- | --- | --- |
| [inbox/](inbox/) | Captured | Notes awaiting initial triage |
| [promoted/](promoted/) | Promoted | Lessons applied to durable guidance |
| [deferred/](deferred/) | Deferred | Set aside for later re-evaluation |
| [rejected/](rejected/) | Rejected | Considered and declined |

- Read the [inbox rules](inbox/README.md).
- Create notes from the [retrospective template](inbox/template.md).
- After triage, move the note to the matching sibling directory and update its status.
INDEXEOF
  echo "Created $INDEX_FILE"
  CREATED=$((CREATED + 1))
fi

# Create rejected/INDEX.md if missing
REJECTED_INDEX="$RETRO_DIR/rejected/INDEX.md"
if [[ ! -f "$REJECTED_INDEX" ]]; then
  cat > "$REJECTED_INDEX" <<'REJEOF'
# Rejected Project Retrospectives

This directory stores project retrospectives whose triage decision was `Rejected`. Notes are retained per the "do not delete" principle so the same lesson is not re-proposed without new evidence.

## Current Notes

None yet.
REJEOF
  echo "Created $REJECTED_INDEX"
  CREATED=$((CREATED + 1))
fi

echo "Done: $MOVED note(s) moved, $CREATED file(s) created."
