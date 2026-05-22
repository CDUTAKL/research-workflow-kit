# Task Board Sync

## Update Rules

- Use this file to mirror task-management state between `docs/thesis/` and Notion.
- Keep scientific evidence in `docs/thesis/`; use Notion for planning, deadlines, status, and supervisor communication.
- Do not store Notion API tokens or private workspace credentials here.

## Notion Scope

| Notion Area | Purpose | Source Of Truth |
|---|---|---|
| Thesis Dashboard | high-level progress and milestones | summary from `docs/thesis/` |
| Task Board | implementation, writing, literature, experiment tasks | this sync table plus Notion |
| Supervisor Feedback | meeting notes and action items | Notion, with important decisions copied to `docs/thesis/` |
| Weekly Plan | near-term execution plan | Notion |

## Sync Table

| Task ID | Stage | Task | Source File | Notion Page / Database | Status | Due Date | Next Action |
|---|---|---|---|---|---|---|---|
| TASK-001 | 1 paper planning | define thesis question | `thesis-brief.md` | TBD | planned | TBD | update brief |
| TASK-002 | 4 experiment architecture | define EXP-001 architecture | `experiment-architecture.md` | TBD | planned | TBD | draft module boundaries |

## Status Mapping

| docs/thesis status | Notion status |
|---|---|
| planned | Not started |
| running | In progress |
| blocked | Blocked |
| done / reviewed | Done |
| invalid / needs_rerun | Needs revision |

## Sync Rules

- When a thesis console file creates a concrete next action, add or update a Notion task.
- When supervisor feedback changes scope, copy the decision back into the relevant `docs/thesis/` file.
- Keep Notion task descriptions short and link back to the local file path or experiment ID.
- Do not use Notion as the only location for experiment evidence, citation status, or reproducibility records.
