# Final Artifact Manifest

## Purpose

Use this file as the handoff manifest for stages 11-12, when final DOCX, PDF, PPTX, figure exports, tables, and appendices move from the Mac research console to the laptop finalization environment.

This file does not replace the source records. It records which final artifacts exist, where they live on the Mac, where they should land on the laptop, and whether the copied version was verified.

## Update Rules

- Register every final thesis, defense, appendix, figure export, and spreadsheet artifact before laptop handoff.
- Keep one stable `Artifact Key` for each deliverable, such as `thesis-docx`, `final-pdf`, or `defense-pptx`.
- Link source evidence IDs with `CLM-*`, `FIG-*`, `DATA-*`, and `EXP-*` where applicable.
- Record a checksum when an artifact becomes advisor-ready or final.
- Do not mark an artifact `verified` until it has been opened or rendered on the laptop.

## Status Legend

| Transfer Status | Meaning |
|---|---|
| `pending` | Artifact is expected but not copied or verified yet |
| `copied` | Artifact was copied to the laptop target path |
| `verified` | Laptop copy was opened, rendered, exported, or otherwise checked |
| `blocked` | Handoff cannot proceed until a missing artifact, path, or decision is fixed |

## Artifact Manifest

| Artifact Key | Stage | Source IDs | Mac Source Path | Laptop Target Path | Format | Checksum | Produced By | Transfer Status | Laptop Verification | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| thesis-docx | 11-doc-production | CLM-001/TBD; FIG-001/TBD; DATA-001/TBD | TBD | TBD | docx | TBD | Documents / Pages / optional Word / TBD | pending | pending | main thesis document |
| final-pdf | 11-doc-production | CLM-001/TBD; FIG-001/TBD; DATA-001/TBD | TBD | TBD | pdf | TBD | Documents / LaTeX / PDF export / TBD | pending | pending | final rendered thesis |
| defense-pptx | 12-final-audit-defense | CLM-001/TBD; FIG-001/TBD | TBD | TBD | pptx | TBD | Presentations / PPTX / TBD | pending | pending | defense slide deck |

## Handoff Checklist

| Check | Status | Notes |
|---|---|---|
| All required DOCX/PDF/PPTX artifacts have manifest rows | pending |  |
| Mac source paths exist before transfer | pending |  |
| Checksums are recorded for advisor-ready and final artifacts | pending |  |
| Laptop target paths are filled before final audit | pending |  |
| Laptop copies are opened and verified | pending |  |
| Final artifact versions match `final-audit.md` and `defense-prep.md` | pending |  |
