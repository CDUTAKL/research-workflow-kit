#!/usr/bin/env python3
"""Scaffold Topic Intake -> Research Blueprint records for thesis planning.

This helper creates or updates topic-intake.md and inserts review-only
auto-generated blocks into thesis console files. It does not replace reasoning
by the research-paper-plan skill.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


BLOCK_PREFIX = "topic_intake"


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def split_title_terms(title: str) -> list[str]:
    title = normalize_space(title)
    rough = re.split(r"[，,、;；:：\s（）()《》<>/\\|]+", title)
    terms = [term.strip() for term in rough if term.strip()]
    if not terms and title:
        return [title]
    return terms


def detect_task(title: str) -> str:
    patterns = [
        ("classification", ["分类", "识别", "classif"]),
        ("prediction", ["预测", "forecast", "predict"]),
        ("detection", ["检测", "探测", "detect"]),
        ("segmentation", ["分割", "segment"]),
        ("optimization", ["优化", "optimi"]),
        ("generation", ["生成", "generate"]),
        ("review/survey", ["综述", "review", "survey"]),
    ]
    lower = title.lower()
    matched = [name for name, keys in patterns if any(key in lower for key in keys)]
    return ", ".join(matched) if matched else "TBD"


def infer_method_terms(title: str) -> str:
    lower = title.lower()
    terms = []
    known = [
        ("deep learning", ["深度学习", "deep learning"]),
        ("machine learning", ["机器学习", "machine learning"]),
        ("neural network", ["神经网络", "cnn", "transformer", "lstm", "rnn"]),
        ("feature engineering", ["特征", "feature"]),
        ("signal processing", ["信号", "spectrum", "spectral", "频谱", "能谱"]),
    ]
    for name, keys in known:
        if any(key in lower for key in keys):
            terms.append(name)
    return ", ".join(terms) if terms else "TBD"


def make_topic_intake(title: str, paper_type: str, advisor_notes: str) -> str:
    now = dt.date.today().isoformat()
    terms = split_title_terms(title)
    task = detect_task(title)
    method_terms = infer_method_terms(title)
    keyword_candidates = ", ".join(dict.fromkeys(terms + ([task] if task != "TBD" else []) + ([method_terms] if method_terms != "TBD" else [])))

    return f"""# Topic Intake

## Update Rules

- Use this file when the advisor gives a title or fixed topic.
- Preserve the advisor's original wording before rewriting or narrowing it.
- Mark uncertain interpretations as `TBD` and confirm them with the advisor.
- After topic intake, update `thesis-brief.md`, `writing-outline.md`, `literature-matrix.md`, and `experiment-architecture.md`.

## Advisor Topic Record

| Field | Content |
|---|---|
| Original advisor title | {title} |
| Received date | {now} |
| Advisor notes | {advisor_notes or 'TBD'} |
| Degree/project requirement | {paper_type} |
| Known constraints | data/compute/time/template/TBD |

## Topic Intake -> Research Blueprint

| Item | Output |
|---|---|
| 1. Topic decomposition | Title terms: {', '.join(terms) if terms else 'TBD'} |
| 2. Research object | TBD |
| 3. Research task | {task} |
| 4. Keywords and synonyms | {keyword_candidates or 'TBD'} |
| 5. Possible technical routes | baseline route; proposed route; ablation route; robustness/error-analysis route |
| 6. Preliminary innovation candidates | TBD; must be verified by literature and experiments |
| 7. Paper question tree | Main question: what does the topic need to prove? Subquestions: data, method, evaluation, limitation |
| 8. Literature search directions | problem literature; method literature; dataset/metric literature; recent competitor literature; limitation literature |
| 9. Experiment needs | baseline, main comparison, ablation, robustness or error analysis, reproducibility record |
| 10. Figure/table needs | method diagram, data overview, main result table, ablation figure/table, error analysis figure/table |
| 11. Risks and infeasible directions | unclear data, weak novelty, insufficient compute, missing baseline, overbroad title |
| 12. Questions for advisor | confirm data/object, required method, minimum experiment scope, required format, deadline |

## Advisor Confirmation Questions

| Question | Why It Matters | Status | Answer |
|---|---|---|---|
| What is the required research object or dataset? | decides data pipeline and feasibility | pending | TBD |
| Is a specific method required or only suggested? | decides technical route | pending | TBD |
| What is the minimum expected experiment scope? | decides time and compute plan | pending | TBD |
| What format or school template must be followed? | decides writing outline | pending | TBD |

## First-Week Action Plan

