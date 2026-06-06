# Literature Review Workflow

## Search Strategy

Use `docs/thesis/academic-search-policy.md` to choose the right source route before broad searching or metadata verification.

Create queries in layers:

1. Problem terms.
2. Method terms.
3. Data/task terms.
4. Metric/evaluation terms.
5. Application/domain terms.
6. Synonyms and abbreviations.

Example search table:

| Layer | Terms | Purpose |
|---|---|---|
| Problem | classification, prediction, detection | Broad task |
| Method | transformer, CNN, ensemble, self-supervised | Method family |
| Data/task | spectrum, signal, image, sequence | Data modality |
| Evaluation | accuracy, F1, AUC, calibration | Comparable metrics |

## Paper Roles

Classify each paper by role:

- Foundational: defines the problem, method, or standard metric.
- Direct competitor: solves a similar task.
- Method source: introduces a model or algorithm used by the paper.
- Dataset/benchmark: defines data, labels, splits, or evaluation.
- Survey/review: helps structure background, but should not replace primary citations.
- Negative or limitation evidence: shows known failure modes or open gaps.

## Literature Matrix

Use this table.

| Paper | Year | Venue | Identifier | Role | Method/data | Main finding | Limitation | Use in manuscript | Source status | Next action | Zotero status | Scite/support status | Reading status | Reader path | Source map path | Key blocks |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Title | 2024 | Journal/conf | DOI/arXiv/S2/PubMed | Competitor | Method/data | Result | Gap | Related work/method | candidate | verify_metadata | not_added | not_checked | not_read | TBD | TBD | TBD |

Source status:

- `candidate`: discovered but not yet verified.
- `metadata_verified`: title, authors, year, venue, DOI/arXiv/URL checked.
- `source_read_verified`: source-map-backed reading confirms relevance.
- `scite_checked`: support/contrast/mention status has been checked.
- `in_zotero`: added to the local Zotero library and ready for BibTeX/export workflow.
- `claim_support_checked`: checked against a concrete manuscript claim through Scite or direct reading.

Next action:

- `verify_metadata`: check DOI, publisher, arXiv, PubMed, or official page.
- `add_to_zotero`: add to Zotero and attach PDF or notes.
- `check_with_scite`: check whether the paper supports or contrasts a specific claim.
- `cite_in_related_work`: ready to cite in the related-work structure.
- `do_not_cite_yet`: do not cite until relevance or metadata is resolved.

Zotero status:

- `not_added`: not yet in the local library.
- `in_zotero`: visible in Zotero Desktop/local plugin.
- `pdf_attached`: PDF or attachment is linked.
- `bibtex_exported`: final BibTeX was exported from Zotero.

Scite/support status:

- `not_checked`: no support/contrast check yet.
- `supports_claim`: supports the specific manuscript statement.
- `contrasts_claim`: contrasts or disputes the statement.
- `mentions_only`: related but does not support the statement.
- `needs_direct_reading`: Scite or metadata is insufficient; read the paper.

Reading status:

- `not_read`: candidate has not been read beyond metadata or abstract.
- `skimmed`: abstract, figures, or selected sections checked.
- `full_reader_created`: a source-grounded reader exists under `docs/thesis/paper-readings/<paper-slug>/`.
- `directly_read`: relevant claims were checked against source text, figures, or tables.

## Related Work Structure

Prefer grouped synthesis:

```text
Paragraph 1: problem and task development.
Paragraph 2: classical or baseline methods.
Paragraph 3: modern/deep learning methods.
Paragraph 4: evaluation gaps and limitations.
Paragraph 5: positioning of the user's work.
```

Avoid:

- One paragraph per paper.
- Unsupported "few studies have..." claims.
- Citing a survey for a method that has an original paper.
- Mixing dataset, method, and result comparisons without a clear organizing axis.

## Citation Follow-Up

When exact metadata matters:

