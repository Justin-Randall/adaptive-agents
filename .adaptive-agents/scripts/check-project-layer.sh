#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAYER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

find_python() {
  if command -v python3 >/dev/null 2>&1 && python3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
  elif command -v python >/dev/null 2>&1 && python --version >/dev/null 2>&1; then
    PYTHON_CMD=(python)
  elif command -v py >/dev/null 2>&1 && py -3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
  else
    echo "ERROR: Python 3 is required by the Project Layer validator." >&2
    exit 1
  fi
}

find_python

"${PYTHON_CMD[@]}" - "$LAYER_ROOT" <<'PY'
import re
import sys
from collections import deque
from pathlib import Path

root = Path(sys.argv[1]).resolve()
failures = []
required = (
    "INDEX.md",
    "README.md",
    "instructions/INDEX.md",
    "instructions/project.instructions.md",
    "skills/INDEX.md",
    "skills/manage-planning/SKILL.md",
    "skills/manage-retrospectives/SKILL.md",
    "memory/INDEX.md",
    "retrospectives/INDEX.md",
    "retrospectives/inbox/README.md",
    "retrospectives/inbox/template.md",
    "planning/INDEX.md",
    "planning/active/ACTIVE.md",
    "planning/active/MEMORY.md",
    "planning/backlog/INDEX.md",
    "planning/closed/INDEX.md",
    "playbooks/INDEX.md",
    "playbooks/end-work.md",
    "scripts/README.md",
    "scripts/check-project-layer.sh",
)

for relative in required:
    if not (root / relative).exists():
        failures.append(f"missing required path: {relative}")

link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
graph = {}

for source in sorted(root.rglob("*.md")):
    graph.setdefault(source, set())
    text = source.read_text(encoding="utf-8")
    for raw_target in link_pattern.findall(text):
        target = raw_target.strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean_target = target.split("#", 1)[0]
        resolved = (source.parent / clean_target).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            failures.append(f"{source.relative_to(root).as_posix()}: link escapes Project Layer: {target}")
            continue
        if not resolved.exists():
            failures.append(f"{source.relative_to(root).as_posix()}: missing link target: {target}")
        elif resolved.suffix == ".md":
            graph[source].add(resolved)

entrypoint = root / "INDEX.md"
reachable = set()
queue = deque([entrypoint])
while queue:
    current = queue.popleft()
    if current in reachable:
        continue
    reachable.add(current)
    queue.extend(graph.get(current, ()))

for markdown in sorted(root.rglob("*.md")):
    if markdown not in reachable:
        failures.append(f"orphan Markdown file: {markdown.relative_to(root).as_posix()}")

active_text = (root / "planning/active/ACTIVE.md").read_text(encoding="utf-8") if (root / "planning/active/ACTIVE.md").exists() else ""
active_match = re.search(r"^# ((?:PL-[0-9]{8}T[0-9]{6}Z|PL-[0-9]{4})|\{\{ACTIVE_PLAN_ID\}\}): (.+)$", active_text, re.MULTILINE)
if not active_match:
    failures.append("planning/active/ACTIVE.md must start with '# PL-YYYYMMDDTHHMMSSZ: descriptive title' (or legacy '# PL-####: ...')")

for support_file in sorted((root / "planning/active").glob("*.md")):
    if support_file.name == "ACTIVE.md":
        continue
    if support_file.resolve() not in graph.get((root / "planning/active/ACTIVE.md").resolve(), set()):
        failures.append(f"active supporting document is not linked from ACTIVE.md: {support_file.name}")

backlog_pattern = re.compile(r"^((?:PL-[0-9]{8}T[0-9]{6}Z|PL-[0-9]{4}))-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
closed_pattern = re.compile(r"^((?:PL-[0-9]{8}T[0-9]{6}Z|PL-[0-9]{4}))-[a-z0-9]+(?:-[a-z0-9]+)*$")
plan_locations = {}

for plan in sorted((root / "planning/backlog").glob("PL-*.md")):
    m = backlog_pattern.match(plan.name)
    if not m:
        failures.append(f"invalid backlog plan filename: {plan.name}")
        plan_id = plan.name
    else:
        plan_id = m.group(1)
    plan_locations.setdefault(plan_id, []).append(plan.relative_to(root).as_posix())

for packet in sorted((root / "planning/closed").glob("PL-*")):
    if not packet.is_dir():
        continue
    m = closed_pattern.match(packet.name)
    if not m:
        failures.append(f"invalid closed packet directory: {packet.name}")
        plan_id = packet.name
    else:
        plan_id = m.group(1)
    plan_locations.setdefault(plan_id, []).append(packet.relative_to(root).as_posix())
    if not (packet / f"{plan_id}.sdd.md").exists() and not (packet / "ACTIVE.md").exists():
        failures.append(f"closed packet is missing {plan_id}.sdd.md (or ACTIVE.md): {packet.name}")

if active_match and not active_match.group(1).startswith("{{"):
    plan_locations.setdefault(active_match.group(1), []).append("planning/active/ACTIVE.md")

for plan_id, locations in sorted(plan_locations.items()):
    if len(locations) > 1:
        failures.append(f"plan ID appears in multiple lifecycle locations: {plan_id}: {', '.join(locations)}")

retrospective_statuses = {"Captured", "Deferred", "Promoted", "Rejected"}
retrospective_scopes = {"Project Layer", "Undetermined"}
retrospective_name = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
for retrospective in sorted((root / "retrospectives/inbox").glob("*.md")):
    if retrospective.name in {"README.md", "template.md"}:
        continue
    if not retrospective_name.fullmatch(retrospective.name):
        failures.append(f"invalid retrospective filename: {retrospective.name}")
    text = retrospective.read_text(encoding="utf-8")
    status_match = re.search(r"^- Status: (.+)$", text, re.MULTILINE)
    scope_match = re.search(r"^- Scope: (.+)$", text, re.MULTILINE)
    status = status_match.group(1).strip() if status_match else ""
    scope = scope_match.group(1).strip() if scope_match else ""
    if status not in retrospective_statuses:
        failures.append(f"invalid project retrospective status in {retrospective.name}: {status or 'missing'}")
    if scope not in retrospective_scopes:
        failures.append(f"invalid project retrospective scope in {retrospective.name}: {scope or 'missing'}")

if failures:
    for failure in failures:
        print(f"FAIL: {failure}")
    print(f"Project Layer check: {len(failures)} failure(s)")
    sys.exit(1)

print("Project Layer check: 0 failure(s)")
PY