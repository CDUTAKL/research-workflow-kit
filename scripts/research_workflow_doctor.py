"""One-command health check for a thesis workflow console."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

from export_evidence_graph import build_graph


THESIS_DIR = Path("docs/thesis")
ID_RE = re.compile(r"\b(?:SEC|CLM|EXP|DATA|FIG)-(?:AUTO-)?[A-Za-z0-9.-]+\b")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def markdown_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    return rows


def ids(text: str) -> list[str]:
    return list(dict.fromkeys(ID_RE.findall(text or "")))


def missing(value: str) -> bool:
    return value.strip().lower() in {"", "tbd", "missing", "pending", "n/a", "none"}


def collect(thesis_dir: Path) -> dict[str, object]:
    claims: dict[str, dict[str, str]] = {}
    experiments: dict[str, dict[str, str]] = {}
    datasets: dict[str, dict[str, str]] = {}
    figures: dict[str, dict[str, str]] = {}
    sections: dict[str, dict[str, str]] = {}

    for cells in markdown_rows(read_text(thesis_dir / "claim-evidence-map.md")):
        if cells and len(cells) >= 8 and re.fullmatch(r"CLM-[A-Za-z0-9.-]+", cells[0]):
            claims[cells[0]] = {
                "status": cells[2] if len(cells) > 2 else "",
                "experiments": cells[3] if len(cells) > 3 else "",
                "figures": cells[4] if len(cells) > 4 else "",
                "literature": cells[5] if len(cells) > 5 else "",
                "row": " | ".join(cells),
            }

    for cells in markdown_rows(read_text(thesis_dir / "experiment-registry.md")):
        if cells and re.fullmatch(r"EXP-(?:AUTO-)?[A-Za-z0-9.-]+", cells[0]):
            experiments[cells[0]] = {
                "claim": cells[1] if len(cells) > 1 else "",
                "output": cells[5] if len(cells) > 5 else "",
                "status": cells[7] if len(cells) > 7 else "",
                "row": " | ".join(cells),
            }

    for cells in markdown_rows(read_text(thesis_dir / "data-availability.md")):
        if cells and re.fullmatch(r"DATA-[A-Za-z0-9.-]+", cells[0]):
            datasets[cells[0]] = {
                "claims": cells[2] if len(cells) > 2 else "",
                "experiments": cells[3] if len(cells) > 3 else "",
                "hash": cells[6] if len(cells) > 6 else "",
                "access": cells[7] if len(cells) > 7 else "",
                "status": cells[11] if len(cells) > 11 else "",
            }

    for cells in markdown_rows(read_text(thesis_dir / "figure-plan.md")):
        if cells and re.fullmatch(r"FIG-[A-Za-z0-9.-]+", cells[0]):
            figures[cells[0]] = {"row": " | ".join(cells), "status": cells[-1] if cells else ""}

    for cells in markdown_rows(read_text(thesis_dir / "section-citation-map.md")):
        if cells and re.fullmatch(r"SEC-[A-Za-z0-9.-]+", cells[0]):
            sections[cells[0]] = {
                "coverage": cells[4] if len(cells) > 4 else "",
                "row": " | ".join(cells),
            }

    return {
        "claims": claims,
        "experiments": experiments,
        "datasets": datasets,
        "figures": figures,
        "sections": sections,
    }


def diagnose(thesis_dir: Path) -> tuple[list[str], list[str], list[str], dict[str, object]]:
    data = collect(thesis_dir)
    claims = data["claims"]  # type: ignore[assignment]
    experiments = data["experiments"]  # type: ignore[assignment]
    datasets = data["datasets"]  # type: ignore[assignment]
    figures = data["figures"]  # type: ignore[assignment]
    sections = data["sections"]  # type: ignore[assignment]

    p0: list[str] = []
    p1: list[str] = []
    info: list[str] = []

    required_files = [
        "workflow-dashboard.md",
        "evidence-promotion-policy.md",
        "claim-evidence-map.md",
        "experiment-registry.md",
        "data-availability.md",
        "section-citation-map.md",
        "figure-plan.md",
        "final-audit.md",
    ]
    for name in required_files:
        if not (thesis_dir / name).exists():
            p1.append(f"missing console file: {name}")

    for claim_id, claim in claims.items():
        evidence_text = " | ".join([claim["experiments"], claim["figures"], claim["literature"]])
        if claim["status"].lower() in {"supported", "final"} and not ids(evidence_text):
            p0.append(f"{claim_id} is marked supported but has no structured evidence ID")
        elif not ids(evidence_text) and missing(claim["literature"]):
            p1.append(f"{claim_id} has no experiment, figure, data, section, or literature evidence")

    for exp_id, exp in experiments.items():
        output = exp["output"].strip("` ")
        status = exp["status"].lower()
        if status in {"done", "reviewed"} and missing(output):
            p1.append(f"{exp_id} is {status} but has no output path")
        if status in {"done", "reviewed"} and "remote_desktop_4060" in exp["row"]:
            snapshot = Path(output) / "environment.txt" if output else Path()
            if output and not snapshot.exists():
                p1.append(f"{exp_id} is a formal 4060 run but missing {snapshot}")

    for data_id, dataset in datasets.items():
        if dataset["status"].lower() in {"reviewed", "availability_ready", "restricted_ready"}:
            if missing(dataset["hash"]):
                p1.append(f"{data_id} is reviewed but missing hash/manifest")
            if missing(dataset["access"]):
                p1.append(f"{data_id} is reviewed but missing access level")

    for fig_id, figure in figures.items():
        if figure["status"].lower() in {"final", "done"} and not ids(figure["row"]):
            p1.append(f"{fig_id} is final but has no linked claim/data/experiment ID")

    for section_id, section in sections.items():
        if section["coverage"].lower() in {"missing", "pending", "tbd", ""}:
            p1.append(f"{section_id} has missing section citation coverage")

    info.append(f"claims={len(claims)} experiments={len(experiments)} datasets={len(datasets)} figures={len(figures)} sections={len(sections)}")
    return p0, p1, info, data


def health_status(p0: list[str], p1: list[str]) -> str:
    return "blocked" if p0 else "warning" if p1 else "ok"


def parse_stage_snapshot(thesis_dir: Path) -> list[dict[str, str]]:
    rows = markdown_rows(read_text(thesis_dir / "workflow-dashboard.md"))
    stages: list[dict[str, str]] = []
    for cells in rows:
        if not cells or not cells[0].isdigit():
            continue
        stages.append(
            {
                "stage": cells[0],
                "name": cells[1] if len(cells) > 1 else "",
                "status": cells[2] if len(cells) > 2 else "",
                "record": cells[3] if len(cells) > 3 else "",
                "notes": cells[4] if len(cells) > 4 else "",
            }
        )
    return stages


def parse_current_status(thesis_dir: Path) -> dict[str, str]:
    status: dict[str, str] = {}
    for cells in markdown_rows(read_text(thesis_dir / "workflow-dashboard.md")):
        if len(cells) >= 2 and cells[0].lower() in {
            "current stage",
            "active focus",
            "current audit tier",
            "main blocker",
            "next concrete action",
            "last dashboard refresh",
        }:
            status[cells[0]] = cells[1]
    return status


def to_records(data: dict[str, object]) -> dict[str, list[dict[str, str]]]:
    records: dict[str, list[dict[str, str]]] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            records[key] = [
                {"id": item_id, **item}
                for item_id, item in value.items()
                if isinstance(item, dict)
            ]
    return records


def dashboard_data(
    thesis_dir: Path,
    p0: list[str],
    p1: list[str],
    info: list[str],
    data: dict[str, object],
) -> dict[str, object]:
    records = to_records(data)
    experiments = records.get("experiments", [])
    graph = build_graph(thesis_dir)
    return {
        "generatedAt": dt.datetime.now().isoformat(timespec="seconds"),
        "health": health_status(p0, p1),
        "counts": {
            "claims": len(records.get("claims", [])),
            "experiments": len(records.get("experiments", [])),
            "datasets": len(records.get("datasets", [])),
            "figures": len(records.get("figures", [])),
            "sections": len(records.get("sections", [])),
            "graphNodes": len(graph["nodes"]),
            "graphEdges": len(graph["edges"]),
        },
        "currentStatus": parse_current_status(thesis_dir),
        "stages": parse_stage_snapshot(thesis_dir),
        "issues": {"p0": p0, "p1": p1},
        "summary": info[0] if info else "",
        "recentExperiments": experiments[-5:],
        "records": records,
        "graph": graph,
        "links": {
            "dashboard": "docs/thesis/workflow-dashboard.md",
            "claimMap": "docs/thesis/claim-evidence-map.md",
            "experimentRegistry": "docs/thesis/experiment-registry.md",
            "dataAvailability": "docs/thesis/data-availability.md",
            "figurePlan": "docs/thesis/figure-plan.md",
            "finalAudit": "docs/thesis/final-audit.md",
            "evidenceGraph": "docs/thesis/evidence-graph.json",
        },
    }


def dashboard_block(p0: list[str], p1: list[str], info: list[str], data: dict[str, object]) -> str:
    now = dt.datetime.now().isoformat(timespec="seconds")
    health = health_status(p0, p1)
    lines = [
        f"Generated: {now}",
        "",
        f"**Workflow Health:** `{health}`",
        "",
        "### Counts",
        "",
        f"- {info[0] if info else 'no counts'}",
        "",
        "### P0 Blockers",
        "",
    ]
    lines.extend([f"- {item}" for item in p0] or ["- none"])
    lines.extend(["", "### P1 Issues", ""])
    lines.extend([f"- {item}" for item in p1] or ["- none"])
    lines.extend(["", "### Recent Experiment Candidates", ""])
    experiments = data["experiments"]  # type: ignore[index]
    recent = list(experiments.keys())[-5:] if isinstance(experiments, dict) else []
    lines.extend([f"- {item}" for item in recent] or ["- none"])
    return "\n".join(lines) + "\n"


def write_dashboard(thesis_dir: Path, block: str) -> None:
    path = thesis_dir / "workflow-dashboard.md"
    text = read_text(path)
    start = "<!-- workflow-doctor:start -->"
    end = "<!-- workflow-doctor:end -->"
    if start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        text = before + start + "\n" + block + end + after
    else:
        text = text.rstrip() + "\n\n" + start + "\n" + block + end + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a one-command research workflow health check.")
    parser.add_argument("--thesis-dir", default="docs/thesis")
    parser.add_argument("--write-dashboard", action="store_true")
    parser.add_argument("--write-data", action="store_true", help="Write dashboard JSON for the React/Vite web dashboard.")
    parser.add_argument("--json-out", default="docs/thesis/dashboard-data.json")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()

    thesis_dir = Path(args.thesis_dir)
    p0, p1, info, data = diagnose(thesis_dir)
    block = dashboard_block(p0, p1, info, data)
    print(block.rstrip())
    if args.write_dashboard:
        write_dashboard(thesis_dir, block)
        print(f"\nwrote dashboard: {thesis_dir / 'workflow-dashboard.md'}")
    if args.write_data:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(dashboard_data(thesis_dir, p0, p1, info, data), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"wrote dashboard data: {out}")
    if p0 and not args.warn_only:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
