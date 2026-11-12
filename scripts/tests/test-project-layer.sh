#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEMP_ROOT"' EXIT

PASSES=0
FAILURES=0
BASELINE_FIXTURE=""

pass() {
  PASSES=$((PASSES + 1))
}

fail() {
  printf 'FAIL: %s\n' "$1"
  FAILURES=$((FAILURES + 1))
}

empty_plan_closure_rule="If no replacement work is requested, write the empty-state marker"
for closure_guidance_file in \
  "$REPO_ROOT/instructions/planning-conventions.md" \
  "$REPO_ROOT/skills/manage-planning/SKILL.md" \
  "$REPO_ROOT/templates/project-layer/.adaptive-agents/playbooks/end-work.md"; do
  if grep -Fq -- "$empty_plan_closure_rule" "$closure_guidance_file"; then
    pass
  else
    fail "Closure guidance must state the no-replacement empty-plan rule: $closure_guidance_file"
  fi
done

new_fixture() {
  local name="$1"
  local target="$TEMP_ROOT/$name"
  mkdir -p "$target"
  if [[ -n "$BASELINE_FIXTURE" ]]; then
    cp -R "$BASELINE_FIXTURE" "$target/.adaptive-agents"
    printf '%s\n' "$target/.adaptive-agents"
    return
  fi
  bash "$REPO_ROOT/scripts/bootstrap-project-layer.sh" \
    --target "$target" \
    --project-name "Validator fixture" \
    --active-plan-id "${2:-PL-20260710}" \
    --active-title "Validate project layer" \
    --persistence tracked >/dev/null
  printf '%s\n' "$target/.adaptive-agents"
}

expect_failure() {
  local fixture="$1"
  local expected="$2"
  local output

  if output="$(bash "$fixture/scripts/check-project-layer.sh" 2>&1)"; then
    fail "Validator unexpectedly accepted: $expected"
  elif grep -Fq -- "$expected" <<<"$output"; then
    pass
  else
    fail "Validator failed without expected diagnostic: $expected"
    printf '%s\n' "$output"
  fi
}

baseline="$(new_fixture baseline)"
BASELINE_FIXTURE="$baseline"
if bash "$baseline/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "Canonical template baseline should pass"
fi

if grep -Fq -- '"templateVersion": "0.10.0"' "$baseline/project-layer.json" \
  && grep -Fq -- "## User-Facing Validation" "$baseline/planning/active/ACTIVE.md" \
  && ! grep -Fq -- "## Browser Dogfood" "$baseline/planning/active/ACTIVE.md"; then
  pass
else
  fail "Bootstrap should use generic user-facing validation in template version 0.10.0"
fi

if grep -Fq -- '[Project agents](agents/INDEX.md)' "$baseline/INDEX.md" \
  && [[ -f "$baseline/agents/INDEX.md" ]] \
  && grep -Fq -- 'project-owned roles and refinements' "$baseline/agents/INDEX.md"; then
  pass
else
  fail "Bootstrap should route to the project-owned agent roles index"
fi

if grep -Fxq -- '## Supervision and Delegation' "$baseline/planning/active/ACTIVE.md" \
  && grep -Fxq -- '## Done Conditions and Execution Loop' "$baseline/planning/active/ACTIVE.md" \
  && grep -Fq -- 'delegate suitable bounded work' "$baseline/planning/active/ACTIVE.md" \
  && grep -Fq -- 'repeat assignment, implementation, validation, review, correction' "$baseline/planning/active/ACTIVE.md" \
  && grep -Fq -- 'single-agent fallback' "$baseline/skills/manage-planning/SKILL.md"; then
  pass
else
  fail "Bootstrap should include supervision, execution-loop and fallback guidance"
fi

if grep -Fq -- "Status: Backlog" "$baseline/planning/backlog/backlog-item-template.md" \
  && grep -Fq -- "## Children (epics only)" "$baseline/planning/backlog/backlog-item-template.md" \
  && grep -Fq -- "Work item | Status | Depends on | Evidence / next action" "$baseline/planning/backlog/backlog-item-template.md" \
  && grep -Fq -- "planning/backlog/backlog-item-template.md" "$REPO_ROOT/skills/upgrade-project-layer/SKILL.md" \
  && cmp -s "$REPO_ROOT/.adaptive-agents/planning/backlog/backlog-item-template.md" \
    "$REPO_ROOT/templates/project-layer/.adaptive-agents/planning/backlog/backlog-item-template.md"; then
  pass
else
  fail "Version 0.9.2 should provide and document the epic child-status backlog template upgrade"
fi

