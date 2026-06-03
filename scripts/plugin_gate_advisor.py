"""Recommend lightweight plugin gates for the research workflow."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Optional

THESIS_DIR = Path("docs/thesis")
REVIEW_OK = {"pass", "passed", "done", "completed", "reviewed", "ok", "not_applicable", "n/a"}

PLUGIN_RULES = [
    {
        "plugin": "Codex Security",
        "stages": {"5", "6"},
        "requiredChangeTypes": {"dashboard", "api", "remote", "ci", "security", "file-write"},
        "defaultLevel": "recommended",
        "reason": "Research code, local dashboard APIs, CI, and remote 4060 scripts can create security or data-safety regressions.",
        "action": "Run a security diff scan or focused security review for changed scripts/APIs, then record the result.",
        "record": "docs/thesis/plugin-review-log.md",
    },
    {
        "plugin": "Build Web Apps",
        "stages": set(),
        "requiredChangeTypes": {"dashboard", "frontend", "react", "ui", "mobile"},
        "defaultLevel": "recommended",
        "reason": "Dashboard and React/Vite changes need rendered UI, responsiveness, interaction, and accessibility checks.",
        "action": "Run the dashboard build plus Browser/Safari QA and record frontend findings.",
        "record": "docs/thesis/dashboard-ux-qa.md",
    },
    {
        "plugin": "Data Analytics",
        "stages": {"7", "8"},
        "requiredChangeTypes": {"formal-results", "claim-promotion", "baseline", "metric"},
        "defaultLevel": "recommended",
        "reason": "Experiment results need data quality, metric diagnostics, baseline-delta, and anomaly checks before claim promotion.",
        "action": "Create or update data quality and metric diagnostics notes before promoting result evidence.",
        "record": "docs/thesis/data-quality-report.md; docs/thesis/metric-diagnostics.md",
    },
    {
        "plugin": "Product Design",
        "stages": {"9", "12"},
        "requiredChangeTypes": {"advisor-facing", "final-defense", "visual-review", "ppt", "dashboard"},
        "defaultLevel": "recommended",
        "reason": "Advisor-facing figures, dashboards, and defense slides should be understandable, scannable, and visually coherent.",
        "action": "Run a visual/UX review for the target artifact and record the design decision.",
        "record": "docs/thesis/visual-design-review.md",
    },
    {
        "plugin": "CodeRabbit",
        "stages": {"5", "6"},
        "requiredChangeTypes": set(),
        "defaultLevel": "optional",
        "reason": "Important script, dashboard, CI, or skill changes can benefit from an authenticated AI code review.",
        "action": "Run CodeRabbit only when authenticated and useful; do not make it a default CI dependency.",
        "record": "docs/thesis/plugin-review-log.md",
    },
]


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


def active_stage_number(thesis_dir: Path) -> str:
    for cells in markdown_rows(read_text(thesis_dir / "workflow-dashboard.md")):
        if len(cells) >= 2 and cells[0].lower() == "current stage":
            match = re.search(r"\b(1[0-2]|[1-9])\b", cells[1])
            return match.group(1) if match else ""
    return ""


def normalize_change_types(values: Optional[list[str]]) -> set[str]:
    normalized: set[str] = set()
    for value in values or []:
        for part in re.split(r"[,/;|\s]+", value.lower()):
            clean = part.strip().replace("_", "-")
            if clean:
                normalized.add(clean)
    return normalized


def infer_change_types(thesis_dir: Path, issues: Optional[list[str]] = None) -> set[str]:
    status_values: list[str] = []
    for cells in markdown_rows(read_text(thesis_dir / "workflow-dashboard.md")):
        if len(cells) >= 2 and cells[0].lower() in {
            "current stage",
            "active focus",
            "current audit tier",
            "main blocker",
            "next concrete action",
            "last dashboard refresh",
        }:
            status_values.append(cells[1])
    text_parts = ["\n".join(status_values), "\n".join(issues or [])]
    text = "\n".join(text_parts).lower()
    inferred: set[str] = set()
    keyword_map = {
        "dashboard": "dashboard",
        "react": "react",
        "vite": "frontend",
        "ui": "ui",
        "mobile": "mobile",
        "dashboard_control_server": "api",
        "open-path": "api",
        "flow editor": "file-write",
        "remote_desktop_4060": "remote",
        "4060": "remote",
        "rsync": "remote",
        "ssh": "remote",
        "github actions": "ci",
        "ci": "ci",
        "baseline": "baseline",
        "metric": "metric",
        "claim promotion": "claim-promotion",
        "正式结果": "formal-results",
        "导师": "advisor-facing",
        "答辩": "final-defense",
        "ppt": "ppt",
        "visual": "visual-review",
        "图表": "visual-review",
    }
    for keyword, change_type in keyword_map.items():
        if re.fullmatch(r"[a-z0-9_-]+", keyword):
            matched = re.search(rf"(?<![a-z0-9_-]){re.escape(keyword)}(?![a-z0-9_-])", text)
        else:
            matched = keyword in text
        if matched:
            inferred.add(change_type)
    return inferred


def review_log_entries(thesis_dir: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for cells in markdown_rows(read_text(thesis_dir / "plugin-review-log.md")):
        if len(cells) >= 9 and re.fullmatch(r"PLG-[A-Za-z0-9.-]+", cells[0]):
            entries.append(
                {
                    "id": cells[0],
                    "date": cells[1],
                    "stage": cells[2],
                    "plugin": cells[3],
                    "trigger": cells[4],
                    "required": cells[5],
                    "result": cells[6],
                    "record": cells[7],
                    "notes": cells[8],
                }
            )
    return entries


def has_review(entries: list[dict[str, str]], plugin: str, stage: str) -> bool:
    for entry in entries:
        result = entry.get("result", "").strip().lower()
        if result not in REVIEW_OK:
            continue
        if entry.get("plugin", "").strip().lower() != plugin.lower():
            continue
        entry_stage = entry.get("stage", "")
        if stage and stage not in entry_stage:
            continue
        return True
    return False


def recommend_plugins(
    thesis_dir: Path,
    stage: Optional[str] = None,
    change_types: Optional[set[str]] = None,
    issues: Optional[list[str]] = None,
) -> dict[str, object]:
    stage_no = stage or active_stage_number(thesis_dir)
    explicit_types = set(change_types or set())
    all_change_types = explicit_types | infer_change_types(thesis_dir, issues)
    entries = review_log_entries(thesis_dir)
    recommendations: list[dict[str, object]] = []

    for rule in PLUGIN_RULES:
        stage_match = bool(stage_no and stage_no in rule["stages"])
        type_match = bool(all_change_types & rule["requiredChangeTypes"]) and (not rule["stages"] or stage_match)
        if not stage_match and not type_match:
            continue
        required = bool(type_match and rule["requiredChangeTypes"])
        level = "required" if required else rule["defaultLevel"]
        recorded = has_review(entries, str(rule["plugin"]), stage_no)
        status = "recorded" if recorded else "pending_required" if required else level
        recommendations.append(
            {
                "plugin": rule["plugin"],
                "stage": stage_no or "TBD",
                "reason": rule["reason"],
                "action": rule["action"],
                "record": rule["record"],
                "required": required,
                "level": level,
                "status": status,
            }
        )

    policy = thesis_dir / "plugin-gate-policy.md"
    log = thesis_dir / "plugin-review-log.md"
    pending_required = [item for item in recommendations if item["status"] == "pending_required"]
    optional = [item for item in recommendations if item["level"] in {"recommended", "optional"}]
    return {
        "stage": stage_no,
        "changeTypes": sorted(all_change_types),
        "recommendations": recommendations,
        "health": {
            "missingPolicy": not policy.exists(),
            "missingReviewLog": not log.exists(),
            "pendingRequiredGates": len(pending_required),
            "optionalSuggestions": len(optional),
        },
    }


def render_text(result: dict[str, object]) -> str:
    lines = [
        "# Plugin Gate Advisor",
        "",
        f"- stage: {result.get('stage') or 'TBD'}",
        f"- change types: {', '.join(result.get('changeTypes', [])) or 'none'}",
    ]
    health = result.get("health", {})
    if isinstance(health, dict):
        lines.extend(
            [
                f"- missing policy: {health.get('missingPolicy')}",
                f"- missing review log: {health.get('missingReviewLog')}",
                f"- pending required gates: {health.get('pendingRequiredGates')}",
            ]
        )
    lines.extend(["", "## Recommendations", ""])
    recommendations = result.get("recommendations", [])
    if not recommendations:
        lines.append("- none")
    elif isinstance(recommendations, list):
        for item in recommendations:
            if isinstance(item, dict):
                lines.append(
                    f"- {item.get('plugin')} [{item.get('level')}/{item.get('status')}]: "
                    f"{item.get('action')} -> {item.get('record')}"
                )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend lightweight plugin gates for a research workflow.")
    parser.add_argument("--thesis-dir", default="docs/thesis")
    parser.add_argument("--stage", default="")
    parser.add_argument("--change-type", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()

    thesis_dir = Path(args.thesis_dir)
    result = recommend_plugins(thesis_dir, stage=args.stage or None, change_types=normalize_change_types(args.change_type))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result).rstrip())

    health = result["health"]
    if args.audit_only and isinstance(health, dict) and (health["missingPolicy"] or health["missingReviewLog"]) and not args.warn_only:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
