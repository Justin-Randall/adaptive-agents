#!/usr/bin/env python3
"""Focused tests for the managed Codex Total Recall runtime installer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

MODULE_PATH = Path(__file__).resolve().parents[1] / "codex_total_recall_installer.py"
SPEC = importlib.util.spec_from_file_location("codex_total_recall_installer", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
RECALL_SPEC = importlib.util.spec_from_file_location("recall", Path(__file__).resolve().parents[1] / "codex_total_recall.py")
assert RECALL_SPEC and RECALL_SPEC.loader
RECALL = importlib.util.module_from_spec(RECALL_SPEC)
RECALL_SPEC.loader.exec_module(RECALL)


class ManagedRuntimeTests(unittest.TestCase):
    def test_existing_installed_reader_survives_checkout_source_relocation(self) -> None:
        old_scripts = Path(self.temporary.name) / "old checkout" / "scripts"
        old_scripts.mkdir(parents=True)
        adapter = old_scripts / "codex_total_recall.py"
        source = Path(__file__).resolve().parents[1]
        shutil.copy2(source / "codex_total_recall.py", adapter)
        runtime = MODULE.ManagedRuntime(
            self.root, adapter, source / "codex_total_recall_launcher.py",
            sys.executable, Path(__file__).resolve().parents[3])
        runtime.install()
        launcher = self.root / "launcher.py"
        capture = subprocess.run(
            [sys.executable, str(launcher), "--root", str(old_scripts / "sessions")],
            input=json.dumps({"session_id": "existing", "hook_event_name": "PostToolUse",
                              "tool_response": "Evidence before source relocation."}).encode("utf-8"),
            capture_output=True, timeout=60)
        self.assertEqual(capture.returncode, 0, capture.stderr)
        session = next(old_scripts.glob("sessions/*/ledger.md")).parent
        event = RECALL.read_events(session)[0]
        active = (self.root / "active.json").read_bytes()
        relocated = old_scripts / "codex"
        relocated.mkdir()
        adapter.rename(relocated / adapter.name)
        read = subprocess.run(
            [sys.executable, str(launcher), "--read", str(session), "--anchor", event["event_id"]],
            cwd=self.temporary.name, capture_output=True, timeout=60)
        self.assertEqual(read.returncode, 0, read.stderr)
        self.assertIn("Evidence before source relocation.", json.loads(read.stdout)["text"])
        self.assertEqual((self.root / "active.json").read_bytes(), active)

    def test_installed_adapter_uses_only_markdown_and_delivers_result_handles(self) -> None:
        runtime = MODULE.ManagedRuntime(
            self.root, Path(__file__).resolve().parents[1] / "codex_total_recall.py",
            Path(__file__).resolve().parents[1] / "codex_total_recall_launcher.py",
            sys.executable, Path(__file__).resolve().parents[3])
        runtime.install()
        store = Path(self.temporary.name) / "markdown sessions"
        result = subprocess.run(
            [sys.executable, str(self.root / "launcher.py"), "--root", str(store)],
            input=json.dumps({"session_id": "markdown-install", "hook_event_name": "PostToolUse",
                              "tool_response": "Received exact result."}).encode("utf-8"),
            capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        ledgers = list(store.glob("*/ledger.md"))
        self.assertEqual(len(ledgers), 1)
        self.assertFalse(list(store.glob("*/ledger.jsonl")))
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("ledger.md#evt-", context)
        self.assertIn("Received exact result.", ledgers[0].read_text(encoding="utf-8"))

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "managed runtime"
        self.source = Path(self.temporary.name) / "codex_total_recall.py"
        self.launcher_source = Path(self.temporary.name) / "codex_total_recall_launcher.py"
        self.source.write_text("print('adapter')\n", encoding="utf-8")
        self.launcher_source.write_text("# stable launcher\n", encoding="utf-8")
        self.runtime = MODULE.ManagedRuntime(
            self.root,
            self.source,
            self.launcher_source,
            sys.executable,
        )

    def test_install_writes_versioned_payload_manifest_and_active_pointer(self) -> None:
        self.runtime.install()

        active = json.loads((self.root / "active.json").read_text(encoding="utf-8"))
        version_dir = self.root / active["version_directory"]
        manifest_path = version_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        adapter = version_dir / "codex_total_recall.py"

        self.assertEqual(manifest["manifest_schema_version"], MODULE.MANIFEST_SCHEMA_VERSION)
        self.assertEqual(manifest["runtime_version"], MODULE.RUNTIME_VERSION)
        self.assertEqual(manifest["minimum_python"], list(MODULE.MINIMUM_PYTHON))
        self.assertEqual(manifest["python_executable"], str(Path(sys.executable).resolve()))
        self.assertEqual(
            manifest["reader"],
            {
                "python_executable": str(Path(sys.executable).resolve()),
                "launcher_path": str((self.root / "launcher.py").resolve()),
            },
        )
        self.assertEqual(
            manifest["files"]["codex_total_recall.py"],
            hashlib.sha256(adapter.read_bytes()).hexdigest(),
        )
        self.assertEqual(adapter.read_text(encoding="utf-8"), "print('adapter')\n")
        self.assertTrue((self.root / "launcher.py").is_file())
        self.runtime.check_installed()

    def test_same_version_install_is_content_idempotent(self) -> None:
        self.runtime.install()
        before = {
            path.relative_to(self.root): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }

        self.runtime.install()

        after = {
            path.relative_to(self.root): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)

    @unittest.skipUnless(os.name == "nt", "Windows inherited ACL regression")
    def test_version_payload_inherits_parent_read_execute_access(self) -> None:
        self.root.mkdir(parents=True)
        environment = dict(os.environ, ADAPTIVE_TEST_RUNTIME=str(self.root))
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if shell is None:
            self.fail("Windows ACL regression requires PowerShell")
        environment.pop("PSModulePath", None)
        setup = subprocess.run(
            [shell, "-NoProfile", "-Command",
             "$acl = Get-Acl -LiteralPath $env:ADAPTIVE_TEST_RUNTIME; "
             "$sid = [System.Security.Principal.SecurityIdentifier]::new('S-1-5-32-545'); "
             "$rule = [System.Security.AccessControl.FileSystemAccessRule]::new("
             "$sid, 'ReadAndExecute', 'ContainerInherit,ObjectInherit', 'None', 'Allow'); "
             "$acl.AddAccessRule($rule); Set-Acl -LiteralPath $env:ADAPTIVE_TEST_RUNTIME -AclObject $acl"],
            env=environment, capture_output=True, text=True, timeout=60)
        self.assertEqual(setup.returncode, 0, setup.stdout + setup.stderr)
        self.runtime.install()
        active = json.loads(self.runtime.active_path.read_text(encoding="utf-8"))
        version = self.root / active["version_directory"]
        result = subprocess.run(
            [shell, "-NoProfile", "-Command",
             "$paths = @($env:ADAPTIVE_TEST_RUNTIME, "
             "(Join-Path $env:ADAPTIVE_TEST_RUNTIME 'codex_total_recall.py'), "
             "(Join-Path $env:ADAPTIVE_TEST_RUNTIME 'manifest.json')); "
             "@(foreach ($path in $paths) { $acl = Get-Acl -LiteralPath $path; "
             "$readers = @($acl.Access | Where-Object { $_.IsInherited -and "
             "$_.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value "
             "-eq 'S-1-5-32-545' -and "
             "($_.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::ReadAndExecute) "
             "-eq [System.Security.AccessControl.FileSystemRights]::ReadAndExecute }); "
             "[ordered]@{ protected = $acl.AreAccessRulesProtected; inherited_readers = $readers.Count } "
             "}) | ConvertTo-Json -Compress"],
            env={**environment, "ADAPTIVE_TEST_RUNTIME": str(version)},
            check=True, capture_output=True, text=True, timeout=60)
        for entry in json.loads(result.stdout):
            self.assertFalse(entry["protected"], "Private staging ACL survived installation")
            self.assertGreater(entry["inherited_readers"], 0, "Parent read access was lost")

    def test_dry_run_does_not_create_runtime_files(self) -> None:
        self.runtime.preview()

        self.assertFalse(self.root.exists())

    def test_health_check_rejects_modified_managed_payload(self) -> None:
        self.runtime.install()
        active = json.loads((self.root / "active.json").read_text(encoding="utf-8"))
        adapter = self.root / active["version_directory"] / "codex_total_recall.py"
        adapter.write_text("print('tampered')\n", encoding="utf-8")

        with self.assertRaisesRegex(MODULE.InstallationError, "hash"):
            self.runtime.check()

    def test_failed_staging_keeps_previous_active_runtime(self) -> None:
        self.runtime.install()
        active_before = (self.root / "active.json").read_bytes()
        self.source.write_text("print('new adapter')\n", encoding="utf-8")

        with patch.object(MODULE.shutil, "copy2", side_effect=OSError("simulated copy failure")):
            with self.assertRaisesRegex(OSError, "simulated copy failure"):
                self.runtime.install()

        self.assertEqual(active_before, (self.root / "active.json").read_bytes())
        self.runtime.check_installed()
        self.assertEqual(
            {path.name for path in (self.root / "staging").iterdir()} if (self.root / "staging").exists() else set(),
            set(),
        )

    def test_modified_stable_launcher_is_not_overwritten(self) -> None:
        self.runtime.install()
        launcher = self.root / "launcher.py"
        launcher.write_text("user change\n", encoding="utf-8")

        with self.assertRaisesRegex(MODULE.InstallationError, "launcher"):
            self.runtime.install()

        self.assertEqual(launcher.read_text(encoding="utf-8"), "user change\n")

    def test_launcher_dispatches_with_canonical_guidance_root(self) -> None:
        marker = Path(self.temporary.name) / "dispatch.json"
        canonical_root = Path(self.temporary.name) / "canonical guidance"
        self.source.write_text(
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "Path(os.environ['ADAPTIVE_TEST_MARKER']).write_text(json.dumps({"
            "'root': os.environ.get('ADAPTIVE_AGENTS_ROOT'), "
            "'arguments': sys.argv[1:]}), encoding='utf-8')\n",
            encoding="utf-8",
        )
        self.runtime = MODULE.ManagedRuntime(
            self.root,
            self.source,
            Path(__file__).resolve().parents[1] / "codex_total_recall_launcher.py",
            sys.executable,
            canonical_root,
        )
        self.runtime.install()
        environment = os.environ.copy()
        environment["ADAPTIVE_TEST_MARKER"] = str(marker)

        result = subprocess.run(
            [sys.executable, str(self.root / "launcher.py"), "session-start", "event.json"],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        dispatch = json.loads(marker.read_text(encoding="utf-8"))
        self.assertEqual(dispatch["root"], str(canonical_root.resolve()))
        self.assertEqual(dispatch["arguments"], ["session-start", "event.json"])

    def test_installed_index_reader_uses_manifest_paths_and_stable_launcher(self) -> None:
        self.runtime = MODULE.ManagedRuntime(
            self.root,
            Path(__file__).resolve().parents[1] / "codex_total_recall.py",
            Path(__file__).resolve().parents[1] / "codex_total_recall_launcher.py",
            sys.executable,
            Path(__file__).resolve().parents[3],
        )
        self.runtime.install()
        store = Path(self.temporary.name) / "installed sessions & user's"
        payload = {
            "session_id": "installed-reader-session",
            "hook_event_name": "SessionStart",
            "cwd": str(self.temporary.name),
        }
        capture = subprocess.run(
            [sys.executable, str(self.root / "launcher.py"), "--root", str(store)],
            input=json.dumps(payload).encode("utf-8"),
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(capture.returncode, 0, capture.stderr.decode("utf-8", errors="replace"))

        mapping = json.loads((store / "session-map.json").read_text(encoding="utf-8"))
        session_id = mapping["sessions"]["installed-reader-session"]["adaptive_session_id"]
        session = store / session_id
        index = (session / "INDEX.md").read_text(encoding="utf-8")
        match = re.search(
            r"<!-- source-reader:start -->\s*```text\n(.*?)\n```",
            index,
            re.DOTALL,
        )
        self.assertIsNotNone(match, "Installed index must contain a rendered source reader")
        assert match is not None
        event = RECALL.read_events(session)[0]
        command = match.group(1).replace("ACTUAL_ANCHOR", event["event_id"])
        self.assertIn(str(Path(sys.executable).resolve()), command)
        self.assertIn(str((self.root / "launcher.py").resolve()), command)
        self.assertNotIn(str(self.root / "versions"), command)

        if os.name == "nt":
            shell = shutil.which("pwsh") or shutil.which("powershell")
            self.assertIsNotNone(shell, "Windows reader regression requires PowerShell")
            assert shell is not None
            args = [shell, "-NoProfile", "-Command", command]
        else:
            args = ["/bin/sh", "-c", command]
        result = subprocess.run(
            args,
            cwd=self.temporary.name,
            env=dict(os.environ, PATH=""),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["source"], "ledger.md#" + event["event_id"])
        search_match = re.search(
            r"<!-- source-search:start -->\s*```text\n(.*?)\n```", index, re.DOTALL)
        self.assertIsNotNone(search_match, "Installed index must contain a rendered source search")
        assert search_match is not None
        args[-1] = search_match.group(1).replace("distinctive phrase", "installed-reader-session")
        searched = subprocess.run(args, cwd=self.temporary.name, env=dict(os.environ, PATH=""),
                                  capture_output=True, text=True, timeout=60)
        self.assertEqual(searched.returncode, 0, searched.stdout + searched.stderr)
        self.assertEqual(json.loads(searched.stdout)["matches"][0]["anchor"], event["event_id"])

    def test_real_installed_adapter_retains_long_raw_utf8_payloads(self) -> None:
        runtime = MODULE.ManagedRuntime(
            self.root, Path(__file__).resolve().parents[1] / "codex_total_recall.py",
            Path(__file__).resolve().parents[1] / "codex_total_recall_launcher.py",
            sys.executable, Path(__file__).resolve().parents[3])
        runtime.install()
        store = Path(self.temporary.name) / "sessions"
        environment = dict(os.environ, PYTHONIOENCODING="cp1252:surrogateescape", PYTHONUTF8="0")
        for index, text in enumerate(("ASCII", "I\u2019ll return.", "\u201cReturn\u201d \u03bb \U0001f642\n" * 6000)):
            payload = {"session_id": "unicode-wire", "hook_event_name": "Stop",
                       "turn_id": str(index), "last_assistant_message": text}
            result = subprocess.run(
                [sys.executable, str(self.root / "launcher.py"), "--root", str(store)],
                input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                capture_output=True, env=environment, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            ledger = next(store.glob("*/ledger.md"))
            events = RECALL.read_events(ledger.parent)
            self.assertEqual(events[-1]["payload"], payload)


if __name__ == "__main__":
    unittest.main()
