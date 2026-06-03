"""One-command health check for a thesis workflow console."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

from audit_final_artifacts import audit as audit_final_artifacts
from audit_id_lifecycle import audit as audit_id_lifecycle
from audit_skills import audit_repo, render_report
from export_evidence_graph import build_graph
from plugin_gate_advisor import recommend_plugins

THESIS_DIR = Path("docs/thesis")
ID_RE = re.compile(r"\b(?:SEC|SEG|CLM|EXP|DATA|FIG|MAT|CIT|BMK|ZCOL|DRT|ZREV)-(?:AUTO-)?[A-Za-z0-9.-]+\b")

STAGE_WORKSPACES = {
    "1": {
        "name": "Paper planning",
        "fileKeys": ["dashboard", "dailyWorkflowEntry"],
        "commands": ["python scripts/research_workflow_doctor.py --warn-only"],
        "recommendedActions": ["Clarify current thesis topic, blocker, and next concrete action."],
    },
    "2": {
        "name": "Literature discovery and review",
        "fileKeys": ["sectionCitationMap", "deepResearchTasks", "citationProvenance", "zoteroScreeningLoop"],
        "commands": ["python scripts/suggest_section_citations.py --section-id SEC-INTRO-001"],
        "recommendedActions": ["Check citation coverage and confirm which suggested papers should become formal citation evidence."],
    },
    "3": {
        "name": "Experiment question definition",
        "fileKeys": ["claimMap", "dailyWorkflowEntry"],
        "commands": ["python scripts/research_workflow_doctor.py --warn-only"],
        "recommendedActions": ["Map the next thesis claim to required experiment, data, citation, or figure evidence."],
    },
    "4": {
        "name": "Experiment architecture planning",
        "fileKeys": ["experimentRegistry", "benchmarkReportSchema"],
        "commands": ["python scripts/check_experiment_contract.py --experiment-id EXP-001 --warn-only"],
        "recommendedActions": ["Define config, split, metric, output path, and smoke-test contract before coding."],
    },
    "5": {
        "name": "Research code implementation",
        "fileKeys": ["experimentRegistry", "benchmarkReportSchema"],
        "commands": ["python scripts/check_experiment_contract.py --experiment-id EXP-001 --warn-only"],
        "recommendedActions": ["Keep code config-driven and make the next experiment runnable as a smoke test."],
    },
    "6": {
        "name": "Experiment run and monitoring",
        "fileKeys": ["experimentRegistry", "benchmarkReportSchema"],
        "commands": ["python scripts/write_environment_snapshot.py --out outputs/EXP-001/environment.txt --label remote_desktop_4060"],
        "recommendedActions": ["Run local smoke first, then 4060 formal run with environment snapshot and output manifest."],
    },
    "7": {
        "name": "Experiment recording and result scan",
        "fileKeys": ["experimentRegistry", "dataAvailability"],
        "commands": ["python scripts/new_experiment_report.py --experiment-id EXP-001 --baseline EXP-000"],
        "recommendedActions": ["Record outputs, metrics, baseline delta, and data trace before promoting evidence."],
    },
    "8": {
        "name": "Results analysis and claim mapping",
        "fileKeys": ["claimMap", "dataAvailability", "benchmarkReportSchema"],
        "commands": ["python scripts/new_experiment_report.py --experiment-id EXP-001 --baseline EXP-000"],
        "recommendedActions": ["Promote only conservative claims that match result, data, and citation evidence."],
    },
    "9": {
        "name": "Figure and table production",
        "fileKeys": ["figurePlan", "diagramReplicaTasks"],
        "commands": ["python scripts/export_evidence_graph.py"],
        "recommendedActions": ["Check source data and source-of-truth notes before final draw.io/Python/PPTX exports."],
    },
    "10": {
        "name": "Paper writing and polishing",
        "fileKeys": ["sectionCitationMap", "citationProvenance", "claimMap"],
        "commands": ["python scripts/audit_section_citations.py --warn-only"],
        "recommendedActions": ["Write only from supported claims and verified section citation coverage."],
    },
    "11": {
        "name": "Laptop DOCX / PDF production",
        "fileKeys": ["finalArtifactManifest", "dailyWorkflowEntry"],
        "commands": ["python scripts/package_final_handoff.py"],
        "recommendedActions": ["Package final artifacts from the manifest and move the zip to the laptop."],
    },
    "12": {
        "name": "Final audit and defense",
        "fileKeys": ["finalAudit", "finalArtifactManifest"],
        "commands": ["python scripts/audit_final_artifacts.py --tier final --warn-only"],
        "recommendedActions": ["Verify laptop artifacts, checksums, final audit tier, and defense slide evidence."],
    },
}


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
        "daily-workflow-entry.md",
        "evidence-promotion-policy.md",
        "id-lifecycle-policy.md",
        "material-passport.md",
        "claim-evidence-map.md",
        "experiment-registry.md",
        "benchmark-report-schema.md",
        "data-availability.md",
        "section-citation-map.md",
        "citation-provenance.md",
        "zotero-screening-loop.md",
        "zotero-collection-coverage.md",
        "figure-plan.md",
        "diagram-replica-tasks.md",
        "final-artifact-manifest.md",
        "final-audit.md",
        "workflow-edit-log.md",
        "plugin-gate-policy.md",
        "plugin-review-log.md",
        "dashboard-ux-qa.md",
        "data-quality-report.md",
        "metric-diagnostics.md",
        "visual-design-review.md",
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

    final_p0, final_p1, final_info, final_artifacts = audit_final_artifacts(thesis_dir, tier="quick")
    id_p0, id_p1, id_info, id_details = audit_id_lifecycle(thesis_dir)
    p0.extend(final_p0)
    p0.extend(id_p0)
    p1.extend(final_p1)
    p1.extend(id_p1)
    plugin_gate = recommend_plugins(thesis_dir, issues=p0 + p1)
    plugin_health = plugin_gate.get("health", {})
    if isinstance(plugin_health, dict):
        if plugin_health.get("missingPolicy"):
            p1.append("missing plugin gate policy")
        if plugin_health.get("missingReviewLog"):
            p1.append("missing plugin review log")
    for item in plugin_gate.get("recommendations", []):
        if isinstance(item, dict) and item.get("status") == "pending_required":
            p1.append(f"plugin gate pending: {item.get('plugin')} for stage {item.get('stage')} -> {item.get('record')}")

    info.append(f"claims={len(claims)} experiments={len(experiments)} datasets={len(datasets)} figures={len(figures)} sections={len(sections)}")
    data["final_artifacts"] = final_artifacts
    data["id_lifecycle"] = id_details
    data["plugin_gate"] = plugin_gate
    info.extend(final_info)
    info.extend(id_info)
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


def collect_experiment_reports(thesis_dir: Path) -> list[dict[str, str]]:
    reports_dir = thesis_dir / "experiment-reports"
    if not reports_dir.exists():
        return []
    reports: list[dict[str, str]] = []
    for path in sorted(reports_dir.glob("EXP-*.md")):
        text = read_text(path)
        report_id = path.stem
        promotion = ""
        env_status = ""
        for line in text.splitlines():
            if line.startswith("- Claim promotion decision:"):
                promotion = line.split(":", 1)[1].strip()
            elif line.startswith("- Environment snapshot:"):
                env_status = line.split(":", 1)[1].strip()
            elif line.startswith("| Environment Snapshot |"):
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                env_status = cells[1] if len(cells) > 1 else env_status
            elif line.startswith("| pending |") and "Promote only after" in line:
                promotion = "pending"
        reports.append(
            {
                "id": report_id,
                "path": path.as_posix(),
                "status": promotion or "TBD",
                "row": f"env: {env_status or 'TBD'} | {path.as_posix()}",
            }
        )
    return reports


def collect_citation_suggestions(thesis_dir: Path) -> list[dict[str, str]]:
    suggestions: list[dict[str, str]] = []
    for cells in markdown_rows(read_text(thesis_dir / "section-citation-suggestions.md")):
        if len(cells) >= 10 and cells[0].isdigit():
            suggestions.append(
                {
                    "rank": cells[0],
                    "score": cells[1],
                    "sectionId": cells[2],
                    "segmentId": cells[3],
                    "candidateReference": cells[4],
                    "identifier": cells[5],
                    "source": cells[6],
                    "status": cells[7],
                    "suggestedUse": cells[8],
                    "reasons": cells[9],
                }
            )
    return suggestions[:10]


def truthy_status(value: str, positive: set[str]) -> str:
    normalized = value.strip().lower()
    if not normalized or normalized in {"tbd", "missing", "not_checked", "not_added", "unchecked", "pending"}:
        return "missing"
    if "/" in normalized and "tbd" in normalized:
        return "missing"
    return "verified" if normalized in positive else "candidate"


def support_cell_status(support: str, source_status: str, reader_status: str) -> str:
    support_normalized = support.strip().lower()
    if support_normalized in {"contradictory", "contradicts", "limiting", "limit"}:
        return "risk"
    if support_normalized in {"strong", "partial", "background", "supports", "support"}:
        if truthy_status(source_status, {"metadata_verified", "verified", "final"}) == "verified" or truthy_status(
            reader_status,
            {"supports", "supports_claim", "partial", "background", "source_map", "reader_checked", "directly_read"},
        ) == "verified":
            return "verified"
        return "candidate"
    return "missing"


def stronger_status(current: str, candidate: str) -> str:
    order = {"missing": 0, "candidate": 1, "verified": 2, "risk": 3}
    return candidate if order.get(candidate, 0) > order.get(current, 0) else current


def collect_section_citation_coverage(thesis_dir: Path) -> list[dict[str, str]]:
    coverage: dict[str, dict[str, str]] = {}

    def ensure(section_id: str, segment_id: str = "") -> dict[str, str]:
        key = segment_id or section_id
        item = coverage.setdefault(
            key,
            {
                "sectionId": section_id,
                "segmentId": segment_id,
                "strong": "missing",
                "partial": "missing",
                "background": "missing",
                "contradictory": "missing",
                "zoteroChecked": "missing",
                "readerChecked": "missing",
                "status": "missing",
                "candidateReferences": "",
                "identifiers": "",
                "zoteroStatus": "",
                "readerStatus": "",
                "nextAction": "",
            },
        )
        return item

    def add_detail(item: dict[str, str], field: str, value: str) -> None:
        clean = value.strip()
        if missing(clean):
            return
        parts = [part.strip() for part in item[field].split(";") if part.strip()]
        if clean not in parts:
            parts.append(clean)
        item[field] = "; ".join(parts)

    for cells in markdown_rows(read_text(thesis_dir / "section-citation-map.md")):
        if len(cells) >= 6 and re.fullmatch(r"SEC-[A-Za-z0-9.-]+", cells[0]):
            item = ensure(cells[0])
            status = cells[4].strip().lower()
            item["status"] = "missing" if status in {"missing", "pending", "tbd", ""} else "candidate"
            add_detail(item, "nextAction", cells[5] if len(cells) > 5 else "")
        elif len(cells) >= 11 and re.fullmatch(r"SEG-[A-Za-z0-9.-]+", cells[0]):
            item = ensure(cells[1], cells[0])
            support = cells[5]
            source_status = cells[6]
            zotero_status = cells[7]
            reader_status = cells[8]
            support_status = support_cell_status(support, source_status, reader_status)
            support_lower = support.strip().lower()
            if support_lower == "strong":
                item["strong"] = stronger_status(item["strong"], support_status)
            elif support_lower == "partial":
                item["partial"] = stronger_status(item["partial"], support_status)
            elif support_lower == "background":
                item["background"] = stronger_status(item["background"], support_status)
            elif support_lower in {"limiting", "contradictory"}:
                item["contradictory"] = stronger_status(item["contradictory"], "risk")
            item["zoteroChecked"] = stronger_status(item["zoteroChecked"], truthy_status(zotero_status, {"in_zotero", "final"}))
            item["readerChecked"] = stronger_status(
                item["readerChecked"],
                truthy_status(reader_status, {"supports_claim", "supports", "source_map", "reader_checked", "directly_read"}),
            )
            add_detail(item, "candidateReferences", cells[3])
            add_detail(item, "identifiers", cells[4])
            add_detail(item, "zoteroStatus", zotero_status)
            add_detail(item, "readerStatus", reader_status)
            add_detail(item, "nextAction", cells[10])

    for cells in markdown_rows(read_text(thesis_dir / "citation-provenance.md")):
        if len(cells) >= 15 and re.fullmatch(r"CIT-[A-Za-z0-9.-]+", cells[0]):
            item = ensure(cells[1], "" if missing(cells[2]) else cells[2])
            support_status = cells[8].strip().lower()
            if support_status == "supports":
                item["strong"] = stronger_status(item["strong"], "verified")
            elif support_status == "partial":
                item["partial"] = stronger_status(item["partial"], "verified")
            elif support_status == "background":
                item["background"] = stronger_status(item["background"], "verified")
            elif support_status in {"contradicts", "contradictory"}:
                item["contradictory"] = stronger_status(item["contradictory"], "risk")
            item["zoteroChecked"] = stronger_status(item["zoteroChecked"], truthy_status(cells[9], {"in_zotero", "final"}))
            item["readerChecked"] = stronger_status(
                item["readerChecked"],
                truthy_status(cells[10], {"scite", "reader", "source_map", "supports", "directly_read"}),
            )
            add_detail(item, "candidateReferences", cells[4])
            add_detail(item, "identifiers", cells[5])
            add_detail(item, "zoteroStatus", cells[9])
            add_detail(item, "readerStatus", cells[10])
            add_detail(item, "nextAction", cells[14])

    for cells in markdown_rows(read_text(thesis_dir / "section-citation-suggestions.md")):
        if len(cells) >= 10 and cells[0].isdigit() and re.fullmatch(r"SEC-[A-Za-z0-9.-]+", cells[2]):
            item = ensure(cells[2], "" if missing(cells[3]) else cells[3])
            use = cells[8].lower()
            if "strong" in use or "support" in use or "优先" in use:
                item["strong"] = stronger_status(item["strong"], "candidate")
            elif "background" in use or "背景" in use:
                item["background"] = stronger_status(item["background"], "candidate")
            else:
                item["partial"] = stronger_status(item["partial"], "candidate")
            add_detail(item, "candidateReferences", cells[4])
            add_detail(item, "identifiers", cells[5])
            add_detail(item, "nextAction", cells[8])

    for item in coverage.values():
        evidence_values = [item["strong"], item["partial"], item["background"], item["contradictory"]]
        if "risk" in evidence_values:
            item["status"] = "risk"
        elif "verified" in evidence_values and (item["zoteroChecked"] == "verified" or item["readerChecked"] == "verified"):
            item["status"] = "verified"
        elif "candidate" in evidence_values or "verified" in evidence_values:
            item["status"] = "candidate"
        elif not item["status"] or item["status"] == "missing":
            item["status"] = "missing"

    return sorted(coverage.values(), key=lambda item: (item["sectionId"], item["segmentId"]))


def collect_handoff_package(root: Path) -> dict[str, str]:
    zips = sorted((root / "handoff-packages").glob("final-handoff-*/*.zip"))
    if not zips:
        return {"exists": "false", "latestZip": "", "latestDir": "", "verifyReport": ""}
    latest = zips[-1]
    return {
        "exists": "true",
        "latestZip": latest.as_posix(),
        "latestDir": latest.parent.as_posix(),
        "verifyReport": "docs/thesis/final-handoff-verify-report.md",
    }


def active_stage_number(current_status: dict[str, str]) -> str:
    raw = current_status.get("Current stage", "")
    match = re.search(r"\b(1[0-2]|[1-9])\b", raw)
    return match.group(1) if match else ""


def build_stage_workspace(thesis_dir: Path, p0: list[str], p1: list[str]) -> dict[str, object]:
    current = parse_current_status(thesis_dir)
    stage_no = active_stage_number(current)
    base = STAGE_WORKSPACES.get(stage_no)
    if base is None:
        return {
            "stage": "",
            "name": "Select a stage",
            "fileKeys": ["dashboard", "dailyWorkflowEntry"],
            "commands": ["python scripts/research_workflow_doctor.py --warn-only"],
            "recommendedActions": ["Set the current stage in the Dashboard flow editor or daily workflow entry."],
            "issues": {"p0": p0[:3], "p1": p1[:5]},
        }
    file_keys = list(base["fileKeys"])  # type: ignore[index]
    if "dailyWorkflowEntry" not in file_keys:
        file_keys.insert(0, "dailyWorkflowEntry")
    return {
        "stage": stage_no,
        "name": base["name"],
        "fileKeys": file_keys,
        "commands": base["commands"],
        "recommendedActions": base["recommendedActions"],
        "issues": {"p0": p0[:3], "p1": p1[:5]},
    }


def collect_skill_health() -> dict[str, object]:
    result = audit_repo(Path("."))
    summary = result["summary"]  # type: ignore[index]
    return {
        "totalSkills": summary["totalSkills"],
        "metadataIssues": summary.get("metadataIssues", 0),
        "metadataWarnings": summary.get("metadataWarnings", 0),
        "brokenReferences": summary["brokenReferences"],
        "missingScripts": summary["missingScripts"],
        "outdatedAssumptions": summary["outdatedAssumptions"],
        "reportPath": "docs/thesis/skill-audit-report.md",
    }


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
    skill_health = collect_skill_health()
    experiment_reports = collect_experiment_reports(thesis_dir)
    citation_suggestions = collect_citation_suggestions(thesis_dir)
    section_citation_coverage = collect_section_citation_coverage(thesis_dir)
    handoff_package = collect_handoff_package(thesis_dir.resolve().parents[1] if thesis_dir.name == "thesis" and thesis_dir.parent.name == "docs" else Path("."))
    final_artifacts = data.get("final_artifacts", [])
    id_lifecycle = data.get("id_lifecycle", {})
    plugin_gate = data.get("plugin_gate", {})
    plugin_recommendations = plugin_gate.get("recommendations", []) if isinstance(plugin_gate, dict) else []
    plugin_gate_health = plugin_gate.get("health", {}) if isinstance(plugin_gate, dict) else {}
    active_workspace = build_stage_workspace(thesis_dir, p0, p1)
    final_artifact_records = [
        {
            "id": item.get("artifact_key", "TBD"),
            "status": item.get("transfer_status", "TBD"),
            "row": f"{item.get('format', 'TBD')} | laptop: {item.get('laptop_target_path', 'TBD')} | verification: {item.get('laptop_verification', 'TBD')}",
        }
        for item in final_artifacts
        if isinstance(item, dict)
    ] if isinstance(final_artifacts, list) else []
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
            "finalArtifacts": len(final_artifacts) if isinstance(final_artifacts, list) else 0,
            "idLifecycleRecords": len(id_lifecycle.get("lifecycle", {})) if isinstance(id_lifecycle, dict) else 0,
            "skillIssues": (
                int(skill_health["metadataIssues"])
                + int(skill_health["brokenReferences"])
                + int(skill_health["missingScripts"])
                + int(skill_health["outdatedAssumptions"])
            ),
            "citationSuggestions": len(citation_suggestions),
            "pluginRecommendations": len(plugin_recommendations) if isinstance(plugin_recommendations, list) else 0,
        },
        "currentStatus": parse_current_status(thesis_dir),
        "activeStageWorkspace": active_workspace,
        "stages": parse_stage_snapshot(thesis_dir),
        "issues": {"p0": p0, "p1": p1},
        "summary": info[0] if info else "",
        "recentExperiments": experiments[-5:],
        "experimentReports": experiment_reports[-5:],
        "citationSuggestions": citation_suggestions,
        "sectionCitationCoverage": section_citation_coverage,
        "pluginRecommendations": plugin_recommendations if isinstance(plugin_recommendations, list) else [],
        "pluginGateHealth": plugin_gate_health if isinstance(plugin_gate_health, dict) else {},
        "finalArtifacts": final_artifact_records[-5:],
        "handoffPackage": handoff_package,
        "skillHealth": skill_health,
        "records": records,
        "graph": graph,
        "links": {
            "dashboard": "docs/thesis/workflow-dashboard.md",
            "dailyWorkflowEntry": "docs/thesis/daily-workflow-entry.md",
            "claimMap": "docs/thesis/claim-evidence-map.md",
            "experimentRegistry": "docs/thesis/experiment-registry.md",
            "benchmarkReportSchema": "docs/thesis/benchmark-report-schema.md",
            "dataAvailability": "docs/thesis/data-availability.md",
            "materialPassport": "docs/thesis/material-passport.md",
            "citationProvenance": "docs/thesis/citation-provenance.md",
            "sectionCitationMap": "docs/thesis/section-citation-map.md",
            "deepResearchTasks": "docs/thesis/deep-research-tasks.md",
            "finalArtifactManifest": "docs/thesis/final-artifact-manifest.md",
            "idLifecyclePolicy": "docs/thesis/id-lifecycle-policy.md",
            "workflowEditLog": "docs/thesis/workflow-edit-log.md",
            "figurePlan": "docs/thesis/figure-plan.md",
            "diagramReplicaTasks": "docs/thesis/diagram-replica-tasks.md",
            "zoteroScreeningLoop": "docs/thesis/zotero-screening-loop.md",
            "zoteroCollectionCoverage": "docs/thesis/zotero-collection-coverage.md",
            "finalAudit": "docs/thesis/final-audit.md",
            "evidenceGraph": "docs/thesis/evidence-graph.json",
            "pluginGatePolicy": "docs/thesis/plugin-gate-policy.md",
            "pluginReviewLog": "docs/thesis/plugin-review-log.md",
            "dashboardUxQa": "docs/thesis/dashboard-ux-qa.md",
            "dataQualityReport": "docs/thesis/data-quality-report.md",
            "metricDiagnostics": "docs/thesis/metric-diagnostics.md",
            "visualDesignReview": "docs/thesis/visual-design-review.md",
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
    parser.add_argument("--write-skill-audit", action="store_true")
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
    if args.write_skill_audit:
        skill_result = audit_repo(Path("."))
        report = thesis_dir / "skill-audit-report.md"
        report.write_text(render_report(skill_result), encoding="utf-8")
        print(f"wrote skill audit report: {report}")
    if p0 and not args.warn_only:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
