# Material Passport

## Purpose

Use this file as the identity card for thesis materials. A material can be a dataset, experiment output, figure, paper-reading note, Zotero collection, code commit, notebook, slide deck, or final document artifact.

This is inspired by academic workflow Material Passport patterns, adapted for a graduation thesis. It does not replace source files; it records where each source lives, how it was produced, and which thesis evidence IDs depend on it.

## Update Rules

- Register important materials before they are used for final `CLM-*` claims, `FIG-*` figures, or defense slides.
- Keep private data paths and access limits explicit, but do not commit secrets, credentials, or private raw data.
- Use stable IDs: `MAT-*` for materials, linked to `SEC-*`, `CLM-*`, `EXP-*`, `DATA-*`, and `FIG-*`.
- Treat `repro_lock` as a configuration record, not a promise that AI-written text or stochastic training is byte-reproducible.

## Material Registry

| Material ID | Type | Title / Description | Source Path / URL | Owner | Created / Updated | Related IDs | Access Level | License / Permission | Integrity Check | Repro Lock | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MAT-001 | dataset/experiment/figure/paper-reading/zotero/code/notebook/slides/document/TBD | TBD | TBD | user/advisor/public/TBD | TBD | CLM-001; EXP-001; DATA-001; FIG-001/TBD | public/private/restricted/TBD | TBD | hash/manifest/commit/TBD | config/seed/env/TBD | planned |  |

## Repro Lock

| Material ID | Code Commit | Config Path | Environment Snapshot | Seed / Split | Command / Notebook | Output Manifest | Replay Status | Notes |
|---|---|---|---|---|---|---|---|---|
| MAT-001 | TBD | TBD | `outputs/EXP-001/environment.txt`/TBD | TBD | TBD | TBD | not_run / smoke_only / replayed / not_applicable / TBD |  |

## Claim Handoff

| Claim ID | Required Materials | Available Materials | Missing Materials | Promotion Ready? | Next Action |
|---|---|---|---|---|---|
| CLM-001 | DATA-001; EXP-001; FIG-001/TBD | MAT-001/TBD | TBD | no | complete material passport before final audit |