missing_user_facing_validation="$(new_fixture missing-user-facing-validation)"
sed -i 's/^## User-Facing Validation$/## Validation Notes/' \
  "$missing_user_facing_validation/planning/active/ACTIVE.md"
expect_failure "$missing_user_facing_validation" \
  "planning/active/ACTIVE.md must include a '## User-Facing Validation' section"

legacy_browser_validation="$(new_fixture legacy-browser-validation)"
python -c "import json,sys; p=sys.argv[1]; d=json.load(open(p,encoding='utf-8')); d['templateVersion']='0.8.0'; json.dump(d,open(p,'w',encoding='utf-8'),indent='\\t'); open(p,'a').write('\\n')" \
  "$legacy_browser_validation/project-layer.json"
sed -i 's/^## User-Facing Validation$/## Browser Dogfood/' \
  "$legacy_browser_validation/planning/active/ACTIVE.md"
if bash "$legacy_browser_validation/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "A 0.8.0 layer should retain its Browser Dogfood validation contract"
fi

legacy_missing_browser_validation="$(new_fixture legacy-missing-browser-validation)"
python -c "import json,sys; p=sys.argv[1]; d=json.load(open(p,encoding='utf-8')); d['templateVersion']='0.8.0'; json.dump(d,open(p,'w',encoding='utf-8'),indent='\\t'); open(p,'a').write('\\n')" \
  "$legacy_missing_browser_validation/project-layer.json"
sed -i 's/^## User-Facing Validation$/## Validation Notes/' \
  "$legacy_missing_browser_validation/planning/active/ACTIVE.md"
expect_failure "$legacy_missing_browser_validation" \
  "planning/active/ACTIVE.md must include a '## Browser Dogfood' section"

expected_work_unit="PL-20260710-validate-project-layer"
expected_memory="$baseline/planning/active/$expected_work_unit.memory.md"
if [[ -f "$expected_memory" ]] \
  && grep -Fq -- "- Work Unit: $expected_work_unit" "$baseline/planning/active/ACTIVE.md" \
  && grep -Fq -- "[$expected_work_unit memory]($expected_work_unit.memory.md)" "$baseline/planning/active/ACTIVE.md" \
  && grep -Fq -- '"adaptiveAgentsHome"' "$baseline/project-layer.json" \
  && [[ ! -e "$baseline/planning/active/MEMORY.md" ]]; then
  pass
else
  fail "Bootstrap should create work-unit-first active memory and record Adaptive Agents home"
fi

baseline_target="$(dirname "$baseline")"
before_rerun="$(cksum "$baseline/planning/active/ACTIVE.md" "$expected_memory")"
bash "$REPO_ROOT/scripts/bootstrap-project-layer.sh" \
  --target "$baseline_target" \
  --project-name "Validator fixture" \
  --active-plan-id "PL-20260710" \
  --active-title "Validate project layer" \
  --persistence tracked >/dev/null
after_rerun="$(cksum "$baseline/planning/active/ACTIVE.md" "$expected_memory")"
if [[ "$before_rerun" == "$after_rerun" ]]; then
  pass
else
  fail "Bootstrap rerun should preserve active work-unit files"
fi

upgrade_review="$(new_fixture upgrade-review)"
python -c "import json,sys; p=sys.argv[1]; d=json.load(open(p,encoding='utf-8')); d['templateVersion']='0.7.1'; json.dump(d,open(p,'w',encoding='utf-8'),indent='\t'); open(p,'a').write('\n')" \
  "$upgrade_review/project-layer.json"
sed -i '/^> Keep this checklist up to date as you work\./d' \
  "$upgrade_review/planning/active/ACTIVE.md"
upgrade_report="$(bash "$REPO_ROOT/scripts/inspect-project-layer-upgrade.sh" --target "$(dirname "$upgrade_review")")"
if grep -Fq -- "Upgrade available: yes" <<<"$upgrade_report" \
  && grep -Fq -- "Content requiring review: 2" <<<"$upgrade_report" \
  && grep -Fq -- "- planning/active/ACTIVE.md" <<<"$upgrade_report" \
  && grep -Fq -- "- project-layer.json" <<<"$upgrade_report" \
  && grep -Fq -- "Missing canonical paths: 0" <<<"$upgrade_report"; then
  pass
else
  fail "Upgrade inspection should flag the 0.7.1 progress guidance change for review"
  printf '%s\n' "$upgrade_report"
fi

