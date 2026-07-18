#!/usr/bin/env python3
"""Compatibility wrapper for the system-owned Markdown Browser.

Prefer running from the canonical Adaptive Agents repository:

  py -3 scripts/ui.py serve --target .
"""

from pathlib import Path
import sys

SYSTEM_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SYSTEM_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SYSTEM_SCRIPTS))

from markdown_browser import *  # noqa: F401,F403
from markdown_browser import main


if __name__ == "__main__":
    raise SystemExit(main())