# Literature and Citations

## Default Search Stack

Use this order for research literature workflows:

1. `$research-literature-review` to define search scope, paper roles, and the literature matrix.
2. `$semanticscholar-skill` for real discovery, metadata, citations, recommendations, and BibTeX candidates.
3. Scite when the user needs to know whether a paper supports or contrasts a specific claim.
4. Zotero plugin/local Zotero Desktop for local library search, BibTeX export, and citation insertion.
5. Publisher, DOI, arXiv, PubMed, or official pages for final metadata verification.

## Zotero Priority

Use local Zotero first when available:

```text
If local Zotero Desktop/plugin is available:
  use Zotero plugin for local library search, BibTeX export, citation insertion.
Else if Zotero Web API credentials are explicitly provided:
  use pyzotero-style Web API guidance as a fallback.
Else:
  use Semantic Scholar + BibTeX candidates and mark Zotero sync as pending.
```

Do not ask for Zotero API keys unless the user explicitly wants Web API automation.

## Literature Matrix Fields

| Paper | Year | Venue | Identifier | Role | Method/data | Main finding | Limitation | Use in manuscript | Source status | Next action | Zotero status | Scite/support status |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|

Roles:

- foundational
- direct competitor
- method source
- dataset or benchmark source
- survey or review
- limitation or negative evidence

Source status:

- `candidate`: discovered but not verified.
- `metadata_verified`: title, authors, year, venue, DOI/arXiv/URL checked.
- `in_zotero`: local library entry exists.
- `claim_support_checked`: support/contrast has been checked for a concrete claim.

Zotero status:

- `not_added`
- `in_zotero`
- `pdf_attached`
- `bibtex_exported`

Scite/support status:

- `not_checked`
- `supports_claim`
- `contrasts_claim`
- `mentions_only`
- `needs_direct_reading`

## Matrix To Citation Workflow

```text
Semantic Scholar discovery
  -> metadata verification through DOI / publisher / arXiv / PubMed
  -> Zotero local-library sync and BibTeX export
  -> Scite or direct-reading support check for important claims
  -> related-work citation or do-not-cite decision
```

Use `docs/thesis/literature-matrix.md` queues to track Zotero sync, Scite claim checks, and citation decisions.

## Citation Audit Rules

- Do not cite an unverified paper as final evidence.
- Prefer primary sources for methods, datasets, metrics, and factual claims.
- Mark exact unsupported sentences as `[citation needed]` or `[evidence needed]`.
- Keep citation keys stable once manuscripts use them.
