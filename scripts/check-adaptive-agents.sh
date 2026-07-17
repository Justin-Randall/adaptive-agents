#!/usr/bin/env bash
set -euo pipefail

# check-adaptive-agents.sh
#
# Runs deterministic repository-health checks for the Adaptive Agents knowledgebase.
# The script is read-only: it reports structural drift but does not edit files.

usage() {
  cat <<EOF
Usage:
  bash scripts/check-adaptive-agents.sh [options]

Options:
  --verbose   Print every passing check.
  -h, --help  Show this help.

Checks:
  - required root files and guidance directories exist
  - prompt files have required frontmatter and are routed from INDEX.md and README.md
  - retrospective inbox notes use known status values
  - promoted retrospectives include promotion links
  - checked-in retrospectives avoid blocked private/raw link patterns
  - local Markdown links resolve
  - guidance Markdown files are reachable from INDEX.md through local links
  - canonical and dogfood Project Layers pass their bundled validators
  - Project Layer validator regression tests reject known defects
  - instruction-load budget regression tests pass
  - static startup instruction load remains within budget
  - VS Code integration has a valid deterministic SessionStart hook and read-access trust grant
  - OpenCode config satisfies the single-entrypoint contract
  - Claude Code integration has instructions loading and read-access grant
  - Antigravity integration has instructions loading
EOF
}

VERBOSE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --verbose)
      VERBOSE=1
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

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

detect_repo_root() {
  if command_exists git && git rev-parse --show-toplevel >/dev/null 2>&1; then
    git rev-parse --show-toplevel
    return
  fi

  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "$script_dir/.." && pwd
}

find_python() {
  if python3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
    return 0
  fi

  if python --version >/dev/null 2>&1; then
    PYTHON_CMD=(python)
    return 0
  fi

  if py -3 --version >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
    return 0
  fi

  return 1
}

REPO_ROOT="$(detect_repo_root)"
cd "$REPO_ROOT"

FAILURES=0
WARNINGS=0
PASSES=0

fail() {
  printf 'FAIL: %s\n' "$1"
  FAILURES=$((FAILURES + 1))
}

warn() {
  printf 'WARN: %s\n' "$1"
  WARNINGS=$((WARNINGS + 1))
}

pass() {
  PASSES=$((PASSES + 1))
  if [[ "$VERBOSE" -eq 1 ]]; then
    printf 'PASS: %s\n' "$1"
  fi
}

verbose_evidence() {
  local label="$1"
  local output="$2"
  if [[ "$VERBOSE" -eq 1 && -n "$output" ]]; then
    printf 'EVIDENCE: %s\n%s\n' "$label" "$output"
  fi
}

file_contains() {
  local file="$1"
  local text="$2"
  grep -Fq -- "$text" "$file"
}

check_required_paths() {
  local path
  local required_paths=(
    AGENTS.md
    README.md
    INDEX.md
    instructions
    skills
    playbooks
    prompts
    memory
    retrospectives/inbox
    retrospectives/promoted
    retrospectives/deferred
    retrospectives/rejected
    schemas
    agents
    scripts
    instruction-load-routes.json
    instruction-load-baseline.json
    schemas/instruction-load-routes.schema.json
    schemas/instruction-load-baseline.schema.json
    scripts/check-instruction-load-budget.sh
    scripts/check-instruction-load-budget.py
    scripts/test-instruction-load-budget.py
    .github/workflows/static-validation.yml
    scripts/bootstrap-project-layer.sh
    scripts/inspect-project-layer-upgrade.sh
    scripts/test-project-layer.sh
    scripts/install-opencode.sh
    scripts/test-opencode.sh
    scripts/test-install-vscode.sh
    scripts/test-install.sh
    scripts/vscode-session-start.py
    scripts/test-vscode-session-start.py
    scripts/check-vscode-integration.py
    scripts/test-vscode-integration.py
    .adaptive-agents/INDEX.md
    .adaptive-agents/project-layer.json
    .adaptive-agents/scripts/check-project-layer.sh
    templates/project-layer/template.json
    templates/project-layer/.adaptive-agents/INDEX.md
    templates/project-layer/.adaptive-agents/scripts/check-project-layer.sh
  )

  for path in "${required_paths[@]}"; do
    if [[ -e "$path" ]]; then
      pass "Required path exists: $path"
    else
      fail "Required path missing: $path"
    fi
  done

  if [[ -f "AGENTS.md" ]] && grep -q "ADAPTIVE_AGENTS_GLOBAL_LOADED" "AGENTS.md" 2>/dev/null; then
    pass "AGENTS.md defines the installation sentinel"
  elif [[ -f "AGENTS.md" ]]; then
    fail "AGENTS.md is missing the installation sentinel (ADAPTIVE_AGENTS_GLOBAL_LOADED)"
  fi
}

