---
name: research-code-quality
description: Use when creating, reviewing, or validating research experiment code quality, project skeletons, config-driven training, experiment contracts, smoke tests, output manifests, remote 4060 run templates, or pre-GPU code checks.
---

# Research Code Quality

Use this skill before expensive experiments or when research code needs to become reproducible enough to support thesis claims.

## Core Rules

- Prefer the existing repository style, but keep data/model/train/evaluate/metrics/reporting boundaries visible.
- Use config-driven experiments; avoid hard-coded paths, seeds, metrics, and output folders.
- Every formal run should have a contract: config, seed, split, metric, output path, registry row, and smoke config.
- Machine-readable outputs should include manifest, resolved config, metrics, logs, and predictions when applicable.
- Formal `remote_desktop_4060` or cloud GPU evidence should include `outputs/EXP-*/environment.txt`.
- Remote templates must not store passwords, tokens, or private-key contents.

## Workflow

Read `references/code-quality.md` for the checks and template layout. Read `references/source-map.md` for provenance.

1. Inspect existing project structure before proposing changes.
2. If a new project needs structure, use or recommend `scripts/render_project_skeleton.py`.
3. Confirm config-driven entrypoints for train, evaluate, predict, and figures.
4. Run or recommend `scripts/check_experiment_contract.py`.
5. Prepare `local_mac` smoke config before `remote_desktop_4060` formal runs.
6. Write or require an environment snapshot for formal remote runs.
7. Use the 4060 sync/run/fetch templates only after the user fills SSH alias and remote paths.
8. Route valid experiments back to `$research-experiment-engineering`.

## Output Contract

Always include:

- inspected or proposed code structure
- config and entrypoint contract
- smoke test plan
- output artifact contract
- experiment contract check command
- remote 4060 handoff notes when relevant
- environment snapshot requirement when the run is formal GPU evidence
- risks such as leakage, config drift, missing metrics, or hard-coded paths
