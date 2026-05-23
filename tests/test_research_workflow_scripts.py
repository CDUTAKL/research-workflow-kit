import subprocess
import sys
import tempfile
import textwrap
import unittest
import json
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
                "evidence-promotion-policy.md",
                "section-citation-map.md",
                "figure-plan.md",
                "final-audit.md",
            ):
                (thesis / name).write_text("# placeholder\n", encoding="utf-8")
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
                [sys.executable, str(RESEARCH_WORKFLOW_DOCTOR), "--write-dashboard", "--warn-only"],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            dashboard = (thesis / "workflow-dashboard.md").read_text(encoding="utf-8")
            self.assertIn("Workflow Health", result.stdout)
            self.assertIn("claims=1 experiments=1 datasets=1", dashboard)
            self.assertNotIn("old", dashboard)


if __name__ == "__main__":
    unittest.main()
