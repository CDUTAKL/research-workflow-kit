from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "recompute_prediction_metrics.py"
REPO = Path(__file__).resolve().parents[1]


class RecomputePredictionMetricsTests(unittest.TestCase):
    def write_predictions(self, root: Path, rows: list[dict[str, str]]) -> Path:
        path = root / "predictions.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["sample_id", "model_id", "y_true", "y_pred", "cluster_id"])
            writer.writeheader()
            writer.writerows(rows)
        return path

    def run_script(self, predictions: Path, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--input",
                str(predictions),
                "--out",
                str(output),
                "--baseline-model",
                "baseline",
                "--candidate-model",
                "candidate",
                "--bootstrap-resamples",
                "300",
                "--seed",
                "17",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_recomputes_paired_metrics_and_cluster_bootstrap_interval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            predictions = self.write_predictions(
                root,
                [
                    {"sample_id": "s1", "model_id": "baseline", "y_true": "0", "y_pred": "0", "cluster_id": "d1"},
                    {"sample_id": "s1", "model_id": "candidate", "y_true": "0", "y_pred": "1", "cluster_id": "d1"},
                    {"sample_id": "s2", "model_id": "baseline", "y_true": "2", "y_pred": "2", "cluster_id": "d1"},
                    {"sample_id": "s2", "model_id": "candidate", "y_true": "2", "y_pred": "1", "cluster_id": "d1"},
                    {"sample_id": "s3", "model_id": "baseline", "y_true": "3", "y_pred": "1", "cluster_id": "d2"},
                    {"sample_id": "s3", "model_id": "candidate", "y_true": "3", "y_pred": "2", "cluster_id": "d2"},
                    {"sample_id": "s4", "model_id": "baseline", "y_true": "4", "y_pred": "4", "cluster_id": "d2"},
                    {"sample_id": "s4", "model_id": "candidate", "y_true": "4", "y_pred": "2", "cluster_id": "d2"},
                ],
            )
            output = root / "recomputed.json"

            result = self.run_script(predictions, output)

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertAlmostEqual(report["models"]["baseline"]["mae"], 0.5)
            comparison = report["comparison"]
            self.assertAlmostEqual(comparison["mae"]["delta_candidate_minus_baseline"], 0.75)
            self.assertEqual(comparison["mae"]["resampling_unit"], "cluster_id")
            self.assertEqual(comparison["mae"]["bootstrap_resamples"], 300)
            self.assertEqual(len(comparison["mae"]["confidence_interval_95"]), 2)

    def test_rejects_comparison_when_model_samples_do_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            predictions = self.write_predictions(
                root,
                [
                    {"sample_id": "s1", "model_id": "baseline", "y_true": "0", "y_pred": "0", "cluster_id": "d1"},
                    {"sample_id": "s2", "model_id": "baseline", "y_true": "2", "y_pred": "2", "cluster_id": "d2"},
                    {"sample_id": "s1", "model_id": "candidate", "y_true": "0", "y_pred": "1", "cluster_id": "d1"},
                    {"sample_id": "s3", "model_id": "candidate", "y_true": "3", "y_pred": "1", "cluster_id": "d2"},
                ],
            )

            result = self.run_script(predictions, root / "recomputed.json")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("same sample IDs", result.stderr)
            self.assertFalse((root / "recomputed.json").exists())

    def test_project_initialization_copies_quality_templates_and_recompute_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "smoke-project"
            result = subprocess.run(
                [sys.executable, str(REPO / "init_research_workflow.py"), "--project", str(project)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            integrity = project / "docs/thesis/experiment-integrity-checklist.md"
            final_audit = project / "docs/thesis/final-audit.md"
            self.assertIn("Test-Set Access Log", integrity.read_text(encoding="utf-8"))
            self.assertIn("verified_closed", final_audit.read_text(encoding="utf-8"))
            self.assertTrue((project / "scripts/recompute_prediction_metrics.py").is_file())


if __name__ == "__main__":
    unittest.main()
