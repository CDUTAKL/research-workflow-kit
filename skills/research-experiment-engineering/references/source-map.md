# Source Map

This skill is a lightweight Codex-native synthesis for research experiment engineering. It borrows engineering patterns, not source code.

## Reference Sources

- Cookiecutter Data Science
  - https://github.com/drivendataorg/cookiecutter-data-science
  - Used for project-structure and data-science reproducibility conventions.
- cookiecutter-reproducible-science
  - https://github.com/mkrapp/cookiecutter-reproducible-science
  - Used for reproducible research project organization ideas.
- Lightning-Hydra Template
  - https://github.com/ashleve/lightning-hydra-template
  - Used for config, training entrypoint, logging, and experiment organization inspiration.
- Hydra documentation
  - https://hydra.cc/docs/tutorials/basic/running_your_app/multi-run/
  - Used for optional config composition and multirun/sweep concepts.
- MLflow Tracking documentation
  - https://mlflow.org/docs/latest/ml/tracking
  - Used for optional parameters, metrics, artifacts, and run tracking concepts.
- DVC metrics/parameters/plots documentation
  - https://doc.dvc.org/start/data-pipelines/metrics-parameters-plots
  - Used for optional params, metrics, plots, and pipeline reproducibility concepts.
- `external-skill-candidates/codex-autoresearch`
  - MIT licensed. Used as inspiration for iteration logging, resumable state, and preflight discipline.
- `external-skill-candidates/aris`
  - MIT licensed. Used as inspiration for code review before GPU runs, experiment integrity checks, and remote monitoring.
- `external-skill-candidates/AI-research-SKILLs`
  - MIT licensed. Used as a technical reference for evaluation, fine-tuning, optimization, inference, and MLOps when needed.

## Local Adaptation Notes

- No external repository source code is copied.
- The default workflow is plain Python plus JSON/YAML files and stable output directories.
- Hydra, MLflow, DVC, and W&B are optional tools, not dependencies.
- macOS Codex plus `remote_desktop_4060` is the default device workflow.
- This skill plans experiment engineering and handoffs; final empirical claims belong to `$research-results-analysis`.
- Code contract details live in `$research-code-quality`.
- Iterative experiment logging lives in `$research-autoresearch-loop`.