- Use `$semanticscholar-skill` for real Semantic Scholar discovery, citation graph, author lookup, similar papers, and candidate BibTeX/JSON.
- Use Zotero for local library organization, PDF attachment management, final BibTeX export, and citation insertion once Zotero Desktop is available.
- Use Scite for whether a paper supports, contrasts, or only mentions a concrete claim.
- Use PubMed for biomedical PMID/MeSH-driven searches, CrossRef or DOI pages for metadata, arXiv for preprints, and publisher pages for final title, author, year, venue, and DOI checks.

## Literature Matrix To Zotero / Scite Workflow

Use this as the default handoff sequence after candidate discovery:

| Stage | Input | Tool | Output field to update | Stop condition |
|---|---|---|---|---|
| Candidate discovery | topic query, seed papers | `$semanticscholar-skill` | `source_status=candidate`, `next_action=verify_metadata` | enough relevant candidates found |
| Metadata verification | DOI/arXiv/S2/PubMed/publisher page | Web / DOI / publisher | `source_status=metadata_verified` | title, authors, year, venue, identifier checked |
| Library sync | verified paper | Zotero plugin | `zotero_status=in_zotero` or `pdf_attached` | paper appears in local Zotero collection |
| BibTeX export | Zotero library entry | Zotero plugin | `zotero_status=bibtex_exported` | BibTeX key is stable for manuscript use |
| Claim support check | manuscript claim + paper | Scite plugin or direct reading | `scite/support status` and `source_status=claim_support_checked` | claim is supportable, weakened, or citation rejected |
| Citation decision | matrix row + claim map | `$research-literature-review` | `next_action=cite_in_related_work` or `do_not_cite_yet` | row is ready or blocked |

Use these queues in `docs/thesis/literature-matrix.md`:

- `Zotero Queue` for papers that need local library or BibTeX work.
- `Scite / Claim Support Queue` for papers tied to important claims.
- `Literature Workflow Log` for recording discovery, sync, and verification passes.

Do not move a paper to `cite_in_related_work` until metadata is verified. Do not use a citation as evidence for a claim until Scite or direct reading confirms support.

## Source-Grounded Paper Reading

Use this workflow when the user asks for full-paper translation, paper reading notes, PDF deep reading, original/Chinese alignment, figure-text correspondence, or when Scite is insufficient for a key claim.

Default artifact location:

```text
docs/thesis/paper-readings/<paper-slug>/
  paper.md
  source_map.json
  translation_notes.md
  assets/
```

Handoff:

```text
PDF / arXiv / publisher HTML / pasted paper
-> `$pdf` for extraction, rendering checks, figure/table crops
-> source-grounded paper reader artifact
-> `literature-matrix.md` reading fields
-> `claim-evidence-map.md` if the paper supports an important claim
```

Reader artifact rules:

- Process the full paper unless the user explicitly asks for a preview.
- Keep original text and Chinese translation together when translation is requested.
- Preserve section order, paragraph order, citations, equations, units, and terminology.
- Assign stable anchors: `S001` body text, `C001` captions, `F001` figures, `T001` tables.
- Place figures and tables near the body text that first discusses them.
- Do not turn a full-paper reader into summary bullets.

Update the literature matrix with:

| Field | Meaning |
|---|---|
| `reading_status` | `not_read`, `skimmed`, `full_reader_created`, or `directly_read` |
| `reader_path` | path to `paper.md` |
| `source_map_path` | path to `source_map.json` |
| `key_blocks` | source block IDs used later, such as `p.4 S012-S013` |
| `figure_table_notes` | important figure/table evidence and crop notes |

Before marking a citation as `claim_support_checked`, require either a Scite result or source-map-backed direct reading evidence.

## Long-Article Citation Batch Strategy

Use this strategy when a paragraph, thesis section, or manuscript draft contains many citation-worthy claims. It adapts the latest `nature-citation` batch logic while preserving this workflow's Semantic Scholar + Zotero + Scite responsibilities.

| Segment count | Strategy | Output |
|---:|---|---|
| 1-10 | search once and allow detailed inline analysis | candidate table + next actions |
| 11-25 | process batches of about 10 segments | compact citation summary + matrix updates |
| 26+ | split by section and process each section independently | section-level files, compact summary, DOI/title dedupe |

Batch rules:

