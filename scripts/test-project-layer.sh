#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
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
if bash "$legacy_no_progress/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "A 0.6.0 layer without a ## Progress section should still validate"
fi

unversioned_no_progress="$(new_fixture unversioned-no-progress)"
python -c "import json,sys; p=sys.argv[1]; d=json.load(open(p,encoding='utf-8')); d.pop('templateVersion',None); json.dump(d,open(p,'w',encoding='utf-8'),indent='\t'); open(p,'a').write('\n')" \
  "$unversioned_no_progress/project-layer.json"
sed -i '/^## Progress$/,/^## Objective$/ { /^## Progress$/d; /^## Objective$/!d }' \
  "$unversioned_no_progress/planning/active/ACTIVE.md"
if bash "$unversioned_no_progress/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "An unversioned layer without a ## Progress section should still validate"
fi

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