# Templates

This directory contains canonical reusable source trees for explicitly bootstrapped project-owned features.

Templates are copied or rendered into target projects by scripts or skills. Keep template files generic, placeholder-driven, and validated by tests where possible.

## Current Templates

- [project-layer](project-layer/template.json) — source template for `.adaptive-agents/` Project Layer bootstrap.

## Versioning

Project Layer templates use SemVer-style pre-1.0 versions: `0.<minor>.<patch>`.

- Increment `patch` for additive documentation, metadata, validation refinements, and bug fixes that do not require project-owned content changes.
- Increment `minor` for new Project Layer capabilities, new required files, migrations, or structural changes that need upgrade review.
- Reserve `1.0.0` for the first stable Project Layer contract.

Do not treat `0.x.y` as a decimal sequence. Versions such as `0.5.12` are valid and expected when a template receives many small additive updates before the next minor capability.
