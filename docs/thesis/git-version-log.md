# Git Version Log

## Update Rules

- Use this file to connect code changes, experiments, and thesis claims.
- Every large code change should have a git checkpoint before formal experiments.
- Every formal experiment should record branch, commit, and dirty/clean state when available.

## Code Change Log

| Change ID | Date | Branch | Commit | Scope | Related Experiment | Related Claim | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| GIT-001 | TBD | TBD | TBD | data/model/train/evaluate/TBD | EXP-001/TBD | CLM-001/TBD | planned |  |

## Formal Experiment Version Records

| Experiment ID | Branch | Commit | Dirty State | Config | Output Path | Result Status | Notes |
|---|---|---|---|---|---|---|---|
| EXP-001 | TBD | TBD | clean/dirty/TBD | TBD | TBD | pending |  |

## GitHub Workflow Rules

- Before a large code change, inspect `git status`.
- After a coherent implementation, create a clear commit if the user asks or commit workflow is approved.
- Before AutoDL or other formal cloud training, record branch and commit.
- If the tree is dirty during a formal run, record the changed files or avoid using the result as final evidence.
- Use GitHub issues/PRs when changes are broad, reviewable, or need remote backup.

## Commit Message Hints

| Change Type | Example |
|---|---|
| experiment architecture | `feat: add EXP-001 training pipeline` |
| dataset/preprocessing | `feat: add reproducible split loader` |
| model | `feat: implement baseline classifier` |
| evaluation | `feat: save metrics and predictions for thesis runs` |
| bugfix | `fix: correct validation split metric computation` |