check_prompt_frontmatter() {
  local prompt_file="$1"
  local frontmatter

  if [[ "$(sed -n '1p' "$prompt_file")" != "---" ]]; then
    fail "$prompt_file is missing opening frontmatter delimiter"
    return
  fi

  frontmatter="$(awk 'NR == 1 { next } /^---$/ { exit } { print }' "$prompt_file")"

  if grep -Eq '^description: .+' <<<"$frontmatter"; then
    pass "$prompt_file has description frontmatter"
  else
    fail "$prompt_file is missing description frontmatter"
  fi

  if grep -Eq '^agent: .+' <<<"$frontmatter"; then
    pass "$prompt_file has agent frontmatter"
  else
    fail "$prompt_file is missing agent frontmatter"
  fi

  if grep -Eq '^argument-hint: .+' <<<"$frontmatter"; then
    pass "$prompt_file has argument-hint frontmatter"
  else
    fail "$prompt_file is missing argument-hint frontmatter"
  fi
}

check_prompts() {
  local prompt_file
  shopt -s nullglob
  local prompt_files=(prompts/*.prompt.md)
  shopt -u nullglob

  if [[ "${#prompt_files[@]}" -eq 0 ]]; then
    fail "No prompt files found under prompts/"
    return
  fi

  for prompt_file in "${prompt_files[@]}"; do
    check_prompt_frontmatter "$prompt_file"

    if file_contains INDEX.md "$prompt_file"; then
      pass "$prompt_file is routed from INDEX.md"
    else
      fail "$prompt_file is not routed from INDEX.md"
    fi

    if file_contains README.md "$prompt_file"; then
      pass "$prompt_file is listed in README.md"
    else
      fail "$prompt_file is not listed in README.md"
    fi
  done
}

check_opencode() {
  # Validates the live OpenCode config against the single-entrypoint contract:
  # one canonical instructions entry, an external_directory read/write grant,
  # and no leftover legacy layers. Skips silently when OpenCode is not set up.
  # Docs: https://opencode.ai/docs/config/  https://opencode.ai/docs/rules/
  #       https://opencode.ai/docs/permissions/
  local config_dir="$HOME/.config/opencode"
  local config_path=""
  local -a PYTHON_CMD=()

  if [[ -f "$config_dir/opencode.jsonc" ]]; then
    config_path="$config_dir/opencode.jsonc"
  elif [[ -f "$config_dir/opencode.json" ]]; then
    config_path="$config_dir/opencode.json"
  else
    return 0
  fi

  if ! find_python; then
    warn "Python not found; cannot validate the OpenCode configuration"
    return 0
  fi

  local check_output
  if check_output="$("${PYTHON_CMD[@]}" - "$config_path" "$REPO_ROOT" <<'PY'
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
repo_root = sys.argv[2].replace("\\", "/")


def clean_jsonc(text):
    """Strip // and /* */ comments and trailing commas, preserving strings."""
    out = []
    i, n = 0, len(text)
    in_string = escape = False
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if in_string:
            out.append(c)
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_string = False
            i += 1
        elif c == '"':
            in_string = True
            out.append(c)
            i += 1
        elif c == "/" and nxt == "/":
            while i < n and text[i] not in "\r\n":
                i += 1
        elif c == "/" and nxt == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
        elif c == ",":
            j = i + 1
            while j < n and text[j].isspace():
                j += 1
            if j < n and text[j] in "}]":
                i += 1
            else:
                out.append(c)
                i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


try:
    config = json.loads(clean_jsonc(config_path.read_text(encoding="utf-8")))
except (json.JSONDecodeError, OSError) as exc:
    print(f"could not parse {config_path}: {exc}")
    raise SystemExit(1)

problems = []

entry = f"{repo_root}/AGENTS.md"
instructions = [
    i.replace("\\", "/") if isinstance(i, str) else i
    for i in config.get("instructions", [])
]
if entry not in instructions:
    problems.append(f"instructions is missing the canonical entry {entry}")

legacy = [
    i for i in instructions
    if isinstance(i, str) and i.startswith(repo_root) and i != entry
]
if legacy:
    problems.append(f"legacy instructions entries remain: {legacy}")

grant = config.get("permission", {}).get("external_directory", {})
if not (isinstance(grant, dict) and grant.get(f"{repo_root}/**") == "allow"):
    problems.append("permission.external_directory does not allow the repository")

print("\n".join(problems))
raise SystemExit(1 if problems else 0)
PY
  )"; then
    pass "OpenCode config satisfies the single-entrypoint contract"
  else
    warn "OpenCode config drift: ${check_output:-unparseable config at $config_path}"
  fi

  local legacy_agents="$config_dir/AGENTS.md"
  if [[ -f "$legacy_agents" ]] && [[ "$(sed -n '1p' "$legacy_agents")" == "# Adaptive Agents — OpenCode Global Rules" ]]; then
    warn "Legacy sentinel-duplicating copy remains: $legacy_agents (re-run scripts/install-opencode.sh)"
  else
    pass "No legacy OpenCode AGENTS.md copy present"
  fi
}

check_claude_code() {
  local claude_md="$HOME/.claude/CLAUDE.md"
  local settings_path="$HOME/.claude/settings.json"
  local -a PYTHON_CMD=()

  if [[ ! -f "$claude_md" ]]; then
    return 0
  fi

  if grep -q "^#==ADAPTIVE_AGENTS_START==" "$claude_md" 2>/dev/null; then
    pass "Claude Code CLAUDE.md has Adaptive Agents delegation section"
  else
    warn "Claude Code CLAUDE.md exists but missing Adaptive Agents delegation section"
  fi

  if grep -Fxq "@$REPO_ROOT/AGENTS.md" "$claude_md" 2>/dev/null; then
    pass "Claude Code CLAUDE.md imports the canonical AGENTS.md"
  else
    warn "Claude Code CLAUDE.md does not import @$REPO_ROOT/AGENTS.md"
  fi

  if [[ ! -f "$settings_path" ]]; then
    warn "Claude Code settings.json is missing the Adaptive Agents repository access grant"
    return 0
  fi

  if ! find_python; then
    warn "Python not found; cannot validate the Claude Code repository access grant"
    return 0
  fi

  if "${PYTHON_CMD[@]}" - "$settings_path" "$REPO_ROOT" >/dev/null 2>&1 <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as settings_file:
    settings = json.load(settings_file)

directories = settings.get("permissions", {}).get("additionalDirectories", [])
raise SystemExit(0 if sys.argv[2] in directories else 1)
PY
  then
    pass "Claude Code settings grant access to the Adaptive Agents repository"
  else
    warn "Claude Code settings do not grant access to the Adaptive Agents repository"
  fi
}

extract_top_status() {
  local file="$1"
  grep -Em1 '^- Status: ' "$file" | sed 's/^- Status: *//'
}

extract_top_scope() {
  local file="$1"
  grep -Em1 '^- Scope: ' "$file" | sed 's/^- Scope: *//'
}

has_promotion_link() {
  local file="$1"
  awk '
    /^## Promotion Links/ { in_links = 1; next }
    /^## / && in_links { exit }
    in_links && /^- \[[^]]+\]\([^)]+\)/ { found = 1 }
    END { exit found ? 0 : 1 }
  ' "$file"
}

check_vscode_integration() {
  local settings_path="${ADAPTIVE_AGENTS_VSCODE_SETTINGS_PATH:-}"
  local hook_path="${ADAPTIVE_AGENTS_VSCODE_HOOK_PATH:-$HOME/.copilot/hooks/adaptive-agents.json}"
  local version_output="${ADAPTIVE_AGENTS_VSCODE_VERSION_OUTPUT:-}"
  local uname_s
  uname_s="$(uname -s 2>/dev/null || echo unknown)"

  if [[ -z "$settings_path" ]]; then
    case "$uname_s" in
      MINGW*|MSYS*|CYGWIN*)
        if [[ -n "${APPDATA:-}" ]]; then
          settings_path="$APPDATA/Code/User/settings.json"
        fi
        ;;
      Darwin*) settings_path="$HOME/Library/Application Support/Code/User/settings.json" ;;
      *) settings_path="$HOME/.config/Code/User/settings.json" ;;
    esac
  fi

  if [[ ! -f "$settings_path" && ! -f "$hook_path" ]] && ! command_exists code; then
    pass "VS Code integration SKIP (VS Code not detected)"
    return 0
  fi
  if ! find_python; then
    warn "Python not found; cannot validate the VS Code integration"
    return 0
  fi
  if [[ -z "$version_output" ]]; then
    if command_exists code; then
      version_output="$(code --version 2>&1 || printf 'unknown')"
    else
      version_output="unknown"
    fi
  fi

  local repo_setting_path
  if command_exists cygpath; then
    repo_setting_path="$(cygpath -m "$REPO_ROOT" 2>/dev/null || printf '%s\n' "$REPO_ROOT")"
  else
    repo_setting_path="$REPO_ROOT"
  fi

  local check_output
  if check_output="$("${PYTHON_CMD[@]}" "$REPO_ROOT/scripts/check-vscode-integration.py" \
    --settings "$settings_path" \
    --hook "$hook_path" \
    --repo-root "$repo_setting_path" \
    --version-output "$version_output")"; then
    pass "VS Code integration has a valid deterministic SessionStart hook and read grant"
  else
    warn "VS Code integration drift: ${check_output:-validator returned no details}"
  fi
  return 0
}

check_antigravity() {
  local context_file="$HOME/.gemini/GEMINI.md"

  # Detect the Antigravity 2.0 desktop app (same logic as install-antigravity.sh)
  local detected=""
  if [[ -n "${LOCALAPPDATA:-}" ]] && [[ -f "$LOCALAPPDATA/Programs/Antigravity/Antigravity.exe" ]]; then
    detected="$LOCALAPPDATA/Programs/Antigravity/Antigravity.exe"
  elif [[ -n "${PROGRAMFILES:-}" ]] && [[ -f "$PROGRAMFILES/Antigravity/Antigravity.exe" ]]; then
    detected="$PROGRAMFILES/Antigravity/Antigravity.exe"
  elif [[ -n "${PROGRAMFILES_X86:-}" ]] && [[ -f "$PROGRAMFILES_X86/Antigravity/Antigravity.exe" ]]; then
    detected="$PROGRAMFILES_X86/Antigravity/Antigravity.exe"
  elif [[ -d "/Applications/Antigravity.app" ]]; then
    detected="/Applications/Antigravity.app"
  elif [[ -f "/opt/antigravity/antigravity" ]]; then
    detected="/opt/antigravity/antigravity"
  elif command_exists antigravity; then
    detected="$(command -v antigravity)"
  fi

  if [[ -z "$detected" ]]; then
    pass "Antigravity 2.0 is not installed (SKIP)"
    return 0
  fi

  if [[ ! -f "$context_file" ]]; then
    warn "Antigravity 2.0 — global context file (~/.gemini/GEMINI.md) does not exist"
    return 0
  fi

  if grep -q "^#==ADAPTIVE_AGENTS_START==" "$context_file" 2>/dev/null; then
    pass "Antigravity 2.0 — ~/.gemini/GEMINI.md has Adaptive Agents delegation section"
  else
    warn "Antigravity 2.0 — ~/.gemini/GEMINI.md exists but missing Adaptive Agents delegation section"
  fi

  if grep -Fxq "@$REPO_ROOT/AGENTS.md" "$context_file" 2>/dev/null; then
    pass "Antigravity 2.0 — ~/.gemini/GEMINI.md imports the canonical AGENTS.md"
  else
    warn "Antigravity 2.0 — ~/.gemini/GEMINI.md does not import @$REPO_ROOT/AGENTS.md"
  fi

  warn "Antigravity 2.0 — File permissions must be granted via one-time dialog (select 'Yes, and always allow' on first access)"
}

check_retrospectives() {
  local retro_file status scope expected_status dir
  local -a retro_files
  for dir in retrospectives/inbox retrospectives/promoted retrospectives/deferred retrospectives/rejected; do
    case "$dir" in
      retrospectives/inbox)     expected_status="Captured" ;;
      retrospectives/promoted)  expected_status="Promoted" ;;
      retrospectives/deferred)  expected_status="Deferred" ;;
      retrospectives/rejected)  expected_status="Rejected" ;;
    esac
    shopt -s nullglob
    retro_files=("$dir"/*.md)
    shopt -u nullglob
    for retro_file in "${retro_files[@]}"; do
      case "$retro_file" in
        retrospectives/inbox/README.md|retrospectives/inbox/template.md)
          continue
          ;;
      esac
      if [[ "$(basename "$retro_file")" == "INDEX.md" ]]; then
        continue
      fi

      if [[ ! "$(basename "$retro_file")" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+\.md$ ]]; then
        fail "$retro_file does not match YYYY-MM-DD-short-title.md"
      else
        pass "$retro_file filename matches convention"
      fi

      status="$(extract_top_status "$retro_file" || true)"
      case "$status" in
        Captured|Deferred|Promoted|Rejected)
          pass "$retro_file uses known status: $status"
          ;;
        "")
          fail "$retro_file is missing top-level status"
          ;;
        *)
          fail "$retro_file uses unknown status: $status"
          ;;
      esac

      # Status-directory invariant: status must match parent directory
      if [[ "$status" != "$expected_status" ]]; then
        fail "$retro_file in ${dir#retrospectives/}/ has status $status but must be $expected_status"
      fi

      scope="$(extract_top_scope "$retro_file" || true)"
      if [[ "$scope" == "User-wide" ]]; then
        pass "$retro_file uses canonical scope: User-wide"
      elif [[ -z "$scope" ]]; then
        fail "$retro_file is missing top-level scope"
      else
        fail "$retro_file uses invalid canonical scope: $scope"
      fi

      if [[ "$status" == "Promoted" ]]; then
        if has_promotion_link "$retro_file"; then
          pass "$retro_file has promotion link"
        else
          fail "$retro_file is promoted but has no promotion link"
        fi
      fi
    done
  done
}

check_retrospective_private_patterns() {
  local matches
  matches="$(grep -RInE 'vscode-file://|workbench\.html|vscode://|[A-Za-z]:\\\\|/Users/|/home/[^ )]+' retrospectives --include='*.md' || true)"

  if [[ -n "$matches" ]]; then
    fail "Checked-in retrospectives contain blocked private/raw link patterns:"
    printf '%s\n' "$matches"
  else
    pass "Checked-in retrospectives avoid blocked private/raw link patterns"
  fi
}

check_markdown_links() {
  local -a PYTHON_CMD=()
  if ! find_python; then
    warn "Python not found; skipping Markdown link resolution check"
    return
  fi

  if "${PYTHON_CMD[@]}" - <<'PY'
import os
import re
import sys
from collections import deque
from pathlib import Path

root = Path.cwd()
link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
skip_prefixes = ("http://", "https://", "mailto:", "#")
failures = []
graph = {}
guidance_roots = {"instructions", "skills", "playbooks", "prompts", "memory", "agents", "schemas"}


def should_skip(path: Path) -> bool:
    rel_path = path.relative_to(root).as_posix()
    return ".git" in path.parts or "node_modules" in path.parts or rel_path.startswith("vscode/") or rel_path.startswith("opencode/")


def normalize_target(source: Path, target: str):
    target = target.strip()
    if not target or target.startswith(skip_prefixes):
        return None
    if "://" in target:
        failures.append(f"{source.relative_to(root).as_posix()}: external or editor URI is not allowed in checked-in guidance link: {target}")
        return None

    clean_target = target.split("#", 1)[0]
    if not clean_target:
        return None

    resolved = (source.parent / clean_target).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        failures.append(f"{source.relative_to(root).as_posix()}: link escapes repository: {target}")
        return None
    if not resolved.exists():
        failures.append(f"{source.relative_to(root).as_posix()}: missing link target: {target}")
        return None
    return resolved

for path in sorted(root.rglob("*.md")):
    rel_path = path.relative_to(root).as_posix()
    if should_skip(path):
        continue

    text = path.read_text(encoding="utf-8")
    graph.setdefault(path.resolve(), set())
    for match in link_pattern.finditer(text):
        resolved = normalize_target(path, match.group(1))
        if resolved and resolved.suffix == ".md" and not should_skip(resolved):
            graph[path.resolve()].add(resolved)

start = (root / "INDEX.md").resolve()
reachable = set()
queue = deque([start])

while queue:
    current = queue.popleft()
    if current in reachable:
        continue
    reachable.add(current)
    for neighbor in graph.get(current, set()):
        if neighbor not in reachable:
            queue.append(neighbor)

for path in sorted(root.rglob("*.md")):
    if should_skip(path):
        continue

    rel_path = path.relative_to(root).as_posix()
    first_part = path.relative_to(root).parts[0]
    if first_part not in guidance_roots:
        continue
    if rel_path.endswith("/.gitkeep"):
        continue

    if path.resolve() not in reachable:
        failures.append(f"{rel_path}: guidance Markdown file is not reachable from INDEX.md through local Markdown links")

if failures:
    print("\n".join(failures))
    sys.exit(1)
PY
  then
    pass "Local Markdown links resolve and guidance files are reachable from INDEX.md"
  else
    fail "Local Markdown link or INDEX.md reachability check failed"
  fi
}

check_project_layer_template() {
  local output
  if output="$(bash templates/project-layer/.adaptive-agents/scripts/check-project-layer.sh 2>&1)"; then
    pass "Canonical Project Layer template passes its validator"
    verbose_evidence "Canonical Project Layer validator" "$output"
  else
    fail "Canonical Project Layer template fails its validator"
    printf '%s\n' "$output"
  fi
}

check_project_layer_tests() {
  local output
  if output="$(bash scripts/test-project-layer.sh 2>&1)"; then
    pass "Project Layer validator regression tests pass"
    verbose_evidence "Project Layer regression tests" "$output"
  else
    fail "Project Layer validator regression tests fail"
    printf '%s\n' "$output"
  fi
}

check_dogfood_project_layer() {
  local output
  if output="$(bash .adaptive-agents/scripts/check-project-layer.sh 2>&1)"; then
    pass "Dogfood Project Layer passes its validator"
    verbose_evidence "Dogfood Project Layer validator" "$output"
  else
    fail "Dogfood Project Layer fails its validator"
    printf '%s\n' "$output"
  fi
}

check_instruction_load_budget() {
  local output
  if output="$(bash scripts/check-instruction-load-budget.sh --check 2>&1)"; then
    pass "Instruction load budget passes"
    if [[ "$VERBOSE" -eq 1 ]]; then
      local status_output
      status_output="$(bash scripts/check-instruction-load-budget.sh 2>&1)"
      verbose_evidence "TOKEN THRESHOLD GATE (warning=26,215; hard limit=32,768; fails above limit)" "$status_output"$'\n'"STRICT BASELINE: $output"
    fi
    if [[ "$output" == *"WARN:"* ]]; then
      printf '%s\n' "$output"
    fi
  else
    fail "Instruction load budget fails"
    printf '%s\n' "$output"
  fi
}

check_instruction_load_budget_tests() {
  local output
  if output="$("${PYTHON_CMD[@]}" scripts/test-instruction-load-budget.py --verbose 2>&1)"; then
    pass "Instruction load budget regression tests pass"
    verbose_evidence "Instruction load budget regression tests" "$output"
  else
    fail "Instruction load budget regression tests fail"
    printf '%s\n' "$output"
  fi
}

check_required_paths
check_project_layer_template
check_project_layer_tests
check_dogfood_project_layer
if find_python; then
  check_instruction_load_budget_tests
else
  fail "Python 3 not found; cannot run instruction load budget regression tests"
fi
check_instruction_load_budget
check_prompts
check_opencode
check_claude_code
check_vscode_integration
check_antigravity
check_retrospectives
check_retrospective_private_patterns
check_markdown_links

printf '\nAdaptive Agents check complete: %d passed, %d failure(s), %d warning(s).\n' "$PASSES" "$FAILURES" "$WARNINGS"

if [[ "$FAILURES" -gt 0 ]]; then
  exit 1
fi