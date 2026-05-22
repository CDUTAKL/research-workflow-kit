# Source Map

## Source

- Upstream: `external-skill-candidates/agents365-semanticscholar-skill`
- License: MIT in upstream frontmatter and repository metadata.
- Retained code: `s2.py`

## Adaptation Notes

- Frontmatter was simplified to `name` and `description`.
- Platform-specific home-directory assumptions were replaced with Windows + Codex paths.
- Update-check behavior was omitted from this local version.
- API keys are not bundled. `S2_API_KEY` remains optional.
- This skill is intended to work with `$research-literature-review` and `$research-workflow-orchestrator`.
