---
applyTo: "**"
---

# {{PROJECT_NAME}} Instructions

No additional project-specific rules were approved during bootstrap.

Add focused rules only after confirming they are specific to this project and do not duplicate an existing authoritative project document.

## User-Facing Validation

For every feature or behavior change that affects a user-facing workflow, identify the actual user-facing surface in the active plan and define an appropriate dogfood scenario. The agent must exercise the changed workflow in its real runtime before handing it to the user for independent validation.

- Use the project's actual runtime and deployment path; do not assume every project has a browser deployment.
- Exercise the changed workflow as a user would and record the scenario, endpoint or runtime, observed result, and relevant evidence in the active plan.
- For browser-based workflows, load the matching web-application instructions from the installed Adaptive Agents guidance and follow its Playwright guidance.
- For workflows without a browser surface, record why browser testing is not applicable and use the project's native runtime proof.
- Do not claim a user-facing change is complete when its planned runtime proof remains pending.