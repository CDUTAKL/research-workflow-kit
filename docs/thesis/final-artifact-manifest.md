# Final Artifact Manifest

## Purpose

Use this file as the final artifact review manifest for stages 11-12. Stage 11 now produces the main DOCX/PDF/PPTX artifacts on the Mac. Stage 12 verifies the Mac-produced artifacts on the Windows laptop for Word/WPS/PowerPoint compatibility, final submission readiness, and defense playback.

This file does not replace the source records. It records which final artifacts exist, where they live on the Mac, where the Windows review copy should land, and whether the copied version was opened/rendered/checked.

Use the packaging helper before Windows compatibility review:

```bash
python scripts/package_final_handoff.py --update-manifest-checksums
```

After copying the generated zip or extracted directory to the Windows laptop, verify it with:

```bash
python scripts/verify_final_handoff.py final-handoff-YYYYMMDD-HHMMSS.zip --write-report docs/thesis/final-handoff-verify-report.md
```

## Update Rules

- Register every final thesis, defense, appendix, figure export, and spreadsheet artifact before Windows compatibility review.
- Keep one stable `Artifact Key` for each deliverable, such as `thesis-docx`, `final-pdf`, or `defense-pptx`.
- Link source evidence IDs with `CLM-*`, `FIG-*`, `DATA-*`, and `EXP-*` where applicable.
- Record a checksum when an artifact becomes advisor-ready or final.
- Do not mark an artifact `verified` until it has been opened, rendered, exported, or checked on the Windows laptop.

## Status Legend

| Transfer Status | Meaning |
|---|---|
| `pending` | Artifact is expected but not copied or compatibility-verified yet |
| `copied` | Artifact was copied to the Windows review path |
| `verified` | Windows copy was opened, rendered, exported, or otherwise checked |
| `blocked` | Final review cannot proceed until a missing artifact, path, or decision is fixed |

## Artifact Manifest

| Artifact Key | Stage | Source IDs | Mac Source Path | Laptop Target Path | Format | Checksum | Produced By | Transfer Status | Laptop Verification | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| thesis-docx | 11-mac-docx-pdf-pptx-production | CLM-001/TBD; FIG-001/TBD; DATA-001/TBD | TBD | TBD | docx | TBD | WPS / Documents / Pages / TBD | pending | pending | main thesis document, produced on Mac |
| final-pdf | 11-mac-docx-pdf-pptx-production | CLM-001/TBD; FIG-001/TBD; DATA-001/TBD | TBD | TBD | pdf | TBD | WPS / Documents / PDF export / LaTeX optional / TBD | pending | pending | final rendered thesis candidate, produced on Mac |
| defense-pptx | 11-mac-docx-pdf-pptx-production | CLM-001/TBD; FIG-001/TBD | TBD | TBD | pptx | TBD | Presentations / WPS Presentation / PPTX / TBD | pending | pending | defense slide deck candidate, produced on Mac |

## Handoff Checklist

| Check | Status | Notes |
|---|---|---|
| All required DOCX/PDF/PPTX artifacts have manifest rows | pending |  |
| Mac source paths exist before Windows review | pending |  |
| Checksums are recorded for advisor-ready and final artifacts | pending |  |
| Windows review target paths are filled before final audit | pending |  |
| Windows copies are opened and verified for compatibility | pending |  |
| Final artifact package checksum verification report exists | pending | `final-handoff-verify-report.md` |
| Final artifact versions match `final-audit.md` and `defense-prep.md` | pending |  |
