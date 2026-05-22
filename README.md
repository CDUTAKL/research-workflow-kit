# Research Workflow Kit

A reusable Codex research workflow kit for thesis and paper projects.

This repository contains:

- reusable Codex research skills;
- a project-local `docs/thesis/` evidence console template;
- lightweight scripts for experiment registration, data hashing, result/claim audit, and figure workflows;
- figure folder templates for visual references, formal exports, and architecture diagrams;
- an initialization script for new research projects.

It is designed to be project-independent. It does **not** include private datasets, trained model weights, experiment outputs, API keys, SSH keys, Zotero credentials, or paper drafts.

## Repository Layout

```text
research-workflow-kit/
  skills/                       # Reusable Codex skills
  docs/thesis/                  # Project research console templates
  scripts/                      # Lightweight reusable automation scripts
  figures/                      # Figure reference/final/architecture folders
  .claude/                      # Optional Claude Code hook template
  init_research_workflow.py     # Initialize a project-local research console
```

## Included Skills

```text
research-workflow-orchestrator
research-paper-plan
research-literature-review
semanticscholar-skill
research-experiment-engineering
research-results-analysis
research-paper-figures
research-paper-writing
research-final-audit
```

## Install Skills On A New Computer

### macOS / Linux

```bash
mkdir -p ~/.codex/skills
cp -R skills/* ~/.codex/skills/
```

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills"
Copy-Item -Recurse -Force .\skills\* "$env:USERPROFILE\.codex\skills\"
```

## Initialize A New Research Project

### macOS / Linux

```bash
python init_research_workflow.py --project "/path/to/my-research-project"
```

### Windows PowerShell

```powershell
python .\init_research_workflow.py --project "E:\path\to\my-research-project"
```

This creates or updates:

```text
docs/thesis/
scripts/
figures/
.claude/settings.local.template.json
```

Use `--overwrite` only when you intentionally want template files to replace existing project files.

## Workflow Summary

The workflow has 12 stages:

1. Paper planning
2. Literature discovery and review
3. Experiment question definition
4. Experiment architecture planning
5. Research code implementation
6. Experiment run and monitoring
7. Experiment recording and result scan
8. Results analysis and claim mapping
9. Figure, table, and model diagram production
10. Paper writing and polishing
11. Word / LaTeX / PDF production
12. Final audit and defense preparation

`docs/thesis/` is the project evidence source of truth. Notion or other task tools should be used for progress tracking only, not as the primary evidence archive.

## Figure Workflow

For model architecture, method pipeline, workflow, and schematic figures:

1. Use Image Gen only to create a visual reference.
2. Check the reference for technical accuracy.
3. Redraw the final figure from source-of-truth information with Figma, PPTX, SVG, TikZ, or Python.
4. Export final thesis-ready files.
5. Record provenance and audit status in `docs/thesis/figure-plan.md`.

Do not use AI-generated raster images directly as final thesis figures unless the project explicitly accepts that provenance.

## Sensitive Information Policy

Do not commit:

- SSH keys or AutoDL temporary passwords;
- API keys or tokens;
- browser cookies;
- Zotero credentials;
- private datasets;
- trained checkpoints or model weights;
- large experiment outputs;
- private thesis drafts unless intentionally published.

## License

MIT License. See [LICENSE](LICENSE).
