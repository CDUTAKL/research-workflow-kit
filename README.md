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

### macOS / Codex

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
.venv/bin/python install_skills.py --overwrite
```

This installs the bundled research skills into `~/.codex/skills`. The repository
`.venv` is used for local script execution and keeps dependencies out of the
system Python and Codex runtime cache.

Recommended verification:

```bash
.venv/bin/python -c "import requests, matplotlib, pandas, pptx, numpy"
test -f ~/.codex/skills/research-workflow-orchestrator/SKILL.md
test -f ~/.codex/skills/semanticscholar-skill/s2.py
```

### macOS / Linux Manual Copy

```bash
mkdir -p ~/.codex/skills
cp -R skills/* ~/.codex/skills/
```

Use the installer above when possible because it copies each skill directory
including internal `references/`, `scripts/`, `examples/`, `presets/`, and
assets.

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills"
Copy-Item -Recurse -Force .\skills\* "$env:USERPROFILE\.codex\skills\"
```

## Initialize A New Research Project

### macOS / Linux

```bash
.venv/bin/python init_research_workflow.py --project "/path/to/my-research-project"
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
11. Laptop-based DOCX / optional Word / optional LaTeX / PDF production
12. Laptop-based final audit and defense preparation

`docs/thesis/` is the project evidence source of truth. Notion or other task tools should be used for progress tracking only, not as the primary evidence archive.

## macOS Toolchain Notes

- `local_mac` is the research console and orchestration machine for stages 1-10: planning, literature, code editing, remote run control, result analysis, figure planning, and writing drafts. It may run CPU-only smoke tests, but GPU work is not assumed.
- `remote_desktop_4060` is the primary GPU experiment target for training, evaluation, tuning, reproducibility runs, and artifact generation.
- `cloud_autodl` is an optional stronger fallback when the desktop 4060 is unavailable or insufficient.
- Remote training uses macOS Terminal, VS Code SSH, `ssh`, `scp`, and `rsync`; MobaXterm is a Windows-only convenience and is not assumed.
- Stages 11-12 are intended to move to the user's laptop for final DOCX/optional Word/optional LaTeX/PDF production, final audit, and defense material finishing.
- DOCX work uses the Documents plugin and local `.docx` files. Pages can open or review documents locally; Microsoft Word is optional when installed.
- LaTeX is optional. Run the LaTeX doctor first, then compile only when a TeX runtime is available.
- Defense and diagram polish use Presentations, Figma, and BioRender when available. Canva is not assumed on this Mac.

## Script Locations

- Project bootstrap scripts live in root `scripts/`.
- Result scanning lives in `skills/research-results-analysis/scripts/scan_results.py` and `skills/research-results-analysis/scripts/result_scan_to_registry.py`.
- Figure rendering lives in `skills/research-paper-figures/scripts/nature_plot_templates.py` and `skills/research-paper-figures/scripts/render_network_architecture.py`.
- Root `scripts/render_network_architecture.py` is a legacy placeholder; use the skill-local renderer for formal architecture figures.

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
