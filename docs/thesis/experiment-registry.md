# Experiment Registry

## Update Rules

- Register every experiment before using its result in writing.
- Keep one stable experiment ID per run or comparable run group.
- Link result files, logs, notebooks, configs, and generated figures.
- Use this registry as a local thesis evidence index. Large logs, checkpoints, predictions, and full run folders may live on `remote_desktop_4060`, NAS, iCloud/OneDrive, or object storage.
- Record the cloud/remote location, hash/manifest, and remote status whenever artifacts are not fully stored on the Mac.
- Link architecture and runbook records for experiments that require code implementation.
- Mark results as `invalid` if leakage, split mismatch, metric mismatch, or missing artifacts are found.
- Use `EXP-*` for stable reviewed experiment records and `EXP-AUTO-*` for result-scan candidates.
- `experiment-log.md` is a legacy compatibility file; this registry is the primary experiment evidence source.
- Promote experiments according to `evidence-promotion-policy.md`; formal `remote_desktop_4060` evidence requires an environment snapshot.

## Status Legend

| Status | Meaning |
|---|---|
| `planned` | Designed but not run |
| `running` | In progress |
| `done` | Completed and artifacts exist |
| `blocked` | Cannot run until a dependency or decision is resolved |
| `invalid` | Should not support claims |
| `candidate` | Auto-detected or proposed experiment that still needs review |
| `candidate_review` | Candidate experiment with warnings or anomalies to resolve |
| `ready_to_run` | Architecture, config, and run command are defined |
| `completed_unreviewed` | Outputs exist but have not been analyzed |

## Storage Model

| Layer | Location | Purpose | Notes |
|---|---|---|---|
| Local evidence index | `docs/thesis/experiment-registry.md`, `experiment-reports/`, `autoresearch-results.tsv` | thesis-readable experiment evidence | committed and reviewed |
| Local lightweight output | `outputs/EXP-*/manifest.json`, `metrics.json`, `environment.txt`, selected figures/tables | small machine-readable index | may be ignored by git if project-specific |
| Remote run folder | `ssh://desktop-4060/.../research-runs/EXP-*` or equivalent | full logs, checkpoints, predictions, large artifacts | primary storage for formal 4060 runs |
| Archive / cloud | NAS, iCloud/OneDrive, OSS/COS/S3, or institutional storage | long-term preservation | record URI and hash before final audit |

## Experiment Table

| Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes | Storage Backend | Remote Artifact URI | Remote Status | Artifact Hash / Manifest |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EXP-001 | TBD | TBD | TBD | TBD | outputs/EXP-001 | TBD | planned | TBD |  | local_mac/remote_desktop_4060/cloud_autodl/archive/TBD | ssh://desktop-4060/research-runs/EXP-001/TBD | pending | outputs/EXP-001/manifest.json/TBD |

## Promotion Rules

- Auto-generated `EXP-AUTO-*` rows are review candidates, not final evidence.
- Promote a candidate to a stable `EXP-*` ID only after checking split, seed, config, metric computation, and baseline comparability.
- Keep rejected candidates visible as `invalid` or document why they were not used.
- Add promoted claims to `claim-evidence-map.md`; do not cite raw scan rows directly in the thesis.
- For code-backed experiments, update `experiment-architecture.md`, `experiment-runbook.md`, and `reproducibility-checklist.md` before marking the experiment as `done`.
- For iterative method changes, record verify/guard outcomes in `autoresearch-results.tsv` before promoting the result to a thesis claim.
- For data-backed claims, ensure `data-availability.md` maps the output artifact to source data.
- For formal baseline comparisons, update `benchmark-report-schema.md` and register evidence-critical outputs in `material-passport.md`.
- For formal 4060 or cloud results, do not mark a run `reviewed` unless `Storage Backend`, `Remote Artifact URI`, `Remote Status`, and `Artifact Hash / Manifest` are explicit.

## Engineering Links

| File | Purpose |
|---|---|
| `experiment-architecture.md` | code architecture, data/model/train/evaluate boundaries |
| `experiment-runbook.md` | exact run commands, expected outputs, monitoring, failure handling |
| `reproducibility-checklist.md` | environment, seed, config, artifacts, rerun command, claim mapping |
| `experiment-integrity-checklist.md` | leakage, fake ground truth, metric, config, artifact, and scope checks |
| `autoresearch-results.tsv` | human-supervised iteration record and verify/guard decisions |
| `benchmark-report-schema.md` | baseline/new metric comparison schema and benchmark guard checklist |
| `material-passport.md` | identity card for evidence-critical outputs and final artifacts |
| `data-availability.md` | dataset provenance and claim-to-data traceability |
| `outputs/EXP-*/environment.txt` | required environment snapshot for formal 4060 or cloud GPU evidence |
| `ssh://desktop-4060/.../research-runs/EXP-*` | preferred full-artifact storage for formal 4060 runs |

## Result Scan Imports

Use `$research-results-analysis` or the skill-local scan script to populate candidate metrics:

```bash
python ~/.codex/skills/research-results-analysis/scripts/scan_results.py --root . --out-dir docs/thesis
python ~/.codex/skills/research-results-analysis/scripts/result_scan_to_registry.py --scan-table docs/thesis/result-scan-table.csv --registry docs/thesis/experiment-registry.md
```

| Scan Report | Table | Reviewed By | Review Status | Notes |
|---|---|---|---|---|
| `result-scan-summary.md` | `result-scan-table.csv` | TBD | pending | Script output is preliminary and must be reviewed before writing claims |

## Experiment Risks

| Risk | Affected Experiments | Evidence | Severity | Fix |
|---|---|---|---|---|
| Data leakage | TBD | TBD | high/medium/low | TBD |
| Split mismatch | TBD | TBD | high/medium/low | TBD |
| Metric mismatch | TBD | TBD | high/medium/low | TBD |
| Missing baseline | TBD | TBD | high/medium/low | TBD |
| Single seed only | TBD | TBD | high/medium/low | TBD |
