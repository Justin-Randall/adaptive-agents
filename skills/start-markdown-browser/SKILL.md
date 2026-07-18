---
name: start-markdown-browser
description: "Use when: the user asks to start, open, run, dogfood, or browse with the Adaptive Agents Markdown Browser for the current project or another target project."
---

# Start Markdown Browser

Start the system-owned Adaptive Agents Markdown Browser for a target project without making the user remember commands or paths.

## Intent

Use this skill when the user asks for any of these naturally:

- "Start the Adaptive Agents browser."
- "Open the markdown browser for this project."
- "Dogfood the browser here."
- "Browse this project with Adaptive Agents."

Do not ask the user to run setup commands first. Infer the target and start the server when possible.

## Resolve Paths

1. Treat the current workspace folder or Git root as the target project root unless the user names a different target.
2. Resolve the Adaptive Agents home in this order:
   - If `<target>/.adaptive-agents/project-layer.json` exists and contains `adaptiveAgentsHome`, use that path.
   - Otherwise, use the Adaptive Agents repository that contains this skill file. The browser is system-owned and does not require a target Project Layer manifest to start.
3. Verify `<adaptive-agents-home>/scripts/ui.py` exists. If it does not, report that the Adaptive Agents install cannot be found and ask for its path.

## Start Server

1. Use port `8099` by default.
2. If `8099` is already in use, choose the next free port and tell the user which URL to open.
3. Start the server from the Adaptive Agents home:

```bash
py -3 scripts/ui.py serve --target "<target-project-root>" --port <port> --no-open
```

Keep it running in the background when the tool environment supports long-running commands.

## Verify Before Reporting

Before telling the user the browser is ready, fetch `http://127.0.0.1:<port>/api/context` and verify:

- `targetRoot` is the selected target project root, not the Adaptive Agents home unless the target really is Adaptive Agents.
- `systemHome` is the Adaptive Agents home.
- `projectLayerRoot` is `<target-project-root>/.adaptive-agents`.

If the context does not match, stop the server you started and fix the target or port before reporting success. Do not tell the user it is ready when the browser is serving the wrong Project Layer.

## Expected Result

- Project files are served from the selected target root.
- The Project Repo sidebar section shows the selected target root and root Markdown tree. Use it to catch wrong-root starts immediately.
- If the target has `.adaptive-agents/INDEX.md`, the Project Layer sidebar shows that tree.
- If the target has no Project Layer, the browser still starts and can browse target Markdown files; the Project Layer tree may be empty.
- The System sidebar resolves from the Adaptive Agents home that started the browser.

## Response

After starting and verifying the server, answer with only the URL and the resolved target root unless there is a problem. Do not paste the command unless the user asks for implementation details.