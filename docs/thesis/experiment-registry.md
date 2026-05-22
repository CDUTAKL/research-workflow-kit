# Experiment Registry

## Update Rules

- Register every experiment before using its result in writing.
- Keep one stable experiment ID per run or comparable run group.
- Link result files, logs, notebooks, configs, and generated figures.
- Link architecture and runbook records for experiments that require code implementation.
- Mark results as `invalid` if leakage, split mismatch, metric mismatch, or missing artifacts are found.
- Use `EXP-*` for stable reviewed experiment records and `EXP-AUTO-*` for result-scan candidates.
- `experiment-log.md` is a legacy compatibility file; this registry is the primary experiment evidence source.

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

## Experiment Table

| Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
| EXP-001 | TBD | TBD | TBD | TBD | TBD | TBD | planned | TBD |  |

## Promotion Rules

- Auto-generated `EXP-AUTO-*` rows are review candidates, not final evidence.
- Promote a candidate to a stable `EXP-*` ID only after checking split, seed, config, metric computation, and baseline comparability.
- Keep rejected candidates visible as `invalid` or document why they were not used.
- Add promoted claims to `claim-evidence-map.md`; do not cite raw scan rows directly in the thesis.
- For code-backed experiments, update `experiment-architecture.md`, `experiment-runbook.md`, and `reproducibility-checklist.md` before marking the experiment as `done`.

## Engineering Links

| File | Purpose |
|---|---|
| `experiment-architecture.md` | code architecture, data/model/train/evaluate boundaries |
| `experiment-runbook.md` | exact run commands, expected outputs, monitoring, failure handling |
| `reproducibility-checklist.md` | environment, seed, config, artifacts, rerun command, claim mapping |

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
