#!/usr/bin/env python3

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile


MANIFEST_NAME = "instruction-load-routes.json"
BASELINE_NAME = "instruction-load-baseline.json"
ALLOWED_CLASSIFICATIONS = {"always", "profile", "conditional", "optional"}
FORMULA = {
    "characterEstimate": "(characters + 3) // 4",
    "estimatedTokens": "max(wordEstimate, characterEstimate)",
    "wordEstimate": "(words * 3 + 1) // 2",
}
USAGE = """Usage:
    bash scripts/check-instruction-load-budget.sh
  bash scripts/check-instruction-load-budget.sh --report
  bash scripts/check-instruction-load-budget.sh --check
  bash scripts/check-instruction-load-budget.sh --update-baseline
"""


class ValidationError(Exception):
    pass


def _reject_unknown_keys(value, allowed, label):
    unknown = sorted(set(value) - set(allowed))
    if unknown:
        raise ValidationError(f"{label} has unexpected properties: {', '.join(unknown)}")


def ceil_word_estimate(words):
    return (words * 3 + 1) // 2


def ceil_character_estimate(characters):
    return (characters + 3) // 4


def normalize_text(text):
    return text.replace("\r\n", "\n").replace("\r", "\n")


def measure_bytes(content, display_path):
    try:
        text = content.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise ValidationError(f"{display_path}: content is not strict UTF-8: {error}") from error

    normalized = normalize_text(text)
    normalized_bytes = normalized.encode("utf-8")
    characters = len(normalized)
    words = len(normalized.split())
    word_estimate = ceil_word_estimate(words)
    character_estimate = ceil_character_estimate(characters)
    return {
        "normalizedBytes": len(normalized_bytes),
        "characters": characters,
        "words": words,
        "wordEstimate": word_estimate,
        "characterEstimate": character_estimate,
        "estimatedTokens": max(word_estimate, character_estimate),
        "sha256": hashlib.sha256(normalized_bytes).hexdigest(),
    }


