---
name: research-autoresearch-loop
description: Use when running human-supervised iterative research experiments, recording autoresearch results, maintaining resume state, applying verify/guard gates, or coordinating local_mac smoke tests with remote_desktop_4060 formal runs.
---

# Research Autoresearch Loop

Use this skill for human-AI collaborative experiment iteration. It borrows useful ideas from autoresearch systems but keeps the user in control of research direction, claims, and final decisions.

## Core Rules

- Do not run unattended autonomous research.
- Every iteration must target a claim, hypothesis, metric, or integrity risk.
- Record iterations in `docs/thesis/autoresearch-results.tsv`.
- Record resumable state in `docs/thesis/autoresearch-state.json`.
- Use a dual gate: verify improvement, then guard against invalid science.
- Formal GPU work defaults to `remote_desktop_4060`; `cloud_autodl` is fallback.

## Workflow

Read `references/loop.md` for the iteration contract. Read `references/source-map.md` for provenance.

1. Choose the target claim, current best run, primary metric, and candidate change.
2. Confirm code quality and experiment contract before remote GPU work.
3. Run `local_mac` smoke test.
4. Run formal experiment on `remote_desktop_4060` when needed.
5. Recover artifacts and update `experiment-registry.md`.
6. Apply verify gate: did the experiment answer the question or improve the metric?
7. Apply guard gate: no leakage, config drift, phantom result, or claim inflation.
8. Record the iteration with `scripts/new_autoresearch_iteration.py`.
9. Hand reviewed results to `$research-results-analysis`.

## Output Contract

Always include:

- target claim or research question
- current best run
- candidate experiment and expected improvement
- local smoke-test command
- remote target and recovery path
- verify gate and guard gate
- registry and autoresearch files to update
- human decision needed before promotion

