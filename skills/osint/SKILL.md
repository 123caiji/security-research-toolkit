---
name: osint
description: "Authorized penetration-testing skill for OSINT. Use for reconnaissance and OSINT, red-team validation, exploitability triage, evidence collection, remediation guidance, and retesting within a written scope."
---

# OSINT

## Owner

- Owner ID: lin


## Operating Rules

- Use only inside an explicitly authorized assessment scope.
- Start by confirming targets, accounts, rate limits, testing window, and forbidden actions.
- Prefer the least intrusive validation that proves exploitability or control failure.
- Record commands, timestamps, request IDs, affected assets, and cleanup actions.

## Workflow

1. Confirm scope, passive collection limits, and attribution-safe collection methods.
2. Collect domains, hosts, certificates, leaked metadata, public code, and exposed services.
3. Normalize findings into target lists, confidence levels, and follow-up hypotheses.
4. Flag high-risk exposures without touching out-of-scope assets.

## Focus Areas

- Identify the trust boundary, prerequisite access, attacker position, and affected asset class.
- Separate confirmed impact from hypotheses, scanner output, and environmental assumptions.
- Keep proof-of-concept steps reproducible but bounded; avoid persistence, data removal, or destructive payloads unless the rules of engagement allow it.
- Link each finding to a concrete fix, compensating control, and retest condition.

## Useful Tools

- scope notes
- intercepting proxy
- target-specific CLI
- evidence log

## Deliverables

- A concise attack narrative or validation path.
- Evidence: sanitized requests, screenshots, logs, payloads, tool output, and affected object IDs.
- Risk rating with exploit prerequisites, likelihood, business impact, and affected scope.
- Remediation guidance and a retest checklist.

## Cleanup And Retest

- Remove test artifacts, temporary accounts, uploaded tools, callbacks, and configuration changes created during validation.
- Preserve sanitized evidence before cleanup so findings remain reproducible.
- Retest the exact affected control after remediation and record pass, fail, or residual-risk status.
