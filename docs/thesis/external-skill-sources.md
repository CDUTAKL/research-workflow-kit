# External Skill Sources

## Update Rules

- Use this file to record external repositories that informed the local research workflow.
- Do not treat external skills as installed behavior unless they are rewritten into local `research-*` skills.
- Do not commit cloned external repositories; keep them under ignored `external-skill-candidates/`.
- Record only source, commit, license, useful ideas, and local adaptation target.

## Source Registry

| Source ID | Repository | Local Reference Path | Commit | License | Useful Ideas | Local Adaptation | Status |
|---|---|---|---|---|---|---|---|
| EXT-NATURE | `https://github.com/Yuan1z0825/nature-skills` | `external-skill-candidates/nature-skills` | `62fcfa8` | MIT | data availability, citation batches, source-grounded readers, paper-to-PPT QA, figure/prose polish | `research-data-availability`, `$research-literature-review`, `$research-final-audit`, `$research-paper-figures` | referenced |
| EXT-AUTORESEARCH | `https://github.com/leo-lilinxiao/codex-autoresearch` | `external-skill-candidates/codex-autoresearch` | `239c686` | MIT | `results.tsv`, resumable `state.json`, dual-gate verification, iteration logging | `research-autoresearch-loop` | referenced |
| EXT-ARIS | `https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep` | `external-skill-candidates/aris` | `d5f450c` | MIT | experiment audit, code review before GPU runs, monitoring and recovery discipline | `research-autoresearch-loop`, `research-code-quality` | referenced |
| EXT-PAPERORCH | `https://github.com/Ar9av/PaperOrchestra` | `external-skill-candidates/PaperOrchestra` | `5eda989` | MIT | research material aggregation, paper autorating, handoff schemas | `research-materials-index.md`, `$research-paper-writing`, `$research-final-audit` | referenced |
| EXT-AI-SKILLS | `https://github.com/Orchestra-Research/AI-research-SKILLs` | `external-skill-candidates/AI-research-SKILLs` | `28f2d29` | MIT | evaluation, fine-tuning, optimization, inference, MLOps, autoresearch inner/outer loop | source-map reference only; do not install all skills | referenced |
| EXT-IDEA | `https://github.com/foryourhealth111-pixel/research-innovation-explorer` | `external-skill-candidates/research-innovation-explorer` | `1429c9b` | MIT | paper pool, idea matrix, novelty risk, shortlist | `idea-discovery.md`, `$research-paper-plan` | referenced |
| EXT-ZOTERO-MED | `https://github.com/Chip-G0202/zotero-med-pipeline` | `external-skill-candidates/zotero-med-pipeline` | `9f1e307` | MIT | staged literature intake, A/B/C/D screening, Zotero writeback, title translation, spreadsheet feedback learning | `zotero-screening-loop.md`, `$research-literature-review` | adapted |
| EXT-VISIO-REPLICA | `https://github.com/uigiuf/codex-visio-replica-workflow` | `external-skill-candidates/codex-visio-replica-workflow` | `ba09a87` | no license file observed | reference-image decomposition, JSON diagram plans, Visio COM generation, export preview QA | `diagram-replica-tasks.md`, `diagram-plans/`, `$research-paper-figures` | adapted as reference only |
| EXT-ARS-CODEX | `https://github.com/Imbad0202/academic-research-skills-codex` | not cloned | web scan | unknown | Material Passport, benchmark schema, cross-model verification, data access levels | `material-passport.md`, `benchmark-report-schema.md`, `$research-final-audit` | idea adapted |
| EXT-AGENT-RESEARCH-SKILLS | `https://github.com/lingzhi227/agent-research-skills` | not cloned | web scan | unknown | multi-source discovery, novelty assessment, idea generation | `idea-discovery.md`, `citation-provenance.md`, `zotero-collection-coverage.md` | referenced |
| EXT-LLM-ZOTERO | `https://github.com/yilewang/llm-for-zotero` | not cloned | web scan | unknown | library chat, paper chat, Zotero collection/tag workflows | `zotero-collection-coverage.md`, `citation-provenance.md` | idea adapted |
| EXT-PAPER-SEARCH-MCP | `https://github.com/openags/paper-search-mcp` | not cloned | web scan | unknown | arXiv/PubMed/bioRxiv style paper search as MCP/CLI/skill | `$research-literature-review`, `citation-provenance.md` | referenced |
| EXT-AI-RESEARCH-ZOTERO | `https://github.com/WenyuChiou/ai-research-skills` | not cloned | web scan | unknown | Zotero CRUD, claim-evidence audit, research workspace | `citation-provenance.md`, `zotero-collection-coverage.md`, `$research-final-audit` | referenced |
| EXT-BEAMER | `https://github.com/Noi1r/beamer-skill` | not cloned | web scan | unknown | optional Beamer slides, TikZ audit, defense presentation checks | optional future stage 12 Beamer route | watch |

## Local Adaptation Rules

| Rule | Reason |
|---|---|
| Rewrite ideas into local workflow language | Avoid mixing incompatible tool assumptions |
| Keep `docs/thesis/` as evidence source of truth | External skills may use different storage conventions |
| Keep automation human-supervised | Thesis work should remain auditable and defensible |
| Preserve source-map notes | License and provenance should be visible |
| Avoid full external skill installation | Large skill packs can conflict with local routing |
