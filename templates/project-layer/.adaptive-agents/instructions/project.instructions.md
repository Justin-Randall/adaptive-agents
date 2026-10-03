---
applyTo: "**"
---

# {{PROJECT_NAME}} Instructions

No additional project-specific rules were approved during bootstrap.

Add focused rules only after confirming they are specific to this project and do not duplicate an existing authoritative project document.

## User-Facing Browser Validation

For every feature or behavior change that affects a user-facing workflow, identify the browser surface in the active plan and define a Playwright dogfood scenario. The agent must run that scenario against the deployed application before handing the workflow to the user for independent validation.

- Use the project's production deployment path and browser URL.
- Use a fresh browser context or session and exercise the changed workflow as a user would.
- Record the scenario, endpoint, observed result, and any console, screenshot, or trace evidence in the active plan.
- Do not claim the user-facing change is complete when automated tests pass but the deployed browser proof is still pending.
- For changes with no user-facing browser surface, record the reason in the active plan instead of inventing a browser test.