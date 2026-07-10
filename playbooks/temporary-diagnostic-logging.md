# Temporary Diagnostic Logging

Use this playbook when a bug investigation needs temporary runtime diagnostics to test a concrete hypothesis across one or more files or subsystems.

## Outcome

Temporary diagnostics should produce searchable evidence, remain scoped to the active investigation, and be removed once the behavior is proven or the hypothesis is abandoned.

## 1. Define the hypothesis

Write one falsifiable hypothesis and the cheapest check that could disprove it. Keep the diagnostics tied to that check; do not add broad exploratory logging without a stated purpose.

## 2. Assign stable diagnostic IDs

Give each diagnostic family a short, unique identifier, for example:

```text
FEATURE_TAG D1
FEATURE_TAG D2
```

Use the same prefix for all logs in the slice and a distinct suffix for each evidence stream. Choose an identifier that is unlikely to collide with existing logs and is easy to search with `rg` or `grep`.

## 3. Register a diagnostic ledger

In the active plan or issue record, record one row per diagnostic with:

- ID and file/function location
- purpose and expected evidence
- phase or change slice where it was added
- explicit removal condition
- status (`Planned`, `Active`, `Proven`, `Removed`, or `Abandoned`)

Add the ledger entry in the same change as the diagnostic whenever practical.

## 4. Collect and interpret evidence

Run the narrowest useful scenario first. Search by the stable prefix, then correlate entries across the relevant logs and timestamps. Update the ledger with what the evidence proved or falsified.

Do not treat a successful test command as proof of the runtime hypothesis when dogfood or a targeted log check is required.

## 5. Clean up on resolution

When the hypothesis is proven, falsified, or replaced:

1. Remove every temporary log associated with the diagnostic IDs.
2. Remove diagnostic-only parameters or plumbing that no longer have a purpose.
3. Mark each ledger row `Removed` or `Abandoned` and record the evidence.
4. Search the source tree for the stable prefix and require zero remaining hits.
5. Run focused build/tests after cleanup.

If the investigation remains open, keep diagnostics active and keep the removal condition visible in the ledger.

## Guardrails

- Prefer structured, low-volume logs over per-tick output; use sampling or transition-only logging for hot paths.
- Never log secrets, credentials, private user data, or unnecessary proprietary payloads.
- Keep diagnostic prefixes out of permanent user-facing behavior and protocol contracts.
- Do not leave temporary logs in source after the plan's cleanup condition is satisfied.
