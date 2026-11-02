#!/usr/bin/env python3
"""Retired JSONL recovery entrypoint. No historical files are modified."""

from pathlib import Path
import sys
from typing import Any


def recover(session: Path, transcript: Path, *, apply: bool = False) -> dict[str, Any]:
    raise ValueError(
        "JSON/JSONL recall recovery is deprecated. Start a fresh Codex session "
        "after installing the Markdown runtime. Historical files are unchanged.")


if __name__ == "__main__":
    print("ERROR: JSON/JSONL recall recovery is deprecated; start a fresh Codex session. "
          "Historical files are unchanged.", file=sys.stderr)
    raise SystemExit(1)