old_roles_layer="$(new_fixture old-roles-layer)"
python -c "import json,sys; p=sys.argv[1]; d=json.load(open(p,encoding='utf-8')); d['templateVersion']='0.9.2'; json.dump(d,open(p,'w',encoding='utf-8'),indent='\t'); open(p,'a').write('\n')" \
  "$old_roles_layer/project-layer.json"
rm "$old_roles_layer/agents/INDEX.md"
sed -i '\|\[Project agents\](agents/INDEX.md)|d' "$old_roles_layer/INDEX.md"
python - "$old_roles_layer/skills/manage-planning/SKILL.md" <<'PY'
import re, sys
from pathlib import Path
path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = re.sub(r"^For active implementation,.*\n", "", text, flags=re.MULTILINE)
text = "\n".join(
    '5. Create `ACTIVE.md` with `- Work Unit: <work-unit-id>` and create `<work-unit-id>.memory.md`. '
    'Link the memory from `ACTIVE.md` and `planning/INDEX.md`.'
    if line.startswith("5.") and "template" in line.lower() and "ACTIVE.md" in line else line
    for line in text.split("\n")
)
text = text.replace("## Start Work\n", "## Start Work\n\nProject-specific start-work review is required.\n", 1)
path.write_text(text, encoding="utf-8", newline="\n")
PY
sed -i '/^## Supervision and Delegation$/,/^## Test Plan$/ { /^## Test Plan$/!d; }' \
  "$old_roles_layer/planning/active/ACTIVE.md"
printf '\nProject-specific active work must be preserved.\n' >> "$old_roles_layer/planning/active/ACTIVE.md"
printf '\nProject-specific memory must be preserved.\n' >> "$old_roles_layer/planning/active/$expected_work_unit.memory.md"
printf '\nProject-specific instructions must be preserved.\n' >> "$old_roles_layer/instructions/project.instructions.md"
printf '\nProject-specific planning guidance must be preserved.\n' >> "$old_roles_layer/skills/manage-planning/SKILL.md"
printf 'Project-owned notes must be preserved.\n' > "$old_roles_layer/project-notes.txt"

snapshot_layer() {
  (cd "$1" && find . -type d -print | sort && find . -type f -print | sort | while IFS= read -r file; do cksum "$file"; done)
}

before_inspection="$(snapshot_layer "$old_roles_layer")"
old_roles_report="$(bash "$REPO_ROOT/scripts/inspect-project-layer-upgrade.sh" --target "$(dirname "$old_roles_layer")")"
after_inspection="$(snapshot_layer "$old_roles_layer")"
repeat_roles_report="$(bash "$REPO_ROOT/scripts/inspect-project-layer-upgrade.sh" --target "$(dirname "$old_roles_layer")")"
after_repeat_inspection="$(snapshot_layer "$old_roles_layer")"
missing_roles_section="$(sed -n '/^Missing canonical paths:/,/^Content requiring review:/p' <<<"$old_roles_report")"
changed_roles_section="$(sed -n '/^Content requiring review:/,/^Project-only paths:/p' <<<"$old_roles_report")"
if grep -Fxq -- 'Installed template version: 0.9.2' <<<"$old_roles_report" \
  && grep -Fxq -- 'Canonical template version: 0.10.0' <<<"$old_roles_report" \
  && grep -Fxq -- 'Upgrade available: yes' <<<"$old_roles_report" \
  && grep -Fxq -- '- agents/INDEX.md' <<<"$missing_roles_section" \
  && grep -Fxq -- '- INDEX.md' <<<"$changed_roles_section" \
  && grep -Fxq -- '- planning/active/ACTIVE.md' <<<"$changed_roles_section" \
  && grep -Fxq -- '- skills/manage-planning/SKILL.md' <<<"$changed_roles_section" \
  && grep -Fxq -- '- project-notes.txt' <<<"$old_roles_report"; then
  pass
else
  fail "Upgrade inspection should classify missing roles and changed planning for the old layer"
  printf '%s\n' "$old_roles_report"
fi
if [[ "$before_inspection" == "$after_inspection" && "$before_inspection" == "$after_repeat_inspection" \
  && "$old_roles_report" == "$repeat_roles_report" ]]; then
  pass
else
  fail "Repeated upgrade inspection should preserve the entire old layer and return the same report"
fi

