---
name: research-final-audit
description: Use when performing final checks before submitting, defending, compiling, or revising a research paper, graduation thesis, dissertation, journal manuscript, conference paper, report, response letter, reference list, figure set, or defense presentation.
---

# Research Final Audit

Use this skill as the last quality gate before submission or defense. It checks whether the manuscript's claims, citations, figures, formatting, and presentation materials are ready and traceable.

## Core Rules

- Treat unsupported claims as blockers.
- Verify every quantitative claim against raw result artifacts when files are available.
- Treat unverifiable references as blockers until checked.
- Treat missing data availability for core data-backed claims as a blocker.
- Apply `evidence-promotion-policy.md` before promoting `SEC-*`, `CLM-*`, `EXP-*`, `DATA-*`, or `FIG-*` records to final evidence.
- Apply `id-lifecycle-policy.md` before final writing so deprecated or superseded IDs do not leak into thesis text, figures, slides, or final artifact records.
- Check `final-artifact-manifest.md`, `material-passport.md`, `benchmark-report-schema.md`, `citation-provenance.md`, `zotero-literature-hub.md`, and `zotero-collection-coverage.md` when the project uses those records.
- For formal GPU/cloud results, check both the local output index and remote artifact fields in `experiment-registry.md`: storage backend, remote URI, remote status, and hash/manifest.
- Choose the audit tier explicitly: `quick`, `advisor`, or `final`.
- Use `workflow-dashboard.md`, `research_workflow_doctor.py`, and `evidence-graph.mmd` as navigation aids when the project console is large.
- When the dashboard or evidence graph is shown to an advisor, audit it with Build Web Data Visualization principles: simple truthful visual encodings, readable labels, accessible contrast, and no hidden uncertainty.
- Check `plugin-gate-policy.md` and `plugin-review-log.md` when plugin gates were triggered. Missing review logs are normally P1 issues; treat them as blockers only when the unresolved gate affects local file writing, remote scripts, secrets, or final advisor-facing artifacts.
- Separate scientific issues from formatting issues.
- Prioritize fixes by submission risk.
- Do not silently rewrite claims to be stronger than the evidence.

## Workflow

Read `references/workflow.md` for audit tables and checklists. Read `references/source-map.md` for source provenance.

1. Identify the target artifact: manuscript, thesis, references, figures, LaTeX/PDF, Word document, or slides.
2. Extract quantitative claims, comparisons, scope wording, figure/table captions, and citation-backed statements.
3. Audit claims against raw result files, cited evidence, configs, and rendered figures/tables.
4. Audit citations for existence, metadata accuracy, claim support, provenance, Zotero hub/collection coverage, and export trace.
5. Audit reproducibility and benchmark records, including run commands, configs, seeds, splits, code version, metric files, output directories, local output indexes, 4060/cloud environment snapshots, remote artifact URI/hash/status records, code contract checks, benchmark report schema, material passports, ID lifecycle records, final artifact handoff records, and autoresearch verify/guard records when the thesis console exists.
6. Audit tool-layer records when available: task board sync, git version log, spreadsheet exports, and defense prep.
7. Audit data availability records, including dataset provenance, access restrictions, hash/manifest, data dictionary, and claim-to-data traceability.
8. Check section citation coverage for citation-heavy manuscript sections.
9. Check figures, tables, equations, numbering, captions, cross-references, rendering, and publication-grade figure readiness. For final figures, require the Nature-derived figure audit standard or explicit revision items.
10. Check dashboard/evidence-graph views when they are used for advisor review, defense preparation, or project handoff.
11. Check plugin gate records for Codex Security, Build Web Apps, Data Analytics, Product Design, or CodeRabbit when they were recommended or required by `plugin_gate_advisor.py`.
12. For defense or paper-to-PPT work, check slide claims, selected figures, speaker notes, and paper-to-slide traceability.
13. Route each issue to the right revision skill and return a prioritized fix list.

## Output Contract

Always include:

- claim audit table
- paper-to-evidence audit table
- citation issue table
- formatting issue table
- figure/table/equation checks
- figure-audit status for final figures and network architecture diagrams
- source-grounded reading status for important citations when Scite is insufficient
- citation provenance, Zotero literature hub, bibliography export, and Zotero collection coverage issues
- ID lifecycle issues
- final artifact manifest, Mac production, and Windows compatibility-review issues
- reproducibility checklist issues
- remote experiment artifact URI/hash/status issues
- material passport and benchmark report schema issues
- 4060 or cloud environment snapshot issues for cited formal GPU runs
- data availability issues
- section citation map issues
- workflow dashboard and evidence graph issues
- dashboard/evidence graph visual readability issues
- plugin gate policy/log issues and unresolved required gate status
- code contract and autoresearch verify/guard issues
- tool-layer issues: Notion sync, git traceability, spreadsheet staleness, defense slide gaps
- audit-to-revision routing
- compile/export advice
- defense preparation checklist when relevant
- paper-to-PPT or slide-evidence issues when relevant
- final modification priority

Use Scite, Zotero, Semantic Scholar, web search, local files, or LaTeX/Document tools when the user asks for precise verification and those tools are available.
