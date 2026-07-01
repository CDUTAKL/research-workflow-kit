# Stage 9 Key Figures QA

## Generated Figures

| Figure ID | Output | Source Trace | QA Status | Notes |
|---|---|---|---|---|
| FIG-METHOD-001 | `figures/final/FIG-METHOD-001_method_pipeline.svg` | `docs/thesis/experiment-reports/frozen-experiment-result-tables.md`, `docs/thesis/experiment-architecture.md`, `docs/thesis/experiment-runbook.md` | draft-pass | Image Gen reference copied to `figures/references/FIG-METHOD-001_reference.png`; formal SVG is source-traceable draft and should be opened in draw.io for final manual polish. |
| FIG-METHOD-002 | `figures/final/FIG-METHOD-002_event_triggered_correction.svg` | `docs/thesis/method-event-deferral-v6.md`, EXP-103 frozen metrics | draft-pass | Image Gen reference copied to `figures/references/FIG-METHOD-002_reference.png`; formal SVG highlights stable fallback and conservative trigger. |
| FIG-RESULT-001 | `figures/final/FIG-RESULT-001_exp103_main_result.svg` | `/Users/xushuyuan/Documents/Codex/EVCS-EventGraph-Thesis/files-mentioned-by-the-user-research/research-workflow-kit/outputs/EXP-103-v6-event-deferral-rule-frozen/offline_deferral_metrics.csv`, `/Users/xushuyuan/Documents/Codex/EVCS-EventGraph-Thesis/files-mentioned-by-the-user-research/research-workflow-kit/outputs/EXP-103-v6-event-deferral-rule-frozen/wape_nmae_nrmse_delta.csv` | draft-pass | Uses frozen test metrics; axes are not truncated to exaggerate small global MAE improvement. |

## Reference QA

- Image Gen references are stored as visual mother drafts only, not final thesis evidence.
- Formal SVG drafts are editable and should be treated as draw.io redraw bases.
- No generated bitmap is used as a final data-backed figure.

## Remaining Polish

- Open method SVGs in draw.io and align spacing/icons manually if advisor-facing polish is required.
- Export final draw.io versions as SVG/PDF/PNG after manual review.
- Insert into DOCX/PDF and verify label readability after scaling.