- Split by section or paragraph before arbitrary sentence chunks.
- Assign stable `segment_id` values so citation candidates can be traced back to manuscript claims.
- Deduplicate by DOI, arXiv ID, Semantic Scholar CorpusId, or normalized title.
- Do not present candidate citations as final references until metadata is verified.
- Keep long per-segment reasoning out of chat; write compact tables and update queues.

Recommended citation batch fields:

| Field | Purpose |
|---|---|
| `citation_batch` | batch or section ID |
| `segment_id` | stable claim/segment ID |
| `candidate_reference` | candidate paper or DOI/arXiv/S2 ID |
| `support_grade` | strong, partial, background, limiting, contradictory, or metadata_only |
| `dedupe_key` | DOI/arXiv/title key used for merging |
| `export_format` | `bibtex`, `ris`, `zotero-rdf`, or `enw` |

Tool responsibilities remain:

- Semantic Scholar: discovery, citation graph, similar papers.
- Nature-citation strategy: long-text segmentation, batching, candidate export discipline.
- Zotero: final library, PDF attachments, stable BibTeX.
- Scite: supports/contrasts/mentions checks for concrete claims.
- DOI/publisher/arXiv: final metadata verification.

## Section-Level Citation Matching

Use `docs/thesis/section-citation-map.md` when the user wants papers matched to each thesis chapter, section, paragraph, or claim unit.

Default sequence:

```text
thesis section or outline
-> SEC-* section records
-> SEG-* citation-worthy segments
-> Semantic Scholar candidate search
-> metadata verification
-> Zotero queue
-> Scite or source-grounded reader check
-> cite / do_not_cite_yet decision
```

Required fields:

| Field | Purpose |
|---|---|
| `Section ID` | stable `SEC-*` ID for chapter or subsection |
| `Segment ID` | stable `SEG-*` ID for claim-bearing text |
| `Candidate Reference` | paper title, DOI, arXiv, or S2 ID |
| `Support Grade` | strong, partial, background, limiting, contradictory, or metadata_only |
| `Source Status` | candidate, metadata_verified, in_zotero, or claim_support_checked |
| `Scite / Reader Status` | not_checked, supports_claim, mentions_only, needs_direct_reading, or source-map block |
| `Export Format` | bibtex, ris, enw, or zotero-rdf |

Run the audit script when a section is ready for writing:

```bash
python scripts/audit_section_citations.py --warn-only
```

## Tool Responsibility Table

| Tool | Best use | Not suitable for |
|---|---|---|
| `$semanticscholar-skill` | Discover papers, inspect authors, traverse citations, find similar papers, export candidate BibTeX/JSON | Acting as the only final authority for citation truth |
| Zotero plugin | Manage the local literature library, export final BibTeX, insert citations, organize PDF attachments | Broad discovery of new literature |
| Scite plugin | Check whether a specific paper supports or contrasts a specific statement | Replacing a literature manager |
| Web / DOI / publisher | Verify final title, authors, year, venue, DOI, and official versions | Batch literature organization |
| `$pdf` + source-grounded reader | Full-paper reading, original/translation alignment, figure/table grounding, page/block anchors | Large-scale discovery or final reference-manager export |

Recommended chain:

```text
Discovery:
$semanticscholar-skill

Screening and grouping:
$research-literature-review

Claim-support checks:
Scite

Local library and final BibTeX:
Zotero

Final metadata verification:
DOI / publisher / arXiv / PubMed
```

## Integrated Workflow

For a full literature task, use this sequence:

```text
$research-workflow-orchestrator
  -> $research-literature-review for scope and matrix design
  -> $semanticscholar-skill for actual paper discovery and metadata
  -> Scite for support/contrast checks on important claims
  -> Zotero plugin for local library organization when available
```

If local Zotero is unavailable, keep BibTeX candidates and mark Zotero sync as pending.

## Final Output Checklist

- Keywords cover problem, method, data, and metric terms.
- Matrix separates role and citation use.
- Each core paper has `source_status` and `next_action`.
- Zotero and Scite/support statuses are explicit for important papers.
- Related work is grouped by concept.
- Missing literature is explicit.
- No unverified references are presented as final citations.