def _require_int(value, label, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValidationError(f"{label} must be an integer >= {minimum}")
    return value


def _validate_path(path, label):
    if not isinstance(path, str) or not path:
        raise ValidationError(f"{label} must be a non-empty string")
    if "\\" in path or "://" in path or re.match(r"^[A-Za-z]:", path):
        raise ValidationError(f"{label} is not a repository-relative POSIX path: {path}")
    pure_path = PurePosixPath(path)
    if pure_path.is_absolute() or ".." in pure_path.parts:
        raise ValidationError(f"{label} escapes the repository: {path}")
    if any(character in path for character in "*?["):
        raise ValidationError(f"{label} may not contain glob syntax: {path}")


def _validate_file_entry(entry, profile_name, index):
    label = f"profile {profile_name} file {index}"
    if not isinstance(entry, dict):
        raise ValidationError(f"{label} must be an object")
    _reject_unknown_keys(entry, {"path", "classification", "reason"}, label)
    for key in ("path", "classification", "reason"):
        if key not in entry:
            raise ValidationError(f"{label} is missing {key}")
    _validate_path(entry["path"], f"{label} path")
    if entry["classification"] not in ALLOWED_CLASSIFICATIONS:
        raise ValidationError(
            f"{label} classification must be one of {sorted(ALLOWED_CLASSIFICATIONS)}"
        )
    if not isinstance(entry["reason"], str) or not entry["reason"].strip():
        raise ValidationError(f"{label} reason must be a non-empty string")


def validate_and_expand_manifest(manifest, repo_root):
    if not isinstance(manifest, dict):
        raise ValidationError("manifest must be a JSON object")
    _reject_unknown_keys(
        manifest,
        {
            "schemaVersion",
            "metricVersion",
            "highWaterEstimatedTokens",
            "warningEstimatedTokens",
            "profiles",
        },
        "manifest",
    )
    for key in (
        "schemaVersion",
        "metricVersion",
        "highWaterEstimatedTokens",
        "warningEstimatedTokens",
        "profiles",
    ):
        if key not in manifest:
            raise ValidationError(f"manifest is missing {key}")

    if _require_int(manifest["schemaVersion"], "schemaVersion", 1) != 1:
        raise ValidationError("schemaVersion 1 is required")
    if _require_int(manifest["metricVersion"], "metricVersion", 1) != 1:
        raise ValidationError("metricVersion 1 is required")
    high_water = _require_int(manifest["highWaterEstimatedTokens"], "highWaterEstimatedTokens", 1)
    warning = _require_int(manifest["warningEstimatedTokens"], "warningEstimatedTokens", 0)
    if warning > high_water:
        raise ValidationError("warningEstimatedTokens may not exceed highWaterEstimatedTokens")
    if not isinstance(manifest["profiles"], list) or not manifest["profiles"]:
        raise ValidationError("profiles must be a non-empty array")

    profiles_by_name = {}
    profile_order = []
    for index, profile in enumerate(manifest["profiles"]):
        if not isinstance(profile, dict):
            raise ValidationError(f"profile {index} must be an object")
        _reject_unknown_keys(
            profile,
            {"name", "extends", "maxEstimatedTokens", "maxGrowthEstimatedTokens", "files"},
            f"profile {index}",
        )
        for key in ("name", "extends", "files"):
            if key not in profile:
                raise ValidationError(f"profile {index} is missing {key}")
        name = profile["name"]
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ValidationError(f"profile {index} has invalid name: {name!r}")
        if name in profiles_by_name:
            raise ValidationError(f"duplicate profile name: {name}")
        if not isinstance(profile["extends"], list) or not all(
            isinstance(parent, str) for parent in profile["extends"]
        ):
            raise ValidationError(f"profile {name} extends must be an array of names")
        if len(profile["extends"]) != len(set(profile["extends"])):
            raise ValidationError(f"profile {name} has duplicate parent profiles")
        if not isinstance(profile["files"], list):
            raise ValidationError(f"profile {name} files must be an array")
        own_paths = set()
        for file_index, entry in enumerate(profile["files"]):
            _validate_file_entry(entry, name, file_index)
            if entry["path"] in own_paths:
                raise ValidationError(f"profile {name} has duplicate path: {entry['path']}")
            own_paths.add(entry["path"])

        profile_limit = profile.get("maxEstimatedTokens", high_water)
        _require_int(profile_limit, f"profile {name} maxEstimatedTokens", 1)
        if profile_limit > high_water:
            raise ValidationError(f"profile {name} maxEstimatedTokens is looser than the global limit")
        growth_limit = profile.get("maxGrowthEstimatedTokens")
        if growth_limit is not None:
            _require_int(growth_limit, f"profile {name} maxGrowthEstimatedTokens")
        profiles_by_name[name] = profile
        profile_order.append(name)

    expanded_by_name = {}
    visiting = []

    def expand(name):
        if name in expanded_by_name:
            return expanded_by_name[name]
        if name in visiting:
            cycle = " -> ".join(visiting + [name])
            raise ValidationError(f"profile inheritance cycle: {cycle}")
        if name not in profiles_by_name:
            raise ValidationError(f"unknown extended profile: {name}")
        visiting.append(name)
        profile = profiles_by_name[name]
        files = []
        seen = set()
        for parent in profile["extends"]:
            for entry in expand(parent)["files"]:
                if entry["path"] not in seen:
                    files.append(entry)
                    seen.add(entry["path"])
        for entry in profile["files"]:
            if entry["classification"] == "optional":
                continue
            if entry["path"] not in seen:
                files.append(entry)
                seen.add(entry["path"])
        visiting.pop()
        expanded = {
            "name": name,
            "maxEstimatedTokens": profile.get("maxEstimatedTokens", high_water),
            "maxGrowthEstimatedTokens": profile.get("maxGrowthEstimatedTokens"),
            "files": files,
        }
        expanded_by_name[name] = expanded
        return expanded

    expanded_profiles = [expand(name) for name in profile_order]
    root = Path(repo_root).resolve()
    for profile in expanded_profiles:
        for entry in profile["files"]:
            candidate = root / PurePosixPath(entry["path"])
            try:
                candidate.resolve().relative_to(root)
            except ValueError as error:
                raise ValidationError(f"profile {profile['name']} path escapes repository: {entry['path']}") from error
            if not candidate.is_file():
                raise ValidationError(f"profile {profile['name']} missing counted file: {entry['path']}")

    _validate_active_memory(expanded_by_name, root)
    return expanded_profiles


def _validate_active_memory(expanded_by_name, root):
    profile = expanded_by_name.get("adaptive_agents_planned_change")
    if profile is None:
        return
    active_relative = ".adaptive-agents/planning/active/ACTIVE.md"
    paths = {entry["path"] for entry in profile["files"]}
    if active_relative not in paths:
        raise ValidationError(f"profile adaptive_agents_planned_change must count {active_relative}")
    active_path = root / active_relative
    try:
        active_text = normalize_text(active_path.read_bytes().decode("utf-8", errors="strict"))
    except UnicodeDecodeError as error:
        raise ValidationError(f"{active_relative}: content is not strict UTF-8: {error}") from error
    memory_paths = {
        path
        for path in paths
        if path.startswith(".adaptive-agents/planning/active/") and path.endswith(".memory.md")
    }
    if active_text.startswith("# No Active Plan"):
        if memory_paths:
            raise ValidationError("no active plan must omit active work-unit memory")
        return
    match = re.search(r"^- Work Unit: ([A-Za-z0-9_-]+)\s*$", active_text, flags=re.MULTILINE)
    if match is None:
        raise ValidationError("active plan does not declare a Work Unit for memory validation")
    expected = f".adaptive-agents/planning/active/{match.group(1)}.memory.md"
    if memory_paths != {expected}:
        raise ValidationError(f"active plan requires exact memory path {expected}")


def build_baseline(repo_root, manifest, enforce_limits=True):
    root = Path(repo_root).resolve()
    expanded_profiles = validate_and_expand_manifest(manifest, root)
    baseline_profiles = []
    for profile in expanded_profiles:
        measured_files = []
        totals = {
            "normalizedBytes": 0,
            "characters": 0,
            "words": 0,
            "wordEstimate": 0,
            "characterEstimate": 0,
            "estimatedTokens": 0,
        }
        for entry in profile["files"]:
            metrics = measure_bytes((root / entry["path"]).read_bytes(), entry["path"])
            measured = {"path": entry["path"], **metrics}
            measured_files.append(measured)
            for key in ("normalizedBytes", "characters", "words", "wordEstimate", "characterEstimate"):
                totals[key] += metrics[key]
        totals["estimatedTokens"] = max(totals["wordEstimate"], totals["characterEstimate"])
        if enforce_limits and totals["estimatedTokens"] > profile["maxEstimatedTokens"]:
            raise ValidationError(
                f"profile {profile['name']} estimatedTokens {totals['estimatedTokens']} "
                f"exceeds profile limit {profile['maxEstimatedTokens']}"
            )
        baseline_profiles.append(
            {
                "name": profile["name"],
                "maxEstimatedTokens": profile["maxEstimatedTokens"],
                "maxGrowthEstimatedTokens": profile["maxGrowthEstimatedTokens"],
                "files": measured_files,
                "totals": totals,
            }
        )
    return {
        "schemaVersion": manifest["schemaVersion"],
        "metricVersion": manifest["metricVersion"],
        "highWaterEstimatedTokens": manifest["highWaterEstimatedTokens"],
        "warningEstimatedTokens": manifest["warningEstimatedTokens"],
        "formula": FORMULA,
        "profiles": baseline_profiles,
    }


def serialize_baseline(baseline):
    return (json.dumps(baseline, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _load_json(path, label):
    try:
        content = path.read_text(encoding="utf-8", errors="strict")
    except FileNotFoundError as error:
        raise ValidationError(f"missing {label}: {path.name}") from error
    except UnicodeDecodeError as error:
        raise ValidationError(f"{path.name}: content is not strict UTF-8: {error}") from error
    try:
        return json.loads(content)
    except json.JSONDecodeError as error:
        raise ValidationError(f"invalid {label} JSON in {path.name}: {error}") from error


def select_startup_manifest(manifest):
    profiles = manifest.get("profiles") if isinstance(manifest, dict) else None
    if not isinstance(profiles, list):
        raise ValidationError("manifest profiles must be an array")
    startup_profiles = [
        profile for profile in profiles if isinstance(profile, dict) and profile.get("name") == "startup"
    ]
    if len(startup_profiles) != 1:
        raise ValidationError("manifest must define exactly one startup profile")
    return {**manifest, "profiles": startup_profiles}


def validate_baseline(baseline):
    if not isinstance(baseline, dict):
        raise ValidationError("baseline must be a JSON object")
    top_level_keys = {
        "schemaVersion",
        "metricVersion",
        "highWaterEstimatedTokens",
        "warningEstimatedTokens",
        "formula",
        "profiles",
    }
    _reject_unknown_keys(baseline, top_level_keys, "baseline")
    for key in top_level_keys:
        if key not in baseline:
            raise ValidationError(f"baseline is missing {key}")
    _require_int(baseline["schemaVersion"], "baseline schemaVersion", 1)
    _require_int(baseline["metricVersion"], "baseline metricVersion", 1)
    _require_int(baseline["highWaterEstimatedTokens"], "baseline highWaterEstimatedTokens", 1)
    _require_int(baseline["warningEstimatedTokens"], "baseline warningEstimatedTokens", 0)
    if baseline["formula"] != FORMULA:
        raise ValidationError("baseline formula does not match metricVersion 1")
    if not isinstance(baseline["profiles"], list):
        raise ValidationError("baseline profiles must be an array")

    metric_keys = {
        "normalizedBytes",
        "characters",
        "words",
        "wordEstimate",
        "characterEstimate",
        "estimatedTokens",
    }
    profile_names = set()
    for profile_index, profile in enumerate(baseline["profiles"]):
        if not isinstance(profile, dict):
            raise ValidationError(f"baseline profile {profile_index} must be an object")
        name = profile.get("name", profile_index)
        profile_keys = {
            "name",
            "maxEstimatedTokens",
            "maxGrowthEstimatedTokens",
            "files",
            "totals",
        }
        _reject_unknown_keys(profile, profile_keys, f"baseline profile {name}")
        for key in profile_keys:
            if key not in profile:
                raise ValidationError(f"baseline profile {name} is missing {key}")
        if not isinstance(profile["name"], str) or not profile["name"]:
            raise ValidationError(f"baseline profile {profile_index} has invalid name")
        if profile["name"] in profile_names:
            raise ValidationError(f"baseline has duplicate profile: {profile['name']}")
        profile_names.add(profile["name"])
        _require_int(profile["maxEstimatedTokens"], f"baseline profile {name} maxEstimatedTokens", 1)
        if profile["maxGrowthEstimatedTokens"] is not None:
            _require_int(
                profile["maxGrowthEstimatedTokens"],
                f"baseline profile {name} maxGrowthEstimatedTokens",
            )
        if not isinstance(profile["files"], list):
            raise ValidationError(f"baseline profile {name} files must be an array")
        for file_index, file_metrics in enumerate(profile["files"]):
            if not isinstance(file_metrics, dict):
                raise ValidationError(f"baseline profile {name} file {file_index} must be an object")
            file_keys = metric_keys | {"path", "sha256"}
            _reject_unknown_keys(file_metrics, file_keys, f"baseline profile {name} file {file_index}")
            for key in file_keys:
                if key not in file_metrics:
                    raise ValidationError(f"baseline profile {name} file {file_index} is missing {key}")
            _validate_path(file_metrics["path"], f"baseline profile {name} file {file_index} path")
            if not isinstance(file_metrics["sha256"], str) or not re.fullmatch(
                r"[0-9a-f]{64}", file_metrics["sha256"]
            ):
                raise ValidationError(f"baseline profile {name} file {file_index} has invalid sha256")
            for key in metric_keys:
                _require_int(file_metrics[key], f"baseline profile {name} file {file_index} {key}")
        if not isinstance(profile["totals"], dict):
            raise ValidationError(f"baseline profile {name} totals must be an object")
        _reject_unknown_keys(profile["totals"], metric_keys, f"baseline profile {name} totals")
        for key in metric_keys:
            if key not in profile["totals"]:
                raise ValidationError(f"baseline profile {name} totals is missing {key}")
            _require_int(profile["totals"][key], f"baseline profile {name} totals {key}")


def _profile_map(baseline):
    return {profile["name"]: profile for profile in baseline.get("profiles", [])}


def _baseline_diagnostics(current, committed):
    diagnostics = []
    committed_profiles = _profile_map(committed) if isinstance(committed, dict) else {}
    current_profiles = _profile_map(current)
    if current.get("schemaVersion") != committed.get("schemaVersion"):
        diagnostics.append(
            f"stale baseline: schemaVersion baseline={committed.get('schemaVersion')} "
            f"current={current.get('schemaVersion')} delta=version"
        )
    if current.get("metricVersion") != committed.get("metricVersion"):
        diagnostics.append(
            f"stale baseline: metricVersion baseline={committed.get('metricVersion')} "
            f"current={current.get('metricVersion')} delta=version"
        )
    for profile in current["profiles"]:
        old_profile = committed_profiles.get(profile["name"])
        if old_profile is None:
            diagnostics.append(f"profile {profile['name']}: stale baseline missing profile; delta=added")
            continue
        old_files = {item["path"]: item for item in old_profile.get("files", [])}
        new_paths = [item["path"] for item in profile["files"]]
        old_paths = [item["path"] for item in old_profile.get("files", [])]
        if new_paths != old_paths:
            diagnostics.append(
                f"profile {profile['name']}: stale baseline route paths baseline={old_paths} "
                f"current={new_paths} delta=route-drift"
            )
        for item in profile["files"]:
            old_item = old_files.get(item["path"])
            if old_item is None:
                continue
            for metric in ("normalizedBytes", "characters", "words", "sha256"):
                if item[metric] != old_item.get(metric):
                    if metric == "sha256":
                        delta = "content-changed"
                    else:
                        delta = item[metric] - old_item.get(metric, 0)
                    diagnostics.append(
                        f"profile {profile['name']} file {item['path']} metric {metric}: "
                        f"stale baseline={old_item.get(metric)} current={item[metric]} delta={delta}"
                    )
        growth_limit = profile.get("maxGrowthEstimatedTokens")
        if growth_limit is not None:
            old_total = old_profile.get("totals", {}).get("estimatedTokens", 0)
            current_total = profile["totals"]["estimatedTokens"]
            growth = current_total - old_total
            if growth > growth_limit:
                diagnostics.append(
                    f"profile {profile['name']} growth limit exceeded: baseline={old_total} "
                    f"current={current_total} delta={growth} limit={growth_limit}"
                )
    for name in committed_profiles:
        if name not in current_profiles:
            diagnostics.append(f"profile {name}: stale baseline profile removed; delta=route-drift")
    if serialize_baseline(current) != serialize_baseline(committed) and not diagnostics:
        diagnostics.append("stale baseline: generated content differs; delta=metadata")
    return diagnostics


def _warning_lines(baseline):
    warning = baseline["warningEstimatedTokens"]
    lines = []
    for profile in baseline["profiles"]:
        total = profile["totals"]["estimatedTokens"]
        if total >= warning:
            utilization = total * 100 / profile["maxEstimatedTokens"]
            lines.append(
                f"WARN: profile {profile['name']} estimatedTokens={total} "
                f"limit={profile['maxEstimatedTokens']} utilization={utilization:.1f}%"
            )
    return lines


def render_report(current, committed=None):
    committed_profiles = _profile_map(committed) if isinstance(committed, dict) else {}
    lines = [
        f"Instruction load budget (schema {current['schemaVersion']}, metric {current['metricVersion']})"
    ]
    for profile in current["profiles"]:
        total = profile["totals"]["estimatedTokens"]
        old_total = committed_profiles.get(profile["name"], {}).get("totals", {}).get("estimatedTokens")
        delta = "n/a" if old_total is None else f"{total - old_total:+d}"
        utilization = total * 100 / profile["maxEstimatedTokens"]
        lines.append(
            f"PROFILE {profile['name']}: estimatedTokens={total} "
            f"limit={profile['maxEstimatedTokens']} utilization={utilization:.1f}% baselineDelta={delta}"
        )
        for item in profile["files"]:
            lines.append(
                f"  {item['path']}: bytes={item['normalizedBytes']} characters={item['characters']} "
                f"words={item['words']} estimatedTokens={item['estimatedTokens']} sha256={item['sha256']}"
            )
        totals = profile["totals"]
        lines.append(
            f"  TOTAL: bytes={totals['normalizedBytes']} characters={totals['characters']} "
            f"words={totals['words']} wordEstimate={totals['wordEstimate']} "
            f"characterEstimate={totals['characterEstimate']} estimatedTokens={totals['estimatedTokens']}"
        )
    lines.extend(_warning_lines(current))
    return "\n".join(lines) + "\n"


def render_status(current):
    startup = next(
        (profile for profile in current["profiles"] if profile["name"] == "startup"), None
    )
    if startup is None:
        raise ValidationError("manifest must define a startup profile for default status")
    total = startup["totals"]["estimatedTokens"]
    limit = startup["maxEstimatedTokens"]
    failed = total > limit
    utilization = total * 100 / limit
    lines = [
        f"Adaptive Agents static startup cost ({len(startup['files'])} counted files)",
        f"STARTUP {'FAIL' if failed else 'PASS'}: used={total:,} estimated tokens "
        f"limit={limit:,} remaining={limit - total:,} utilization={utilization:.1f}%",
    ]
    return "\n".join(lines) + "\n", failed


def update_baseline_atomic(path, baseline):
    data = serialize_baseline(baseline)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(data)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _parse_args(args):
    modes = [argument for argument in args if argument in {"--check", "--report", "--update-baseline"}]
    root = None
    index = 0
    while index < len(args):
        argument = args[index]
        if argument in {"--check", "--report", "--update-baseline"}:
            index += 1
            continue
        if argument == "--repo-root" and index + 1 < len(args):
            root = Path(args[index + 1])
            index += 2
            continue
        raise ValueError
    if len(modes) > 1:
        raise ValueError
    return modes[0] if modes else "--status", root


def run(args, repo_root=None, stdout=sys.stdout, stderr=sys.stderr):
    try:
        mode, argument_root = _parse_args(args)
    except ValueError:
        stderr.write(USAGE)
        return 2
    root = Path(repo_root or argument_root or Path(__file__).resolve().parent.parent).resolve()
    manifest_path = root / MANIFEST_NAME
    baseline_path = root / BASELINE_NAME
    try:
        manifest = _load_json(manifest_path, "route manifest")
        measurement_manifest = manifest if mode == "--report" else select_startup_manifest(manifest)
        current = build_baseline(
            root,
            measurement_manifest,
            enforce_limits=mode in {"--check", "--update-baseline"},
        )
        if mode == "--status":
            status, failed = render_status(current)
            stdout.write(status)
            return 1 if failed else 0
        committed = None
        if baseline_path.is_file():
            committed = _load_json(baseline_path, "baseline")
            validate_baseline(committed)
        if mode == "--report":
            stdout.write(render_report(current, committed))
            return 0
        if mode == "--update-baseline":
            update_baseline_atomic(baseline_path, current)
            stdout.write(f"Updated {BASELINE_NAME}\n")
            for line in _warning_lines(current):
                stdout.write(line + "\n")
            return 0
        if committed is None:
            raise ValidationError(f"missing baseline: {BASELINE_NAME}")
        diagnostics = _baseline_diagnostics(current, committed)
        for line in _warning_lines(current):
            stdout.write(line + "\n")
        if diagnostics:
            for diagnostic in diagnostics:
                stderr.write(f"FAIL: {diagnostic}\n")
            return 1
        stdout.write("Instruction load budget check passed.\n")
        return 0
    except ValidationError as error:
        stderr.write(f"FAIL: {error}\n")
        return 1


def main():
    return run(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())