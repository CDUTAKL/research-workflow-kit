"""Local-only control API for the React workflow dashboard."""
from __future__ import annotations

import argparse
import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
ALLOWED_OPEN_PATHS = {
    "dashboard": ROOT / "docs" / "thesis" / "workflow-dashboard.md",
    "claimMap": ROOT / "docs" / "thesis" / "claim-evidence-map.md",
    "experimentRegistry": ROOT / "docs" / "thesis" / "experiment-registry.md",
    "dataAvailability": ROOT / "docs" / "thesis" / "data-availability.md",
    "figurePlan": ROOT / "docs" / "thesis" / "figure-plan.md",
    "finalAudit": ROOT / "docs" / "thesis" / "final-audit.md",
    "deepResearchTasks": ROOT / "docs" / "thesis" / "deep-research-tasks.md",
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
