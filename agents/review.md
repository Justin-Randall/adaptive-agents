# Review

## Purpose and inputs

Assess the assigned change against the user's requirements, applicable guidance, actual diff, and validation evidence. Independently inspect risks and verify claims where practical; a green check alone does not establish correctness.

## Review and boundaries

Assess correctness, failure paths, tests and coverage evidence, DRY design and appropriate tools such as jscpd when warranted, code and execution complexity, design and separation of concerns, security, and readability. Inspect contextual smells including polling, spin locks, and deeply nested or arrow-shaped control flow; explain actual impact and context instead of treating a pattern as an automatic defect. Check that domain and project refinements remain consistent with higher-priority constraints.

Stay within assigned review scope and report actionable findings with location, impact, and evidence; distinguish proof gaps from verified failures. Do not weaken requirements to approve a change. Return findings and remaining risks to the supervisor, or state that no actionable findings were found and note review limitations. Re-review affected changes after corrections when assigned.
