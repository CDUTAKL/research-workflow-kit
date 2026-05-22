# Source Map

This skill is a lightweight Codex-native synthesis for empirical result analysis.

## Primary MIT Sources

- `external-skill-candidates/wanshuiyin-auto-research-skills/skills/analyze-results`
  - Used as inspiration for parsing and summarizing experiment artifacts.
- `external-skill-candidates/wanshuiyin-auto-research-skills/skills/result-to-claim`
  - Used as inspiration for turning results into claim tables.
- `external-skill-candidates/wanshuiyin-auto-research-skills/skills/experiment-audit`
  - Used as inspiration for reproducibility and leakage checks.
- `external-skill-candidates/k-dense-scientific-agent-skills/scientific-skills/exploratory-data-analysis`
  - Used as inspiration for data structure, quality, missingness, distribution, and downstream-analysis gates.
- `external-skill-candidates/k-dense-scientific-agent-skills/scientific-skills/statistical-analysis`
  - Used as inspiration for test selection, assumption checks, effect-size awareness, and cautious reporting.
- `external-skill-candidates/k-dense-scientific-agent-skills/scientific-skills/seaborn`
  - Used as inspiration for exploratory statistical visualization choices.
- `external-skill-candidates/k-dense-scientific-agent-skills/scientific-skills/matplotlib`
  - Used as inspiration for publication handoff and object-oriented figure generation expectations.
- `external-skill-candidates/nousresearch-hermes-agent/skills/research/research-paper-writing`
  - Used as inspiration for treating experiments, analysis, writing, and review as an iterative loop.

## Local Adaptation Notes

- No source scripts were copied in this first version.
- `skills/research-results-analysis/scripts/scan_results.py` is a local standard-library utility for lightweight metric inventory and traceability.
- `skills/research-results-analysis/scripts/result_scan_to_registry.py` is a local standard-library utility for turning scan output into review-only experiment registry candidates.
- Keep the workflow file project-agnostic.
- Add project-specific parsers later only after real result formats stabilize.
