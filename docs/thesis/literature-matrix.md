# Literature Matrix

## Update Rules

- Add papers here as candidates first, then promote them only after metadata and relevance are checked.
- Use Semantic Scholar for discovery, Zotero for the local library and final BibTeX, and Scite for support/contrast checks on specific claims.
- Do not cite papers marked `do_not_cite_yet` in the manuscript.
- When a new advisor topic is received, start from `topic-intake.md` search directions before broadening the literature search.
- For full-paper reading, store source-grounded artifacts under `docs/thesis/paper-readings/<paper-slug>/` and record reader/source-map paths here.
- For long citation-seeking text, use `section-citation-map.md` plus batch rows so candidate references remain traceable to claim segments.

## Search Scope

| Item | Content |
|---|---|
| Topic | TBD |
| Date range | TBD |
| Search keywords | TBD |
| Excluded topics | TBD |
| Target databases/tools | Semantic Scholar, Zotero, Scite, Web/DOI/publisher |

## Source Status Legend

| Status | Meaning |
|---|---|
| `candidate` | Found during discovery, not yet verified |
| `metadata_verified` | Title, authors, year, venue, and identifier checked |
| `in_zotero` | Added to local Zotero library with attachment or citation data |
| `claim_support_checked` | Scite or direct reading checked whether it supports a concrete claim |

## Reading Status Legend

| Status | Meaning |
|---|---|
| `not_read` | Candidate has not been read beyond metadata or abstract |
| `skimmed` | Abstract, figures, or selected sections checked |
| `full_reader_created` | `paper.md` and source map exist under `docs/thesis/paper-readings/` |
| `directly_read` | Relevant claims were checked against source text, figures, or tables |

## Next Action Legend

| Action | Meaning |
|---|---|
| `verify_metadata` | Check DOI, publisher, arXiv, PubMed, or official page |
| `add_to_zotero` | Add to Zotero and attach PDF or note |
| `check_with_scite` | Check support/contrast context for a manuscript claim |
| `cite_in_related_work` | Ready to cite in the related-work structure |
| `do_not_cite_yet` | Do not cite until relevance or metadata is resolved |

## Core Literature Table

| Paper | Year | Venue | Identifier | Role | Method/Data | Main Finding | Limitation | Use In Manuscript | Source Status | Next Action | Zotero Status | Scite/Support Status | Reading Status | Reader Path | Source Map Path | Key Blocks | Figure/Table Notes | Notes |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TBD | TBD | TBD | DOI/arXiv/S2/PubMed/TBD | foundational/direct competitor/method/dataset/survey | TBD | TBD | TBD | background/related work/method/experiment | candidate | verify_metadata | not_added | not_checked | not_read | TBD | TBD | TBD | TBD |  |

## Related Work Groups

| Group | Representative Papers | Synthesis Point | Citation Gap | Writing Location |
|---|---|---|---|---|
| Problem background | TBD | TBD | TBD | Chapter/section TBD |
| Classical or baseline methods | TBD | TBD | TBD | Chapter/section TBD |
| Modern methods | TBD | TBD | TBD | Chapter/section TBD |
| Datasets and metrics | TBD | TBD | TBD | Chapter/section TBD |
| Limitations and open gaps | TBD | TBD | TBD | Chapter/section TBD |

## Zotero Queue

| Paper | Identifier | Collection / Tag | PDF Attachment | BibTeX Status | Zotero Status | Final Metadata Check | Next Action |
|---|---|---|---|---|---|---|---|
| TBD | DOI/arXiv/S2/PubMed/TBD | thesis/TBD | missing/attached | missing/candidate/final | not_added/in_zotero | pending | add_to_zotero |

## Scite / Claim Support Queue

Use this queue only for claims that matter to the manuscript. Scite checks whether a cited paper supports, contrasts, or merely mentions a specific statement; it does not replace reading the paper.

| Claim ID | Manuscript Statement | Candidate Citation | Expected Support | Scite / Direct Reading Result | Decision | Next Action |
|---|---|---|---|---|---|---|
| CLM-001 | TBD | TBD | supports/contrasts/background | not_checked | pending | check_with_scite |

## Paper Reading Queue

| Paper | Identifier | Reading Status | Reader Path | Source Map Path | Key Blocks | Figure/Table Notes | Next Action |
|---|---|---|---|---|---|---|---|
| TBD | DOI/arXiv/S2/PubMed/TBD | not_read | docs/thesis/paper-readings/TBD/paper.md | docs/thesis/paper-readings/TBD/source_map.json | TBD | TBD | create_reader/skim/direct_read |

## Citation Batch Queue

Use this queue when a thesis section or manuscript paragraph contains many citation-worthy claims.

| Citation Batch | Segment ID | Claim / Segment | Candidate Reference | Support Grade | Dedupe Key | Export Format | Verification Status | Next Action |
|---|---|---|---|---|---|---|---|---|
| BATCH-001 | SEG-001 | TBD | TBD | strong/partial/background/limiting/contradictory/metadata_only | DOI/arXiv/title/TBD | bibtex/ris/zotero-rdf/enw | candidate | verify_metadata/add_to_zotero/check_with_scite |

## Section Citation Map Handoff

| Section ID | Segment Range | Citation Coverage | Reader Evidence Needed | Export Target | Next Action |
|---|---|---|---|---|---|
| SEC-001 | SEG-001/TBD | missing | TBD | BibTeX/RIS/ENW/Zotero RDF | update `section-citation-map.md` |

## Literature Workflow Log

| Date | Action | Tool | Output | Follow-Up |
|---|---|---|---|---|
| TBD | discovery/screening/zotero_sync/scite_check/metadata_verify | Semantic Scholar/Zotero/Scite/Web | TBD | TBD |
