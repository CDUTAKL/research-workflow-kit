# Source Map

This skill is a lightweight Codex-native synthesis for literature search and review planning.

## Primary MIT Sources

- `external-skill-candidates/agents365-semanticscholar-skill`
  - Used as inspiration for Semantic Scholar search roles, citation traversal, metadata lookup, and BibTeX export workflows.
- `external-skill-candidates/k-dense-scientific-agent-skills/scientific-skills/literature-review`
  - Used as inspiration for scientific literature review organization.
- `external-skill-candidates/wanshuiyin-auto-research-skills/skills/arxiv`
  - Used as inspiration for preprint discovery workflows.
- `external-skill-candidates/nature-skills/skills/nature-citation`
  - MIT licensed. Used as inspiration for section/segment citation batching, support grades, DOI/arXiv/S2 dedupe, and BibTeX/RIS/ENW/Zotero RDF export discipline.
- `external-skill-candidates/nature-skills/skills/nature-reader`
  - MIT licensed. Used as inspiration for source-grounded `paper.md`, `source_map.json`, figure/table notes, and direct-reading evidence.
- `external-skill-candidates/research-innovation-explorer`
  - MIT licensed. Used as inspiration for paper pools, idea matrices, novelty risk, and shortlist records.
- `external-skill-candidates/zotero-med-pipeline`
  - MIT licensed. Used as inspiration for staged literature intake, A/B/C/D screening, Zotero writeback queues, title/abstract translation notes, spreadsheet review, and feedback-learning guardrails. Local adaptation generalizes the workflow beyond medical-only RSS/PubMed defaults.

## Local Plugins to Prefer When Available

- Scite: evidence support/contrast checks.
- Zotero: local reference library search, BibTeX export, citation insertion.
- Web search: current metadata, publisher pages, venue details, author instructions.

## Excluded or Reference-Only Sources

- CC BY-NC and private/unclear-license repositories were not copied.
- This skill does not bundle external API keys or hard-coded credentials.
- Local section-level citation records live in `docs/thesis/section-citation-map.md`.
- Local screening-loop records live in `docs/thesis/zotero-screening-loop.md`.
