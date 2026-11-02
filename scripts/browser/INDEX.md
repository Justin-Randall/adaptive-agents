# Markdown Browser Scripts

[markdown_browser.py](markdown_browser.py) owns the HTTP server, system/project
navigation, SSE and watchdog implementation. Browser assets remain in
[ui/markdown-browser](../../ui/markdown-browser/).

Keep using the stable [ui.py](../ui.py) command:

```text
py -3 scripts/ui.py serve --target <project-root>
```

The root [markdown_browser.py](../markdown_browser.py) import bridge preserves
older Project Layer launchers. [Script-layout tests](../tests/test-script-layout.py)
verify both entrypoints and canonical-root discovery.
