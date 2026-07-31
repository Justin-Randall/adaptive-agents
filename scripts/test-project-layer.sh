#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEMP_ROOT"' EXIT

PASSES=0
FAILURES=0

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

There is no active Project Layer work unit.

Use [Planning](../INDEX.md) to select backlog work or review closed work.
EOF
rm -f "$no_active_plan/planning/active/PL-20260710-validate-project-layer.memory.md"
sed -i '\|active/PL-20260710-validate-project-layer.memory.md|d' "$no_active_plan/planning/INDEX.md"
if bash "$no_active_plan/scripts/check-project-layer.sh" >/dev/null; then
  pass
else
  fail "No Active Plan placeholder should not require a ## Test Plan section"
fi

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

missing_architecture_route="$TEMP_ROOT/missing-architecture-route"
mkdir -p "$missing_architecture_route"
cp -R "$REPO_ROOT/.adaptive-agents/." "$missing_architecture_route/"
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