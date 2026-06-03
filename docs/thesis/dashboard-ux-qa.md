# Dashboard UX QA

Use this file when Dashboard changes affect layout, interaction, mobile readability, or local control-service behavior.

| QA ID | Date | Trigger | View / Flow | Checks Run | Result | Follow-Up | Reviewer |
|---|---|---|---|---|---|---|---|
| TBD | TBD | dashboard/frontend/TBD | Today workspace / tabs / flow editor | `pnpm run build`; Browser/Safari check; mobile sanity | pending |  | Codex/user |

## Checklist

- First screen shows current stage, blocker, next action, P0/P1, audit tier, latest experiment.
- Buttons are visible, clickable, and have readable labels.
- Mobile layout does not overflow horizontally.
- Local API actions do not expose arbitrary paths or commands.
- Visual polish does not hide evidence gaps or unsupported claims.
