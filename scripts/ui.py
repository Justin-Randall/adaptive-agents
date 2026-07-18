#!/usr/bin/env python3
"""Run the system-wide Adaptive Agents Markdown Browser."""

from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from markdown_browser import *  # noqa: F401,F403
from markdown_browser import main


if __name__ == "__main__":
    main()