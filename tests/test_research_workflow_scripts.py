import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
NEW_EXPERIMENT = REPO_ROOT / "scripts" / "new_experiment.py"
AUDIT_CLAIMS = REPO_ROOT / "scripts" / "audit_claim_evidence.py"


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


if __name__ == "__main__":
    unittest.main()