| Task | Destination | Status | Notes |
|---|---|---|---|
| Confirm title interpretation | advisor / Notion | planned |  |
| Build first literature query set | `literature-matrix.md` | planned |  |
| Draft experiment feasibility notes | `experiment-architecture.md` | planned |  |
| Update thesis brief | `thesis-brief.md` | planned |  |
"""


def block(name: str, content: str) -> str:
    start = f"<!-- AUTO-GENERATED: {BLOCK_PREFIX}:{name} START -->"
    end = f"<!-- AUTO-GENERATED: {BLOCK_PREFIX}:{name} END -->"
    return f"{start}\n{content.strip()}\n{end}\n"


def replace_block(existing: str, name: str, content: str) -> str:
    new_block = block(name, content)
    start = f"<!-- AUTO-GENERATED: {BLOCK_PREFIX}:{name} START -->"
    end = f"<!-- AUTO-GENERATED: {BLOCK_PREFIX}:{name} END -->"
    if start in existing and end in existing:
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
        return pattern.sub(new_block.strip(), existing).rstrip() + "\n"
    return existing.rstrip() + "\n\n" + new_block


def make_handoff_blocks(title: str, paper_type: str) -> dict[str, str]:
    task = detect_task(title)
    method_terms = infer_method_terms(title)
    return {
        "thesis-brief": f"""## Topic Intake Snapshot

| Field | Draft |
|---|---|
| Advisor title | {title} |
| Paper type | {paper_type} |
| Research task | {task} |
| Method scope | {method_terms} |
| Immediate status | topic received; advisor confirmation pending |
""",
        "writing-outline": f"""## Topic-Derived Writing Blueprint

| Section | Topic-Derived Goal | Evidence Needed | Status |
|---|---|---|---|
| Introduction | explain the title's background, task, gap, and contribution | topic intake + literature matrix | planned |
| Related Work | organize literature by problem, method, data/metric, and limitations | first search directions | planned |
| Method | explain the selected technical route after advisor confirmation | experiment architecture | planned |
| Experiments | test the title-derived claims with baselines and ablations | experiment registry + reproducibility checklist | planned |
""",
        "literature-matrix": f"""## Topic-Derived Search Directions

| Direction | Query Seeds | Purpose | Status |
|---|---|---|---|
| Problem/task literature | {title}; {task} | define research background and task | planned |
| Method literature | {method_terms} | identify candidate routes and baselines | planned |
| Dataset/metric literature | dataset; benchmark; evaluation metric | define experiment protocol | planned |
| Recent competitors | recent papers + direct task terms | identify comparison methods | planned |
| Limitations | failure mode; robustness; error analysis | support discussion and risk framing | planned |
""",
        "experiment-architecture": f"""## Topic-Derived Experiment Blueprint

| Area | Draft Decision | Status |
|---|---|---|
| Advisor title | {title} | received |
| Research task | {task} | draft |
| Candidate method scope | {method_terms} | draft |
| Baseline need | at least one simple and one strong baseline if feasible | planned |
| Main experiment need | full protocol after data and metric are confirmed | planned |
| Ablation need | remove/test proposed components | planned |
| Reproducibility need | config, seed, split, metrics, output path, code version | planned |
""",
    }


def update_file(path: Path, name: str, content: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else f"# {path.stem}\n"
    path.write_text(replace_block(existing, name, content), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Topic Intake -> Research Blueprint console drafts.")
    parser.add_argument("--title", default="", help="Advisor-provided title or topic.")
    parser.add_argument("--title-file", default="", help="UTF-8 text file containing the advisor title; useful for non-ASCII titles.")
    parser.add_argument("--out-dir", default="docs/thesis", help="Thesis console directory.")
    parser.add_argument("--paper-type", default="graduation thesis", help="Paper/project type.")
    parser.add_argument("--advisor-notes", default="", help="Optional advisor notes.")
    parser.add_argument("--dry-run", action="store_true", help="Print drafts without writing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.title_file:
        title = Path(args.title_file).read_text(encoding="utf-8").strip()
    else:
        title = args.title
    title = normalize_space(title)
    if not title:
        raise SystemExit("Provide --title or --title-file.")
    out_dir = Path(args.out_dir)
    intake = make_topic_intake(title, args.paper_type, args.advisor_notes)
    handoffs = make_handoff_blocks(title, args.paper_type)

    if args.dry_run:
        print(intake)
        for name, content in handoffs.items():
            print("\n" + block(name, content))
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "topic-intake.md").write_text(intake, encoding="utf-8")
    update_file(out_dir / "thesis-brief.md", "thesis-brief", handoffs["thesis-brief"])
    update_file(out_dir / "writing-outline.md", "writing-outline", handoffs["writing-outline"])
    update_file(out_dir / "literature-matrix.md", "literature-matrix", handoffs["literature-matrix"])
    update_file(out_dir / "experiment-architecture.md", "experiment-architecture", handoffs["experiment-architecture"])

    print(f"Updated topic intake console in {out_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
