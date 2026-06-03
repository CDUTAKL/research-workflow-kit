# Plugin Gate Policy

## Purpose

Use this file to decide when optional plugins become useful quality gates. Plugins improve review, design, analysis, or safety, but they do not replace `docs/thesis/` source records.

## Gate Rules

| Plugin | Primary Stages | Trigger | Level | Required Record | Must Not Replace |
|---|---|---|---|---|---|
| Codex Security | 5-6 | Dashboard API, local file writing, remote 4060 scripts, CI, security-sensitive code | required when triggered; otherwise recommended | `plugin-review-log.md` | tests, human review, source records, secrets policy |
| Build Web Apps | Dashboard changes | React/Vite component changes, mobile layout, interaction fixes, frontend QA | required when triggered; otherwise recommended | `dashboard-ux-qa.md` | workflow evidence, source Markdown, final audit |
| Data Analytics | 7-8 | formal result analysis, baseline comparison, metric diagnostics, claim promotion | required when triggered; otherwise recommended | `data-quality-report.md`, `metric-diagnostics.md` | experiment registry, metrics files, data availability |
| Product Design | 9, 12 | advisor-facing dashboard, figures, PPT, final visual review | required when triggered; otherwise recommended | `visual-design-review.md` | draw.io/Python/PPTX source artifacts, figure provenance |
| CodeRabbit | 5-6, pre-merge | important scripts, dashboard, CI, or skill changes with authentication available | optional | `plugin-review-log.md` | CI, tests, security review, human judgment |

## Review Result Values

Use one of these values in `plugin-review-log.md`:

| Result | Meaning |
|---|---|
| `pass` | Gate was run and no blocking issue remains |
| `reviewed` | Gate was run and non-blocking follow-ups are recorded |
| `not_applicable` | Gate was considered but not useful for this change |
| `pending` | Gate should still be run or confirmed |
| `blocked` | Gate could not be completed and needs human action |

## Non-Replacement Rules

- Plugin outputs are review notes, not thesis evidence.
- Final claims still require `CLM-*`, `EXP-*`, `DATA-*`, `FIG-*`, or `CIT-*` evidence links.
- Dashboard and visual reviews must not hide missing data, missing baselines, weak citations, or unsupported claims.
- Security reviews must never store passwords, tokens, private keys, or account recovery material.
