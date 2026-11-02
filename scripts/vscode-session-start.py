#!/usr/bin/env python3
"""Stable entrypoint for installed VS Code SessionStart hooks."""

from vscode.session_start import main


if __name__ == "__main__":
    raise SystemExit(main())
