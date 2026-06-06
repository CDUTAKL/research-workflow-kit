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
- Formal `remote_desktop_4060` or cloud GPU evidence should include `outputs/EXP-*/environment.txt` or `environment_snapshot.json`, plus remote artifact URI/hash/status when full outputs live off-Mac.
- AutoDL fallback templates should save logs, exit code, run summary, environment snapshot, archive checksums, and then shut down by default.
- Remote templates must not store passwords, tokens, or private-key contents.
- When editing or installing workflow skills, run `scripts/audit_skills.py --warn-only --write-report` before merging to keep references, scripts, and tool assumptions consistent.
- For important workflow, script, dashboard, or CI changes, CodeRabbit review is optional when authenticated: `coderabbit review --agent -c AGENTS.md`. Do not make it a required local dependency or CI step.
- For Dashboard APIs, local file-writing scripts, remote 4060 sync/run/fetch scripts, CI, open-path whitelists, or other security-sensitive changes, use `scripts/plugin_gate_advisor.py` to determine whether a Codex Security diff scan or focused security review should be recorded in `docs/thesis/plugin-review-log.md`.
- GitHub Actions CI should stay lightweight: Python compile/tests, skill audit, workflow doctor, initialization smoke, and dashboard build. Do not add account-dependent checks by default.

## Workflow

Read `references/code-quality.md` for the checks and template layout. Read `references/source-map.md` for provenance.

1. Inspect existing project structure before proposing changes.
2. If a new project needs structure, use or recommend `scripts/render_project_skeleton.py`.
3. Confirm config-driven entrypoints for train, evaluate, predict, and figures.
4. Run or recommend `scripts/check_experiment_contract.py`.
5. Prepare `local_mac` smoke config before `remote_desktop_4060` or AutoDL formal runs.
6. Write or require an environment snapshot for formal remote runs.
7. Use the 4060 or AutoDL sync/run/fetch/archive templates only after the user fills SSH alias and remote paths.
8. Route valid experiments back to `$research-experiment-engineering`.
9. Run skill self-checks after workflow-skill changes when this kit itself is being maintained.
10. For kit infrastructure changes, update `AGENTS.md`, `CONTRIBUTING.md`, PR templates, or CI only when the verification commands and safety boundaries remain clear.
11. For plugin-gated changes, update `plugin-review-log.md` or explain why the gate is not applicable.

## Output Contract

Always include:

- inspected or proposed code structure
- config and entrypoint contract
- smoke test plan
- output artifact contract
- experiment contract check command
- remote 4060 handoff notes when relevant
- AutoDL auto-save/auto-shutdown notes when relevant
- remote artifact storage notes when full outputs live on 4060/cloud/archive storage
- environment snapshot requirement when the run is formal GPU evidence
- risks such as leakage, config drift, missing metrics, or hard-coded paths
- skill audit status when maintaining this workflow kit
- CI and optional CodeRabbit review status when maintaining this workflow kit
- plugin gate status, especially Codex Security status for security-sensitive code paths
