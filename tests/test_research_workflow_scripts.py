import subprocess
import socket
import sys
import tempfile
import textwrap
import time
import unittest
import json
import urllib.error
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
NEW_EXPERIMENT = REPO_ROOT / "scripts" / "new_experiment.py"
AUDIT_CLAIMS = REPO_ROOT / "scripts" / "audit_claim_evidence.py"
CHECK_CONTRACT = REPO_ROOT / "scripts" / "check_experiment_contract.py"
AUDIT_SECTION_CITATIONS = REPO_ROOT / "scripts" / "audit_section_citations.py"
AUDIT_DATA_AVAILABILITY = REPO_ROOT / "scripts" / "audit_data_availability.py"
NEW_AUTORESEARCH_ITERATION = REPO_ROOT / "scripts" / "new_autoresearch_iteration.py"
WRITE_ENV_SNAPSHOT = REPO_ROOT / "scripts" / "write_environment_snapshot.py"
EXPORT_EVIDENCE_GRAPH = REPO_ROOT / "scripts" / "export_evidence_graph.py"
RESEARCH_WORKFLOW_DOCTOR = REPO_ROOT / "scripts" / "research_workflow_doctor.py"
NEW_DEEP_RESEARCH_TASK = REPO_ROOT / "scripts" / "new_deep_research_task.py"
NEW_EXPERIMENT_REPORT = REPO_ROOT / "scripts" / "new_experiment_report.py"
AUDIT_SKILLS = REPO_ROOT / "scripts" / "audit_skills.py"
DASHBOARD_CONTROL_SERVER = REPO_ROOT / "scripts" / "dashboard_control_server.py"
EDIT_WORKFLOW_RECORD = REPO_ROOT / "scripts" / "edit_workflow_record.py"
AUDIT_FINAL_ARTIFACTS = REPO_ROOT / "scripts" / "audit_final_artifacts.py"
AUDIT_ID_LIFECYCLE = REPO_ROOT / "scripts" / "audit_id_lifecycle.py"
UPDATE_DAILY_WORKFLOW = REPO_ROOT / "scripts" / "update_daily_workflow.py"
SUGGEST_SECTION_CITATIONS = REPO_ROOT / "scripts" / "suggest_section_citations.py"
PACKAGE_FINAL_HANDOFF = REPO_ROOT / "scripts" / "package_final_handoff.py"
VERIFY_FINAL_HANDOFF = REPO_ROOT / "scripts" / "verify_final_handoff.py"


