#!/usr/bin/env python3
"""Isolated dogfood entrypoint for the canonical Markdown runtime."""

import codex_total_recall as core
from codex_total_recall import (
    HEADER, SessionStore as MarkdownStore, handle_hook, read_events, read_source,
    recent, render_event, search, text_parts, validate,
)


if __name__ == "__main__":
    raise SystemExit(core.main(require_explicit_root=True))
