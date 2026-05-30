"""Local-only control API for the React workflow dashboard."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from edit_workflow_record import FLOW_EDITOR_SCHEMA, handle_payload
from research_workflow_doctor import build_stage_workspace, diagnose
from update_daily_workflow import update_daily


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
ALLOWED_OPEN_PATHS = {
    "dashboard": ROOT / "docs" / "thesis" / "workflow-dashboard.md",
    "dailyWorkflowEntry": ROOT / "docs" / "thesis" / "daily-workflow-entry.md",
    "claimMap": ROOT / "docs" / "thesis" / "claim-evidence-map.md",
    "experimentRegistry": ROOT / "docs" / "thesis" / "experiment-registry.md",
    "benchmarkReportSchema": ROOT / "docs" / "thesis" / "benchmark-report-schema.md",
    "dataAvailability": ROOT / "docs" / "thesis" / "data-availability.md",
    "materialPassport": ROOT / "docs" / "thesis" / "material-passport.md",
    "citationProvenance": ROOT / "docs" / "thesis" / "citation-provenance.md",
    "sectionCitationMap": ROOT / "docs" / "thesis" / "section-citation-map.md",
    "sectionCitationSuggestions": ROOT / "docs" / "thesis" / "section-citation-suggestions.md",
    "finalArtifactManifest": ROOT / "docs" / "thesis" / "final-artifact-manifest.md",
    "finalHandoffVerifyReport": ROOT / "docs" / "thesis" / "final-handoff-verify-report.md",
    "idLifecyclePolicy": ROOT / "docs" / "thesis" / "id-lifecycle-policy.md",
    "workflowEditLog": ROOT / "docs" / "thesis" / "workflow-edit-log.md",
    "figurePlan": ROOT / "docs" / "thesis" / "figure-plan.md",
    "finalAudit": ROOT / "docs" / "thesis" / "final-audit.md",
    "deepResearchTasks": ROOT / "docs" / "thesis" / "deep-research-tasks.md",
    "diagramReplicaTasks": ROOT / "docs" / "thesis" / "diagram-replica-tasks.md",
    "zoteroScreeningLoop": ROOT / "docs" / "thesis" / "zotero-screening-loop.md",
    "zoteroCollectionCoverage": ROOT / "docs" / "thesis" / "zotero-collection-coverage.md",
    "experimentReports": ROOT / "docs" / "thesis" / "experiment-reports",
}


def run_command(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return result.returncode, output


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:5173")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "ResearchDashboardControl/0.1"

    def do_OPTIONS(self) -> None:  # noqa: N802
        json_response(self, 200, {"ok": True})

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/status":
            data_path = ROOT / "dashboard-web" / "public" / "data" / "dashboard-data.json"
            json_response(self, 200, {"ok": True, "root": str(ROOT), "dataExists": data_path.exists()})
            return
        if path == "/api/flow-editor/schema":
            json_response(self, 200, {"ok": True, "schema": FLOW_EDITOR_SCHEMA})
            return
        if path == "/api/stage-workspace":
            thesis_dir = ROOT / "docs" / "thesis"
            p0, p1, _info, _data = diagnose(thesis_dir)
            json_response(self, 200, {"ok": True, "workspace": build_stage_workspace(thesis_dir, p0, p1)})
            return
        json_response(self, 404, {"ok": False, "error": "unknown endpoint"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            json_response(self, 400, {"ok": False, "error": "invalid json"})
            return

        if path == "/api/refresh-dashboard":
            code, output = run_command([
                "python3",
                "scripts/research_workflow_doctor.py",
                "--write-dashboard",
                "--write-data",
                "--write-skill-audit",
                "--json-out",
                "dashboard-web/public/data/dashboard-data.json",
                "--warn-only",
            ])
            json_response(self, 200 if code == 0 else 500, {"ok": code == 0, "output": output})
            return

        if path == "/api/export-evidence-graph":
            code, output = run_command([
                "python3",
                "scripts/export_evidence_graph.py",
                "--out",
                "dashboard-web/public/data/evidence-graph.json",
                "--mermaid",
                "dashboard-web/public/data/evidence-graph.mmd",
            ])
            json_response(self, 200 if code == 0 else 500, {"ok": code == 0, "output": output})
            return

        if path == "/api/run-doctor":
            code, output = run_command(["python3", "scripts/research_workflow_doctor.py", "--warn-only"])
            json_response(self, 200 if code == 0 else 500, {"ok": code == 0, "output": output})
            return

        if path == "/api/daily-workflow/update":
            fields = payload.get("fields") if isinstance(payload.get("fields"), dict) else payload
            try:
                result = update_daily(ROOT, fields)
            except Exception as exc:  # pragma: no cover - defensive API boundary
                json_response(self, 500, {"ok": False, "error": str(exc)})
                return
            json_response(self, 200, {"ok": True, "output": f"updated {result.get('target', '')}", **result})
            return

        if path == "/api/suggest-section-citations":
            section_id = str(payload.get("section_id", "") or payload.get("sectionId", "")).strip()
            if section_id and not re.fullmatch(r"SEC-[A-Za-z0-9.-]+", section_id):
                json_response(self, 400, {"ok": False, "error": "section_id must be empty or a SEC-* ID"})
                return
            command = [
                "python3",
                "scripts/suggest_section_citations.py",
                "--json-out",
                "dashboard-web/public/data/citation-suggestions.json",
            ]
            if section_id:
                command.extend(["--section-id", section_id])
            code, output = run_command(command)
            json_response(self, 200 if code == 0 else 500, {"ok": code == 0, "output": output})
            return

        if path == "/api/package-final-handoff":
            code, output = run_command(["python3", "scripts/package_final_handoff.py", "--json"])
            json_response(self, 200 if code == 0 else 500, {"ok": code == 0, "output": output})
            return

        if path == "/api/verify-final-handoff":
            code, output = run_command([
                "python3",
                "scripts/verify_final_handoff.py",
                "--latest",
                "--write-report",
                "docs/thesis/final-handoff-verify-report.md",
            ])
            json_response(self, 200 if code == 0 else 500, {"ok": code == 0, "output": output})
            return

        if path == "/api/open-path":
            key = str(payload.get("key", ""))
            target = ALLOWED_OPEN_PATHS.get(key)
            if target is None:
                json_response(self, 403, {"ok": False, "error": "path key is not allowed"})
                return
            if not target.exists():
                json_response(self, 404, {"ok": False, "error": f"path not found: {target}"})
                return
            code, output = run_command(["open", str(target)])
            json_response(self, 200 if code == 0 else 500, {"ok": code == 0, "output": output or str(target)})
            return

        flow_actions = {
            "/api/flow-editor/update-status": "update-status",
            "/api/flow-editor/create-record": "create-record",
            "/api/flow-editor/update-id-lifecycle": "update-id-lifecycle",
            "/api/flow-editor/create-final-artifact": "create-final-artifact",
        }
        if path in flow_actions:
            try:
                result = handle_payload(ROOT, {"action": flow_actions[path], **payload})
            except ValueError as exc:
                json_response(self, 400, {"ok": False, "error": str(exc)})
                return
            except Exception as exc:  # pragma: no cover - defensive API boundary
                json_response(self, 500, {"ok": False, "error": str(exc)})
                return
            json_response(self, 200, {"ok": True, "output": f"updated {result.get('target', '')}", **result})
            return

        json_response(self, 404, {"ok": False, "error": "unknown endpoint"})

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local workflow dashboard control server.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    if args.host != DEFAULT_HOST:
        raise SystemExit("dashboard control server must bind to 127.0.0.1")
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"dashboard control server listening on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
