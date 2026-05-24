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
- Use `SEC-*` for thesis sections and `SEG-*` only for section-level citation units; connect literature support back to `CLM-*` through `claim-evidence-map.md`.
- Never fabricate references, DOI values, author lists, venues, or BibTeX entries.
- Use web search, Scite, Zotero, Semantic Scholar, arXiv, or publisher pages when current or precise source metadata matters.

## Workflow

Read `references/workflow.md` for the literature matrix and related-work templates. Read `references/source-map.md` for provenance and license notes.

1. Clarify the research topic, domain terms, target date range, and paper type.
2. Build search queries with synonyms, method names, datasets, metrics, and application terms.
3. Collect candidate papers and classify them by role.
4. Build a literature matrix with relationship-to-paper and citation-use columns.
5. For papers requiring direct reading, create or request a source-grounded reader artifact under `docs/thesis/paper-readings/<paper-slug>/`.
6. For long citation-seeking text, split into `SEC-*` sections and `SEG-*` claim/segment batches before searching.
7. For each weak section, create a deep research packet containing section question, keyword set, search queries, candidate papers, must-read papers, citation gaps, Scite/Zotero status, and final citation decisions.
8. Propose a related-work outline that groups literature by concept, not chronologically.
9. Flag missing citations and unverifiable claims.

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
- missing literature
- BibTeX/Zotero follow-up actions

If the user asks for exact quotes, latest papers, DOI metadata, BibTeX, or citation verification, browse or use available research plugins instead of relying on memory.
