---
name: semanticscholar-skill
description: Use when searching Semantic Scholar for academic papers, citations, authors, similar papers, DOI/arXiv/PMID metadata, BibTeX candidates, citation graphs, or literature discovery for research papers, theses, surveys, or related work.
---

# Semantic Scholar Skill

Use this skill for real Semantic Scholar API searches and metadata lookup. It keeps literature discovery grounded in returned API data instead of memory.

## Requirements

- Python 3.
- Python package `requests`.
- Optional environment variable `S2_API_KEY` for higher rate limits.
- Skill directory: `~/.codex/skills/semanticscholar-skill` when globally installed.

If `S2_API_KEY` is missing, anonymous requests may still work with stricter rate limits. Do not ask for an API key unless rate limits block the task or the user wants higher throughput.

## Core Rule

For real API work, write one temporary Python script that imports `s2.py`, performs all planned queries in one run, and prints Markdown/JSON/BibTeX output. Avoid many separate API calls from the shell.

## Workflow

Read `references/workflow.md` for query patterns and examples. Read `references/source-map.md` for provenance and license notes.

1. Classify the request: broad topic, exact title, DOI/arXiv/PMID, author, citation traversal, or recommendations.
2. Build focused queries with synonyms, exclusions, year filters, field filters, and result limits.
3. Run one Python script using `s2.py`.
4. Deduplicate and rank results by relevance to the user's research question.
5. Return a table plus follow-up actions.

## Output Contract

For each important paper, include:

- title
- authors
- year
- venue
- DOI, arXiv, URL, or Semantic Scholar ID when available
- citation count if available
- why it is relevant
- `source_status`: normally `candidate` until metadata is verified elsewhere
- `next_action`: usually `verify_metadata`, `add_to_zotero`, `check_with_scite`, `cite_in_related_work`, or `do_not_cite_yet`
- default `zotero_status=not_added` and `scite/support_status=not_checked` when handing candidates to a thesis literature matrix
- BibTeX, JSON, or Zotero follow-up when requested

Mark metadata as unverified if the API result is incomplete or suspicious. Use publisher, DOI, arXiv, PubMed, Scite, or Zotero follow-up for final citation verification.
