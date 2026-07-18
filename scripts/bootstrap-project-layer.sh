#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/bootstrap-project-layer.sh [options]

Options:
  --target PATH          Project directory. Default: current Git root or directory.
  --project-name NAME    Project display name. Required.
  --active-plan-id ID    Initial ID in PL-YYYYMMDD format (or legacy PL-YYYYMMDDTHHMMSSZ, PL-####). Default: auto-generated from current date.
  --active-title TITLE   Initial active plan title. Required.
  --persistence MODE     tracked, local-exclude, or gitignore. Required.
  --dry-run              Preview changes without writing files.
  -h, --help             Show this help.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_ROOT="$REPO_ROOT/templates/project-layer"
TARGET=""
PROJECT_NAME=""
ACTIVE_PLAN_ID="$(date -u +PL-%Y%m%d 2>/dev/null || echo 'PL-19700101')"
ACTIVE_TITLE=""
PERSISTENCE=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    --project-name)
      PROJECT_NAME="${2:-}"
      shift 2
      ;;
    --active-plan-id)
      ACTIVE_PLAN_ID="${2:-}"
      shift 2
      ;;
    --active-title)
      ACTIVE_TITLE="${2:-}"
      shift 2
      ;;
    --persistence)
      PERSISTENCE="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
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

if [[ -z "$TARGET" ]]; then
  TARGET="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi

if [[ -z "$PROJECT_NAME" || -z "$ACTIVE_TITLE" || -z "$PERSISTENCE" ]]; then
  echo "ERROR: --project-name, --active-title, and --persistence are required." >&2
  usage
  exit 1
fi

if [[ ! "$ACTIVE_PLAN_ID" =~ ^PL-[0-9]{8}$ && ! "$ACTIVE_PLAN_ID" =~ ^PL-[0-9]{8}T[0-9]{6}Z$ && ! "$ACTIVE_PLAN_ID" =~ ^PL-[0-9]{4}$ ]]; then
  echo "ERROR: --active-plan-id must match PL-YYYYMMDD (or legacy PL-YYYYMMDDTHHMMSSZ, PL-####)." >&2
  exit 1
fi

case "$PERSISTENCE" in
  tracked|local-exclude|gitignore)
    ;;
  *)
    echo "ERROR: --persistence must be tracked, local-exclude, or gitignore." >&2
    exit 1
    ;;
esac

if [[ ! -d "$TARGET" ]]; then
  echo "ERROR: Target directory does not exist: $TARGET" >&2
  exit 1
fi

TARGET="$(cd "$TARGET" && pwd)"
LAYER_ROOT="$TARGET/.adaptive-agents"

if [[ -d "$LAYER_ROOT" ]]; then
  if [[ ! -f "$LAYER_ROOT/project-layer.json" || ! -f "$LAYER_ROOT/scripts/check-project-layer.sh" ]]; then
    echo "ERROR: $LAYER_ROOT exists but is not a recognized Project Layer; refusing to overwrite it." >&2
    exit 1
  fi
  echo "Project Layer already exists; validating without changing authored content."
  bash "$LAYER_ROOT/scripts/check-project-layer.sh"
  exit 0
fi

GIT_ROOT="$(git -C "$TARGET" rev-parse --show-toplevel 2>/dev/null || true)"
GIT_PREFIX="$(git -C "$TARGET" rev-parse --show-prefix 2>/dev/null || true)"
if [[ "$PERSISTENCE" != "tracked" && -z "$GIT_ROOT" ]]; then
  echo "ERROR: Persistence mode '$PERSISTENCE' requires a Git repository." >&2
  exit 1
fi

