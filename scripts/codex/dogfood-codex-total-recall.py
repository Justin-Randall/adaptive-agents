#!/usr/bin/env python3
"""Opt-in real-model recall test using Codex app-server.

Default: disposable isolated profile. With --installed: existing trusted hooks,
normal profile and stores, and retained original artifacts. Neither mode installs
or changes hook trust. May incur model usage. Requires app-server v2.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import queue
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any
import uuid


REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("recall", REPO / "scripts" / "codex" / "codex_total_recall.py")
assert SPEC and SPEC.loader
RECALL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RECALL)


class Client:
    def __init__(self, executable: str, home: Path, workspace: Path, *, isolated: bool = True) -> None:
        self.messages: queue.Queue[dict[str, Any]] = queue.Queue()
        self.counter = 0
        self.hooks: list[dict[str, Any]] = []
        self.completed: list[dict[str, Any]] = []
        self.items: list[dict[str, Any]] = []
        self.trace: list[dict[str, Any]] = []
        self.errors: list[str] = []
        env = dict(os.environ, CODEX_HOME=str(home))
        if isolated:
            env.update(ADAPTIVE_AGENTS_ROOT=str(workspace),
                       PYTHONIOENCODING="cp1252:surrogateescape", PYTHONUTF8="0")
        self.process = subprocess.Popen(
            [executable, "app-server", "--stdio"], cwd=workspace, env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8",
        )
        threading.Thread(target=self._read, daemon=True).start()
        threading.Thread(target=self._errors, daemon=True).start()
        try:
            self.call("initialize", {"clientInfo": {"name": "total_recall_dogfood", "version": "1"},
                                     "capabilities": {"experimentalApi": True}})
            self.send({"method": "initialized"})
        except (RuntimeError, TimeoutError, OSError):
            self.close()
            raise

    def _read(self) -> None:
        assert self.process.stdout
        for line in self.process.stdout:
            try:
                self.messages.put(json.loads(line))
            except json.JSONDecodeError:
                self.messages.put({"protocol_error": "non-JSON app-server output"})
        self.messages.put({"protocol_error": "app-server exited"})

    def _errors(self) -> None:
        assert self.process.stderr
        for line in self.process.stderr:
            self.errors.append(line)

    def send(self, value: dict[str, Any]) -> None:
        assert self.process.stdin
        self.process.stdin.write(json.dumps(value) + "\n")
        self.process.stdin.flush()

    def receive(self, deadline: float) -> dict[str, Any]:
        try:
            message = self.messages.get(timeout=max(0.01, deadline - time.monotonic()))
        except queue.Empty as exc:
            raise TimeoutError("Codex did not respond within the bounded probe deadline") from exc
        if message.get("protocol_error"):
            raise RuntimeError(str(message["protocol_error"]))
        method = message.get("method")
        if method in {"item/started", "item/completed"}:
            params = message["params"]
            item = params["item"]
            if item.get("type") in {"commandExecution", "fileChange", "agentMessage", "contextCompaction"}:
                self.trace.append({
                    "sequence": len(self.trace) + 1, "method": method,
                    "thread_id": params.get("threadId"), "turn_id": params.get("turnId"),
                    "item": {key: item[key] for key in
                             ("id", "type", "command", "aggregatedOutput", "exitCode", "status", "text", "changes")
                             if key in item},
                })
        if method == "hook/completed":
            run = message["params"]["run"]
            self.hooks.append({"event": run["eventName"], "status": run["status"],
                               "duration_ms": run.get("durationMs"), "details": run})
            print(f"hook {run['eventName']}: {run['status']}", flush=True)
        elif method == "turn/completed":
            self.completed.append(message["params"]["turn"])
        elif method == "item/completed":
            self.items.append(message["params"]["item"])
        elif method == "error":
            raise RuntimeError("Codex provider error: " + str(message["params"].get("error", "unknown error")))
        if method and "id" in message:
            self.send({"id": message["id"], "error": {"code": -32601, "message": "Probe cannot authorize this request"}})
        return message

    def call(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self.counter += 1
        request_id = self.counter
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            message = self.receive(deadline)
            if message.get("id") == request_id and "method" not in message:
                if "error" in message:
                    raise RuntimeError(f"{method}: {message['error']}")
                return message["result"]
        raise TimeoutError(method)

    def wait_turn(self, count: int, *, timeout: float = 600) -> None:
        deadline = time.monotonic() + timeout
        while len(self.completed) == count:
            if time.monotonic() >= deadline:
                raise TimeoutError("Codex turn exceeded the bounded probe deadline")
            self.receive(deadline)
        if self.completed[-1]["status"] != "completed":
            raise RuntimeError(f"Codex turn did not complete: {self.completed[-1].get('error')}")

    def turn(self, thread: str, prompt: str, *, timeout: float = 600) -> str:
        old_count, old_items = len(self.completed), len(self.items)
        self.call("turn/start", {"threadId": thread, "input": [{"type": "text", "text": prompt}]})
        self.wait_turn(old_count, timeout=timeout)
        answers = [item["text"] for item in self.items[old_items:] if item.get("type") == "agentMessage"]
        if not answers:
            raise RuntimeError("Codex completed without a visible answer")
        return answers[-1]

    def close(self) -> None:
        if self.process.stdin and not self.process.stdin.closed:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=15)


def reader_pages(output: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in output.splitlines()
            if line.startswith('{"ledger_line":') and '"next_offset":' in line]


def assistant_capture(answer: str, events: list[dict[str, Any]]) -> dict[str, Any]:
    matches = [event for event in events if event["kind"] == "Stop"
               and event["payload"].get("last_assistant_message") == answer]
    keys = re.findall(r"\b(OBSERVATORY|ORCHARD|CLINIC) KEY: ([A-Z0-9]{8})\b", answer)
    return {
        "characters": len(answer), "sha256": hashlib.sha256(answer.encode("utf-8")).hexdigest(),
        "source_line": matches[0]["sequence"] if len(matches) == 1 else None,
        "keys": dict(keys),
        "checks": {
            "at_least_12000_characters": len(answer) >= 12000,
            "curly_quotes_and_apostrophe": all(char in answer for char in "\u201c\u201d\u2019"),
            "three_distinct_story_keys": len(keys) == 3 and len(dict(keys)) == 3
            and len({value for _, value in keys}) == 3,
            "exact_stop_payload": len(matches) == 1,
        },
    }


def topic_route_labels(index_text: str, source_line: int) -> list[str]:
    labels: list[str] = []
    for label, target in RECALL.MARKDOWN_LINK.findall(RECALL._without_fenced_code(index_text)):
        source, separator, fragment = target.partition("#")
        match = re.fullmatch(r"L(\d+)(?:-L?(\d+))?", fragment)
        span = ((int(match[1]), int(match[2] or match[1]))
                if match and separator and Path(source).name == "ledger.jsonl" else None)
        if span is not None and span[0] <= source_line <= span[1]:
            labels.append(label.casefold())
    return labels


def content_topic_checks(index_text: str, tool_result_line: int) -> dict[str, bool]:
    labels = topic_route_labels(index_text, tool_result_line)
    return {
        "calibration": any("calibrat" in label or "pressure" in label for label in labels),
        "release": any("release" in label or "deploy" in label for label in labels),
        "nesting": any("nest" in label or "wetland" in label or "swallow" in label
                       for label in labels),
    }


def verify_provenance(*, fact: str, source_line: int, index_text: str, context_serialized: str,
                      question: str, trace: list[dict[str, Any]], answer: str) -> dict[str, bool]:
    routes = [(label, target) for label, target in RECALL.MARKDOWN_LINK.findall(index_text)
              if target.endswith(f"ledger.jsonl#L{source_line}-L{source_line}")
              and any(word in label.casefold() for word in ("survey", "archive", "nest", "wetland", "swallow"))]
    completed = [event for event in trace if event["method"] == "item/completed"]
    index_reads = [event for event in completed
                   if event["item"].get("type") == "commandExecution"
                   and event["item"].get("exitCode") == 0
                   and "INDEX.md" in event["item"].get("command", "")
                   and "--read" not in event["item"].get("command", "")
                   and any(f"[{label}]({target})" in event["item"].get("aggregatedOutput", "")
                           for label, target in routes)]
    source_reads = [event for event in completed
                    if event["item"].get("type") == "commandExecution"
                    and event["item"].get("exitCode") == 0
                    and "--read" in event["item"].get("command", "")
                    and "--line" in event["item"].get("command", "")
                    and any(page["ledger_line"] == source_line
                            for page in reader_pages(event["item"].get("aggregatedOutput", "")))]
    starts = {event["item"]["id"]: event["sequence"] for event in trace if event["method"] == "item/started"}
    index_end = min((event["sequence"] for event in index_reads), default=0)
    source_start = min((starts.get(event["item"]["id"], 0) for event in source_reads), default=0)
    disclosures = [event for event in trace if fact.casefold() in json.dumps(event["item"]).casefold()]
    first_disclosure = min(disclosures, key=lambda event: event["sequence"]) if disclosures else None
    return {
        "fact_absent_from_visible_compacted_context": fact.casefold() not in context_serialized.casefold(),
        "fact_absent_from_index": fact.casefold() not in index_text.casefold(),
        "fact_absent_from_question": fact.casefold() not in question.casefold(),
        "topical_route_observed": bool(index_reads),
        "index_result_precedes_source_call": bool(index_end and source_start > index_end),
        "selected_ledger_range_read": bool(source_reads),
        "first_fact_disclosure_is_ledger_output": first_disclosure is not None and first_disclosure in source_reads,
        "answer_matches_source": fact.casefold() in answer.casefold(),
        "answer_cites_source_line": re.search(rf"(?:\bL{source_line}\b|ledger\.jsonl:{source_line}\b)", answer) is not None,
    }


def compactions(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [record["payload"] for line in stream if (record := json.loads(line)).get("type") == "compacted"]


def prove_provenance(executable: str, home: Path, workspace: Path, thread: str, session: Path,
                     source_line: int, accessions: dict[str, str], proof: dict[str, Any]) -> None:
    client = Client(executable, home, workspace)
    try:
        resumed = client.call("thread/resume", {"threadId": thread, "cwd": str(workspace),
            "sandbox": "workspace-write", "approvalPolicy": "never", "config": {"features.hooks": False}})
        if resumed["thread"]["id"] != thread:
            raise RuntimeError("Provenance test did not resume the original capture thread")
        path = Path(resumed["thread"]["path"]).resolve()
        proof["rollout_path"] = str(path)
        proof["private_profile"] = str(home.resolve())
        # Resume returns extended Windows paths; compare directory identities.
        if not any(parent.samefile(home) for parent in path.parents):
            raise RuntimeError("Provider rollout is outside the private test profile")
        before = compactions(path)
        old_count = len(client.completed)
        client.call("thread/compact/start", {"threadId": thread})
        client.wait_turn(old_count)
        after = compactions(path)
        if len(after) != len(before) + 1:
            raise RuntimeError("No newly persisted native compaction record")
        history = after[-1].get("replacement_history")
        if not isinstance(history, list) or not history:
            proof["compaction_payload_keys"] = list(after[-1])
            raise RuntimeError("Provider did not expose a complete replacement history; context absence is unproven")
        context = json.dumps(history, ensure_ascii=True)
        index = (session / "INDEX.md").read_text(encoding="utf-8")
        graph_text = "\n".join(p.read_text(encoding="utf-8") for p in session.rglob("*.md"))
        candidates = [(sector, value) for sector, value in accessions.items()
                      if value.casefold() not in (context + graph_text).casefold()]
        proof.update({
            "same_thread_id": thread, "native_compactions_before": len(before),
            "native_compactions_after": len(after), "selection": "First seeded accession absent from inspectable replacement-history text and all graph Markdown",
            "eligible_facts": len(candidates), "total_seeded_facts": len(accessions),
            "context_sha256": hashlib.sha256(context.encode()).hexdigest(),
            "context_item_types": [item.get("type") for item in history],
            "opaque_compaction_items": sum(item.get("type") == "compaction" for item in history),
            "full_internal_context_absence_proven": False,
            "absence_evidence": "Inspectable text absence plus a no-tools UNKNOWN control; opaque provider compaction state cannot be decoded or certified.",
            "compacted_visible_messages": [
                item for item in history if item.get("type") == "message"
                and item.get("role") in {"user", "assistant"} and item.get("channel") != "analysis"],
            "context_export_note": "Plaintext occurrence checked across serialized native replacement_history. This does not inspect opaque content. System/developer and reasoning items are not exported.",
            "index_before_retrieval": index, "source_line_range": [source_line, source_line],
            "retrieval_hooks_disabled": True,
        })
        if not candidates:
            raise RuntimeError("All seeded facts survived compaction or appear in the graph; no forgotten-fact proof")
        sector, fact = candidates[0]
        proof["target_sector"], proof["expected_fact"] = sector, fact
        source = RECALL.read_events(session)[source_line - 1]
        if fact not in str(source["payload"].get("tool_response", "")):
            raise RuntimeError("Selected fact is not in the original received tool result")
        proof["original_source_event_id"] = source["event_id"]
        ledger = session / "ledger.jsonl"
        retained = ledger.read_bytes()
        runtime = workspace / "scripts" / "codex" / "codex_total_recall.py"
        runtime_before = runtime.read_bytes()
        proof["ledger_sha256"] = hashlib.sha256(retained).hexdigest()
        proof["runtime_sha256"] = hashlib.sha256(runtime_before).hexdigest()
        control_start = len(client.trace)
        proof["control_question"] = (
            f"Without tools or files, what is the exact archive accession for nesting survey sector {sector}? "
            "If it is unavailable in your current context, answer UNKNOWN. Do not guess.")
        proof["control_answer"] = client.turn(thread, proof["control_question"])
        proof["control_trace"] = client.trace[control_start:]
        if ("UNKNOWN" not in proof["control_answer"].upper()
                or fact.casefold() in proof["control_answer"].casefold()
                or any(event["item"]["type"] == "commandExecution" for event in proof["control_trace"])):
            raise RuntimeError("No-tools control did not establish that the model lacked the answer")
        start = len(client.trace)
        question = (f"Now recover that nesting survey sector {sector} archive accession. "
                    f"First read {session / 'INDEX.md'} for topical context, then follow its linked ledger line range "
                    "using the bounded reader. Do not scan the ledger, read provider history, or use another source. "
                    "Give the accession with a ledger line citation.")
        proof["question"] = question
        proof["answer"] = client.turn(thread, question)
        proof["trace"] = client.trace[start:]
        checks = verify_provenance(fact=fact, source_line=source_line, index_text=index,
                                  context_serialized=context, question=question,
                                  trace=proof["trace"], answer=proof["answer"])
        checks["ledger_unchanged"] = ledger.read_bytes() == retained
        checks["runtime_unchanged"] = runtime.read_bytes() == runtime_before
        checks["no_retrieval_hooks"] = not client.hooks
        checks["source_fixture_deleted"] = not (workspace / "seed.py").exists()
        checks["no_tools_control_unknown"] = True
        proof["checks"] = checks
        if not all(checks.values()):
            raise RuntimeError("Ordered recall provenance failed: " + ", ".join(k for k, v in checks.items() if not v))
        proof["status"] = "passed"
    finally:
        client.close()


def run(executable: str, report: dict[str, Any]) -> None:
    # Python 3.13+ creates TemporaryDirectory with a Windows owner-only ACL.
    # Model workspace files need normal inherited ACLs plus the Codex sandbox.
    # Authentication remains in a separate, private TemporaryDirectory.
    workspace = Path(tempfile.gettempdir()) / f".recall-dogfood-{uuid.uuid4()}"
    workspace.mkdir()
    report["wire_environment"] = {"PYTHONIOENCODING": "cp1252:surrogateescape", "PYTHONUTF8": "0"}
    report["runtime_sha256"] = hashlib.sha256((REPO / "scripts" / "codex" / "codex_total_recall.py").read_bytes()).hexdigest()
    report["template_sha256"] = hashlib.sha256(RECALL.session_index_template_path().read_bytes()).hexdigest()
    report["manual_graph_repair"] = False
    report["hypotheses"] = {
        "capture": "Raw UTF-8 survives the legacy Windows pipe environment, including a complete long final reply.",
        "maintenance": "Real compaction followed by an ordinary continuation produces model-authored topical links to all frozen events.",
        "recall": "With originals unavailable, index-led ledger reads recover both tool and assistant facts; same-thread control and ordering reject answer leakage.",
    }
    try:
        with tempfile.TemporaryDirectory(prefix="recall-private-profile-") as private:
            home = Path(private)
            auth = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "auth.json"
            shutil.copy2(auth, home / "auth.json")
            subprocess.run(["git", "init", "--quiet", str(workspace)], check=True)
            runtime = workspace / "scripts"
            runtime.mkdir()
            shutil.copy2(REPO / "scripts" / "codex" / "codex_total_recall.py", runtime / "codex_total_recall.py")
            templates = workspace / "templates" / "total-recall"
            templates.mkdir(parents=True)
            shutil.copy2(RECALL.session_index_template_path(), templates / RECALL.session_index_template_path().name)
            (workspace / "AGENTS.md").write_text(
                "# Synthetic recall workspace\nOnly access this workspace. Do not read other profiles or credentials. "
                "Use source evidence and meaningful topical links. Never change retained ledgers or runtime code.\n",
                encoding="utf-8",
            )
            config = home / "config.toml"
            config.write_text('approval_policy = "never"\nsandbox_mode = "workspace-write"\n'
                              '[windows]\nsandbox = "unelevated"\n[analytics]\nenabled = false\n', encoding="utf-8")
            store = workspace / "recall"
            hooks = RECALL.hook_configuration(runtime / "codex_total_recall.py")
            for groups in hooks["hooks"].values():
                for group in groups:
                    for handler in group["hooks"]:
                        command = subprocess.list2cmdline(
                            [sys.executable, str(runtime / "codex_total_recall.py"), "--root", str(store)]
                        )
                        handler["command"] = command
                        handler["commandWindows"] = command
            (home / "hooks.json").write_text(json.dumps(hooks), encoding="utf-8")
            client = Client(executable, home, workspace)
            try:
                listing = client.call("hooks/list", {})
                inspected = [hook for entry in listing["data"] for hook in entry["hooks"]]
                if len(inspected) != 10:
                    raise RuntimeError("Unexpected isolated hook set; refusing to trust it")
                with config.open("a", encoding="utf-8") as stream:
                    for hook in inspected:
                        stream.write(f'\n[hooks.state.{json.dumps(hook["key"])}]\n'
                                     f'trusted_hash = {json.dumps(hook["currentHash"])}\n')
            finally:
                client.close()

            values = {"threshold": str(20 + secrets.randbelow(60)), "wait": str(5 + secrets.randbelow(15)),
                      "bridge": "Nacre-" + secrets.token_hex(3)}
            accessions = {sector: "SURVEY-" + secrets.token_hex(12)
                          for sector in ("Aster", "Birch", "Cedar", "Dune", "Elm", "Flint", "Grove", "Heath")}
            fact_a = f"CALIBRATION: The pressure trip is {values['threshold']} kPa. The reference sensor is quarantined because its seal leaks."
            fact_b = f"RELEASE: Hold deployment for {values['wait']} hours after the amber test. A green dashboard alone does not authorize release."
            fact_c = f"WETLAND: The swallow nests under bridge {values['bridge']}. Keep the upstream sluice closed during nesting to prevent flooding."
            noise = "Repeated equipment heartbeat: nominal; no new decision or requirement.\n" * 70
            unicode_note = "\u201cThe keeper\u2019s log\u201d contains caf\u00e9, \u03bb, and \U0001f642."
            payload = fact_a + "\n" + unicode_note + "\n" + noise + fact_b + "\n" + noise + fact_c + "\n"
            payload += "\n".join(f"Nesting survey sector {sector} archive accession: {value}."
                                 for sector, value in accessions.items())
            seed = workspace / "seed.py"
            seed.write_text("import sys\nsys.stdout.buffer.write(" + repr(payload.encode("utf-8")) + ")\n",
                            encoding="utf-8")
            session: Path | None = None
            client = Client(executable, home, workspace)
            try:
                listing = client.call("hooks/list", {})
                if not all(h["trustStatus"] == "trusted" for entry in listing["data"] for h in entry["hooks"]):
                    raise RuntimeError("Isolated hook review was not applied")
                started = client.call("thread/start", {"cwd": str(workspace), "sandbox": "workspace-write",
                                                       "approvalPolicy": "never"})
                report["model"] = started.get("model")
                report["surface"] = "Codex app-server, manual compaction plus fresh-thread retrieval"
                thread = started["thread"]["id"]
                answer = client.turn(thread,
                    "For this turn only, execute python seed.py once and retain its complete output "
                    "(allow 6000 output tokens). Do not edit any index yet. Then stop. "
                    "For survey archive accessions, create topical source routes rather than copying the opaque "
                    "accession values into the index or your replies.")
                report["capture_answer"] = answer
                sessions = [p for p in store.iterdir() if p.is_dir()]
                if len(sessions) != 1:
                    raise RuntimeError("Capture did not create exactly one session")
                session = sessions[0]
                events = RECALL.read_events(session)
                source_lines = [e["sequence"] for e in events if e["kind"] == "PostToolUse"
                                and all(fact in str(e["payload"].get("tool_response", ""))
                                        for fact in (fact_a, fact_b, fact_c, unicode_note))]
                if len(source_lines) != 1:
                    raise RuntimeError("Actual tool output did not capture all three complete synthetic facts")
                receipts = [item for item in client.items if item.get("type") == "commandExecution"
                            and all(value in item.get("aggregatedOutput", "") for value in accessions.values())]
                if len(receipts) != 1:
                    raise RuntimeError("Original completed tool output did not expose every seeded accession")
                report["original_tool_receipt"] = {
                    "item_id": receipts[0]["id"], "command": receipts[0]["command"],
                    "all_accessions_observed": True,
                    "output_sha256": hashlib.sha256(receipts[0]["aggregatedOutput"].encode()).hexdigest(),
                }
                report["tool_result_line"] = source_lines[0]
                seed.unlink()
                report["original_source_removed"] = not seed.exists()
                story = client.turn(thread,
                    "Now write an original three-chapter story directly in your final reply, without tools or files. "
                    "Write at least 12000 characters (aim for 3000 words), with full paragraphs and dialogue using "
                    "real Unicode curly quotes \u201clike this\u201d and curly apostrophes as in keeper\u2019s. "
                    "Chapter one concerns observatory clock calibration; chapter two concerns orchard grafting; "
                    "chapter three concerns clinic refrigeration. Give each chapter concrete mechanisms, decisions, "
                    "characters and consequences, not repetitive padding. In each chapter invent a distinct "
                    "eight-character uppercase alphanumeric inventory key, displaying it exactly once using "
                    "OBSERVATORY KEY: XXXXXXXX, ORCHARD KEY: XXXXXXXX, and CLINIC KEY: XXXXXXXX respectively "
                    "(replace XXXXXXXX with your invented values). Do not repeat those keys in summaries or indexes. "
                    "Do not edit the recall index yet.")
                report["assistant_capture"] = assistant_capture(story, RECALL.read_events(session))
                if not all(report["assistant_capture"]["checks"].values()):
                    raise RuntimeError("Long Unicode assistant capture failed: " + ", ".join(
                        key for key, passed in report["assistant_capture"]["checks"].items() if not passed))
                story_line = report["assistant_capture"]["source_line"]
                report["curation_answer"] = client.turn(thread,
                    "Before we pause, add concise subject routes for the useful tool and story facts to the recall "
                    "index. Do not copy inventory keys or archive accession values into navigation. This is "
                    "deliberate curation, not an all-event coverage audit.")
                report["index_before_compaction"] = (session / "INDEX.md").read_text(encoding="utf-8")
                retained = (session / "ledger.jsonl").read_bytes()
                old_count = len(client.completed)
                client.call("thread/compact/start", {"threadId": thread})
                client.wait_turn(old_count)
                report["maintenance_answer"] = client.turn(thread, "Continue.")
                events = RECALL.read_events(session)
                cutoff = max(e["sequence"] for e in events if e["kind"] == "PostCompact")
                report["snapshot_cutoff"] = cutoff
                report["structural_errors"] = RECALL.validate_session(session, through_ledger_line=cutoff)
                report["ledger_prefix_preserved"] = (session / "ledger.jsonl").read_bytes().startswith(retained)
                if not report["ledger_prefix_preserved"] or seed.exists():
                    raise RuntimeError("Maintenance changed retained evidence or recreated the removed source")
                report["semantic_index"] = (session / "INDEX.md").read_text(encoding="utf-8").replace(str(workspace), "[workspace]").replace(workspace.as_posix(), "[workspace]")
                if report["structural_errors"]:
                    raise RuntimeError("Post-compaction graph has structural gaps")
                index_texts = []
                pending = [session / "INDEX.md"]
                visited = set()
                while pending:
                    source = pending.pop().resolve()
                    if source in visited:
                        continue
                    visited.add(source)
                    text = source.read_text(encoding="utf-8")
                    if source == session / "INDEX.md":
                        text = RECALL.semantic_section(text)
                    index_texts.append(text)
                    for label, target in RECALL.MARKDOWN_LINK.findall(RECALL._without_fenced_code(text)):
                        linked = (source.parent / target.split("#", 1)[0]).resolve()
                        source_range = RECALL.line_range(target.partition("#")[2])
                        if session in linked.parents and linked.suffix == ".md" and linked.is_file():
                            pending.append(linked)
                index_text = "\n".join(index_texts)
                tool_topic_checks = content_topic_checks(index_text, source_lines[0])
                story_labels = topic_route_labels(index_text, story_line)
                report["topic_checks"] = {
                    "calibration_topic": tool_topic_checks["calibration"],
                    "release_topic": tool_topic_checks["release"],
                    "nesting_topic": tool_topic_checks["nesting"],
                    "observatory_reply_topic": any("observatory" in label or "clock" in label for label in story_labels),
                    "orchard_reply_topic": any("orchard" in label or "graft" in label for label in story_labels),
                    "clinic_reply_topic": any("clinic" in label or "refrigerat" in label for label in story_labels),
                }
                if not all(report["topic_checks"].values()):
                    raise RuntimeError("Index lacks meaningful routes for one or more tool-result subjects")
                new_thread = client.call("thread/start", {"cwd": str(workspace), "sandbox": "workspace-write",
                    "approvalPolicy": "never", "config": {"features.hooks": False}})["thread"]["id"]
                start_items = len(client.items)
                report["retrieval_answer"] = client.turn(new_thread,
                    f"This is an independent retrieval test with no prior conversation. Start at {session / 'INDEX.md'}. "
                    "Use only that graph and the bounded source reader it documents; the original source no longer exists. "
                    "Explain: (1) the pressure trip threshold and why the reference sensor is unavailable; "
                    "(2) the release waiting period and whether a green dashboard suffices; "
                    "(3) the swallow's exact nesting location and sluice restriction with its reason. "
                    "(4) the user's original instructions about execution count, output allowance, and index editing. "
                    "(5) the exact observatory, orchard and clinic inventory keys invented in the story. "
                    "Cite ledger line ranges actually consulted. Return a concise answer, not a marker list.")
                response = report["retrieval_answer"].casefold()
                checks = {
                    "pressure_threshold": values["threshold"] in response and "kpa" in response,
                    "sensor_reason": "seal" in response and "leak" in response,
                    "release_wait": values["wait"] in response and "hour" in response,
                    "dashboard_not_sufficient": "green" in response and any(w in response for w in ("not", "insufficient", "alone", "doesn't")),
                    "nest_location": values["bridge"].casefold() in response,
                    "sluice_reason": "closed" in response and "flood" in response,
                    "source_citation": f"L{source_lines[0]}" in report["retrieval_answer"],
                    "user_execution_count": any(word in response for word in ("once", "one time", "single execution")),
                    "user_output_allowance": "6000" in response.replace(",", "") and "token" in response,
                    "user_index_deferral": "index" in response and any(phrase in response for phrase in
                        ("no index", "not edit", "don't edit", "without editing", "defer", "until after compaction")),
                    **{f"{topic.lower()}_key_recalled": value.casefold() in response
                       for topic, value in report["assistant_capture"]["keys"].items()},
                }
                commands = [str(item.get("command", "")) for item in client.items[start_items:] if item.get("type") == "commandExecution"]
                checks["bounded_source_read"] = any("--read" in command and "--line" in command for command in commands)
                checks["index_consulted"] = any("INDEX.md" in command for command in commands)
                pages = []
                for item in client.items[start_items:]:
                    if item.get("type") != "commandExecution":
                        continue
                    for line in str(item.get("aggregatedOutput", "")).splitlines():
                        if line.startswith('{"ledger_line":') and '"next_offset":' in line:
                            page = json.loads(line)
                            pages.append({key: page[key] for key in ("ledger_line", "offset", "next_offset")})
                            pages[-1]["serialized_bytes"] = len(line.encode("utf-8"))
                cursor = 0
                visited_offsets = set()
                for _ in range(len(pages)):
                    candidates = [page for page in pages if page["ledger_line"] == source_lines[0] and page["offset"] == cursor]
                    if not candidates or cursor in visited_offsets:
                        break
                    visited_offsets.add(cursor)
                    cursor = candidates[0]["next_offset"]
                    if cursor is None:
                        break
                checks["all_source_pages_read"] = bool(pages) and cursor is None
                checks["user_source_read"] = any(
                    0 < page["ledger_line"] <= cutoff
                    and events[page["ledger_line"] - 1]["kind"] == "UserPromptSubmit"
                    and page["offset"] == 0 and page["next_offset"] is None for page in pages)
                checks["assistant_source_read"] = any(page["ledger_line"] == story_line for page in pages)
                checks["reader_byte_limit"] = bool(pages) and all(page["serialized_bytes"] <= RECALL.MAX_READ_BYTES for page in pages)
                report["retrieval_pages"] = pages
                report["retrieval_checks"] = checks
                if not all(checks.values()):
                    raise RuntimeError("Fresh-context semantic retrieval failed one or more evidence checks")
                client.close()
                report["provenance"] = {"status": "failed"}
                prove_provenance(executable, home, workspace, thread, session, source_lines[0],
                                 accessions, report["provenance"])
                report["status"] = "passed"
            finally:
                report["hooks"] = client.hooks
                report["hook_failures"] = [hook for hook in client.hooks if hook["status"] == "failed"]
                report["capture_and_maintenance_trace"] = client.trace
                if session is not None:
                    report["graph"] = {p.relative_to(session).as_posix(): p.read_text(encoding="utf-8")
                                       for p in session.rglob("*.md")}
                    report["maintenance_diagnostics"] = [
                        event["adapter_diagnostics"] for event in RECALL.read_events(session)
                        if "adapter_diagnostics" in event]
                client.close()
    finally:
        shutil.rmtree(workspace)


def run_installed(executable: str, report: dict[str, Any]) -> None:
    """Exercise the user's installed hooks; retain every original session artifact."""
    home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).resolve()
    managed = Path.home() / ".adaptive-agents" / "codex" / "total-recall"
    active = RECALL.read_json(managed / "active.json")
    runtime = (managed / active["version_directory"] / "codex_total_recall.py").resolve()
    if runtime.read_bytes() != (REPO / "scripts" / "codex" / "codex_total_recall.py").read_bytes():
        raise RuntimeError("Installed runtime differs from checkout; no implicit installation is permitted")
    interpreter = RECALL.read_json(runtime.parent / "manifest.json")["python_executable"]
    if not isinstance(interpreter, str) or not Path(interpreter).is_file():
        raise RuntimeError("Installed interpreter is unavailable")
    protected = [home / "config.toml", home / "hooks.json", managed / "active.json",
                 managed / "launcher.py", runtime, runtime.parent / "manifest.json"]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
              for path in protected}
    workspace = managed.parent / "dogfood" / str(uuid.uuid4())
    workspace.mkdir(parents=True)
    report.update(surface="Installed Codex app-server, normal profile and session stores, manual compaction",
                  workspace=str(workspace), codex_home=str(home), installed_runtime=str(runtime),
                  working_directory=str(REPO),
                  installed_manifest=active, configuration_before=before,
                  fixture_interpreter=interpreter,
                  requested_sandbox="workspace-write",
                  artifacts_retained=True, manual_graph_repair=False, hooks_disabled=False,
                  full_internal_context_absence_proven=False)
    print(f"Retained workspace: {workspace}", flush=True)
    accessions = {sector: "SURVEY-" + secrets.token_hex(12)
                  for sector in ("Aster", "Birch", "Cedar", "Dune", "Elm", "Flint", "Grove", "Heath")}
    facts = ["CALIBRATION: Pressure trip is 47 kPa; quarantine the reference sensor because its seal leaks.",
             "RELEASE: Wait 13 hours after the amber test; a green dashboard alone does not authorize release.",
             "WETLAND: Swallows nest beneath Nacre-Delta bridge; keep the upstream sluice closed to prevent flooding.",
             "\u201cThe keeper\u2019s log\u201d preserves caf\u00e9, \u03bb, and \U0001f642 exactly."]
    payload = ("\n" + "Equipment heartbeat nominal.\n" * 80).join(facts)
    payload += "\n" + "\n".join(f"Nesting survey sector {sector} archive accession: {value}."
                                for sector, value in accessions.items())
    seed = workspace / "seed.py"
    seed.write_text("import sys\nsys.stdout.buffer.write(" + repr(payload.encode("utf-8")) + ")\n",
                    encoding="utf-8")
    client = Client(executable, home, REPO, isolated=False)
    session: Path | None = None
    try:
        listing = client.call("hooks/list", {})
        installed_hooks = [hook for entry in listing["data"] for hook in entry["hooks"]
                           if str(managed / "launcher.py") in hook["command"]]
        report["installed_hooks"] = installed_hooks
        if len(installed_hooks) != 10 or any(
                hook["trustStatus"] != "trusted" or not hook["enabled"] for hook in installed_hooks):
            raise RuntimeError("Installed hooks are missing, disabled or untrusted; user review is required")
        started = client.call("thread/start", {"cwd": str(REPO), "sandbox": "workspace-write",
                                                "approvalPolicy": "never"})
        thread = started["thread"]["id"]
        report.update(model=started.get("model"), native_thread_id=thread)
        report["capture_answer"] = client.turn(thread,
            f"This is an authorized installed-hook dogfood session. Work only in the generated fixture directory {workspace} "
            "and the NEW recall session identified by your hooks; canonical guidance may be read. "
            "Never read or modify other sessions, credentials, configuration, runtime code or the benchmark. "
            "Do not modify the repository working directory. "
            f"Do not install, change trust, or launch subagents. Execute & '{interpreter}' '{seed}' once, allowing 6000 "
            "output tokens. Do not edit indexes yet. Do not copy opaque survey accession values into replies "
            "or indexes; create topical source routes when maintenance is requested. Then stop.")
        store = Path.home() / ".adaptive-agents" / "sessions" / "codex"
        mapping = RECALL.read_json(store / "session-map.json")["sessions"]
        if thread not in mapping:
            raise RuntimeError("Installed hooks did not create a normal-store session for the native thread")
        session_id = mapping[thread]["adaptive_session_id"]
        if not isinstance(session_id, str) or str(uuid.UUID(session_id)) != session_id:
            raise RuntimeError("Invalid recall session identifier in the native identity map")
        session = store / session_id
        manifest = RECALL.read_json(session / "manifest.json")
        if manifest["provider_session_id"] != thread:
            raise RuntimeError("Native thread and retained recall manifest disagree")
        report["session_directory"] = str(session)
        print(f"Retained recall session: {session}", flush=True)
        native = client.call("thread/read", {"threadId": thread, "includeTurns": False})["thread"]
        transcript = Path(native["path"])
        if not any(parent.samefile(home) for parent in transcript.resolve().parents):
            raise RuntimeError("Native transcript is not in the selected normal Codex profile")
        report["native_transcript"] = str(transcript)
        print(f"Retained native transcript: {transcript}", flush=True)
        with transcript.open(encoding="utf-8") as stream:
            contexts = [record["payload"] for line in stream
                        if (record := json.loads(line)).get("type") == "turn_context"]
        if not contexts:
            raise RuntimeError("Native transcript has no effective permission context")
        report["effective_sandbox_policy"] = contexts[-1]["sandbox_policy"]
        if report["effective_sandbox_policy"].get("type") != "workspace-write":
            raise RuntimeError("Native model tools are not using the requested workspace-write permission mode")
        events = RECALL.read_events(session)
        report["source_receipt_observed"] = any(
            item.get("type") == "commandExecution" and item.get("exitCode") == 0
            and all(text in item.get("aggregatedOutput", "") for text in facts + list(accessions.values()))
            for item in client.items)
        if not report["source_receipt_observed"]:
            raise RuntimeError("Synthetic source did not execute completely; capture fidelity was not exercised")
        sources = [event["sequence"] for event in events if event["kind"] == "PostToolUse"
                   and all(text in str(event["payload"].get("tool_response", ""))
                           for text in facts + list(accessions.values()))]
        if len(sources) != 1:
            raise RuntimeError("Installed hook did not retain the complete synthetic tool facts")
        report["tool_result_line"] = sources[0]
        seed.unlink()
        report["source_fixture_deleted"] = True
        story = client.turn(thread,
            "Write an original three-chapter story directly in your final reply, with no tools or files. "
            "Use at least 12000 characters, aiming for 3000 words, with full paragraphs and dialogue using "
            "Unicode \u201ccurly quotes\u201d and apostrophes as in keeper\u2019s. The chapters concern observatory "
            "clock calibration, orchard grafting, and clinic refrigeration. Include concrete characters, "
            "mechanisms, decisions and consequences. Invent three distinct eight-character uppercase "
            "alphanumeric keys. Display each once: OBSERVATORY KEY: XXXXXXXX, ORCHARD KEY: XXXXXXXX, "
            "CLINIC KEY: XXXXXXXX (replace placeholders). Never copy the values into indexes or summaries. "
            "Do not edit the recall index yet.")
        report["assistant_capture"] = assistant_capture(story, RECALL.read_events(session))
        if not all(report["assistant_capture"]["checks"].values()):
            raise RuntimeError("Installed long Unicode final-reply capture did not pass its acceptance gates")
        report["curation_answer"] = client.turn(thread,
            "Before we pause, add concise subject routes for the useful tool and story facts to the recall index. "
            "Do not copy inventory keys or archive accession values into navigation. This is deliberate curation, "
            "not an all-event coverage audit.")
        report["index_before_compaction"] = (session / "INDEX.md").read_text(encoding="utf-8")
        prefix = (session / "ledger.jsonl").read_bytes()
        compact_count = len(compactions(transcript))
        old_count = len(client.completed)
        client.call("thread/compact/start", {"threadId": thread})
        client.wait_turn(old_count)
        report["native_compactions_before"] = compact_count
        report["native_compactions_after"] = len(compactions(transcript))
        if report["native_compactions_after"] != compact_count + 1:
            raise RuntimeError("Native transcript does not prove a new real compaction")
        report["maintenance_answer"] = client.turn(thread, "Continue.")
        events = RECALL.read_events(session)
        cutoff = max(event["sequence"] for event in events if event["kind"] == "PostCompact")
        report["snapshot_cutoff"] = cutoff
        report["structural_errors"] = RECALL.validate_session(session, through_ledger_line=cutoff)
        report["ledger_prefix_preserved"] = (session / "ledger.jsonl").read_bytes().startswith(prefix)
        if report["structural_errors"] or not report["ledger_prefix_preserved"]:
            raise RuntimeError("Installed compaction maintenance left gaps or changed retained source bytes")
        graph = "\n".join(path.read_text(encoding="utf-8") for path in session.rglob("*.md"))
        index = (session / "INDEX.md").read_text(encoding="utf-8")
        report["index_after_compaction"] = index
        tool_topic_checks = content_topic_checks(graph, report["tool_result_line"])
        story_labels = topic_route_labels(graph, report["assistant_capture"]["source_line"])
        report["topic_checks"] = {
            **tool_topic_checks,
            "observatory_reply": any("observatory" in label or "clock" in label for label in story_labels),
            "orchard_reply": any("orchard" in label or "graft" in label for label in story_labels),
            "clinic_reply": any("clinic" in label or "refrigerat" in label for label in story_labels),
        }
        if not all(report["topic_checks"].values()):
            raise RuntimeError("Installed graph lacks required tool-content or final-reply topics")
        candidates = [(sector, value) for sector, value in accessions.items() if value not in graph]
        if not candidates:
            raise RuntimeError("Index leaks every accession; no source-only retrieval candidate remains")
        sector, fact = candidates[0]
        fresh = client.call("thread/start", {"cwd": str(REPO), "sandbox": "workspace-write",
                                              "approvalPolicy": "never"})
        retrieval_thread = fresh["thread"]["id"]
        report["retrieval_thread_id"] = retrieval_thread
        start = len(client.trace)
        question = (
            f"This is a read-only recall check for a DIFFERENT retained dogfood session at {session / 'INDEX.md'}. "
            f"Recover the exact archive accession for nesting survey sector {sector}, the pressure limit and "
            "sensor problem, release wait and dashboard constraint, nesting location and sluice rule, "
            "and the three inventory keys in the observatory/orchard/clinic story. "
            "First read that index for topical context, then follow its links using the bounded installed source reader. "
            "Only read the provided graph and its ledger through that reader; do not scan ledgers, read native "
            "transcripts, inspect other sessions or edit the target session. Do not infer values from earlier context. "
            "Cite source ledger lines in the answer.")
        ledger_before = (session / "ledger.jsonl").read_bytes()
        report["retrieval_question"] = question
        report["retrieval_answer"] = client.turn(retrieval_thread, question)
        report["retrieval_trace"] = client.trace[start:]
        retrieval_mapping = RECALL.read_json(store / "session-map.json")["sessions"][retrieval_thread]
        report["retrieval_session_directory"] = str(store / retrieval_mapping["adaptive_session_id"])
        checks = verify_provenance(fact=fact, source_line=sources[0], index_text=index,
                                  context_serialized="", question=question,
                                  trace=report["retrieval_trace"], answer=report["retrieval_answer"])
        # This native-profile proof uses a new thread, not a same-thread absence control.
        del checks["fact_absent_from_visible_compacted_context"]
        checks["independent_retrieval_thread"] = retrieval_thread != thread
        checks["ledger_unchanged_during_retrieval"] = (session / "ledger.jsonl").read_bytes() == ledger_before
        answer = report["retrieval_answer"].casefold()
        checks.update({f"{topic.lower()}_key_recalled": value.casefold() in answer
                       for topic, value in report["assistant_capture"]["keys"].items()})
        report["retrieval_checks"] = checks
        if not all(checks.values()):
            raise RuntimeError("Installed graph-led retrieval failed: " + ", ".join(k for k, v in checks.items() if not v))
        report["status"] = "passed"
    finally:
        client.close()
        report["hooks"] = client.hooks
        report["hook_failures"] = [hook for hook in client.hooks if hook["status"] == "failed"]
        report["trace"] = client.trace
        report["configuration_after"] = {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
            for path in protected}
        report["configuration_unchanged"] = report["configuration_after"] == before
        if session is not None:
            report["retained_file_hashes"] = {
                str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in session.rglob("*") if path.is_file()}
            report["maintenance_diagnostics"] = [
                event["adapter_diagnostics"] for event in RECALL.read_events(session)
                if "adapter_diagnostics" in event]
        if "native_transcript" in report:
            report["native_transcript_sha256"] = hashlib.sha256(
                Path(report["native_transcript"]).read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", required=True, help="path to the installed Codex executable")
    parser.add_argument("--report", type=Path, required=True, help="write synthetic proof results, never credentials")
    parser.add_argument("--installed", action="store_true",
                        help="use existing trusted hooks and normal stores; retain original artifacts (requires user approval)")
    args = parser.parse_args()
    report: dict[str, Any] = {"status": "failed", "automatic_compaction_verified": False}
    try:
        if args.installed:
            run_installed(args.codex, report)
            if not report["configuration_unchanged"]:
                raise RuntimeError("Native configuration or installed runtime changed during the run; do not restore it silently")
        else:
            run(args.codex, report)
        if report.get("hook_failures"):
            raise RuntimeError("Probe observed failed hook invocations")
        print("PASS: real compaction and ordered source retrieval; opaque internal-state absence is not certified", flush=True)
        return 0
    except (OSError, ValueError, RuntimeError, TimeoutError, subprocess.SubprocessError) as exc:
        report["status"] = "failed"
        report["error"] = str(exc)
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(report, indent=2, ensure_ascii=True)
        if not args.installed:
            serialized = re.sub(r"[A-Za-z]:[\\/]+[^\"\n]*?\.recall-dogfood-[0-9a-f-]+", "[workspace]", serialized)
            for spelling in (str(Path.home()), Path.home().as_posix()):
                serialized = serialized.replace(json.dumps(spelling)[1:-1], "[home]")
        args.report.write_text(serialized + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit("ERROR: JSONL dogfood is retired. Use dogfood-codex-markdown.py. Historical reports are unchanged.")