# This is a simulated approval of the exact fixture patch below, not an upgrade
# command: real project-owned layers require the documented review and approval.
apply_approved_roles_upgrade() {
  python - "$1" "$REPO_ROOT/templates/project-layer/.adaptive-agents" <<'PY'
import re, sys
from pathlib import Path

layer, template = map(Path, sys.argv[1:])
def write_if_changed(path, text):
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8", newline="\n")

role = layer / "agents/INDEX.md"
role.parent.mkdir(parents=True, exist_ok=True)
write_if_changed(role, (template / "agents/INDEX.md").read_text(encoding="utf-8"))
index = layer / "INDEX.md"
text = index.read_text(encoding="utf-8")
route = next(line for line in (template / "INDEX.md").read_text(encoding="utf-8").splitlines()
             if "[Project agents](agents/INDEX.md)" in line)
if route not in text:
    text = text.replace("- Read [Planning]", route + "\n- Read [Planning]", 1)
write_if_changed(index, text)

skill = layer / "skills/manage-planning/SKILL.md"
text = skill.read_text(encoding="utf-8")
canonical = (template / "skills/manage-planning/SKILL.md").read_text(encoding="utf-8")
# Insert the reviewed additions without replacing project-owned Start Work content.
canonical_step = next(line for line in canonical.splitlines() if line.startswith("5. "))
template_guidance = canonical_step[3:].split('Create `ACTIVE.md` with', 1)[0].strip()
supervision = next(line for line in canonical.splitlines() if line.startswith("For active implementation,"))
if template_guidance not in text:
    anchor = '5. Create `ACTIVE.md` with'
    if text.count(anchor) != 1:
        raise ValueError("expected the old Start Work step exactly once")
    text = text.replace(anchor, template_guidance + "\n\n" + anchor, 1)
if supervision not in text:
    anchor = "## Link Semantics\n"
    if text.count(anchor) != 1:
        raise ValueError("expected the Link Semantics heading exactly once")
    text = text.replace(anchor, supervision + "\n\n" + anchor, 1)
write_if_changed(skill, text)
metadata = layer / "project-layer.json"
text = metadata.read_text(encoding="utf-8")
text, count = re.subn(r'("templateVersion"\s*:\s*")0\.(?:9\.2|10\.0)(")', r'\g<1>0.10.0\2', text)
if count != 1:
    raise ValueError("unexpected fixture template version")
write_if_changed(metadata, text)
PY
}

preserved_before="$(cksum "$old_roles_layer/instructions/project.instructions.md" \
  "$old_roles_layer/planning/active/ACTIVE.md" "$old_roles_layer/planning/active/$expected_work_unit.memory.md")"
apply_approved_roles_upgrade "$old_roles_layer"
preserved_after="$(cksum "$old_roles_layer/instructions/project.instructions.md" \
  "$old_roles_layer/planning/active/ACTIVE.md" "$old_roles_layer/planning/active/$expected_work_unit.memory.md")"
if [[ "$preserved_before" == "$preserved_after" ]] \
  && grep -Fq -- 'Project-specific planning guidance must be preserved.' "$old_roles_layer/skills/manage-planning/SKILL.md" \
  && sed -n '/^## Start Work$/,/^## Link Semantics$/p' "$old_roles_layer/skills/manage-planning/SKILL.md" \
    | grep -Fxq -- 'Project-specific start-work review is required.' \
  && grep -Fq -- '[Project agents](agents/INDEX.md)' "$old_roles_layer/INDEX.md" \
  && [[ -f "$old_roles_layer/agents/INDEX.md" ]] \
  && grep -Fq -- 'single-agent fallback' "$old_roles_layer/skills/manage-planning/SKILL.md" \
  && grep -Fq -- '"templateVersion": "0.10.0"' "$old_roles_layer/project-layer.json" \
  && bash "$old_roles_layer/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "Approved upgrade should merge roles and planning while preserving and validating project work"
fi
after_upgrade="$(snapshot_layer "$old_roles_layer")"
apply_approved_roles_upgrade "$old_roles_layer"
if [[ "$after_upgrade" == "$(snapshot_layer "$old_roles_layer")" ]]; then
  pass
else
  fail "Repeating the approved upgrade should leave the upgraded layer unchanged"
fi

# Simulate approved closure and a subsequent direct activation, using the
# canonical templates that the upgraded planning guidance must direct agents to consult.
if python - "$old_roles_layer/skills/manage-planning/SKILL.md" <<'PY'
import re, sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding="utf-8")
start = text.split("## Start Work", 1)[1].split("## Link Semantics", 1)[0]
sentences = re.split(r"(?<=[.!?])\s+|\n", start)
if not any("templates/project-layer/.adaptive-agents/planning/active/ACTIVE.md" in s
           and "canonical" in s.lower() and "template" in s.lower()
           and re.search(r"\b(use|consult|read|reference|follow|load)\b", s, re.I)
           for s in sentences):
    sys.exit(1)
PY
then
  pass
