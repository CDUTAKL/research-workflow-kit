# Semantic Scholar Workflow

## Import Pattern

Use this Codex-compatible pattern in temporary scripts:

```python
import os
import sys
from pathlib import Path

skill_dir = Path.home() / ".codex" / "skills" / "semanticscholar-skill"
if not skill_dir.is_dir():
    skill_dir = Path("skills/semanticscholar-skill").resolve()
sys.path.insert(0, str(skill_dir))

from s2 import *
```

## Search Strategy

| User intent | Function |
|---|---|
| Broad topic exploration | `search_relevance()` |
| Precise terms or exact phrases | `search_bulk()` with `build_bool_query()` |
| Known paper title | `match_title()` |
| DOI, arXiv, PMID, CorpusId | `get_paper()` |
| Papers citing a known paper | `get_citations()` |
| Papers referenced by a known paper | `get_references()` |
| Similar papers | `find_similar()` or `recommend()` |
| Author search | `search_authors()` and `get_author_papers()` |

## Temporary Script Example

```python
import sys
from pathlib import Path

skill_dir = Path.home() / ".codex" / "skills" / "semanticscholar-skill"
sys.path.insert(0, str(skill_dir))
from s2 import *

query = build_bool_query(
    phrases=["gamma spectrum classification"],
    required=["machine learning"],
    excluded=["astronomy"]
)
papers = search_bulk(query, max_results=20, year="2018-")
papers = deduplicate(papers)
print(format_results(papers, "gamma spectrum classification"))
```

Run the script once with Python. If no results return, broaden the query before reporting failure.

## Result Review

For each candidate paper, assess:

- Is the task/domain actually relevant?
- Is it a primary source, survey, benchmark, or method source?
- Is metadata complete enough to cite?
- Does it belong in background, related work, method, experiment comparison, or limitations?

## Tool Boundaries

Use Semantic Scholar for discovery and candidate metadata. Do not treat it as the only final source for citation truth.

| Tool | Best use | Not suitable for |
|---|---|---|
| `$semanticscholar-skill` | Discover papers, inspect authors, traverse citation networks, find similar papers, export candidate BibTeX/JSON | Final citation verification as the only source |
| Zotero plugin | Manage the local library, export final BibTeX, insert citations, organize PDF attachments | Large-scale discovery of unfamiliar papers |
| Scite plugin | Check whether a specific paper supports or contrasts a concrete claim | Acting as a document library or citation manager |
| Web / DOI / publisher | Verify final title, authors, year, venue, DOI, and official publication version | Organizing large candidate sets |

Recommended chain:

```text
Discovery:
$semanticscholar-skill

Screening and grouping:
$research-literature-review

Evidence support check:
Scite

Literature library and final BibTeX:
Zotero

Final metadata verification:
DOI / publisher / arXiv / PubMed
```

For every paper handed to `$research-literature-review`, include a `source_status` and `next_action` when possible:

| Field | Allowed values |
|---|---|
| `source_status` | `candidate`, `metadata_verified`, `in_zotero`, `claim_support_checked` |
| `next_action` | `verify_metadata`, `add_to_zotero`, `check_with_scite`, `cite_in_related_work`, `do_not_cite_yet` |

When exporting candidates for `docs/thesis/literature-matrix.md`, also include:

| Field | Default |
|---|---|
| `zotero_status` | `not_added` |
| `scite/support_status` | `not_checked` |
| `reading_status` | `not_read` |

## Long-Text Citation Batch Handoff

When the user provides a long thesis section, manuscript draft, or paragraph with many citation-worthy claims, do not search every sentence inline in one response.

Use the `research-literature-review` batch strategy:

| Segment count | Strategy |
|---:|---|
| 1-10 | one search pass with normal candidate notes |
| 11-25 | split into batches of about 10 segments |
| 26+ | split by section, then process each section separately |

For each segment, return compact fields that can be written to `docs/thesis/literature-matrix.md`:

| Field | Meaning |
|---|---|
| `citation_batch` | batch or section ID |
| `segment_id` | stable claim/segment ID |
| `candidate_reference` | candidate paper or identifier |
| `support_grade` | strong, partial, background, limiting, contradictory, or metadata_only |
| `dedupe_key` | DOI, arXiv, CorpusId, or normalized title |
| `export_format` | `bibtex`, `ris`, `zotero-rdf`, or `enw` |

Semantic Scholar remains the discovery and citation-graph tool. Zotero, Scite, DOI, publisher, or arXiv still handle final library sync, claim-support checks, and metadata verification.

## Export Follow-Up

Use helper exports when requested:

- `export_bibtex(papers)`
- `export_markdown(papers)`
- `export_json(papers)`

Do not treat generated BibTeX as final until metadata is checked for important references.