class ResearchWorkflowScriptTests(unittest.TestCase):
    def test_new_experiment_appends_registry_row_without_experiment_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            registry = project / "docs" / "thesis" / "experiment-registry.md"
            registry.parent.mkdir(parents=True)
            registry.write_text(
                textwrap.dedent(
                    """\
                    # Experiment Registry

                    | Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes |
                    |---|---|---|---|---|---|---|---|---|---|
                    | EXP-001 | Existing claim | baseline | dataset_v1 | `python baseline.py` | `outputs/EXP-001` | accuracy=0.8 | done | 2026-01-01 | existing |
                    """
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(NEW_EXPERIMENT),
                    "--hypothesis",
                    "CLM-001",
                    "--script",
                    "experiments/run.py",
                    "--primary-metric",
                    "accuracy=0.91",
                    "--status",
                    "done",
                    "--checkpoint-path",
                    "outputs/latest",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )

            registry_text = registry.read_text(encoding="utf-8")
            self.assertRegex(registry_text, r"EXP-\d{4}-\d{2}-\d{2}-001")
            self.assertIn("CLM-001", registry_text)
            self.assertIn("experiments/run.py", registry_text)
            self.assertIn("accuracy=0.91", registry_text)
            self.assertIn("outputs/latest", registry_text)
            self.assertIn("appended to docs/thesis/experiment-registry.md", result.stdout)
            self.assertFalse((project / "docs" / "thesis" / "experiment-log.md").exists())

    def test_claim_audit_reads_clm_ids_and_registry_experiment_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "claim-evidence-map.md").write_text(
                textwrap.dedent(
                    """\
                    # Claim Evidence Map

                    | Claim ID | Claim Draft | Status | Experiment Evidence | Figure/Table | Literature Evidence | Caveat | Next Action |
                    |---|---|---|---|---|---|---|---|
                    | CLM-001 | accuracy reaches 91% | supported | EXP-001, EXP-AUTO-002 | Fig. 1 | Paper A | scope limited | cite |
                    """
                ),
                encoding="utf-8",
            )
            (thesis / "experiment-registry.md").write_text(
                textwrap.dedent(
                    """\
                    # Experiment Registry

                    | Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes |
                    |---|---|---|---|---|---|---|---|---|---|
                    | EXP-001 | CLM-001 | model=a | dataset_v1 | `python train.py` | `outputs/EXP-001` | acc=0.91 | done | 2026-01-01 | reviewed |
                    | EXP-AUTO-002 | CLM-001 | model=b | dataset_v1 | `python train.py` | `outputs/EXP-AUTO-002` | acc=0.90 | candidate | 2026-01-02 | scan import |
                    """
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(AUDIT_CLAIMS), "--warn-only"],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("Claims: 1  |  Experiments: 2", result.stdout)
            self.assertIn("Errors: 0", result.stdout)
            self.assertNotIn("Evidence refs with no matching experiment", result.stdout)

    def test_check_experiment_contract_passes_with_config_registry_and_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (project / "configs" / "experiment").mkdir(parents=True)
            (project / "configs" / "smoke").mkdir(parents=True)
            (project / "outputs" / "EXP-001" / "logs").mkdir(parents=True)
            (project / "configs" / "experiment" / "EXP-001.yaml").write_text(
                "seed: 42\nsplit: test\nmetric: accuracy\noutput: outputs/EXP-001\n",
                encoding="utf-8",
            )
            (project / "configs" / "smoke" / "EXP-001-smoke.yaml").write_text(
                "seed: 42\nsplit: smoke\nmetric: accuracy\noutput: outputs/EXP-001-smoke\n",
                encoding="utf-8",
            )
            (thesis / "experiment-registry.md").write_text(
                textwrap.dedent(
                    """\
                    | Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes |
                    |---|---|---|---|---|---|---|---|---|---|
                    | EXP-001 | CLM-001 | configs/experiment/EXP-001.yaml | test | train | outputs/EXP-001 | accuracy | planned | TBD |  |
                    """
                ),
                encoding="utf-8",
            )
            for name in ("manifest.json", "config_resolved.json", "metrics.json"):
                (project / "outputs" / "EXP-001" / name).write_text("{}", encoding="utf-8")
            (project / "outputs" / "EXP-001" / "environment.txt").write_text(
                "target_label: remote_desktop_4060\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_CONTRACT),
                    "--experiment-id",
                    "EXP-001",
                    "--require-outputs",
                    "--require-env-snapshot",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Errors: 0", result.stdout)

    def test_write_environment_snapshot_creates_snapshot_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            out = project / "outputs" / "EXP-001" / "environment.txt"
            result = subprocess.run(
                [
                    sys.executable,
                    str(WRITE_ENV_SNAPSHOT),
                    "--out",
                    str(out),
                    "--label",
                    "remote_desktop_4060",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            text = out.read_text(encoding="utf-8")
            self.assertIn("wrote environment snapshot", result.stdout)
            self.assertIn("target_label: remote_desktop_4060", text)
            self.assertIn("## PyTorch", text)
            self.assertIn("## Git", text)

    def test_section_citation_audit_parses_segments(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "section-citation-map.md").write_text(
                textwrap.dedent(
                    """\
                    | Section ID | Thesis Location | Section Purpose | Required Literature Role | Coverage Status | Notes |
                    |---|---|---|---|---|---|
                    | SEC-INTRO-001 | Ch1 | background | foundational | partial |  |

                    | Segment ID | Section ID | Segment / Claim Draft | Candidate Reference | DOI / arXiv / S2 ID | Support Grade | Source Status | Zotero Status | Scite / Reader Status | Export Format | Next Action |
                    |---|---|---|---|---|---|---|---|---|---|---|
                    | SEG-001 | SEC-INTRO-001 | claim | Paper A | 10.0000/example | strong | metadata_verified | in_zotero | supports_claim | bibtex | cite_in_related_work |
                    """
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(AUDIT_SECTION_CITATIONS)],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Sections: 1  |  Segments: 1", result.stdout)
            self.assertIn("Errors: 0", result.stdout)

    def test_section_citation_audit_reports_pending_suggestions(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "section-citation-map.md").write_text(
                "| Section ID | Thesis Location | Section Purpose | Required Literature Role | Coverage Status | Notes |\n"
                "|---|---|---|---|---|---|\n"
                "| SEC-INTRO-001 | Ch1 | background | foundational | missing |  |\n",
                encoding="utf-8",
            )
            (thesis / "section-citation-suggestions.md").write_text(
                "| Rank | Score | Section ID | Segment ID | Candidate Reference | Identifier | Source | Zotero / Scite / Reader | Suggested Use | Reasons |\n"
                "|---:|---:|---|---|---|---|---|---|---|---|\n"
                "| 1 | 8 | SEC-INTRO-001 | SEG-001 | Paper A | 10.0000/example | local | in_zotero | 优先核查 | section |\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(AUDIT_SECTION_CITATIONS), "--warn-only"],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("local citation suggestions are ready", result.stdout)

    def test_suggest_section_citations_ranks_local_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "section-citation-map.md").write_text(
                "| Section ID | Thesis Location | Section Purpose | Required Literature Role | Coverage Status | Notes |\n"
                "|---|---|---|---|---|---|\n"
                "| SEC-INTRO-001 | Ch1 | background | foundational | missing |  |\n\n"
                "| Segment ID | Section ID | Segment / Claim Draft | Candidate Reference | DOI / arXiv / S2 ID | Support Grade | Source Status | Zotero Status | Scite / Reader Status | Export Format | Next Action |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| SEG-001 | SEC-INTRO-001 | claim | Strong Paper | 10.0000/example | strong | metadata_verified | in_zotero | supports_claim | bibtex | cite |\n",
                encoding="utf-8",
            )
            json_out = project / "dashboard-web" / "public" / "data" / "citation-suggestions.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SUGGEST_SECTION_CITATIONS),
                    "--section-id",
                    "SEC-INTRO-001",
                    "--json-out",
                    str(json_out),
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            suggestions_md = (thesis / "section-citation-suggestions.md").read_text(encoding="utf-8")
            suggestions_json = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertIn("suggestions: 1", result.stdout)
            self.assertIn("Strong Paper", suggestions_md)
            self.assertEqual("SEC-INTRO-001", suggestions_json["sectionId"])
            self.assertGreaterEqual(suggestions_json["suggestions"][0]["score"], 10)

    def test_data_availability_audit_detects_traceable_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "data-availability.md").write_text(
                textwrap.dedent(
                    """\
                    | Dataset ID | Name / Version | Used By Claims | Used By Experiments | Local Path | Remote / Archive Path | Hash / Manifest | Access Level | License / Permission | Data Dictionary | Generation Command | Status | Notes |
                    |---|---|---|---|---|---|---|---|---|---|---|---|---|
                    | DATA-001 | dataset v1 | CLM-001 | EXP-001 | data/raw | remote | sha256:abc | private | advisor-approved | docs/data.md | python prepare.py | reviewed |  |

                    | Claim ID | Experiment / Figure | Source Data | Processed Data | Script / Notebook | Output Artifact | Trace Status | Required Fix |
                    |---|---|---|---|---|---|---|---|
                    | CLM-001 | EXP-001 | DATA-001 | data/processed | scripts/prepare.py | outputs/EXP-001/metrics.json | reviewed | none |
                    """
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(AUDIT_DATA_AVAILABILITY)],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Datasets: 1  |  Claim traces: 1", result.stdout)
            self.assertIn("Errors: 0", result.stdout)

    def test_new_autoresearch_iteration_appends_tsv_and_updates_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(NEW_AUTORESEARCH_ITERATION),
                    "--experiment-id",
                    "EXP-001",
                    "--target-claim",
                    "CLM-001",
                    "--change-summary",
                    "try smaller model",
                    "--primary-metric",
                    "accuracy",
                    "--baseline-value",
                    "0.80",
                    "--new-value",
                    "0.82",
                    "--verify-status",
                    "pass",
                    "--guard-status",
                    "pending",
                    "--decision",
                    "pending",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("appended iteration 1", result.stdout)
            tsv = (project / "docs" / "thesis" / "autoresearch-results.tsv").read_text(encoding="utf-8")
            state = (project / "docs" / "thesis" / "autoresearch-state.json").read_text(encoding="utf-8")
            self.assertIn("EXP-001", tsv)
            self.assertIn("0.02", tsv)
            self.assertIn("CLM-001", state)

    def test_new_deep_research_task_creates_section_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(NEW_DEEP_RESEARCH_TASK),
                    "--section-id",
                    "SEC-INTRO-001",
                    "--topic",
                    "remote sensing segmentation baselines",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            tasks = (project / "docs" / "thesis" / "deep-research-tasks.md").read_text(encoding="utf-8")
            packet = project / "docs" / "thesis" / "section-research-packets" / "SEC-INTRO-001.md"
            self.assertIn("appended deep research task", result.stdout)
            self.assertIn("SEC-INTRO-001", tasks)
            self.assertIn("remote sensing segmentation baselines", packet.read_text(encoding="utf-8"))

    def test_new_experiment_report_compares_baseline_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "experiment-registry.md").write_text(
                "| Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| EXP-000 | CLM-001 | baseline | DATA-001 | train | outputs/EXP-000 | accuracy=0.80 | reviewed | 2026-01-01 | local_mac |\n"
                "| EXP-001 | CLM-001 | improved | DATA-001 | train | outputs/EXP-001 | accuracy=0.83 | reviewed | 2026-01-02 | remote_desktop_4060 |\n",
                encoding="utf-8",
            )
            for exp_id, accuracy in (("EXP-000", 0.80), ("EXP-001", 0.83)):
                out_dir = project / "outputs" / exp_id
                out_dir.mkdir(parents=True)
                (out_dir / "metrics.json").write_text(json.dumps({"accuracy": accuracy}), encoding="utf-8")
            (project / "outputs" / "EXP-001" / "environment.txt").write_text(
                "target_label: remote_desktop_4060\n", encoding="utf-8"
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(NEW_EXPERIMENT_REPORT),
                    "--experiment-id",
                    "EXP-001",
                    "--baseline",
                    "EXP-000",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            report = (thesis / "experiment-reports" / "EXP-001.md").read_text(encoding="utf-8")
            self.assertIn("wrote experiment report", result.stdout)
            self.assertIn("EXP-000", report)
            self.assertIn("accuracy", report)
            self.assertIn("0.03", report)

    def test_audit_skills_reports_missing_reference_without_failing_warn_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            skill = project / "skills" / "demo-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("Read `references/missing.md` and run `scripts/missing.py`.\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SKILLS),
                    "--root",
                    str(project),
                    "--warn-only",
                    "--write-report",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("broken references: 1", result.stdout)
            self.assertIn("missing scripts: 1", result.stdout)
            self.assertTrue((project / "docs" / "thesis" / "skill-audit-report.md").exists())

    def test_export_evidence_graph_writes_json_and_mermaid(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "claim-evidence-map.md").write_text(
                textwrap.dedent(
                    """\
                    | Claim ID | Claim Draft | Status | Experiment Evidence | Figure/Table | Literature Evidence | Caveat | Next Action |
                    |---|---|---|---|---|---|---|---|
                    | CLM-001 | accuracy improves | supported | EXP-001 | FIG-001 | Paper A | bounded | done |
                    """
                ),
                encoding="utf-8",
            )
            (thesis / "experiment-registry.md").write_text(
                "| Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| EXP-001 | CLM-001 | config | DATA-001 | train | outputs/EXP-001 | acc | reviewed | 2026-01-01 | remote_desktop_4060 |\n",
                encoding="utf-8",
            )
            (thesis / "data-availability.md").write_text(
                "| Dataset ID | Name / Version | Used By Claims | Used By Experiments | Local Path | Remote / Archive Path | Hash / Manifest | Access Level | License / Permission | Data Dictionary | Generation Command | Status | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| DATA-001 | dataset | CLM-001 | EXP-001 | data | remote | sha256:abc | private | ok | dict | prepare | reviewed |  |\n",
                encoding="utf-8",
            )
            (thesis / "figure-plan.md").write_text(
                "| Figure ID | Type | Purpose | Related Claim | Role | Source Data | Script | Visual Type | Caption | Status |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| FIG-001 | figure | result | CLM-001 | support | DATA-001 | plot.py | bar | safe | final |\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(EXPORT_EVIDENCE_GRAPH)],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            graph = json.loads((thesis / "evidence-graph.json").read_text(encoding="utf-8"))
            mermaid = (thesis / "evidence-graph.mmd").read_text(encoding="utf-8")
            node_ids = {node["id"] for node in graph["nodes"]}
            self.assertIn("nodes:", result.stdout)
            self.assertTrue({"CLM-001", "EXP-001", "DATA-001", "FIG-001"}.issubset(node_ids))
            self.assertIn("graph LR", mermaid)
            self.assertIn("CLM_001", mermaid)

    def test_research_workflow_doctor_writes_dashboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "workflow-dashboard.md").write_text(
                "# Workflow Dashboard\n\n<!-- workflow-doctor:start -->\nold\n<!-- workflow-doctor:end -->\n",
                encoding="utf-8",
            )
            for name in (
                "daily-workflow-entry.md",
                "evidence-promotion-policy.md",
                "id-lifecycle-policy.md",
                "material-passport.md",
                "section-citation-map.md",
                "citation-provenance.md",
                "zotero-screening-loop.md",
                "zotero-collection-coverage.md",
                "benchmark-report-schema.md",
                "figure-plan.md",
                "diagram-replica-tasks.md",
                "final-artifact-manifest.md",
                "final-audit.md",
                "workflow-edit-log.md",
            ):
                (thesis / name).write_text("# placeholder\n", encoding="utf-8")
            source = project / "outputs" / "final.pdf"
            source.parent.mkdir(parents=True)
            source.write_text("pdf placeholder", encoding="utf-8")
            (thesis / "final-artifact-manifest.md").write_text(
                "| Artifact Key | Stage | Source IDs | Mac Source Path | Laptop Target Path | Format | Checksum | Produced By | Transfer Status | Laptop Verification | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                f"| final-pdf | 11-doc-production | CLM-001; FIG-001; DATA-001 | {source} | /laptop/final.pdf | pdf | sha256:abc | Documents | verified | opened on laptop | test |\n",
                encoding="utf-8",
            )
            (thesis / "id-lifecycle-policy.md").write_text(
                "| ID | Type | Status | Primary File | Related IDs | Replacement ID | Owner | Updated On | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|\n"
                "| CLM-001 | claim | verified | claim-evidence-map.md | EXP-001; FIG-001; DATA-001 |  | user | 2026-01-01 | test |\n",
                encoding="utf-8",
            )
            (thesis / "claim-evidence-map.md").write_text(
                "| Claim ID | Claim Draft | Status | Experiment Evidence | Figure/Table | Literature Evidence | Caveat | Next Action |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| CLM-001 | accuracy improves | supported | EXP-001 | FIG-001 | Paper A | bounded | done |\n",
                encoding="utf-8",
            )
            (thesis / "experiment-registry.md").write_text(
                "| Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| EXP-001 | CLM-001 | config | DATA-001 | train | outputs/EXP-001 | acc | reviewed | 2026-01-01 | reviewed |\n",
                encoding="utf-8",
            )
            (thesis / "data-availability.md").write_text(
                "| Dataset ID | Name / Version | Used By Claims | Used By Experiments | Local Path | Remote / Archive Path | Hash / Manifest | Access Level | License / Permission | Data Dictionary | Generation Command | Status | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| DATA-001 | dataset | CLM-001 | EXP-001 | data | remote | sha256:abc | private | ok | dict | prepare | reviewed |  |\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(RESEARCH_WORKFLOW_DOCTOR),
                    "--write-dashboard",
                    "--write-data",
                    "--json-out",
                    "docs/thesis/dashboard-data.json",
                    "--warn-only",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            dashboard = (thesis / "workflow-dashboard.md").read_text(encoding="utf-8")
            dashboard_json = json.loads((thesis / "dashboard-data.json").read_text(encoding="utf-8"))
            self.assertIn("Workflow Health", result.stdout)
            self.assertIn("wrote dashboard data", result.stdout)
            self.assertIn("claims=1 experiments=1 datasets=1", dashboard)
            self.assertEqual("ok", dashboard_json["health"])
            self.assertEqual(1, dashboard_json["counts"]["claims"])
            self.assertIn("skillHealth", dashboard_json)
            self.assertNotIn("old", dashboard)

    def test_edit_workflow_record_creates_standard_records_and_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "workflow-dashboard.md").write_text(
                "# Workflow Dashboard\n\n## Current Status\n\n| Field | Value |\n|---|---|\n| Current stage | 1-12/TBD |\n| Active focus | TBD |\n| Current audit tier | quick |\n| Main blocker | TBD |\n| Next concrete action | TBD |\n| Last dashboard refresh | TBD |\n",
                encoding="utf-8",
            )
            (thesis / "claim-evidence-map.md").write_text(
                "| Claim ID | Claim Draft | Status | Experiment Evidence | Figure/Table | Literature Evidence | Caveat | Next Action |\n|---|---|---|---|---|---|---|---|\n",
                encoding="utf-8",
            )
            (thesis / "experiment-registry.md").write_text(
                "| Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes |\n|---|---|---|---|---|---|---|---|---|---|\n",
                encoding="utf-8",
            )
            (thesis / "material-passport.md").write_text(
                "| Material ID | Type | Title / Description | Source Path / URL | Owner | Created / Updated | Related IDs | Access Level | License / Permission | Integrity Check | Repro Lock | Status | Notes |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|\n",
                encoding="utf-8",
            )
            (thesis / "citation-provenance.md").write_text(
                "| Citation ID | Section ID | Segment ID | Claim ID | Title | Identifier | Candidate Source | Metadata Status | Support Status | Zotero Status | Scite / Reader Evidence | Verified By | Verified On | Export Status | Notes |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n",
                encoding="utf-8",
            )
            (thesis / "final-artifact-manifest.md").write_text(
                "| Artifact Key | Stage | Source IDs | Mac Source Path | Laptop Target Path | Format | Checksum | Produced By | Transfer Status | Laptop Verification | Notes |\n|---|---|---|---|---|---|---|---|---|---|---|\n",
                encoding="utf-8",
            )
            (thesis / "id-lifecycle-policy.md").write_text(
                "| ID | Type | Status | Primary File | Related IDs | Replacement ID | Owner | Updated On | Notes |\n|---|---|---|---|---|---|---|---|---|\n",
                encoding="utf-8",
            )

            payloads = [
                {"action": "update-status", "fields": {"current_stage": "6 实验运行", "next_action": "run smoke"}},
                {"action": "create-record", "record_type": "claim", "fields": {"claim_draft": "model improves accuracy", "experiment_evidence": "EXP-001"}},
                {"action": "create-record", "record_type": "experiment", "fields": {"claim": "CLM-001", "method_config": "config.yaml", "output_path": "outputs/EXP-001"}},
                {"action": "create-record", "record_type": "material", "fields": {"type": "figure", "title": "Figure source", "related_ids": "FIG-001"}},
                {"action": "create-record", "record_type": "citation", "fields": {"title": "Important paper", "identifier": "10.0000/example"}},
                {"action": "create-final-artifact", "fields": {"artifact_key": "final-pdf", "format": "pdf", "transfer_status": "copied"}},
                {"action": "update-id-lifecycle", "fields": {"id": "CLM-001", "type": "claim", "status": "verified", "primary_file": "claim-evidence-map.md"}},
            ]
            for payload in payloads:
                subprocess.run(
                    [sys.executable, str(EDIT_WORKFLOW_RECORD), "--payload-json", json.dumps(payload)],
                    cwd=project,
                    text=True,
                    capture_output=True,
                    check=True,
                )

            self.assertIn("6 实验运行", (thesis / "workflow-dashboard.md").read_text(encoding="utf-8"))
            self.assertIn("model improves accuracy", (thesis / "claim-evidence-map.md").read_text(encoding="utf-8"))
            self.assertIn("outputs/EXP-001", (thesis / "experiment-registry.md").read_text(encoding="utf-8"))
            self.assertIn("Figure source", (thesis / "material-passport.md").read_text(encoding="utf-8"))
            self.assertIn("Important paper", (thesis / "citation-provenance.md").read_text(encoding="utf-8"))
            self.assertIn("final-pdf", (thesis / "final-artifact-manifest.md").read_text(encoding="utf-8"))
            self.assertIn("verified", (thesis / "id-lifecycle-policy.md").read_text(encoding="utf-8"))
            self.assertIn("create final artifact", (thesis / "workflow-edit-log.md").read_text(encoding="utf-8"))
            self.assertTrue((project / "tmp" / "dashboard-edits" / "backups").exists())

    def test_update_daily_workflow_updates_dashboard_and_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "workflow-dashboard.md").write_text(
                "# Workflow Dashboard\n\n## Current Status\n\n"
                "| Field | Value |\n|---|---|\n"
                "| Current stage | 1-12/TBD |\n"
                "| Active focus | TBD |\n"
                "| Current audit tier | quick |\n"
                "| Main blocker | TBD |\n"
                "| Next concrete action | TBD |\n"
                "| Last dashboard refresh | TBD |\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(UPDATE_DAILY_WORKFLOW),
                    "--stage",
                    "2 文献发现与综述",
                    "--focus",
                    "citation coverage",
                    "--next-action",
                    "confirm section citations",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            daily = (thesis / "daily-workflow-entry.md").read_text(encoding="utf-8")
            dashboard = (thesis / "workflow-dashboard.md").read_text(encoding="utf-8")
            edit_log = (thesis / "workflow-edit-log.md").read_text(encoding="utf-8")
            self.assertIn("updated daily workflow entry", result.stdout)
            self.assertIn("2 文献发现与综述", daily)
            self.assertIn("citation coverage", dashboard)
            self.assertIn("update daily workflow", edit_log)

    def test_final_artifact_audit_detects_missing_final_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            source = project / "outputs" / "final.pdf"
            source.parent.mkdir(parents=True)
            source.write_text("pdf placeholder", encoding="utf-8")
            (thesis / "final-artifact-manifest.md").write_text(
                "| Artifact Key | Stage | Source IDs | Mac Source Path | Laptop Target Path | Format | Checksum | Produced By | Transfer Status | Laptop Verification | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                f"| final-pdf | 11-doc-production | CLM-001 | {source} | TBD | pdf | TBD | Documents | copied | pending | final pdf |\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(AUDIT_FINAL_ARTIFACTS), "--tier", "final", "--warn-only"],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Final Artifacts: 1", result.stdout)
            self.assertIn("missing checksum", result.stdout)
            self.assertIn("not verified on the laptop", result.stdout)

    def test_final_handoff_package_and_verify_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            source = project / "outputs" / "final.pdf"
            source.parent.mkdir(parents=True)
            source.write_text("pdf placeholder", encoding="utf-8")
            (thesis / "final-artifact-manifest.md").write_text(
                "| Artifact Key | Stage | Source IDs | Mac Source Path | Laptop Target Path | Format | Checksum | Produced By | Transfer Status | Laptop Verification | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                f"| final-pdf | 11-doc-production | CLM-001 | {source} | /laptop/final.pdf | pdf | TBD | Documents | copied | pending | final pdf |\n",
                encoding="utf-8",
            )
            package_result = subprocess.run(
                [sys.executable, str(PACKAGE_FINAL_HANDOFF), "--update-manifest-checksums", "--json"],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            package_json = json.loads(package_result.stdout)
            self.assertEqual(1, len(package_json["packaged"]))
            self.assertTrue(Path(package_json["zip_path"]).exists())
            self.assertIn("sha256:", (thesis / "final-artifact-manifest.md").read_text(encoding="utf-8"))

            verify_result = subprocess.run(
                [
                    sys.executable,
                    str(VERIFY_FINAL_HANDOFF),
                    "--latest",
                    "--write-report",
                    "docs/thesis/final-handoff-verify-report.md",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Final handoff verify: PASS", verify_result.stdout)
            self.assertIn("Status: `pass`", (thesis / "final-handoff-verify-report.md").read_text(encoding="utf-8"))

    def test_id_lifecycle_audit_detects_weak_links_and_deprecated_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "id-lifecycle-policy.md").write_text(
                "| ID | Type | Status | Primary File | Related IDs | Replacement ID | Owner | Updated On | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|\n"
                "| CLM-OLD | claim | deprecated | claim-evidence-map.md |  |  | user | 2026-01-01 | old claim |\n",
                encoding="utf-8",
            )
            (thesis / "claim-evidence-map.md").write_text(
                "| Claim ID | Claim Draft | Status | Experiment Evidence | Figure/Table | Literature Evidence | Caveat | Next Action |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| CLM-001 | unsupported claim | supported | TBD | TBD | Paper A | none | fix |\n"
                "| CLM-OLD | old claim | supported | EXP-001 | FIG-001 | Paper B | none | remove |\n",
                encoding="utf-8",
            )
            (thesis / "figure-plan.md").write_text(
                "| Figure ID | Type | Purpose | Related Claim | Role | Source Data | Script | Visual Type | Caption | Status |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| FIG-001 | figure | result | TBD | support | TBD | plot.py | bar | caption | final |\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(AUDIT_ID_LIFECYCLE), "--warn-only"],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("CLM-001 has no EXP/DATA/CIT/FIG evidence link", result.stdout)
            self.assertIn("CLM-OLD is deprecated", result.stdout)
            self.assertIn("FIG-001 is final but has no CLM/EXP/DATA source link", result.stdout)

    def test_dashboard_control_server_rejects_unlisted_open_path(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        proc = subprocess.Popen(
            [sys.executable, str(DASHBOARD_CONTROL_SERVER), "--port", str(port)],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            status_url = f"http://127.0.0.1:{port}/api/status"
            for _ in range(30):
                try:
                    with opener.open(status_url, timeout=0.2) as response:
                        self.assertEqual(200, response.status)
                        break
                except OSError:
                    time.sleep(0.1)
            else:
                stderr = ""
                if proc.poll() is not None:
                    _, stderr = proc.communicate(timeout=1)
                self.fail(f"dashboard control server did not start; exit={proc.poll()} stderr={stderr}")

            request = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/open-path",
                data=json.dumps({"key": "../secrets"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                opener.open(request, timeout=1)
            self.assertEqual(403, ctx.exception.code)

            with opener.open(f"http://127.0.0.1:{port}/api/flow-editor/schema", timeout=1) as response:
                schema = json.loads(response.read().decode("utf-8"))
            self.assertIn("claim", schema["schema"]["recordTypes"])

            with opener.open(f"http://127.0.0.1:{port}/api/stage-workspace", timeout=1) as response:
                workspace = json.loads(response.read().decode("utf-8"))
            self.assertIn("workspace", workspace)

            bad_section_request = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/suggest-section-citations",
                data=json.dumps({"section_id": "../bad"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(urllib.error.HTTPError) as section_ctx:
                opener.open(bad_section_request, timeout=1)
            self.assertEqual(400, section_ctx.exception.code)

            bad_request = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/flow-editor/create-record",
                data=json.dumps({"record_type": "../bad", "fields": {}}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(urllib.error.HTTPError) as bad_ctx:
                opener.open(bad_request, timeout=1)
            self.assertEqual(400, bad_ctx.exception.code)
        finally:
            proc.terminate()
            try:
                proc.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate(timeout=2)


if __name__ == "__main__":
    unittest.main()
