# Document Production

## Tool Routing

- Use `$doc` for `.docx` reading, editing, formatting, and Word thesis templates.
- Use `$pdf` for PDF reading, visual rendering checks, extraction, and final PDF review.
- Use LaTeX Tectonic when the manuscript is LaTeX and compilation or PDF production matters.
- Use `$research-final-audit` before final submission or defense.

## DOCX Workflow

For Word templates:

1. Inspect document structure before editing.
2. Preserve existing styles and layout.
3. Use structured edits with `python-docx` when possible.
4. Render or export to PDF for visual checks when tools are available.
5. Check headings, captions, references, page breaks, and table layout.

## PDF Workflow

For final PDF review:

1. Render pages to images when layout matters.
2. Inspect figure sharpness, table alignment, page numbering, headers, and fonts.
3. Check citations and references in the rendered output, not only source files.
4. Record issues in `docs/thesis/final-audit.md` or the project audit file.

## LaTeX Workflow

For LaTeX manuscripts:

- Compile with the available project command or LaTeX Tectonic.
- Treat missing references, missing citations, overfull boxes in critical areas, and broken figures as final-audit issues.
- Keep figure filenames stable and captions in the source document.

## Final Production Checklist

- Abstract and keywords satisfy template requirements.
- Figures and tables are numbered and cited in text.
- Equations are numbered only when referenced, and variables are defined.
- References render in the required style.
- Appendix and acknowledgments are complete if required.
- Final PDF/Word rendering has no clipped or overlapping content.
