#!/usr/bin/env python3
"""Retained Luna comparison using narrative-only, read-only desktop evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("dogfood", Path(__file__).with_name("dogfood-codex-total-recall.py"))
assert SPEC and SPEC.loader
DOGFOOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DOGFOOD)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def retrieval_checks(answer: str, trace: list[dict], source_line: int, sentence: str) -> dict[str, bool]:
    completed = [t for t in trace if t["method"] == "item/completed"
                 and t["item"]["type"] == "commandExecution" and t["item"].get("exitCode") == 0]
    index_reads = [t["sequence"] for t in completed if "INDEX.md" in t["item"].get("command", "")
                   and "<!-- semantic-breadcrumbs:start -->" in t["item"].get("aggregatedOutput", "")]
    sources = []
    texts = []
    for t in completed:
        if "--read" not in t["item"].get("command", ""):
            continue
        pages = [p for p in DOGFOOD.reader_pages(t["item"].get("aggregatedOutput", ""))
                 if p["ledger_line"] == source_line]
        if pages:
            sources.append(t)
            texts.extend(p["text"] for p in pages)
    starts = [t["sequence"] for t in trace if t["method"] == "item/started"
              and any(t["item"]["id"] == s["item"]["id"] for s in sources)]
    expected = sentence.split(": ", 1)[1]
    return {
        "exact": expected in answer,
        "citation": bool(re.search(rf"(?:#L|line\s+|:){source_line}\b", answer, re.I)),
        "source_read": bool(sources),
        "index_before_source": bool(index_reads and starts and min(index_reads) < min(starts)),
        "source_contains_answer": json.dumps(expected, ensure_ascii=False)[1:-1] in "".join(texts),
        "command_budget": len([t for t in trace if t["method"] == "item/completed"
                               and t["item"]["type"] == "commandExecution"]) <= 8,
    }


def run(args: argparse.Namespace, report: dict) -> None:
    workspace = args.workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=False)
    runtime = workspace / "scripts"
    runtime.mkdir()
    adapter = runtime / "codex_total_recall.py"
    shutil.copy2(ROOT / "scripts" / adapter.name, adapter)
    template = workspace / "templates" / "total-recall" / DOGFOOD.RECALL.session_index_template_path().name
    template.parent.mkdir(parents=True)
    shutil.copy2(ROOT / "templates" / "total-recall" / template.name, template)
    report.update(workspace=str(workspace), runtime_sha256=digest(adapter),
                  template_sha256=digest(template), model="gpt-5.6-luna",
                  source_sha256=digest(args.source), mode="narrative-only historical replay",
                  limitations=["Replayed capture history, not regeneration of the original conversation.",
                               "Isolated CLI app-server/manual compaction, not desktop or automatic compaction."])
    paragraphs = []
    with args.source.open(encoding="utf-8") as stream:
        for line in stream:
            event = json.loads(line)
            if event["kind"] == "PreCompact":
                break
            response = event["payload"].get("tool_response")
            if not isinstance(response, str):
                continue
            selected = [s for s in response.splitlines() if re.match(r"Chapter \d+, paragraph \d+:", s)]
            if selected:
                paragraphs.append({"source_line": event["sequence"], "text": "\n".join(selected)})
    if len(paragraphs) < 100:
        raise ValueError("The reference must contain at least 100 received narrative results")
    report["received_narrative_results"] = len(paragraphs)
    report["received_narrative_bytes"] = sum(len(p["text"].encode()) for p in paragraphs)
    report["fixture_sha256"] = hashlib.sha256(json.dumps(paragraphs, ensure_ascii=False).encode()).hexdigest()
    report["budgets"] = {"postcompact_seconds": 60, "coverage_blocks": 0, "root_bytes": 8192,
                         "root_links": 20, "retrieval_commands_per_fact": 8}
    subprocess.run(["git", "init", "--quiet", str(workspace)], check=True)
    (workspace / "AGENTS.md").write_text(
        "# Recall experiment\nOnly access this workspace. Never read credentials, other profiles or the "
        "original benchmark. Never edit retained ledgers or runtime files. Keep a selective topical index "
        "as useful facts arise, without copying exact narrative sentences into navigation.\n", encoding="utf-8")
    store = workspace / "recall"
    with tempfile.TemporaryDirectory(prefix="recall-pivot-private-") as private:
        home = Path(private)
        shutil.copy2(Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "auth.json",
                     home / "auth.json")
        config = home / "config.toml"
        config.write_text('model = "gpt-5.6-luna"\napproval_policy = "never"\nsandbox_mode = "workspace-write"\n'
                          '[windows]\nsandbox = "unelevated"\n[analytics]\nenabled = false\n', encoding="utf-8")
        hooks = DOGFOOD.RECALL.hook_configuration(adapter)
        for groups in hooks["hooks"].values():
            for group in groups:
                for handler in group["hooks"]:
                    command = subprocess.list2cmdline([sys.executable, str(adapter), "--root", str(store)])
                    handler.update(command=command, commandWindows=command)
        (home / "hooks.json").write_text(json.dumps(hooks), encoding="utf-8")
        client = DOGFOOD.Client(args.codex, home, workspace)
        try:
            inspected = [h for entry in client.call("hooks/list", {})["data"] for h in entry["hooks"]]
            if len(inspected) != 10:
                raise RuntimeError("Unexpected isolated hook set")
            with config.open("a", encoding="utf-8") as stream:
                for hook in inspected:
                    stream.write(f'\n[hooks.state.{json.dumps(hook["key"])}]\n'
                                 f'trusted_hash = {json.dumps(hook["currentHash"])}\n')
        finally:
            client.close()
        client = DOGFOOD.Client(args.codex, home, workspace)
        try:
            started = client.call("thread/start", {"cwd": str(workspace), "model": "gpt-5.6-luna",
                                                  "sandbox": "workspace-write", "approvalPolicy": "never"})
            if started.get("model") != "gpt-5.6-luna":
                raise RuntimeError("Requested Luna was not selected")
            thread = started["thread"]["id"]
            report["thread"] = thread
            client.turn(thread, "We are testing recall of a narrative workload. Acknowledge briefly; do not use tools yet.")
            # Only assistant-owned history is seeded. Original received narrative text is unchanged.
            with tempfile.TemporaryDirectory(prefix="recall-pivot-seed-") as seed_dir:
                fixture = Path(seed_dir) / "fixture.json"
                fixture.write_text(json.dumps(paragraphs, ensure_ascii=False), encoding="utf-8")
                code = (
                    "import json,sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); "
                    "import codex_total_recall as r; s=r.SessionStore(Path(sys.argv[2])); "
                    "items=json.loads(Path(sys.argv[3]).read_text(encoding='utf-8')); "
                    "[(s.capture({'session_id':sys.argv[4],'hook_event_name':kind,'turn_id':str(i),"
                    "'tool_name':'fixture','tool_response':text})) "
                    "for i,p in enumerate(items) for kind,text in "
                    "[('PreToolUse','Generate narrative'),('PostToolUse',p['text']),"
                    "('PreToolUse','Probe for compaction'),('PostToolUse','No compaction file found')]]"
                )
                subprocess.run([sys.executable, "-c", code, str(runtime), str(store), str(fixture), thread],
                               check=True, env=dict(os.environ, ADAPTIVE_AGENTS_ROOT=str(workspace)))
            mapping = json.loads((store / "session-map.json").read_text())
            session = store / mapping["sessions"][thread]["adaptive_session_id"]
            report["session"] = str(session)
            retained = (session / "ledger.jsonl").read_bytes()
            events = DOGFOOD.RECALL.read_events(session)
            narrative = [e for e in events if e["kind"] == "PostToolUse"
                         and str(e["payload"].get("tool_response", "")).startswith("Chapter ")]
            source = narrative[2]
            hidden = narrative[-1]
            report["indexed_source_line"] = source["sequence"]
            report["unindexed_source_line"] = hidden["sequence"]
            report["setup_answer"] = client.turn(
                thread, f"Historical narrative payloads have been retained in {session / 'INDEX.md'}. "
                f"Inspect the narrative at ledger line {source['sequence']} using the root's source reader, "
                "and create up to three useful subject breadcrumbs from that evidence. Do not copy exact "
                "sentences into navigation, scan other narrative events or build a batch/probe inventory. "
                "This is a small topic-curation task; stop after those useful routes.")
            report["index_before_compaction"] = (session / "INDEX.md").read_text(encoding="utf-8")
            count = len(client.completed)
            client.call("thread/compact/start", {"threadId": thread})
            client.wait_turn(count)
            begin = time.monotonic()
            trace_start = len(client.trace)
            hook_start = len(client.hooks)
            try:
                report["followup_answer"] = client.turn(thread, "Thank you.", timeout=60)
            finally:
                report["postcompact_seconds"] = round(time.monotonic() - begin, 3)
                report["postcompact_trace"] = client.trace[trace_start:]
                report["postcompact_hooks"] = client.hooks[hook_start:]
                report["index_after_compaction"] = (session / "INDEX.md").read_text(encoding="utf-8")
            index = (session / "INDEX.md").read_text(encoding="utf-8")
            report["index_after_compaction"] = index
            report["root_bytes"] = len(index.encode())
            report["root_links"] = len(DOGFOOD.RECALL.MARKDOWN_LINK.findall(
                DOGFOOD.RECALL.semantic_section(index)))
            report["ledger_prefix_preserved"] = (session / "ledger.jsonl").read_bytes().startswith(retained)
            report["coverage_blocks"] = sum(h["event"].lower() == "stop" and h["status"] == "blocked"
                                             for h in report["postcompact_hooks"])
            report["checks"] = {
                "retention": report["ledger_prefix_preserved"],
                "no_coverage_blocks": report["coverage_blocks"] == 0,
                "foreground_budget": report["postcompact_seconds"] <= 60,
                "root_budget": report["root_bytes"] <= 8192 and report["root_links"] <= 20,
                "indexed_route": bool(DOGFOOD.topic_route_labels(index, source["sequence"])),
                "hidden_has_no_route": not DOGFOOD.topic_route_labels(index, hidden["sequence"]),
                "hooks_healthy": all(h["status"] in {"completed", "blocked"} for h in client.hooks),
            }
            report["retrieval"] = []
            for label, event in (("indexed", source), ("unindexed", hidden)):
                text = event["payload"]["tool_response"]
                sentence = text.splitlines()[-1]
                marker = sentence.split(": ", 1)[0]
                context = client.call("thread/start", {"cwd": str(workspace), "model": "gpt-5.6-luna",
                                                       "sandbox": "workspace-write", "approvalPolicy": "never"})
                offset = len(client.trace)
                answer = client.turn(context["thread"]["id"],
                    f"Use the historical session at {session / 'INDEX.md'}. Retrieve the complete paragraph "
                    f"body for {marker}, including ALL sentences, not just its first sentence. Start with the "
                    "index; if no useful topic route exists, use its "
                    "bounded source search, then exact source reads. Do not inspect other sessions, the "
                    "original corpus, or dump the ledger. Return the complete paragraph body verbatim "
                    "(omit the Chapter/paragraph label) and cite its ledger line. Do not edit the historical index.")
                trace = client.trace[offset:]
                commands = [t for t in trace if t["method"] == "item/completed"
                            and t["item"]["type"] == "commandExecution"]
                checks = retrieval_checks(answer, trace, event["sequence"], sentence)
                search = any("--search" in t["item"].get("command", "")
                             and t["item"].get("exitCode") == 0 for t in commands)
                report["retrieval"].append({"kind": label, "answer": answer, "trace": trace,
                                            "checks": checks,
                                            "search": search, "commands": len(commands)})
                report["checks"][f"{label}_retrieval"] = all(checks.values())
                if label == "unindexed":
                    report["checks"]["unindexed_search"] = search
            report["passed"] = all(report["checks"].values())
        finally:
            report["hooks"] = client.hooks
            report["trace"] = client.trace
            client.close()
            transcripts = workspace / "transcripts"
            if (home / "sessions").exists():
                shutil.copytree(home / "sessions", transcripts)
            report["transcripts"] = str(transcripts)
            report["artifact_hashes"] = {str(p.relative_to(workspace)): digest(p)
                                        for p in workspace.rglob("*")
                                        if p.is_file() and (p.suffix in {".jsonl", ".md"}
                                                           or p.name == "manifest.json")}
    if digest(args.source) != report["source_sha256"]:
        raise RuntimeError("Original evidence changed during replay")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report: dict = {"run_id": str(uuid.uuid4()), "passed": False}
    try:
        run(args, report)
    except (OSError, ValueError, RuntimeError, TimeoutError, subprocess.SubprocessError) as exc:
        report["error"] = str(exc)
    finally:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("passed", "error", "checks", "workspace") if k in report}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit("ERROR: JSONL pivot replay is retired. Use dogfood-codex-markdown.py. Historical reports are unchanged.")
