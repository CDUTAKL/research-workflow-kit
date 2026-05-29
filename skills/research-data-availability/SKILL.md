---
name: research-data-availability
description: Use when auditing or drafting thesis data availability, dataset provenance, result-data traceability, data hashes, access restrictions, data dictionaries, or final submission/defense data checks.
---

# Research Data Availability

Use this skill when thesis claims, figures, tables, or experiments need traceable data sources. It adapts useful `nature-data` ideas to a graduation-thesis workflow.

## Core Rules

- Keep `docs/thesis/data-availability.md` as the local data availability source of truth.
- Do not store private datasets, credentials, or restricted data in git.
- Every result claim should trace to source data, processed data, script/notebook, and output artifact.
- Use `DATA-*` for datasets/snapshots and connect them to `CLM-*`, `EXP-*`, and `FIG-*` records according to `evidence-promotion-policy.md`.
- Use `docs/thesis/material-passport.md` for evidence material identity cards when datasets, experiment outputs, figures, readings, or document artifacts become important thesis evidence.
- Record why data cannot be shared when privacy, license, advisor, or project constraints apply.
- Data availability is an audit gate, not a substitute for experiment reproducibility.

## Workflow

Read `references/workflow.md` for the checklist and statement pattern. Read `references/source-map.md` for provenance.

1. Identify claims, figures, tables, and experiments that depend on data.
2. Register each dataset as `DATA-*` with version, path, access level, license/permission, and hash/manifest.
3. Map each `CLM-*` claim to source data, processed data, script/notebook, and artifact.
4. Register evidence-critical datasets, outputs, figures, readings, and final document artifacts in `material-passport.md`.
5. Mark sharing status as public, private, restricted, or TBD.
6. Run or recommend `scripts/audit_data_availability.py`.
7. Route missing experiment details to `$research-experiment-engineering` and missing claim mapping to `$research-results-analysis`.
8. Hand unresolved final issues to `$research-final-audit`.

## Output Contract

Always include:

- dataset records to add or update
- claim-to-data traceability gaps
- access and license/permission status
- hash or manifest status
- data dictionary status
- final availability statement draft or required fixes
- suggested updates to `docs/thesis/data-availability.md`
- material passport updates when data or artifacts become final evidence
