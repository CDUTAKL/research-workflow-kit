---
name: research-literature-review
description: Use when building a literature review, related work section, citation matrix, paper search strategy, BibTeX candidate list, or citation plan for a research paper, thesis, dissertation, survey, journal article, or conference paper.
---

# Research Literature Review

Use this skill to find, organize, and synthesize literature into a defensible related-work structure. The goal is not a pile of paper summaries; the goal is a citation-backed map of what is known, what is missing, how the user's work fits, and which citations support each thesis section.

## Core Rules

- Prefer primary sources for methods, datasets, metrics, and claims.
- Separate classic/foundational work, recent work, method competitors, datasets/benchmarks, and surveys.
- Track what each paper supports in the user's manuscript.
- For full-paper reading tasks, preserve source-grounded evidence with page/block anchors before using the paper for important claims.
- For citation-heavy thesis text, map sections and segments in `docs/thesis/section-citation-map.md`.
- When a section needs targeted citation improvement, create a deep research task with `scripts/new_deep_research_task.py --section-id SEC-... --topic "..."` and work inside `docs/thesis/section-research-packets/`.
- Treat Zotero as the literature hub, not the final evidence record: use `docs/thesis/zotero-literature-hub.md` for inventory/policy, then promote papers through `section-citation-map.md` and `citation-provenance.md`.
- When the project needs recurring literature intake, use the Zotero screening loop in `docs/thesis/zotero-screening-loop.md`: candidate pool -> A/B/C/D labels -> Zotero queue -> spreadsheet feedback -> section citation handoff.
- Use `docs/thesis/citation-provenance.md` to distinguish metadata verification from claim-support verification, and `docs/thesis/zotero-collection-coverage.md` to check whether each section has enough Zotero-backed literature coverage.
- Use `SEC-*` for thesis sections and `SEG-*` only for section-level citation units; connect literature support back to `CLM-*` through `claim-evidence-map.md`.
- Never fabricate references, DOI values, author lists, venues, or BibTeX entries.
- Use web search, Scite, Zotero, Semantic Scholar, arXiv, or publisher pages when current or precise source metadata matters.

## Workflow

Read `references/workflow.md` for the literature matrix and related-work templates. Read `references/zotero-screening-loop.md` when adapting Zotero screening, feedback learning, A/B/C/D candidate labels, collection coverage, or citation provenance. Read `references/source-map.md` for provenance and license notes.

1. Clarify the research topic, domain terms, target date range, and paper type.
2. Build search queries with synonyms, method names, datasets, metrics, and application terms.
3. Collect candidate papers and classify them by role.
4. Build a literature matrix with relationship-to-paper and citation-use columns.
5. For papers requiring direct reading, create or request a source-grounded reader artifact under `docs/thesis/paper-readings/<paper-slug>/`.
6. For long citation-seeking text, split into `SEC-*` sections and `SEG-*` claim/segment batches before searching.
7. For each weak section, create a deep research packet containing section question, keyword set, search queries, candidate papers, must-read papers, citation gaps, Scite/Zotero status, and final citation decisions.
8. For recurring intake, maintain the A/B/C/D screening pool and Zotero writeback queue without treating unverified candidates as citations.
9. Record core citations in `citation-provenance.md` with `verified_by`, `verified_on`, metadata status, support status, Zotero status, and export status.
10. Map Zotero collections to `SEC-*`, `SEG-*`, and `CLM-*` in `zotero-collection-coverage.md`.
11. Use `scripts/sync_zotero_inventory.py`, `scripts/audit_zotero_coverage.py`, and `scripts/export_zotero_bibliography.py` when a local Zotero library needs to be connected to the thesis console.
12. Propose a related-work outline that groups literature by concept, not chronologically.
13. Flag missing citations and unverifiable claims.

## Output Contract

Always include:

- search keywords
- search scope
- core literature table
- related-work groups
- representative papers per group
- where each paper can be cited
- `source_status` for each core paper: `candidate`, `metadata_verified`, `in_zotero`, or `claim_support_checked`
- `next_action` for each citation candidate: `verify_metadata`, `add_to_zotero`, `check_with_scite`, `cite_in_related_work`, or `do_not_cite_yet`
- Zotero status and Scite/support status for important citation candidates
- reading status, reader path, source-map path, and key source blocks when a paper has been directly read
- citation batch strategy when the input contains many citation-worthy claims
- section citation map updates when matching papers to thesis chapters, sections, or paragraphs
- deep research packet path when a section needs more precise literature search
- screening label, Zotero queue status, and feedback-learning status when using the screening loop
- Zotero literature hub snapshot path when local library inventory is reviewed
- citation provenance updates for core papers
- Zotero collection coverage gaps by section
- missing literature
- BibTeX/Zotero follow-up actions

If the user asks for exact quotes, latest papers, DOI metadata, BibTeX, or citation verification, browse or use available research plugins instead of relying on memory.
