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
    schemas
    agents
    scripts
  )

  for path in "${required_paths[@]}"; do
    if [[ -e "$path" ]]; then
      pass "Required path exists: $path"
    else
      fail "Required path missing: $path"
    fi
  done
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

extract_top_status() {
  local file="$1"
  grep -Em1 '^- Status: ' "$file" | sed 's/^- Status: *//'
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

check_retrospectives() {
  local retro_file
  local status
  shopt -s nullglob
  local retro_files=(retrospectives/inbox/*.md)
  shopt -u nullglob

  for retro_file in "${retro_files[@]}"; do
    case "$retro_file" in
      retrospectives/inbox/README.md|retrospectives/inbox/template.md)
        continue
        ;;
    esac

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

    if [[ "$status" == "Promoted" ]]; then
      if has_promotion_link "$retro_file"; then
        pass "$retro_file has promotion link"
      else
        fail "$retro_file is promoted but has no promotion link"
      fi
    fi
  done
}

check_retrospective_private_patterns() {
  local matches
  matches="$(grep -RInE 'vscode-file://|workbench\.html|vscode://|[A-Za-z]:\\\\|/Users/|/home/[^ )]+' retrospectives/inbox --include='*.md' || true)"

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
    return ".git" in path.parts or rel_path.startswith("vscode/")


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

check_required_paths
check_prompts
check_retrospectives
check_retrospective_private_patterns
check_markdown_links

printf '\nAdaptive Agents check complete: %d passed, %d failure(s), %d warning(s).\n' "$PASSES" "$FAILURES" "$WARNINGS"

if [[ "$FAILURES" -gt 0 ]]; then
  exit 1
fi