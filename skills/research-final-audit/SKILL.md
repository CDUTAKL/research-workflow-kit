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
- Choose the audit tier explicitly: `quick`, `advisor`, or `final`.
- Separate scientific issues from formatting issues.
- Prioritize fixes by submission risk.
- Do not silently rewrite claims to be stronger than the evidence.

## Workflow

Read `references/workflow.md` for audit tables and checklists. Read `references/source-map.md` for source provenance.

1. Identify the target artifact: manuscript, thesis, references, figures, LaTeX/PDF, Word document, or slides.
2. Extract quantitative claims, comparisons, scope wording, figure/table captions, and citation-backed statements.
3. Audit claims against raw result files, cited evidence, configs, and rendered figures/tables.
4. Audit citations for existence, metadata accuracy, and claim support.
5. Audit reproducibility records, including run commands, configs, seeds, splits, code version, metric files, output directories, 4060 environment snapshots, code contract checks, and autoresearch verify/guard records when the thesis console exists.
6. Audit tool-layer records when available: task board sync, git version log, spreadsheet exports, and defense prep.
7. Audit data availability records, including dataset provenance, access restrictions, hash/manifest, data dictionary, and claim-to-data traceability.
8. Check section citation coverage for citation-heavy manuscript sections.
9. Check figures, tables, equations, numbering, captions, cross-references, rendering, and publication-grade figure readiness. For final figures, require the Nature-derived figure audit standard or explicit revision items.
10. For defense or paper-to-PPT work, check slide claims, selected figures, speaker notes, and paper-to-slide traceability.
11. Route each issue to the right revision skill and return a prioritized fix list.

## Output Contract

Always include:

- claim audit table
- paper-to-evidence audit table
- citation issue table
- formatting issue table
- figure/table/equation checks
- figure-audit status for final figures and network architecture diagrams
- source-grounded reading status for important citations when Scite is insufficient
- reproducibility checklist issues
- 4060 or cloud environment snapshot issues for cited formal GPU runs
- data availability issues
- section citation map issues
- code contract and autoresearch verify/guard issues
- tool-layer issues: Notion sync, git traceability, spreadsheet staleness, defense slide gaps
- audit-to-revision routing
- compile/export advice
- defense preparation checklist when relevant
- paper-to-PPT or slide-evidence issues when relevant
- final modification priority

Use Scite, Zotero, Semantic Scholar, web search, local files, or LaTeX/Document tools when the user asks for precise verification and those tools are available.