else
  fail "Upgraded planning guidance should direct new plans to the canonical ACTIVE.md template"
fi
python - "$old_roles_layer" "$REPO_ROOT/templates/project-layer/.adaptive-agents" "$expected_work_unit" <<'PY'
import sys
from pathlib import Path
layer, template = map(Path, sys.argv[1:3])
old_id = sys.argv[3]
new_id, new_plan, new_title = "PL-20260711-future-work", "PL-20260711", "Future work"
active = layer / "planning/active"
packet = layer / "planning/closed" / old_id
packet.mkdir()
(active / "ACTIVE.md").replace(packet / f"{old_id}.sdd.md")
(active / f"{old_id}.memory.md").replace(packet / f"{old_id}.memory.md")
closed_index = layer / "planning/closed/INDEX.md"
with closed_index.open("a", encoding="utf-8", newline="\n") as f:
    f.write(f"| PL-20260710 | [Previous work]({old_id}/{old_id}.sdd.md) | Completed | Preserved. |\n")
replacements = {"{{ACTIVE_PLAN_ID}}": new_plan, "{{ACTIVE_PLAN_TITLE}}": new_title,
                "{{ACTIVE_WORK_ID}}": new_id}
for source, dest in [(template / "planning/active/ACTIVE.md", active / "ACTIVE.md"),
                     (template / "planning/active/{{ACTIVE_WORK_ID}}.memory.md", active / f"{new_id}.memory.md")]:
    text = source.read_text(encoding="utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    dest.write_text(text, encoding="utf-8", newline="\n")
index = layer / "planning/INDEX.md"
text = index.read_text(encoding="utf-8").replace("PL-20260710: Validate project layer", f"{new_plan}: {new_title}").replace(old_id, new_id)
index.write_text(text, encoding="utf-8", newline="\n")
PY
if grep -Fxq -- '## Supervision and Delegation' "$old_roles_layer/planning/active/ACTIVE.md" \
  && grep -Fxq -- '## Done Conditions and Execution Loop' "$old_roles_layer/planning/active/ACTIVE.md" \
  && grep -Fq -- 'Project-specific active work must be preserved.' "$old_roles_layer/planning/closed/$expected_work_unit/$expected_work_unit.sdd.md" \
  && grep -Fq -- 'Project-specific memory must be preserved.' "$old_roles_layer/planning/closed/$expected_work_unit/$expected_work_unit.memory.md" \
  && bash "$old_roles_layer/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "Future activation should use the current template and retain the closed plan and memory"
fi
after_activation="$(snapshot_layer "$old_roles_layer")"
apply_approved_roles_upgrade "$old_roles_layer"
if [[ "$after_activation" == "$(snapshot_layer "$old_roles_layer")" ]]; then
  pass
else
  fail "Repeating the approved upgrade after future activation should preserve all work"
fi

orphan="$(new_fixture orphan)"
printf '# Orphan\n' > "$orphan/orphan.md"
expect_failure "$orphan" "orphan Markdown file: orphan.md"

generated_outputs="$(new_fixture generated-outputs)"
mkdir -p "$generated_outputs/tests/node_modules/example" "$generated_outputs/tests/test-results/example"
printf '# Dependency documentation\n' > "$generated_outputs/tests/node_modules/example/README.md"
printf '# Test artifact\n' > "$generated_outputs/tests/test-results/example/result.md"
if bash "$generated_outputs/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "Validator should ignore generated dependency and test-output directories"
fi

broken_link="$(new_fixture broken-link)"
printf '\n- [Missing](missing.md)\n' >> "$broken_link/INDEX.md"
expect_failure "$broken_link" "INDEX.md: missing link target: missing.md"

duplicate_id="$(new_fixture duplicate-id)"
mkdir -p "$duplicate_id/planning/closed/PL-20260710-duplicate-work"
cat > "$duplicate_id/planning/closed/PL-20260710-duplicate-work/PL-20260710.sdd.md" <<'EOF'
# PL-20260710: Duplicate Work (closed)
EOF
cat > "$duplicate_id/planning/backlog/PL-20260710-duplicate-work.md" <<'EOF'
# PL-20260710: Duplicate Work (backlog)

This fixture duplicates a closed plan's slug.
EOF
printf '| PL-20260710 | [Duplicate work](PL-20260710-duplicate-work.md) | Test duplicate detection. | Ready |\n' >> "$duplicate_id/planning/backlog/INDEX.md"
printf '| PL-20260710 | [Duplicate Work](PL-20260710-duplicate-work/PL-20260710.sdd.md) | Completed | Test duplicate. |\n' >> "$duplicate_id/planning/closed/INDEX.md"
expect_failure "$duplicate_id" "plan ID appears in multiple lifecycle locations: PL-20260710-duplicate-work"

closed_backlog_source="$(new_fixture closed-backlog-source)"
mkdir -p "$closed_backlog_source/planning/closed/PL-20260710-closed-work"
cat > "$closed_backlog_source/planning/closed/PL-20260710-closed-work/PL-20260710-closed-work.sdd.md" <<'EOF'
# PL-20260710: Closed Work

[Backlog source](PL-20260710-closed-work.backlog.md)
EOF
cat > "$closed_backlog_source/planning/closed/PL-20260710-closed-work/PL-20260710-closed-work.backlog.md" <<'EOF'
# PL-20260710: Closed Work (backlog source)
EOF
cat > "$closed_backlog_source/planning/backlog/PL-20260710-closed-work.md" <<'EOF'
# PL-20260710: Closed Work (original backlog source)
EOF
printf '| PL-20260710 | [Closed Work](PL-20260710-closed-work/PL-20260710-closed-work.sdd.md) | Completed | Test closed packet. |\n' >> "$closed_backlog_source/planning/closed/INDEX.md"
if bash "$closed_backlog_source/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "Validator should allow an unindexed backlog source retained in its closed packet"
fi

unlinked_support="$(new_fixture unlinked-support)"
printf '# Notes\n' > "$unlinked_support/planning/active/NOTES.md"
expect_failure "$unlinked_support" "active supporting document is not linked from ACTIVE.md: NOTES.md"

invalid_name="$(new_fixture invalid-name)"
cat > "$invalid_name/planning/backlog/PL-20260710-Bad-Name.md" <<'EOF'
# PL-20260710: Invalid Filename
EOF
printf '| PL-20260710 | [Invalid filename](PL-20260710-Bad-Name.md) | Test naming. | Ready |\n' >> "$invalid_name/planning/backlog/INDEX.md"
expect_failure "$invalid_name" "invalid backlog plan filename: PL-20260710-Bad-Name.md"

missing_required="$(new_fixture missing-required)"
rm "$missing_required/planning/active/PL-20260710-validate-project-layer.memory.md"
expect_failure "$missing_required" "missing active memory for work unit: PL-20260710-validate-project-layer.memory.md"

if grep -Fq -- "## Test Plan" "$baseline/planning/active/ACTIVE.md"; then
  pass
else
  fail "Bootstrap should include a ## Test Plan section in ACTIVE.md"
fi

if grep -Fq -- "## Progress" "$baseline/planning/active/ACTIVE.md" \
  && grep -Eq -- '^- \[[ xX]\] ' "$baseline/planning/active/ACTIVE.md"; then
  pass
else
  fail "Bootstrap should include a ## Progress checklist in ACTIVE.md"
fi
if grep -Fq -- "Keep this checklist up to date as you work" "$baseline/planning/active/ACTIVE.md" \
  && grep -Fq -- "add newly discovered work" "$baseline/planning/active/ACTIVE.md" \
  && grep -Fq -- "remove eliminated work" "$baseline/planning/active/ACTIVE.md"; then
  pass
else
  fail "Bootstrap should instruct models to keep the progress checklist up to date"
fi

missing_progress="$(new_fixture missing-progress)"
sed -i '/^## Progress$/,/^## Objective$/ { /^## Progress$/d; /^## Objective$/!d }' \
  "$missing_progress/planning/active/ACTIVE.md"
expect_failure "$missing_progress" \
  "planning/active/ACTIVE.md must include a '## Progress' section with checklist items"

custom_progress="$(new_fixture custom-progress)"
sed -i 's/^## Progress$/## Delivery Notes/' "$custom_progress/planning/active/ACTIVE.md"
expect_failure "$custom_progress" \
  "planning/active/ACTIVE.md must include a '## Progress' section with checklist items"

legacy_no_progress="$(new_fixture legacy-no-progress)"
python -c "import json,sys; p=sys.argv[1]; d=json.load(open(p,encoding='utf-8')); d['templateVersion']='0.6.0'; json.dump(d,open(p,'w',encoding='utf-8'),indent='\t'); open(p,'a').write('\n')" \
  "$legacy_no_progress/project-layer.json"
sed -i '/^## Progress$/,/^## Objective$/ { /^## Progress$/d; /^## Objective$/!d }' \
  "$legacy_no_progress/planning/active/ACTIVE.md"
expect_failure "$legacy_no_progress" \
  "planning/active/ACTIVE.md must include a '## Progress' section with checklist items"

unversioned_no_progress="$(new_fixture unversioned-no-progress)"
python -c "import json,sys; p=sys.argv[1]; d=json.load(open(p,encoding='utf-8')); d.pop('templateVersion',None); json.dump(d,open(p,'w',encoding='utf-8'),indent='\t'); open(p,'a').write('\n')" \
  "$unversioned_no_progress/project-layer.json"
sed -i '/^## Progress$/,/^## Objective$/ { /^## Progress$/d; /^## Objective$/!d }' \
  "$unversioned_no_progress/planning/active/ACTIVE.md"
expect_failure "$unversioned_no_progress" \
  "planning/active/ACTIVE.md must include a '## Progress' section with checklist items"

missing_test_plan="$(new_fixture missing-test-plan)"
sed -i '/^## Test Plan$/,/^## Scope$/ { /^## Test Plan$/d; /^## Scope$/!d }' "$missing_test_plan/planning/active/ACTIVE.md"
expect_failure "$missing_test_plan" "planning/active/ACTIVE.md must include a '## Test Plan' section"

old_layer_no_test_plan="$(new_fixture old-layer-no-test-plan)"
python -c "import json,sys; p=sys.argv[1]; d=json.load(open(p,encoding='utf-8')); d['templateVersion']='0.5.1'; json.dump(d,open(p,'w',encoding='utf-8'),indent='\t'); open(p,'a').write('\n')" "$old_layer_no_test_plan/project-layer.json"
sed -i '/^## Test Plan$/,/^## Scope$/ { /^## Test Plan$/d; /^## Scope$/!d }' "$old_layer_no_test_plan/planning/active/ACTIVE.md"
if bash "$old_layer_no_test_plan/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "A 0.5.1 layer without a ## Test Plan section should still validate"
fi

old_layer_no_version="$(new_fixture old-layer-no-version)"
python -c "import json,sys; p=sys.argv[1]; d=json.load(open(p,encoding='utf-8')); d.pop('templateVersion',None); json.dump(d,open(p,'w',encoding='utf-8'),indent='\t'); open(p,'a').write('\n')" "$old_layer_no_version/project-layer.json"
sed -i '/^## Test Plan$/,/^## Scope$/ { /^## Test Plan$/d; /^## Scope$/!d }' "$old_layer_no_version/planning/active/ACTIVE.md"
if bash "$old_layer_no_version/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "A layer without a templateVersion should default safely and validate without a ## Test Plan section"
fi

no_active_plan="$(new_fixture no-active-plan)"
cat > "$no_active_plan/planning/active/ACTIVE.md" <<'EOF'
# No Active Plan

## Context

The next planning decision has not been selected.

Use [Planning](../INDEX.md) to select backlog work or review closed work.
EOF
rm -f "$no_active_plan/planning/active/PL-20260710-validate-project-layer.memory.md"
sed -i '\|active/PL-20260710-validate-project-layer.memory.md|d' "$no_active_plan/planning/INDEX.md"
if bash "$no_active_plan/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "No Active Plan placeholder should not require a ## Test Plan section"
fi

no_active_upgrade_report="$(bash "$REPO_ROOT/scripts/inspect-project-layer-upgrade.sh" --target "$(dirname "$no_active_plan")" 2>&1)"
if grep -Fq -- "Missing canonical paths: 0" <<<"$no_active_upgrade_report"; then
  pass
else
  fail "Upgrade inspection should not require active memory for an empty plan"
fi

stale_body_after_empty_marker="$(new_fixture stale-body-after-empty-marker)"
cat > "$stale_body_after_empty_marker/planning/active/ACTIVE.md" <<'EOF'
# No Active Plan

## Objective

This is stale content from a completed plan.
EOF
expect_failure "$stale_body_after_empty_marker" \
  "empty active plan must not contain former plan sections"

stale_work_unit_after_empty_marker="$(new_fixture stale-work-unit-after-empty-marker)"
cat > "$stale_work_unit_after_empty_marker/planning/active/ACTIVE.md" <<'EOF'
# No Active Plan

- Work Unit: PL-20260912-closed-work
EOF
expect_failure "$stale_work_unit_after_empty_marker" \
  "empty active plan must not contain active work-unit metadata"

canonical_closed="$(new_fixture canonical-closed)"
canonical_packet="$canonical_closed/planning/closed/PL-20260712-preserved-context"
mkdir -p "$canonical_packet"
cat > "$canonical_packet/PL-20260712-preserved-context.sdd.md" <<'EOF'
# PL-20260712: Preserved Context

- [Work-unit memory](PL-20260712-preserved-context.memory.md)
EOF
cat > "$canonical_packet/PL-20260712-preserved-context.memory.md" <<'EOF'
# PL-20260712-preserved-context Memory

- Curated closure context.
EOF
printf '| PL-20260712 | [Preserved Context](PL-20260712-preserved-context/PL-20260712-preserved-context.sdd.md) | Completed | Context preserved. |\n' >> "$canonical_closed/planning/closed/INDEX.md"
if bash "$canonical_closed/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "Validator should accept canonical closed work-unit artifacts"
fi

allowed_current_work="$(new_fixture allowed-current-work)"
if bash "$allowed_current_work/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "Validator should allow planning/INDEX.md to link to the moving active plan"
fi

self_referential_active="$(new_fixture self-referential-active)"
printf '\n- [Current plan](ACTIVE.md)\n' >> "$self_referential_active/planning/active/ACTIVE.md"
expect_failure "$self_referential_active" \
  "planning/active/ACTIVE.md must not link to itself"

historical_active_link="$(new_fixture historical-active-link)"
printf '\n- Depends on [current plan](../active/ACTIVE.md)\n' \
  >> "$historical_active_link/planning/backlog/PL-20260710-validate-project-layer.md"
expect_failure "$historical_active_link" \
  "historical planning record links to moving active path"

closed_historical_active_link="$(new_fixture closed-historical-active-link)"
closed_packet="$closed_historical_active_link/planning/closed/PL-20260712-preserved-context"
mkdir -p "$closed_packet"
cat > "$closed_packet/PL-20260712-preserved-context.sdd.md" <<'EOF'
# PL-20260712: Preserved Context
EOF
printf '\n- Previous work [plan](../../active/ACTIVE.md)\n' \
  >> "$closed_packet/PL-20260712-preserved-context.sdd.md"
expect_failure "$closed_historical_active_link" \
  "historical planning record links to moving active path"

missing_architecture_route="$TEMP_ROOT/missing-architecture-route"
mkdir -p "$missing_architecture_route"
tar \
  --exclude='./tests/node_modules' \
  --exclude='*/__pycache__' \
  --exclude='./tests/test-results' \
  --exclude='./tests/playwright-report' \
  -cf - \
  -C "$REPO_ROOT/.adaptive-agents" . \
  | tar -xf - -C "$missing_architecture_route"
sed -i '\|\[Architecture contract\](../ARCHITECTURE.md)|d' "$missing_architecture_route/instructions/project.instructions.md"
expect_failure "$missing_architecture_route" "project.instructions.md must link to ../ARCHITECTURE.md"

valid_retrospective="$(new_fixture valid-retrospective)"
cat > "$valid_retrospective/retrospectives/inbox/2026-07-10-project-behavior.md" <<'EOF'
# Retrospective: Project behavior

- Date: 2026-07-10
- Status: Captured
- Scope: Project Layer
- Session or task: Validator fixture
EOF
printf '\n- [Project behavior](2026-07-10-project-behavior.md)\n' >> "$valid_retrospective/retrospectives/inbox/README.md"
if bash "$valid_retrospective/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "Validator should accept an indexed project-scoped retrospective"
fi

invalid_scope="$(new_fixture invalid-retrospective-scope)"
cat > "$invalid_scope/retrospectives/inbox/2026-07-10-wrong-scope.md" <<'EOF'
# Retrospective: Wrong scope

- Date: 2026-07-10
- Status: Captured
- Scope: Invalid
- Session or task: Validator fixture
EOF
printf '\n- [Wrong scope](2026-07-10-wrong-scope.md)\n' >> "$invalid_scope/retrospectives/inbox/README.md"
expect_failure "$invalid_scope" "invalid project retrospective scope in retrospectives/inbox/2026-07-10-wrong-scope.md: Invalid"

invalid_status="$(new_fixture invalid-retrospective-status)"
cat > "$invalid_status/retrospectives/inbox/2026-07-10-wrong-status.md" <<'EOF'
# Retrospective: Wrong status

- Date: 2026-07-10
- Status: Pending
- Scope: Project Layer
- Session or task: Validator fixture
EOF
printf '\n- [Wrong status](2026-07-10-wrong-status.md)\n' >> "$invalid_status/retrospectives/inbox/README.md"
expect_failure "$invalid_status" "invalid project retrospective status in retrospectives/inbox/2026-07-10-wrong-status.md: Pending"

printf 'Project Layer validator tests: %d passed, %d failure(s)\n' "$PASSES" "$FAILURES"
if [[ "$FAILURES" -gt 0 ]]; then
  exit 1
fi
