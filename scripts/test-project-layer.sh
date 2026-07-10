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
    --active-plan-id "${2:-PL-20260710T120000Z}" \
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

orphan="$(new_fixture orphan)"
printf '# Orphan\n' > "$orphan/orphan.md"
expect_failure "$orphan" "orphan Markdown file: orphan.md"

broken_link="$(new_fixture broken-link)"
printf '\n- [Missing](missing.md)\n' >> "$broken_link/INDEX.md"
expect_failure "$broken_link" "INDEX.md: missing link target: missing.md"

duplicate_id="$(new_fixture duplicate-id)"
cat > "$duplicate_id/planning/backlog/PL-20260710T120000Z-duplicate-plan.md" <<'EOF'
# PL-20260710T120000Z: Duplicate Plan

This fixture duplicates the active plan identity.
EOF
printf '| PL-20260710T120000Z | [Duplicate plan](PL-20260710T120000Z-duplicate-plan.md) | Test duplicate detection. | Ready |\n' >> "$duplicate_id/planning/backlog/INDEX.md"
expect_failure "$duplicate_id" "plan ID appears in multiple lifecycle locations: PL-20260710T120000Z"

unlinked_support="$(new_fixture unlinked-support)"
printf '# Notes\n' > "$unlinked_support/planning/active/NOTES.md"
expect_failure "$unlinked_support" "active supporting document is not linked from ACTIVE.md: NOTES.md"

invalid_name="$(new_fixture invalid-name)"
cat > "$invalid_name/planning/backlog/PL-20260710T120001Z-Bad-Name.md" <<'EOF'
# PL-20260710T120001Z: Invalid Filename
EOF
printf '| PL-20260710T120001Z | [Invalid filename](PL-20260710T120001Z-Bad-Name.md) | Test naming. | Ready |\n' >> "$invalid_name/planning/backlog/INDEX.md"
expect_failure "$invalid_name" "invalid backlog plan filename: PL-20260710T120001Z-Bad-Name.md"

missing_required="$(new_fixture missing-required)"
rm "$missing_required/planning/active/MEMORY.md"
expect_failure "$missing_required" "missing required path: planning/active/MEMORY.md"

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
expect_failure "$invalid_scope" "invalid project retrospective scope in 2026-07-10-wrong-scope.md: Invalid"

invalid_status="$(new_fixture invalid-retrospective-status)"
cat > "$invalid_status/retrospectives/inbox/2026-07-10-wrong-status.md" <<'EOF'
# Retrospective: Wrong status

- Date: 2026-07-10
- Status: Pending
- Scope: Project Layer
- Session or task: Validator fixture
EOF
printf '\n- [Wrong status](2026-07-10-wrong-status.md)\n' >> "$invalid_status/retrospectives/inbox/README.md"
expect_failure "$invalid_status" "invalid project retrospective status in 2026-07-10-wrong-status.md: Pending"

printf 'Project Layer validator tests: %d passed, %d failure(s)\n' "$PASSES" "$FAILURES"
if [[ "$FAILURES" -gt 0 ]]; then
  exit 1
fi