if [[ "$PERSISTENCE" == "gitignore" && -n "$GIT_PREFIX" ]]; then
  echo "ERROR: gitignore mode requires --target to be the Git repository root." >&2
  exit 1
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[dry-run] Would create: $LAYER_ROOT"
  echo "[dry-run] Template version: $(python -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["templateVersion"])' "$TEMPLATE_ROOT/template.json" 2>/dev/null || echo unknown)"
  echo "[dry-run] Project: $PROJECT_NAME"
  echo "[dry-run] Adaptive Agents home: $REPO_ROOT"
  echo "[dry-run] Active plan: $ACTIVE_PLAN_ID: $ACTIVE_TITLE"
  case "$PERSISTENCE" in
    tracked)
      echo "[dry-run] Would leave .adaptive-agents available for source control."
      ;;
    local-exclude)
      echo "[dry-run] Would add /.adaptive-agents/ to the clone-local Git exclude file."
      ;;
    gitignore)
      echo "[dry-run] Would add /.adaptive-agents/ to $TARGET/.gitignore."
      ;;
  esac
  exit 0
fi

find_python() {
  if command -v python3 >/dev/null 2>&1 && python3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
  elif command -v python >/dev/null 2>&1 && python --version >/dev/null 2>&1; then
    PYTHON_CMD=(python)
  elif command -v py >/dev/null 2>&1 && py -3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
  else
    echo "ERROR: Python 3 is required to render the Project Layer template." >&2
    exit 1
  fi
}

find_python

"${PYTHON_CMD[@]}" - "$TEMPLATE_ROOT" "$TARGET" "$PROJECT_NAME" "$ACTIVE_PLAN_ID" "$ACTIVE_TITLE" "$REPO_ROOT" <<'PY'
import json
import re
import shutil
import sys
from pathlib import Path

template_root = Path(sys.argv[1])
target = Path(sys.argv[2])
project_name, active_plan_id, active_title, adaptive_agents_home_arg = sys.argv[3:7]
manifest = json.loads((template_root / "template.json").read_text(encoding="utf-8"))
source = template_root / manifest["layerDirectory"]
destination = target / manifest["layerDirectory"]
adaptive_agents_home = Path(adaptive_agents_home_arg).resolve().as_posix()

active_slug = re.sub(r"[^a-z0-9]+", "-", active_title.lower()).strip("-")
if not active_slug:
  print("ERROR: --active-title must contain at least one letter or number.", file=sys.stderr)
  sys.exit(1)
active_work_id = f"{active_plan_id}-{active_slug}"

replacements = {
    "{{TEMPLATE_VERSION}}": manifest["templateVersion"],
    "{{PROJECT_NAME}}": project_name,
    "{{ADAPTIVE_AGENTS_HOME}}": adaptive_agents_home,
    "{{ACTIVE_PLAN_ID}}": active_plan_id,
    "{{ACTIVE_PLAN_TITLE}}": active_title,
    "{{ACTIVE_WORK_ID}}": active_work_id,
}

shutil.copytree(source, destination)
for path in destination.rglob("*"):
    if not path.is_file() or path.suffix not in {".md", ".json", ".sh"}:
        continue
    text = path.read_text(encoding="utf-8")
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)
    path.write_text(text, encoding="utf-8", newline="\n")

for path in sorted(path for path in destination.rglob("*") if path.is_file()):
    rendered_name = path.name
    for placeholder, value in replacements.items():
        rendered_name = rendered_name.replace(placeholder, value)
    if rendered_name != path.name:
        path.rename(path.with_name(rendered_name))

(destination / "scripts/check-project-layer.sh").chmod(0o755)
PY

append_if_missing() {
  local file="$1"
  local line="$2"
  mkdir -p "$(dirname "$file")"
  touch "$file"
  if ! grep -Fqx -- "$line" "$file"; then
    printf '\n%s\n' "$line" >> "$file"
  fi
}

case "$PERSISTENCE" in
  tracked)
    ;;
  local-exclude)
    EXCLUDE_FILE="$(git -C "$TARGET" rev-parse --path-format=absolute --git-path info/exclude)"
    append_if_missing "$EXCLUDE_FILE" "/.adaptive-agents/"
    ;;
  gitignore)
    append_if_missing "$TARGET/.gitignore" "/.adaptive-agents/"
    ;;
esac

bash "$LAYER_ROOT/scripts/check-project-layer.sh"
echo "Created Project Layer: $LAYER_ROOT"