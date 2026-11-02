#!/usr/bin/env python3
"""Compatibility import for existing Project Layer browser launchers."""

from browser.markdown_browser import *  # noqa: F401,F403
from browser.markdown_browser import main


if __name__ == "__main__":
    raise SystemExit(main())
