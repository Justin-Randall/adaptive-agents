#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/inspect-project-layer-upgrade.sh [--target PATH]

Compares an existing Project Layer with the current canonical template.
This command is read-only and never applies upgrades.
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_ROOT="$REPO_ROOT/templates/project-layer"
TARGET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:-}"
      shift 2
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

TARGET="$(cd "$TARGET" && pwd)"
LAYER_ROOT="$TARGET/.adaptive-agents"
if [[ ! -f "$LAYER_ROOT/project-layer.json" ]]; then
  echo "ERROR: No recognized Project Layer at $LAYER_ROOT" >&2
  exit 1
fi

find_python() {
  if command -v python3 >/dev/null 2>&1 && python3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
  elif command -v python >/dev/null 2>&1 && python --version >/dev/null 2>&1; then
    PYTHON_CMD=(python)
  elif command -v py >/dev/null 2>&1 && py -3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
  else
    echo "ERROR: Python 3 is required to inspect Project Layer upgrades." >&2
    exit 1
  fi
}

find_python

"${PYTHON_CMD[@]}" - "$TEMPLATE_ROOT" "$LAYER_ROOT" <<'PY'
import json
import re
import sys
from pathlib import Path

template_root = Path(sys.argv[1]).resolve()
layer_root = Path(sys.argv[2]).resolve()
manifest = json.loads((template_root / "template.json").read_text(encoding="utf-8"))
metadata = json.loads((layer_root / "project-layer.json").read_text(encoding="utf-8"))
active_text = (layer_root / "planning/active/ACTIVE.md").read_text(encoding="utf-8")
if "No Active Plan" in active_text:
    print("Active plan is empty (no active work). Upgrade will proceed without active plan content.")
    active_match = None
else:
    active_match = re.search(r"^# ((?:PL-[0-9]{8}|PL-[0-9]{8}T[0-9]{6}Z|PL-[0-9]{4})): (.+)$", active_text, re.MULTILINE)
    if not active_match:
        print("ERROR: Cannot read the active plan ID and title.", file=sys.stderr)
        sys.exit(1)

if active_match:
    work_unit_match = re.search(r"^- Work Unit: (PL-[a-zA-Z0-9-]+)$", active_text, re.MULTILINE)
    active_work_id = work_unit_match.group(1) if work_unit_match else active_match.group(1)
    replacements = {
        "{{TEMPLATE_VERSION}}": manifest["templateVersion"],
        "{{PROJECT_NAME}}": metadata["projectName"],
        "{{ACTIVE_PLAN_ID}}": active_match.group(1),
        "{{ACTIVE_PLAN_TITLE}}": active_match.group(2),
        "{{ACTIVE_WORK_ID}}": active_work_id,
    }
else:
    replacements = {
        "{{TEMPLATE_VERSION}}": manifest["templateVersion"],
        "{{PROJECT_NAME}}": metadata["projectName"],
        "{{ACTIVE_PLAN_ID}}": "PL-19700101",
        "{{ACTIVE_PLAN_TITLE}}": "No active work",
        "{{ACTIVE_WORK_ID}}": "PL-19700101-no-active-work",
    }
source_root = template_root / manifest["layerDirectory"]
missing = []
changed = []
project_only = []

for source in sorted(path for path in source_root.rglob("*") if path.is_file()):
    relative = source.relative_to(source_root)
    rendered_relative = relative.as_posix()
    for placeholder, value in replacements.items():
        rendered_relative = rendered_relative.replace(placeholder, value)
    target = layer_root / rendered_relative
    if not target.exists():
        missing.append(rendered_relative)
        continue
    if source.suffix not in {".md", ".json", ".sh"}:
        continue
    expected = source.read_text(encoding="utf-8")
    for placeholder, value in replacements.items():
        expected = expected.replace(placeholder, value)
    actual = target.read_text(encoding="utf-8")
    if actual != expected:
      changed.append(rendered_relative)

source_paths = set()
for path in source_root.rglob("*"):
    if not path.is_file():
        continue
    rendered_relative = path.relative_to(source_root).as_posix()
    for placeholder, value in replacements.items():
        rendered_relative = rendered_relative.replace(placeholder, value)
    source_paths.add(Path(rendered_relative))
for target in sorted(path for path in layer_root.rglob("*") if path.is_file()):
    relative = target.relative_to(layer_root)
    if relative not in source_paths:
        project_only.append(relative.as_posix())

print(f"Installed template version: {metadata.get('templateVersion', 'unknown')}")
print(f"Canonical template version: {manifest['templateVersion']}")
for label, paths in (("Missing canonical paths", missing), ("Content requiring review", changed), ("Project-only paths", project_only)):
    print(f"\n{label}: {len(paths)}")
    for path in paths:
        print(f"- {path}")
PY