"""Safe writer for lightweight workflow dashboard edits.

The dashboard flow editor calls this module through the local control server.
It only writes known workflow console files, creates backups under ignored
`tmp/dashboard-edits/backups/`, and appends an audit row to
`docs/thesis/workflow-edit-log.md`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
from pathlib import Path
from typing import Any

THESIS_DIR = Path("docs/thesis")
BACKUP_DIR = Path("tmp/dashboard-edits/backups")

RECORD_TARGETS = {
    "claim": THESIS_DIR / "claim-evidence-map.md",
    "experiment": THESIS_DIR / "experiment-registry.md",
    "material": THESIS_DIR / "material-passport.md",
    "citation": THESIS_DIR / "citation-provenance.md",
    "final_artifact": THESIS_DIR / "final-artifact-manifest.md",
    "status": THESIS_DIR / "workflow-dashboard.md",
    "id_lifecycle": THESIS_DIR / "id-lifecycle-policy.md",
}

ID_PREFIXES = {
    "claim": "CLM",
    "experiment": "EXP",
    "material": "MAT",
    "citation": "CIT",
}

FLOW_EDITOR_SCHEMA = {
    "recordTypes": ["claim", "experiment", "material", "citation", "final_artifact"],
    "statusFields": ["current_stage", "active_focus", "audit_tier", "main_blocker", "next_action"],
    "lifecycleStatuses": ["draft", "candidate", "verified", "promoted", "deprecated", "superseded"],
    "transferStatuses": ["pending", "copied", "verified", "blocked"],
}


def today() -> str:
    return dt.date.today().isoformat()


def now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def cell(value: Any, fallback: str = "TBD") -> str:
    text = str(value if value is not None else "").strip()
    if not text:
        text = fallback
    return text.replace("\n", " ").replace("|", "/")


def markdown_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    cells = [part.strip() for part in stripped.strip("|").split("|")]
    if cells and all(set(part) <= {"-", ":"} for part in cells):
        return []
    return cells


def table_separator(line: str) -> bool:
    cells = markdown_cells(line)
    return bool(cells) and all(set(part) <= {"-", ":"} for part in cells)


def backup_file(root: Path, path: Path) -> None:
    if not path.exists():
        return
    rel = path.resolve().relative_to(root.resolve())
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_path = root / BACKUP_DIR / stamp / "__".join(rel.parts)
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_path)


def write_text(root: Path, path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    backup_file(root, path)
    path.write_text(text, encoding="utf-8")


def append_row_to_table(root: Path, path: Path, header_first_cell: str, row: list[str]) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = text.splitlines()
    insert_at: int | None = None
    for index, line in enumerate(lines):
        cells = markdown_cells(line)
        if cells and cells[0].lower() == header_first_cell.lower():
            cursor = index + 1
            while cursor < len(lines) and (lines[cursor].strip() == "" or lines[cursor].strip().startswith("|")):
                if lines[cursor].strip() == "":
                    break
                cursor += 1
            insert_at = cursor
            break
    row_line = "| " + " | ".join(cell(value) for value in row) + " |"
    if insert_at is None:
        if text and not text.endswith("\n"):
            text += "\n"
        text += f"\n| {header_first_cell} |\n|---|\n{row_line}\n"
    else:
        lines.insert(insert_at, row_line)
        text = "\n".join(lines) + "\n"
    write_text(root, path, text)


def upsert_table_row(root: Path, path: Path, header_first_cell: str, key: str, row: list[str]) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = text.splitlines()
    row_line = "| " + " | ".join(cell(value) for value in row) + " |"
    in_target = False
    replaced = False
    for index, line in enumerate(lines):
        cells = markdown_cells(line)
        if cells and cells[0].lower() == header_first_cell.lower():
            in_target = True
            continue
        if in_target and cells and cells[0] == key:
            lines[index] = row_line
            replaced = True
            break
        if in_target and line.strip() == "":
            break
    if replaced:
        write_text(root, path, "\n".join(lines) + "\n")
    else:
        append_row_to_table(root, path, header_first_cell, row)


def existing_ids(root: Path, prefix: str) -> list[str]:
    pattern = re.compile(rf"\b{re.escape(prefix)}-\d{{3}}\b")
    found: list[str] = []
    thesis = root / THESIS_DIR
    if thesis.exists():
        for path in thesis.rglob("*"):
            if path.suffix.lower() not in {".md", ".tsv", ".json"}:
                continue
            try:
                found.extend(pattern.findall(path.read_text(encoding="utf-8")))
            except UnicodeDecodeError:
                continue
    return list(dict.fromkeys(found))


def next_numeric_id(root: Path, prefix: str) -> str:
    max_seen = 0
    for item in existing_ids(root, prefix):
        try:
            max_seen = max(max_seen, int(item.rsplit("-", 1)[1]))
        except ValueError:
            continue
    return f"{prefix}-{max_seen + 1:03d}"


def next_experiment_id(root: Path) -> str:
    date = today()
    pattern = re.compile(rf"\bEXP-{date}-(\d{{3}})\b")
    max_seen = 0
    thesis = root / THESIS_DIR
    if thesis.exists():
        for path in thesis.rglob("*"):
            if path.suffix.lower() not in {".md", ".tsv", ".json"}:
                continue
            for match in pattern.findall(path.read_text(encoding="utf-8", errors="ignore")):
                max_seen = max(max_seen, int(match))
    return f"EXP-{date}-{max_seen + 1:03d}"


def ensure_workflow_log(root: Path) -> Path:
    path = root / THESIS_DIR / "workflow-edit-log.md"
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Workflow Edit Log\n\n"
        "## Purpose\n\n"
        "This log records lightweight edits made through the web dashboard flow editor or `scripts/edit_workflow_record.py`.\n\n"
        "## Edit Log\n\n"
        "| Timestamp | Action | Target File | Generated ID | Summary |\n"
        "|---|---|---|---|---|\n",
        encoding="utf-8",
    )
    return path


def log_edit(root: Path, action: str, target: Path, generated_id: str, summary: str) -> None:
    log_path = ensure_workflow_log(root)
    rel = target.resolve().relative_to(root.resolve()).as_posix()
    append_row_to_table(root, log_path, "Timestamp", [now(), action, rel, generated_id or "TBD", summary])


def create_claim(root: Path, fields: dict[str, Any]) -> dict[str, Any]:
    target = root / RECORD_TARGETS["claim"]
    record_id = cell(fields.get("claim_id"), next_numeric_id(root, "CLM"))
    row = [
        record_id,
        fields.get("claim_draft"),
        fields.get("status", "missing"),
        fields.get("experiment_evidence"),
        fields.get("figure_table"),
        fields.get("literature_evidence"),
        fields.get("caveat"),
        fields.get("next_action"),
    ]
    append_row_to_table(root, target, "Claim ID", row)
    log_edit(root, "create claim", target, record_id, cell(fields.get("claim_draft"), "new claim"))
    return {"ok": True, "id": record_id, "target": target.as_posix()}


def create_experiment(root: Path, fields: dict[str, Any]) -> dict[str, Any]:
    target = root / RECORD_TARGETS["experiment"]
    record_id = cell(fields.get("experiment_id"), next_experiment_id(root))
    output_path = cell(fields.get("output_path"), f"outputs/{record_id}")
    row = [
        record_id,
        fields.get("claim"),
        fields.get("method_config"),
        fields.get("dataset_split"),
        fields.get("command"),
        output_path,
        fields.get("key_metrics"),
        fields.get("status", "planned"),
        fields.get("date", today()),
        fields.get("notes"),
        fields.get("storage_backend", "local_mac"),
        fields.get("remote_artifact_uri"),
        fields.get("remote_status", "not_applicable"),
        fields.get("artifact_hash", f"{output_path}/manifest.json"),
    ]
    append_row_to_table(root, target, "Experiment ID", row)
    log_edit(root, "create experiment", target, record_id, cell(fields.get("claim"), "new experiment"))
    return {"ok": True, "id": record_id, "target": target.as_posix()}


def create_material(root: Path, fields: dict[str, Any]) -> dict[str, Any]:
    target = root / RECORD_TARGETS["material"]
    record_id = cell(fields.get("material_id"), next_numeric_id(root, "MAT"))
    row = [
        record_id,
        fields.get("type"),
        fields.get("title"),
        fields.get("source_path"),
        fields.get("owner"),
        fields.get("created_updated", today()),
        fields.get("related_ids"),
        fields.get("access_level"),
        fields.get("license_permission"),
        fields.get("integrity_check"),
        fields.get("repro_lock"),
        fields.get("status", "planned"),
        fields.get("notes"),
    ]
    append_row_to_table(root, target, "Material ID", row)
    log_edit(root, "create material", target, record_id, cell(fields.get("title"), "new material"))
    return {"ok": True, "id": record_id, "target": target.as_posix()}


def create_citation(root: Path, fields: dict[str, Any]) -> dict[str, Any]:
    target = root / RECORD_TARGETS["citation"]
    record_id = cell(fields.get("citation_id"), next_numeric_id(root, "CIT"))
    row = [
        record_id,
        fields.get("section_id"),
        fields.get("segment_id"),
        fields.get("claim_id"),
        fields.get("title"),
        fields.get("identifier"),
        fields.get("candidate_source"),
        fields.get("metadata_status", "candidate"),
        fields.get("support_status", "unchecked"),
        fields.get("zotero_status"),
        fields.get("scite_reader_evidence"),
        fields.get("verified_by"),
        fields.get("verified_on", today()),
        fields.get("export_status"),
        fields.get("notes"),
    ]
    append_row_to_table(root, target, "Citation ID", row)
    log_edit(root, "create citation", target, record_id, cell(fields.get("title"), "new citation"))
    return {"ok": True, "id": record_id, "target": target.as_posix()}


def create_final_artifact(root: Path, fields: dict[str, Any]) -> dict[str, Any]:
    target = root / RECORD_TARGETS["final_artifact"]
    artifact_key = cell(fields.get("artifact_key"), f"artifact-{today()}")
    row = [
        artifact_key,
        fields.get("stage", "11-doc-production"),
        fields.get("source_ids"),
        fields.get("mac_source_path"),
        fields.get("laptop_target_path"),
        fields.get("format"),
        fields.get("checksum"),
        fields.get("produced_by"),
        fields.get("transfer_status", "pending"),
        fields.get("laptop_verification", "pending"),
        fields.get("notes"),
    ]
    append_row_to_table(root, target, "Artifact Key", row)
    log_edit(root, "create final artifact", target, artifact_key, cell(fields.get("notes"), "new final artifact"))
    return {"ok": True, "id": artifact_key, "target": target.as_posix()}


def update_status(root: Path, fields: dict[str, Any]) -> dict[str, Any]:
    target = root / RECORD_TARGETS["status"]
    text = target.read_text(encoding="utf-8") if target.exists() else "# Workflow Dashboard\n\n## Current Status\n\n| Field | Value |\n|---|---|\n"
    labels = {
        "Current stage": fields.get("current_stage"),
        "Active focus": fields.get("active_focus"),
        "Current audit tier": fields.get("audit_tier"),
        "Main blocker": fields.get("main_blocker"),
        "Next concrete action": fields.get("next_action"),
        "Last dashboard refresh": fields.get("last_dashboard_refresh", now()),
    }
    lines = text.splitlines()
    seen: set[str] = set()
    for index, line in enumerate(lines):
        cells = markdown_cells(line)
        if len(cells) >= 2 and cells[0] in labels:
            value = labels[cells[0]]
            if value is not None:
                lines[index] = f"| {cells[0]} | {cell(value)} |"
            seen.add(cells[0])
    missing_labels = [label for label in labels if label not in seen and labels[label] is not None]
    if missing_labels:
        lines.extend(["", "## Current Status", "", "| Field | Value |", "|---|---|"])
        for label in missing_labels:
            lines.append(f"| {label} | {cell(labels[label])} |")
    write_text(root, target, "\n".join(lines) + "\n")
    log_edit(root, "update status", target, "status", cell(fields.get("next_action"), "status update"))
    return {"ok": True, "id": "status", "target": target.as_posix()}


def update_id_lifecycle(root: Path, fields: dict[str, Any]) -> dict[str, Any]:
    target = root / RECORD_TARGETS["id_lifecycle"]
    item_id = cell(fields.get("id"))
    if item_id == "TBD":
        raise ValueError("id is required for lifecycle updates")
    row = [
        item_id,
        fields.get("type"),
        fields.get("status", "candidate"),
        fields.get("primary_file"),
        fields.get("related_ids"),
        fields.get("replacement_id", ""),
        fields.get("owner", "user/Codex"),
        fields.get("updated_on", today()),
        fields.get("notes"),
    ]
    upsert_table_row(root, target, "ID", item_id, row)
    log_edit(root, "update id lifecycle", target, item_id, cell(fields.get("notes"), "lifecycle update"))
    return {"ok": True, "id": item_id, "target": target.as_posix()}


def create_record(root: Path, record_type: str, fields: dict[str, Any]) -> dict[str, Any]:
    handlers = {
        "claim": create_claim,
        "experiment": create_experiment,
        "material": create_material,
        "citation": create_citation,
        "final_artifact": create_final_artifact,
    }
    handler = handlers.get(record_type)
    if handler is None:
        raise ValueError(f"unsupported record_type: {record_type}")
    return handler(root, fields)


def handle_payload(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    action = str(payload.get("action", "create-record"))
    fields = payload.get("fields")
    if not isinstance(fields, dict):
        fields = {key: value for key, value in payload.items() if key not in {"action", "record_type"}}
    if action == "schema":
        return {"ok": True, "schema": FLOW_EDITOR_SCHEMA}
    if action == "update-status":
        return update_status(root, fields)
    if action == "update-id-lifecycle":
        return update_id_lifecycle(root, fields)
    if action == "create-final-artifact":
        return create_final_artifact(root, fields)
    if action == "create-record":
        record_type = str(payload.get("record_type", fields.get("record_type", "")))
        return create_record(root, record_type, fields)
    raise ValueError(f"unsupported action: {action}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Safely create or update workflow console records.")
    parser.add_argument("--root", default=".", help="Project root. Defaults to current directory.")
    parser.add_argument("--payload-json", required=True, help="JSON payload with action, record_type, and fields.")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    payload = json.loads(args.payload_json)
    result = handle_payload(root, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
