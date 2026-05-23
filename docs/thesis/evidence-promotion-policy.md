# Evidence Promotion Policy

## Purpose

This file defines how thesis evidence moves from rough candidate material to defensible thesis evidence. Use it before promoting claims, experiments, data, figures, citations, or defense slides.

## Stable ID System

| ID Family | Meaning | Example | Primary File | Rule |
|---|---|---|---|---|
| `SEC-*` | thesis section or subsection | `SEC-INTRO-001` | `section-citation-map.md`, `writing-outline.md` | every citation-heavy or claim-heavy section gets a section ID |
| `CLM-*` | thesis claim | `CLM-001` | `claim-evidence-map.md` | every conclusion, contribution, or quantitative statement needs a claim ID |
| `EXP-*` | reviewed experiment or planned experiment | `EXP-001` | `experiment-registry.md` | every result-bearing run needs an experiment ID |
| `EXP-AUTO-*` | imported or iterative candidate experiment | `EXP-AUTO-001` | `autoresearch-results.tsv` | cannot support final claims until reviewed and promoted |
| `DATA-*` | source dataset, processed dataset, split, or data snapshot | `DATA-001` | `data-availability.md` | every data-backed claim must trace to at least one data ID |
| `FIG-*` | final thesis figure, table, or visual evidence artifact | `FIG-001` | `figure-plan.md` | every final figure/table must trace to data, experiment, claim, or literature |

`SEG-*` is allowed as a subordinate citation unit inside a `SEC-*` section. It is useful for chapter-level citation matching, but it does not replace `SEC-*` or `CLM-*`.

Legacy figure IDs such as `Fig-001`, `Table-001`, or `Arch-001` should be mapped to `FIG-*` before final audit. Architecture figures may keep an internal `ARCH-*` note, but the manuscript-facing evidence ID should be `FIG-*`.

## ID Relationship Rules

| Relationship | Required Link |
|---|---|
| `SEC-* -> CLM-*` | every claim-heavy section lists the claims it contains |
| `SEC-* -> SEG-*` | citation-heavy sections can be split into citation units |
| `CLM-* -> EXP-*` | empirical claims link to reviewed experiment evidence |
| `CLM-* -> DATA-*` | data-backed claims link to source or processed data |
| `CLM-* -> FIG-*` | visualized claims link to final figures/tables |
| `EXP-* -> DATA-*` | experiments record dataset/split provenance |
| `EXP-* -> outputs/EXP-*` | experiments record machine-readable artifacts |
| `FIG-* -> DATA-* / EXP-* / CLM-*` | figures/tables record source data and the claim they illustrate |

## Evidence Promotion States

| Evidence Type | Candidate | Intermediate | Promoted | Blocked |
|---|---|---|---|---|
| claim | `missing` | `weak` | `supported` | `unsupported` |
| experiment | `planned` / `candidate` | `ready_to_run` / `completed_unreviewed` | `reviewed` / `done` | `invalid` / `needs_rerun` |
| citation | `candidate` | `metadata_verified` / `in_zotero` | `supports_claim` / `cite_in_related_work` | `contradictory` / `not_supporting` |
| data | `missing` | `recorded` / `traceable` | `availability_ready` / `restricted_ready` | `untraceable` |
| figure/table | `planned` | `generated` / `audited` | `final` | `obsolete` / `misleading` |
| slide | `draft` | `trace_checked` | `defense_ready` | `overclaim` |

## Promotion Gates

| Gate | Minimum Requirement | Blocks |
|---|---|---|
| Claim gate | `CLM-*` has exact scope, evidence links, and caveat when needed | final writing, slides |
| Experiment gate | `EXP-*` has config, seed/split/metric, registry row, outputs, and review status | result claim support |
| Remote GPU gate | `remote_desktop_4060` formal run has an environment snapshot | promoting GPU result to reviewed |
| Data gate | `DATA-*` has source path, access condition, hash/manifest or reason missing, and generation command | data-backed claim support |
| Figure gate | `FIG-*` has source data/script, caption-safe wording, export path, and audit status | final manuscript figure/table |
| Citation gate | important citation has metadata and sentence-level support checked | related work and background claims |
| Slide gate | slide claim links to `CLM-*`, `FIG-*`, `DATA-*`, or `SEC-*` evidence | defense-ready deck |

## Remote Desktop 4060 Environment Snapshot

The desktop 4060 environment is treated as a fixed formal experiment profile once CUDA, PyTorch, Python, driver, and project environment versions are known. Even when fixed, each formal run should save a small snapshot file because reviewers and future reruns need evidence, not memory.

Required snapshot path:

```text
outputs/EXP-001/environment.txt
```

Minimum content:

- timestamp and host label
- GPU and driver output from `nvidia-smi` when available
- Python version
- PyTorch version and CUDA runtime reported by PyTorch
- package list or environment export
- git branch, commit, and dirty-state summary
- command used to produce the snapshot

Use:

```bash
python scripts/write_environment_snapshot.py --out outputs/EXP-001/environment.txt --label remote_desktop_4060
```

Then run the post-run contract check:

```bash
python scripts/check_experiment_contract.py --experiment-id EXP-001 --require-outputs --require-env-snapshot
```

## Audit Tiers

| Tier | When | Main Question | Typical Scope |
|---|---|---|---|
| `quick` | daily or before a small handoff | can this work safely continue? | changed claims, new outputs, new citations, new figures |
| `advisor` | before supervisor review or milestone meeting | is the story defensible enough for feedback? | claims, section citations, figures, data, code contracts, limitations |
| `final` | before submission, defense, or PDF/DOCX release | is the thesis ready to stand on its evidence? | full manuscript, final figures, data availability, environment snapshots, slides, formatting |

## Hard Rules

- Do not promote a `CLM-*` claim to `supported` with only a polished paragraph or slide.
- Do not promote a GPU result to `reviewed` without a 4060 or cloud environment snapshot.
- Do not mark a `FIG-*` final if the source data, script/notebook, or caption-safe claim is missing.
- Do not use `EXP-AUTO-*` as final evidence until it is reviewed and either promoted into an `EXP-*` record or explicitly recorded as supporting but non-final.
- Do not hide data restrictions. Restricted data can still be defensible when access limits, provenance, and verification route are recorded.
