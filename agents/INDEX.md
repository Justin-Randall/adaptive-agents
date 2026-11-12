# Agents

These reusable roles describe responsibilities, boundaries, and handoffs across projects. Load relevant roles with the canonical [entrypoint](../AGENTS.md), [index](../INDEX.md), and applicable project and domain guidance. More specific project guidance refines these roles within higher-priority instructions; it does not grant authority the host or user has withheld. Loading guidance does not create a Project Layer.

| Role | Use for |
| --- | --- |
| [Supervisor](supervisor.md) | Plan, delegate, integrate, and drive work to evidenced completion. |
| [Coding](coding.md) | Implement and test code changes. |
| [Documentation](documentation.md) | Implement and verify documentation changes. |
| [CI](ci.md) | Execute and report configured checks and coverage gates. |
| [Dogfood](dogfood.md) | Exercise representative workflows and retain observable evidence. |
| [Review](review.md) | Independently assess changes, risks, and findings. |

Roles are postures, not a promise that the host provides subagents. One agent can perform several roles when delegation is unavailable or prohibited. A supervisor retains accountability for integration and results. Give each delegated agent its objective, role and relevant guidance, scope, constraints, dependencies, expected evidence, and handoff; avoid overlapping edits. Use existing instructions, skills, and playbooks as authoritative guidance rather than copying their full workflows into roles.
