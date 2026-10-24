---
description: "Use when: implementing or changing a web application or browser-based user workflow."
applyTo: "**/*.{html,css,js,jsx,ts,tsx,vue,svelte}"
---

# Web Application Instructions

Apply these requirements only when the changed workflow has a browser-based application surface.

- Identify the affected browser workflow in the active plan and define a Playwright dogfood scenario.
- Use the project's production deployment path and browser URL when deployment is part of the project workflow.
- Use a fresh browser context or session and exercise the changed workflow as a user would.
- Record the scenario, endpoint, observed result, and any console, screenshot, or trace evidence in the active plan.
- Do not claim the browser workflow is complete when automated tests pass but planned browser proof remains pending.
- For changes without a browser surface, record the reason in the active plan instead of inventing a Playwright test.