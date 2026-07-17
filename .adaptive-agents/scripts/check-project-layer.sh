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
ignored_directories = {"node_modules", "playwright-report", "test-results"}
required = (
    "INDEX.md",
    "README.md",
    "ARCHITECTURE.md",
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
markdown_files = sorted(
    path for path in root.rglob("*.md")
    if not ignored_directories.intersection(path.relative_to(root).parts[:-1])
)

for source in markdown_files:
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

project_instructions = root / "instructions/project.instructions.md"
architecture = root / "ARCHITECTURE.md"
if architecture not in graph.get(project_instructions, set()):
    failures.append("project.instructions.md must link to ../ARCHITECTURE.md")

entrypoint = root / "INDEX.md"
reachable = set()
queue = deque([entrypoint])
while queue:
    current = queue.popleft()
    if current in reachable:
        continue
    reachable.add(current)
    queue.extend(graph.get(current, ()))

for markdown in markdown_files:
    if markdown not in reachable:
        failures.append(f"orphan Markdown file: {markdown.relative_to(root).as_posix()}")

active_text = (root / "planning/active/ACTIVE.md").read_text(encoding="utf-8") if (root / "planning/active/ACTIVE.md").exists() else ""
active_match = re.search(r"^# ((?:PL-[0-9]{8}|PL-[0-9]{8}T[0-9]{6}Z|PL-[0-9]{4})|\{\{ACTIVE_PLAN_ID\}\}): (.+)$", active_text, re.MULTILINE)
if not active_match and "No Active Plan" not in active_text:
    failures.append("planning/active/ACTIVE.md must start with '# PL-YYYYMMDD: descriptive title' (or legacy PL-YYYYMMDDTHHMMSSZ, PL-####)")

work_unit_match = re.search(r"^- Work Unit: ((?:PL-[0-9]{8}|PL-[0-9]{8}T[0-9]{6}Z|PL-[0-9]{4})-[a-z0-9]+(?:-[a-z0-9]+)*|\{\{ACTIVE_WORK_ID\}\})$", active_text, re.MULTILINE)
if active_match and "No Active Plan" not in active_text and not work_unit_match:
    failures.append("planning/active/ACTIVE.md must declare '- Work Unit: PL-YYYYMMDD-descriptive-slug'")
elif work_unit_match:
    work_unit = work_unit_match.group(1)
    active_memory = root / "planning/active" / f"{work_unit}.memory.md"
    if not active_memory.exists():
        failures.append(f"missing active memory for work unit: {work_unit}.memory.md")
    elif active_memory.resolve() not in graph.get((root / "planning/active/ACTIVE.md").resolve(), set()):
        failures.append(f"ACTIVE.md must link to active memory: {work_unit}.memory.md")

for support_file in sorted((root / "planning/active").glob("*.md")):
    if support_file.name == "ACTIVE.md":
        continue
    if "No Active Plan" in active_text:
        break
    if support_file.resolve() not in graph.get((root / "planning/active/ACTIVE.md").resolve(), set()):
        failures.append(f"active supporting document is not linked from ACTIVE.md: {support_file.name}")

backlog_pattern = re.compile(r"^((?:PL-[0-9]{8}|PL-[0-9]{8}T[0-9]{6}Z|PL-[0-9]{4}))-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
closed_pattern = re.compile(r"^((?:PL-[0-9]{8}|PL-[0-9]{8}T[0-9]{6}Z|PL-[0-9]{4}))-[a-z0-9]+(?:-[a-z0-9]+)*$")
plan_locations = {}

for plan in sorted((root / "planning/backlog").glob("PL-*.md")):
    m = backlog_pattern.match(plan.name)
    if not m:
        failures.append(f"invalid backlog plan filename: {plan.name}")
        plan_id = plan.name
    else:
        plan_id = plan.stem  # full slug-based identity, e.g. PL-20260710-descriptive-slug
    plan_locations.setdefault(plan_id, []).append(plan.relative_to(root).as_posix())

for packet in sorted((root / "planning/closed").glob("PL-*")):
    if not packet.is_dir():
        continue
    m = closed_pattern.match(packet.name)
    if not m:
        failures.append(f"invalid closed packet directory: {packet.name}")
        plan_id = packet.name
    else:
        plan_id = packet.name  # full slug-based identity, e.g. PL-20260710-descriptive-slug
    plan_locations.setdefault(plan_id, []).append(packet.relative_to(root).as_posix())
    id_prefix = m.group(1) if m else ""
    canonical_sdd = packet / f"{packet.name}.sdd.md"
    legacy_sdd = packet / f"{id_prefix}.sdd.md"
    if not canonical_sdd.exists() and not legacy_sdd.exists() and not (packet / "ACTIVE.md").exists():
        failures.append(f"closed packet is missing {packet.name}.sdd.md (or legacy {id_prefix}.sdd.md/ACTIVE.md): {packet.name}")

for plan_id, locations in sorted(plan_locations.items()):
    if len(locations) > 1:
        failures.append(f"plan ID appears in multiple lifecycle locations: {plan_id}: {', '.join(locations)}")

retrospective_statuses = {"Captured", "Deferred", "Promoted", "Rejected"}
retrospective_scopes = {"Project Layer", "Undetermined", "User-wide"}
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