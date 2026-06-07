# Experiment Architecture

## Purpose

This file is the global experiment blueprint for the thesis project. Use it before writing experiment code, opening a new `EXP-*`, or running expensive GPU work.

The goal is to keep the experiment system coherent across Mac orchestration, `remote_desktop_4060` formal runs, optional cloud fallback, local result indexing, and final thesis evidence promotion.

## Update Rules

- Update this file when the research question, data flow, model/algorithm boundary, metric definition, baseline, output convention, or remote storage plan changes.
- Every serious experiment should connect to at least one `CLM-*`, one config, one output location, and one evidence-review path.
- When the title contains method-heavy or structure-heavy wording, update `project-scope-control.md` before coding so the experiment can verify or downgrade those title phrases.
- Local Mac records are the thesis evidence index; complete experiment folders may live on `remote_desktop_4060`, NAS, cloud drive, or object storage.
- Formal `remote_desktop_4060` or cloud results require an environment snapshot and a remote artifact URI/hash before they can be marked `reviewed`. AutoDL fallback runs also require an exit code, run summary, checksum file, and recorded shutdown status.
- Do not store passwords, private keys, tokens, or private dataset contents in this file.

## Architecture Summary

| Area | Decision | Status | Notes |
|---|---|---|---|
| Primary research question | TBD | draft | Link to `thesis-brief.md` |
| Target claim family | CLM-001/TBD | draft | Link to `claim-evidence-map.md` |
| Main experiment family | baseline/proposed/ablation/robustness/error-analysis/TBD | draft |  |
| Primary execution target | `remote_desktop_4060` for formal GPU runs | planned | Mac remains control console |
| Local smoke target | `local_mac` CPU-only or small sample | planned | No local GPU assumption |
| Cloud fallback | `cloud_autodl` / other / not needed | pending | Only when 4060 is unavailable or insufficient; AutoDL fallback should auto-save evidence and auto-shutdown after completion |
| Long-term artifact storage | 4060 run folder / NAS / cloud drive / object storage / TBD | pending | Record URI in `experiment-registry.md` |

## Topic-Derived Feasibility Gates

Use this section before implementation when the project begins from a fixed title or a detailed exploration proposal.

| Gate | Required Decision | Source Record | Status | Notes |
|---|---|---|---|---|
| Title phrase under test | Which title phrase is being validated by this experiment family? | `project-scope-control.md` | pending |  |
| Causal availability | Which fields are visible before prediction / decision time? | `project-scope-control.md` | pending |  |
| Node / unit definition | What is a node, sample, unit, or comparable entity? | `project-scope-control.md` | pending |  |
| Edge / relation meaning | What does a relation mean, and can it be computed without leakage? | `project-scope-control.md` | pending |  |
| Downgrade route | What title/method wording will be used if the main route fails? | `project-scope-control.md` | pending |  |

## Claim-To-Experiment Map

| Claim ID | Experiment Family | Required Evidence | Baseline Needed | Main Metric | Status | Notes |
|---|---|---|---|---|---|---|
| CLM-001 | EXP-001/TBD | DATA-001, EXP-001, FIG-001/TBD | yes/no/TBD | TBD | draft |  |

## End-To-End Data Flow

| Stage | Input | Process | Output | Source Record | Risk |
|---|---|---|---|---|---|
| Raw data | TBD | acquisition / filtering / import | raw dataset path | `data-availability.md` | access, privacy, missing metadata |
| Preprocessing | raw data | cleaning, split, feature prep | processed data / split manifest | `data-availability.md` | leakage, duplicate samples |
| Training / inference | config + processed data | baseline/proposed method | logs, checkpoints, predictions | `experiment-runbook.md` | unstable run, wrong config |
| Evaluation | predictions + labels | metric computation | `metrics.json`, tables | `metric-diagnostics.md` | metric mismatch |
| Analysis | metrics + logs | baseline delta, error analysis | `experiment-reports/EXP-*.md` | `benchmark-report-schema.md` | overclaiming |
| Figure / writing | reviewed evidence | plot or table | FIG-* / manuscript claim | `figure-plan.md`, `claim-evidence-map.md` | unsupported claim |

## Code Architecture Contract

| Layer | Responsibility | Preferred Path | Required Interface / Output |
|---|---|---|---|
| Data loading | read raw/processed data and fixed splits | `src/data/` | deterministic split, data version, hash |
| Model / algorithm | baseline and proposed method | `src/models/` or project equivalent | config-driven construction |
| Training | fit model or run method | `src/training/` | logs, checkpoint, resolved config |
| Evaluation | compute final metrics | `src/evaluation/` | `metrics.json`, predictions if needed |
| Metrics | shared metric definitions | `src/metrics/` | named metric, denominator, direction |
| Utilities | seed, logging, paths | `src/utils/` | reproducible seed and artifact paths |
| Figures | data-backed plots | `scripts/figures/` | SVG/PDF/PNG or table export |
| Tests | smoke and contract tests | `tests/` | config, output, metric sanity |

## Config Contract

| Item | Required? | Example | Notes |
|---|---|---|---|
| Stable experiment ID | yes | `EXP-001` | Must match registry |
| Formal config | yes | `configs/experiment/EXP-001.yaml` | Full run |
| Smoke config | yes before formal run | `configs/smoke/EXP-001-smoke.yaml` | Small sample / CPU-friendly |
| Seed | yes | `seed: 42` | Record global/numpy/torch when applicable |
| Split | yes | `split: test` | Must be fixed before comparison |
| Primary metric | yes | `metric: accuracy` | Include direction and denominator in metric diagnostics |
| Output path | yes | `outputs/EXP-001` | Local lightweight index |
| Remote artifact URI | formal remote/cloud | `ssh://desktop-4060/research-runs/EXP-001/` | Full run folder if not stored on Mac |

