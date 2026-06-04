# Document Production

## Tool Routing

- Treat document production as a two-device handoff. Stage 11 happens on the Mac: draft DOCX/PDF/PPTX artifacts, inspect evidence/citations, and prepare the handoff package. Stage 12 happens on the user's laptop: verify the package, finalize layout/export, and finish defense materials.
- Use the Documents plugin (`documents:documents` in Codex plugin contexts) for `.docx` reading, editing, formatting, and thesis templates.
- Use `$pdf` for PDF reading, visual rendering checks, extraction, and final PDF review.
- Use LaTeX only after running the LaTeX doctor; compile only when the doctor finds a usable TeX runtime.
- Use `$research-final-audit` before final submission or defense.

## DOCX Workflow

For DOCX templates:

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

- Run the LaTeX doctor first.
- Compile with the available project command or the LaTeX compile skill only after a runtime is available.
- Treat missing references, missing citations, overfull boxes in critical areas, and broken figures as final-audit issues.
- Keep figure filenames stable and captions in the source document.

## Final Production Checklist

- Mac draft artifact path and laptop final artifact path/version are recorded in `docs/thesis/final-artifact-manifest.md` and `docs/thesis/final-audit.md`.
- Abstract and keywords satisfy template requirements.
- Figures and tables are numbered and cited in text.
- Equations are numbered only when referenced, and variables are defined.
- References render in the required style.
- Appendix and acknowledgments are complete if required.
- Final PDF/Word rendering has no clipped or overlapping content.