## Output Contract

Each evidence-bearing `outputs/EXP-*` folder should contain a lightweight local index:

| Artifact | Required | Purpose |
|---|---|---|
| `manifest.json` | yes after run | artifact inventory, hashes, remote URI |
| `config_resolved.json` | yes after run | exact runtime config |
| `metrics.json` | yes after run | machine-readable metrics |
| `environment.txt` or `environment_snapshot.json` | formal remote/cloud | CUDA/PyTorch/Python/GPU/git state |
| `logs/` | yes after run | training/evaluation trace |
| `figures/` or `tables/` | when produced | candidate thesis visuals |
| `predictions.csv/json` | when needed | error analysis and figure source |
| `checkpoints/` | optional / remote preferred | large files can stay on 4060/cloud |

## Remote Storage Contract

| Field | Preferred Value | Required When | Source Record |
|---|---|---|---|
| Storage Backend | `local_mac`, `remote_desktop_4060`, `cloud_autodl`, `nas`, `icloud`, `onedrive`, `oss/cos/s3` | every experiment | `experiment-registry.md` |
| Remote Artifact URI | `ssh://desktop-4060/research-runs/EXP-001/` | full artifacts not stored on Mac | `experiment-registry.md` |
| Remote Status | `pending`, `synced`, `verified`, `archived`, `blocked` | remote/cloud runs | `experiment-registry.md` |
| Artifact Hash / Manifest | `outputs/EXP-001/manifest.json` or checksum | reviewed evidence | `experiment-registry.md`, `material-passport.md` |
| Local Summary | `experiment-reports/EXP-001.md` | all reviewed results | `experiment-reports/` |

## AutoDL Fallback Path

Use AutoDL only when the desktop 4060 is unavailable, insufficient, or explicitly bypassed. The user creates and starts the AutoDL instance manually; the workflow then uses SSH/rsync templates to sync code, run the experiment, save evidence, archive outputs, and shut down the instance.

| Step | Action | Output |
|---|---|---|
| 1 | User creates/starts AutoDL instance and confirms SSH access | SSH alias such as `autodl-gpu` |
| 2 | Mac syncs code/config to AutoDL | remote project folder |
| 3 | AutoDL writes environment snapshot with `--label cloud_autodl` | `outputs/EXP-*/environment.txt` |
| 4 | AutoDL runs the formal command and writes logs | `train.log`, checkpoints, metrics |
| 5 | AutoDL writes `exit_code.txt` and `autodl_run_summary.json` | machine-readable run outcome |
| 6 | AutoDL archives output and writes `checksums.sha256` | remote archive path |
| 7 | AutoDL runs `/usr/bin/shutdown` when `AUTO_SHUTDOWN=1` | billing-safe shutdown |
| 8 | Mac fetches lightweight evidence after restart if needed | local `outputs/EXP-*` index |
| 9 | Registry is updated with `cloud_autodl`, remote URI, status, and checksum path | reviewed evidence candidate |

## 4060 Formal Run Path

| Step | Action | Output |
|---|---|---|
| 1 | Mac prepares config, smoke config, and registry row | `configs/experiment/EXP-*.yaml`, `experiment-registry.md` |
| 2 | Mac runs local smoke / contract check | pass/fail notes |
| 3 | Mac syncs code/config to `remote_desktop_4060` | remote project folder |
| 4 | 4060 writes environment snapshot | `outputs/EXP-*/environment.txt` |
| 5 | 4060 runs formal experiment | full remote run folder |
| 6 | Mac fetches lightweight index | `manifest.json`, `metrics.json`, selected figures/tables |
| 7 | Full artifacts remain remote or are archived | `Remote Artifact URI`, hash/manifest |
| 8 | Results become report and claim evidence only after review | `experiment-reports/EXP-*.md`, `claim-evidence-map.md` |

## Baseline And Metric Policy

| Policy | Requirement | Notes |
|---|---|---|
| Baseline comparability | same data split and metric definition | otherwise mark comparison invalid or caveated |
| Metric direction | higher/lower is better must be explicit | record in `metric-diagnostics.md` |
| Failed runs | keep visible when they affect interpretation | use `autoresearch-results.tsv` |
| Multiple seeds | required when claim depends on stability | otherwise write caveat |
| Result promotion | verify gate + guard gate required | use `evidence-promotion-policy.md` |

## Risks And Blockers

| Risk | Impact | Detection | Mitigation | Status |
|---|---|---|---|---|
| Missing baseline | weak comparison | experiment plan review | implement or justify baseline | open |
| Split leakage | invalid result | data audit / duplicate checks | fixed split and leakage tests | open |
| No machine-readable metrics | cannot scan/analyze results | contract check | save `metrics.json` | open |
| Full artifacts only on Mac | storage bloat and handoff risk | output audit | move large files to 4060/cloud and record URI | open |
| Remote artifacts unverified | evidence chain breaks | doctor / final audit | write manifest/hash and verify remote status | open |
| Environment snapshot missing | formal GPU evidence weak | contract check | write snapshot before or during formal run | open |
| Title phrase unsupported | final title overclaims method or application value | project scope audit / advisor review | narrow or rename title before final writing | open |
