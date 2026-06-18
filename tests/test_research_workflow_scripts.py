import csv
import gzip
import json
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

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
UPDATE_WEEKLY_REVIEW = REPO_ROOT / "scripts" / "update_weekly_review.py"
SUGGEST_SECTION_CITATIONS = REPO_ROOT / "scripts" / "suggest_section_citations.py"
PACKAGE_FINAL_HANDOFF = REPO_ROOT / "scripts" / "package_final_handoff.py"
VERIFY_FINAL_HANDOFF = REPO_ROOT / "scripts" / "verify_final_handoff.py"
PLUGIN_GATE_ADVISOR = REPO_ROOT / "scripts" / "plugin_gate_advisor.py"
SYNC_ZOTERO_INVENTORY = REPO_ROOT / "scripts" / "sync_zotero_inventory.py"
AUDIT_ZOTERO_COVERAGE = REPO_ROOT / "scripts" / "audit_zotero_coverage.py"
EXPORT_ZOTERO_BIBLIOGRAPHY = REPO_ROOT / "scripts" / "export_zotero_bibliography.py"
INIT_RESEARCH_WORKFLOW = REPO_ROOT / "init_research_workflow.py"
AUDIT_PROJECT_SCOPE = REPO_ROOT / "scripts" / "audit_project_scope.py"
COLLECT_EXP103_RESULTS = REPO_ROOT / "scripts" / "collect_exp103_results.py"
RUN_EXP103_HPARAM_SEARCH = REPO_ROOT / "scripts" / "run_exp103_hparam_search.py"
DIAGNOSE_EXP103_EVENT_GRAPH = REPO_ROOT / "scripts" / "diagnose_exp103_event_graph.py"
SUMMARIZE_EXP103_MULTISEED = REPO_ROOT / "scripts" / "summarize_exp103_multiseed.py"
ANALYZE_EXP103_V5_PLUS_EVIDENCE = REPO_ROOT / "scripts" / "analyze_exp103_v5_plus_evidence.py"
STACK_EXP103_V5_PREDICTIONS = REPO_ROOT / "scripts" / "stack_exp103_v5_predictions.py"

FULL_PREDICTION_COLUMNS = [
    "baseline_id",
    "seed",
    "split",
    "origin_index",
    "timestamp",
    "node_id",
    "horizon_step",
    "target",
    "prediction",
    "abs_error",
    "squared_error",
    "event_window_any",
    "event_window_access",
    "event_window_departure",
    "event_window_load_jump",
]


def _write_full_prediction_fixture(path: Path, baseline_id: str, seed: int, split: str, predictions: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    targets = [10.0, 20.0, 30.0, 40.0]
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FULL_PREDICTION_COLUMNS)
        writer.writeheader()
        for index, (target, prediction) in enumerate(zip(targets, predictions)):
            error = prediction - target
            writer.writerow(
                {
                    "baseline_id": baseline_id,
                    "seed": seed,
                    "split": split,
                    "origin_index": 100 + index,
                    "timestamp": f"2026-01-01T00:{index:02d}:00",
                    "node_id": "N0",
                    "horizon_step": 1,
                    "target": target,
                    "prediction": prediction,
                    "abs_error": abs(error),
                    "squared_error": error * error,
                    "event_window_any": 1 if index % 2 == 0 else 0,
                    "event_window_access": 1 if index == 0 else 0,
                    "event_window_departure": 1 if index == 2 else 0,
                    "event_window_load_jump": 0,
                }
            )


class ResearchWorkflowScriptTests(unittest.TestCase):
    def test_diagnose_exp103_event_graph_writes_report_from_result_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            data = project / "data" / "processed"
            splits = data / "splits"
            data.mkdir(parents=True)
            splits.mkdir(parents=True)
            time_count = 20
            node_count = 4
            feature_count = 2

            np.savez_compressed(
                data / "cache.npz",
                load=np.arange(time_count * node_count, dtype=np.float32).reshape(time_count, node_count),
                event_features=np.arange(time_count * node_count * feature_count, dtype=np.float32).reshape(
                    time_count, node_count, feature_count
                ),
                timestamps=np.asarray([f"2026-01-01T00:{index:02d}:00" for index in range(time_count)]),
                nodes=np.asarray([f"N{index}" for index in range(node_count)]),
                event_feature_names=np.asarray(["access_count", "departure_count"]),
                origin_indices=np.asarray(list(range(3, 17)), dtype=np.int32),
                train_origins=np.asarray(list(range(3, 11)), dtype=np.int32),
                validation_origins=np.asarray(list(range(11, 14)), dtype=np.int32),
                test_origins=np.asarray(list(range(14, 17)), dtype=np.int32),
                load_mean=np.zeros((node_count,), dtype=np.float32),
                load_std=np.ones((node_count,), dtype=np.float32),
                event_mean=np.zeros((node_count, feature_count), dtype=np.float32),
                event_std=np.ones((node_count, feature_count), dtype=np.float32),
            )
            (data / "cache_manifest.json").write_text(
                json.dumps({"history_steps": 4, "horizon_steps": 1}) + "\n",
                encoding="utf-8",
            )
            run_dir = project / "outputs" / "EXP-103-train-optimized-42-5090"
            run_dir.mkdir(parents=True)
            (run_dir / "config_resolved.json").write_text(
                json.dumps(
                    {
                        "seed": 42,
                        "cache": {
                            "tensor_cache_path": str(data / "cache.npz"),
                            "manifest_path": str(data / "cache_manifest.json"),
                        },
                        "graph": {"top_k": 2},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (run_dir / "baseline_metrics.csv").write_text(
                textwrap.dedent(
                    """\
                    baseline_id,MAE,RMSE,prediction_count,best_validation_loss,best_epoch,epochs_ran,train_seconds,uses_events,uses_graph,graph_mode,gate_mean,gate_std
                    behavior_concat,0.023,0.31,100,0.032,8,10,12.0,True,False,gated_residual,,
                    event_graph_dynamic,0.022,0.30,100,0.031,9,11,13.0,True,True,gated_residual,0.04,0.01
                    historical_correlation_graph,0.021,0.29,100,0.030,7,9,14.0,True,True,gated_residual,0.05,0.02
                    shuffled_event_graph,0.0225,0.30,100,0.031,6,8,10.0,True,True,gated_residual,0.03,0.01
                    """
                ),
                encoding="utf-8",
            )
            (run_dir / "event_window_metrics.csv").write_text(
                textwrap.dedent(
                    """\
                    baseline_id,event_window,MAE,RMSE,prediction_count
                    event_graph_dynamic,departure_count,0.9,2.0,20
                    historical_correlation_graph,departure_count,1.0,2.1,20
                    shuffled_event_graph,departure_count,1.1,2.2,20
                    behavior_concat,departure_count,1.2,2.3,20
                    """
                ),
                encoding="utf-8",
            )
            out_dir = project / "outputs" / "diagnostics"

            result = subprocess.run(
                [
                    sys.executable,
                    str(DIAGNOSE_EXP103_EVENT_GRAPH),
                    "--outputs-root",
                    str(project / "outputs"),
                    "--run-glob",
                    "EXP-103-train-optimized-*-5090",
                    "--graph-run-dir",
                    str(run_dir),
                    "--sample-origins",
                    "5",
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("wrote EXP-103 diagnostic outputs", result.stdout)
            report = (out_dir / "EXP-103-event-graph-diagnosis.md").read_text(encoding="utf-8")
            answers = (out_dir / "diagnostic_answers.csv").read_text(encoding="utf-8")
            self.assertIn("Four Diagnostic Questions", report)
            self.assertIn("event_graph_dynamic", report)
            self.assertIn("event_gate_mean", answers)
            self.assertTrue((out_dir / "global_metric_summary.csv").exists())

    def test_run_exp103_hparam_search_dry_run_generates_configs_and_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            base_config = project / "base.json"
            base_config.write_text(
                json.dumps(
                    {
                        "experiment_id": "EXP-103",
                        "seed": 42,
                        "output": "outputs/base",
                        "data": {"source_path": "data/processed/evcs_timeslice.csv"},
                        "cache": {
                            "tensor_cache_path": "data/processed/evcs_tensor_cache_optimized.npz",
                            "split_path": "data/processed/splits/chronological_70_15_15_optimized.json",
                            "manifest_path": "data/processed/evcs_tensor_cache_optimized_manifest.json",
                            "auto_build": False,
                        },
                        "graph": {
                            "top_k": 5,
                            "rho": 0.7,
                            "lambda_event": 0.3,
                            "dtw_max_points": 128,
                            "dtw_cache_path": "data/processed/graphs/dtw_demand_graph_top5_points128.npz",
                        },
                        "features": {"include_time_context": True, "include_enhanced_events": True},
                        "training": {
                            "epochs": 50,
                            "batch_size": 256,
                            "hidden_channels": 64,
                            "lr": 0.001,
                            "dropout": 0.1,
                            "graph_mode": "gated_residual",
                        },
                        "baselines": ["event_graph_dynamic", "behavior_concat"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUN_EXP103_HPARAM_SEARCH),
                    "--base-config",
                    str(base_config),
                    "--out-root",
                    str(project / "outputs" / "hparam"),
                    "--generated-config-dir",
                    str(project / "configs" / "generated"),
                    "--summary-out",
                    str(project / "outputs" / "summary.csv"),
                    "--runs-out",
                    str(project / "outputs" / "runs.csv"),
                    "--command-log",
                    str(project / "outputs" / "commands.sh"),
                    "--batch-sizes",
                    "512",
                    "--graph-modes",
                    "concat,gated_residual",
                    "--top-ks",
                    "3",
                    "--hidden-channels",
                    "64",
                    "--baselines",
                    "event_graph_dynamic,behavior_concat",
                    "--dry-run",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("generated 2 EXP-103 hparam configs", result.stdout)
            generated = sorted((project / "configs" / "generated").glob("*.json"))
            self.assertEqual(len(generated), 2)
            config = json.loads(generated[0].read_text(encoding="utf-8"))
            self.assertEqual(config["training"]["batch_size"], 512)
            self.assertIn(config["training"]["graph_mode"], {"concat", "gated_residual"})
            self.assertEqual(config["graph"]["top_k"], 3)
            self.assertEqual(config["graph"]["dtw_cache_path"], "data/processed/graphs/dtw_demand_graph_top3_points128.npz")
            commands = (project / "outputs" / "commands.sh").read_text(encoding="utf-8")
            self.assertIn("src/training/train_exp103.py", commands)
            self.assertIn("--config", commands)
            summary = (project / "outputs" / "summary.csv").read_text(encoding="utf-8")
            runs = (project / "outputs" / "runs.csv").read_text(encoding="utf-8")
            self.assertIn("event_vs_historical_delta", summary)
            self.assertIn("dry_run", summary)
            self.assertIn("baseline_id", runs)

    def test_summarize_exp103_multiseed_writes_v5_aggregate_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            runs = []
            for seed, mae in [(42, 0.022), (2026, 0.023), (3407, 0.021)]:
                # 回归覆盖正式 full-baseline 命名：旧正则只识别 `v5-42-5090`，
                # 会把 `v5-final-full-42-5090` 解析成 -1，导致 seed_count 被误写成 1。
                run_dir = project / "outputs" / f"EXP-103-v5-final-full-{seed}-5090"
                run_dir.mkdir(parents=True)
                runs.append(run_dir)
                (run_dir / "primary_metric_summary.csv").write_text(
                    textwrap.dedent(
                        f"""\
                        baseline_id,MAE,RMSE,rank_by_MAE
                        historical_event_residual_graph_v5,{mae},0.30,1
                        semantic_shuffled_event_residual_graph_v5,{mae + 0.001},0.31,2
                        """
                    ),
                    encoding="utf-8",
                )
                (run_dir / "baseline_deltas.csv").write_text(
                    textwrap.dedent(
                        f"""\
                        baseline_id,comparator_baseline,metric,baseline_value,comparator_value,delta
                        historical_event_residual_graph_v5,semantic_shuffled_event_residual_graph_v5,MAE,{mae},{mae + 0.001},-0.001
                        """
                    ),
                    encoding="utf-8",
                )
                (run_dir / "event_window_metrics.csv").write_text(
                    textwrap.dedent(
                        f"""\
                        baseline_id,event_window,MAE,RMSE,prediction_count
                        historical_event_residual_graph_v5,departure_count,{mae},0.30,10
                        """
                    ),
                    encoding="utf-8",
                )
                (run_dir / "graph_gate_metrics.csv").write_text(
                    textwrap.dedent(
                        """\
                        baseline_id,gate_scope,gate_event_minus_stable,event_gate_event_window_mean,event_gate_stable_window_mean
                        historical_event_residual_graph_v5,summary,0.08,0.30,0.22
                        """
                    ),
                    encoding="utf-8",
                )
                (run_dir / "residual_diagnostics.csv").write_text(
                    textwrap.dedent(
                        """\
                        baseline_id,residual_abs_mean,residual_abs_event_window_mean,residual_abs_stable_window_mean
                        historical_event_residual_graph_v5,0.01,0.02,0.005
                        """
                    ),
                    encoding="utf-8",
                )
                # 可选诊断表可能存在但没有内容；汇总脚本应跳过它，而不是中断主指标汇总。
                (run_dir / "event_loss_diagnostics.csv").write_text("", encoding="utf-8")
            out = project / "outputs" / "EXP-103-v5-multiseed-summary"

            subprocess.run(
                [
                    sys.executable,
                    str(SUMMARIZE_EXP103_MULTISEED),
                    "--runs",
                    *[str(run) for run in runs],
                    "--out",
                    str(out),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertTrue((out / "primary_metric_summary_all_seeds.csv").exists())
            self.assertTrue((out / "primary_metric_summary_multiseed.csv").exists())
            summary = (out / "primary_metric_summary_multiseed.csv").read_text(encoding="utf-8")
            self.assertIn("MAE_mean", summary)
            self.assertIn("best_mae_seed_count", summary)
            rows = {row["baseline_id"]: row for row in csv.DictReader(summary.splitlines())}
            event_row = rows["historical_event_residual_graph_v5"]
            self.assertEqual(event_row["seed_count"], "3")
            self.assertEqual(event_row["best_mae_seed_count"], "3")
            self.assertAlmostEqual(float(event_row["MAE_mean"]), 0.022)
            self.assertAlmostEqual(float(event_row["rank_by_MAE_mean"]), 1.0)

    def test_analyze_exp103_v5_plus_evidence_writes_bootstrap_and_event_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            run_dir = project / "outputs" / "EXP-103-v5-plus-42-5090"
            pred_dir = run_dir / "predictions_full"
            _write_full_prediction_fixture(
                pred_dir / "test_event_graph_dynamic_v5.csv.gz",
                "event_graph_dynamic_v5",
                42,
                "test",
                [10.1, 19.9, 30.2, 39.8],
            )
            _write_full_prediction_fixture(
                pred_dir / "test_behavior_concat_v5.csv.gz",
                "behavior_concat_v5",
                42,
                "test",
                [11.0, 18.8, 31.2, 38.5],
            )
            _write_full_prediction_fixture(
                pred_dir / "test_historical_correlation_graph_v5.csv.gz",
                "historical_correlation_graph_v5",
                42,
                "test",
                [10.5, 19.5, 30.7, 39.3],
            )
            out = project / "outputs" / "EXP-103-v5-plus-evidence-analysis"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ANALYZE_EXP103_V5_PLUS_EVIDENCE),
                    "--runs",
                    str(run_dir),
                    "--out",
                    str(out),
                    "--primary",
                    "event_graph_dynamic_v5",
                    "--comparators",
                    "behavior_concat_v5,historical_correlation_graph_v5",
                    "--bootstrap-samples",
                    "50",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("wrote V5 Plus paired evidence analysis", result.stdout)
            for name in (
                "paired_deltas.csv",
                "bootstrap_ci.csv",
                "event_window_delta_summary.csv",
                "event_stable_primary_table.csv",
                "v5_plus_decision_summary.md",
            ):
                self.assertTrue((out / name).exists(), name)
            bootstrap_rows = list(csv.DictReader((out / "bootstrap_ci.csv").read_text(encoding="utf-8").splitlines()))
            behavior_row = next(row for row in bootstrap_rows if row["comparator_baseline"] == "behavior_concat_v5")
            self.assertLess(float(behavior_row["delta_mean"]), 0.0)
            primary_rows = list(csv.DictReader((out / "event_stable_primary_table.csv").read_text(encoding="utf-8").splitlines()))
            self.assertEqual(
                list(primary_rows[0].keys()),
                [
                    "baseline_id",
                    "split",
                    "MAE_global",
                    "MAE_event_window",
                    "MAE_stable_window",
                    "delta_global_vs_behavior",
                    "delta_event_vs_behavior",
                    "delta_stable_vs_behavior",
                ],
            )
            decision = (out / "v5_plus_decision_summary.md").read_text(encoding="utf-8")
            self.assertIn("负数 delta 代表 primary baseline", decision)

    def test_stack_exp103_v5_predictions_writes_validation_stack_and_seed_ensemble(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            runs = []
            for seed in (42, 2026):
                run_dir = project / "outputs" / f"EXP-103-v5-plus-{seed}-5090"
                pred_dir = run_dir / "predictions_full"
                runs.append(run_dir)
                _write_full_prediction_fixture(
                    pred_dir / "validation_event_graph_dynamic_v5.csv.gz",
                    "event_graph_dynamic_v5",
                    seed,
                    "validation",
                    [10.0, 20.0, 30.0, 40.0],
                )
                _write_full_prediction_fixture(
                    pred_dir / "validation_event_dtw_fusion_graph_v5.csv.gz",
                    "event_dtw_fusion_graph_v5",
                    seed,
                    "validation",
                    [11.0, 19.0, 31.0, 39.0],
                )
                _write_full_prediction_fixture(
                    pred_dir / "test_event_graph_dynamic_v5.csv.gz",
                    "event_graph_dynamic_v5",
                    seed,
                    "test",
                    [10.2, 19.8, 30.2, 39.8],
                )
                _write_full_prediction_fixture(
                    pred_dir / "test_event_dtw_fusion_graph_v5.csv.gz",
                    "event_dtw_fusion_graph_v5",
                    seed,
                    "test",
                    [10.6, 19.4, 30.6, 39.4],
                )
            out = project / "outputs" / "EXP-103-v5-plus-stacking"

            result = subprocess.run(
                [
                    sys.executable,
                    str(STACK_EXP103_V5_PREDICTIONS),
                    "--runs",
                    *[str(run) for run in runs],
                    "--out",
                    str(out),
                    "--members",
                    "event_graph_dynamic_v5,event_dtw_fusion_graph_v5",
                    "--seed-ensemble-baselines",
                    "event_graph_dynamic_v5",
                    "--grid-step",
                    "0.5",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("wrote V5 Plus stacking outputs", result.stdout)
            for name in (
                "stacking_weights.csv",
                "stacking_metrics.csv",
                "stacking_test_predictions.csv.gz",
                "seed_ensemble_metrics.csv",
                "seed_ensemble_predictions.csv.gz",
            ):
                self.assertTrue((out / name).exists(), name)
            weight_rows = list(csv.DictReader((out / "stacking_weights.csv").read_text(encoding="utf-8").splitlines()))
            weights = {row["baseline_id"]: float(row["weight"]) for row in weight_rows}
            self.assertAlmostEqual(weights["event_graph_dynamic_v5"], 1.0)
            metrics = (out / "stacking_metrics.csv").read_text(encoding="utf-8")
            self.assertIn("v5_plus_validation_stack", metrics)
            seed_metrics = (out / "seed_ensemble_metrics.csv").read_text(encoding="utf-8")
            self.assertIn("event_graph_dynamic_v5_seed_ensemble", seed_metrics)

    def test_collect_exp103_results_builds_reproducible_ledger_without_touching_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            run_dir = project / "outputs" / "EXP-103-train-seed-42"
            run_dir.mkdir(parents=True)
            (run_dir / "baseline_metrics.csv").write_text(
                textwrap.dedent(
                    """\
                    baseline_id,MAE,RMSE,prediction_count,best_validation_loss,epochs_ran,uses_events,uses_graph
                    behavior_concat,0.023,0.31,100,0.032,8,True,False
                    event_graph_dynamic,0.022,0.30,100,0.031,9,True,True
                    dtw_demand_graph,0.021,0.29,100,0.030,7,True,True
                    """
                ),
                encoding="utf-8",
            )
            (run_dir / "graph_ablation_table.csv").write_text(
                textwrap.dedent(
                    """\
                    baseline_id,MAE,RMSE,delta_vs_behavior_concat,delta_vs_dtw_graph,graph_destruction_delta,conclusion_level
                    event_graph_dynamic,0.022,0.30,-0.001,0.001,0.002,training_smoke_or_formal_lite
                    """
                ),
                encoding="utf-8",
            )
            (run_dir / "manifest.json").write_text('{"hashes": {"baseline_metrics.csv": "abc"}}\n', encoding="utf-8")
            (run_dir / "config_resolved.json").write_text(
                json.dumps(
                    {
                        "seed": 42,
                        "graph": {"rho": 0.7, "lambda_event": 0.3},
                        "training": {"graph_mode": "gated_residual"},
                        "features": {"include_time_context": True, "include_enhanced_events": True},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            before = (run_dir / "baseline_metrics.csv").read_text(encoding="utf-8")
            out = project / "outputs" / "EXP-103-run-ledger.csv"
            summary_out = project / "outputs" / "EXP-103-run-summary.csv"
            optimization_out = project / "outputs" / "EXP-103-optimization-ledger.csv"

            result = subprocess.run(
                [
                    sys.executable,
                    str(COLLECT_EXP103_RESULTS),
                    "--outputs-root",
                    str(project / "outputs"),
                    "--out",
                    str(out),
                    "--summary-out",
                    str(summary_out),
                    "--optimization-out",
                    str(optimization_out),
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("wrote EXP-103 run ledger", result.stdout)
            self.assertEqual((run_dir / "baseline_metrics.csv").read_text(encoding="utf-8"), before)
            ledger = out.read_text(encoding="utf-8")
            self.assertIn("EXP-103-train-seed-42", ledger)
            self.assertIn("event_graph_dynamic", ledger)
            self.assertIn("delta_vs_behavior_concat", ledger)
            summary = summary_out.read_text(encoding="utf-8")
            optimization = optimization_out.read_text(encoding="utf-8")
            self.assertIn("MAE_mean", summary)
            self.assertIn("event_vs_behavior_delta", optimization)
            self.assertIn("event_vs_dtw_delta", optimization)
            self.assertIn("gated_residual", optimization)

    def test_new_experiment_appends_registry_row_without_experiment_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            registry = project / "docs" / "thesis" / "experiment-registry.md"
            registry.parent.mkdir(parents=True)
            registry.write_text(
                textwrap.dedent(
                    """\
                    # Experiment Registry

                    | Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes | Storage Backend | Remote Artifact URI | Remote Status | Artifact Hash / Manifest |
                    |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
                    | EXP-001 | Existing claim | baseline | dataset_v1 | `python baseline.py` | `outputs/EXP-001` | accuracy=0.8 | done | 2026-01-01 | existing | local_mac | TBD | not_applicable | outputs/EXP-001/manifest.json |
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
                    "--storage-backend",
                    "remote_desktop_4060",
                    "--remote-artifact-uri",
                    "ssh://desktop-4060/research-runs/EXP-001/",
                    "--remote-status",
                    "synced",
                    "--artifact-hash",
                    "outputs/latest/manifest.json",
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
            self.assertIn("remote_desktop_4060", registry_text)
            self.assertIn("ssh://desktop-4060/research-runs/EXP-001/", registry_text)
            self.assertIn("outputs/latest/manifest.json", registry_text)
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
                    | Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes | Storage Backend | Remote Artifact URI | Remote Status | Artifact Hash / Manifest |
                    |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
                    | EXP-001 | CLM-001 | configs/experiment/EXP-001.yaml | test | train | outputs/EXP-001 | accuracy | planned | TBD | remote_desktop_4060 | remote_desktop_4060 | ssh://desktop-4060/research-runs/EXP-001/ | verified | outputs/EXP-001/manifest.json |
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
                    "--require-remote-artifact",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Errors: 0", result.stdout)

    def test_check_experiment_contract_detects_missing_remote_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (project / "configs" / "experiment").mkdir(parents=True)
            (project / "configs" / "smoke").mkdir(parents=True)
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
                    | Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes | Storage Backend | Remote Artifact URI | Remote Status | Artifact Hash / Manifest |
                    |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
                    | EXP-001 | CLM-001 | configs/experiment/EXP-001.yaml | test | train | outputs/EXP-001 | accuracy | planned | TBD | remote_desktop_4060 | remote_desktop_4060 | TBD | pending | TBD |
                    """
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_CONTRACT),
                    "--experiment-id",
                    "EXP-001",
                    "--require-remote-artifact",
                    "--warn-only",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("remote artifact URI is required", result.stdout)

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
                "| Segment ID | Section ID | Segment / Claim Draft | Candidate Reference | DOI / PMID / arXiv / S2 ID | Support Grade | Source Status | Zotero Status | Scite / Reader Status | Export Format | Next Action | Search Source | Keywords / MeSH | Zotero Collection |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| SEG-001 | SEC-INTRO-001 | claim | Strong Paper | PMID:123456 | strong | source_read_verified | in_zotero | supports_claim | bibtex | cite | PubMed | MeSH: diagnosis | ZCOL-001 |\n",
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
            self.assertIn("doi/pmid", suggestions_md)
            self.assertIn("zotero-collection", suggestions_md)
            self.assertEqual("SEC-INTRO-001", suggestions_json["sectionId"])
            self.assertGreaterEqual(suggestions_json["suggestions"][0]["score"], 16)

    def test_init_research_workflow_includes_nature_quality_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            subprocess.run(
                [sys.executable, str(INIT_RESEARCH_WORKFLOW), "--project", str(project)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            for name in (
                "academic-search-policy.md",
                "figure-style-qa.md",
                "nature-style-writing-checklist.md",
                "project-scope-control.md",
            ):
                self.assertTrue((project / "docs" / "thesis" / name).exists(), name)

    def test_audit_project_scope_reports_pending_title_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "project-scope-control.md").write_text(
                "# Project Scope Control\n\n"
                "## Title Review Gates\n\n| Gate | Status |\n|---|---|\n| title-intake | pending |\n\n"
                "## Causal Availability Contract\n\n| Field | Status |\n|---|---|\n| future field | pending |\n\n"
                "## Graph / Structure Definition Gate\n\n| Item | Status |\n|---|---|\n| node | pending |\n\n"
                "## Downgrade / Rename Policy\n\n| Trigger | Status |\n|---|---|\n| weak graph | pending |\n\n"
                "## Promotion Rule\n\n| Phrase | Status |\n|---|---|\n| dynamic graph | pending |\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(AUDIT_PROJECT_SCOPE), "--warn-only"],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("project scope control still has pending", result.stdout)

    def test_sync_zotero_inventory_writes_hub_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            payload = {
                "items": [
                    {
                        "itemKey": "ABC123",
                        "bibtexKey": "smith2026method",
                        "title": "Important Method Paper",
                        "year": "2026",
                        "creators": ["Smith"],
                        "doi": "10.0000/method",
                        "collections": ["thesis/03_methods"],
                    }
                ]
            }
            source = project / "zotero.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SYNC_ZOTERO_INVENTORY), "--input-json", str(source)],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            hub = project / "docs" / "thesis" / "zotero-literature-hub.md"
            hub_text = hub.read_text(encoding="utf-8")
            self.assertIn("wrote Zotero inventory", result.stdout)
            self.assertIn("Important Method Paper", hub_text)
            self.assertIn("ABC123", hub_text)

    def test_audit_zotero_coverage_reports_section_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "zotero-literature-hub.md").write_text("# hub\n", encoding="utf-8")
            (thesis / "section-citation-map.md").write_text(
                "| Section ID | Thesis Location | Section Purpose | Required Literature Role | Coverage Status | Notes |\n"
                "|---|---|---|---|---|---|\n"
                "| SEC-INTRO-001 | Ch1 | background | foundational | partial | ready |\n\n"
                "| Segment ID | Section ID | Segment / Claim Draft | Candidate Reference | DOI / arXiv / S2 ID | Support Grade | Source Status | Zotero Status | Scite / Reader Status | Export Format | Next Action |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| SEG-001 | SEC-INTRO-001 | claim | Strong Paper | 10.0000/example | strong | metadata_verified | in_zotero | supports_claim | bibtex | cite |\n",
                encoding="utf-8",
            )
            (thesis / "citation-provenance.md").write_text(
                "| Citation ID | Section ID | Segment ID | Claim ID | Title | Identifier | Candidate Source | Metadata Status | Support Status | Zotero Status | Scite / Reader Evidence | Verified By | Verified On | Export Status | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n",
                encoding="utf-8",
            )
            (thesis / "zotero-collection-coverage.md").write_text(
                "| Section ID | Required Literature Roles | Zotero Collections | A-Core Papers | B-Section Papers | Verified Citation IDs | Gap | Status |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| SEC-INTRO-001 | foundational | ZCOL-001 | Strong Paper | TBD | CIT-001 | none | covered |\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(AUDIT_ZOTERO_COVERAGE), "--json"],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual([], payload["p1"])
            self.assertEqual(1, payload["details"]["sections"]["SEC-INTRO-001"]["strongVerified"])

    def test_export_zotero_bibliography_writes_verified_stub(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "citation-provenance.md").write_text(
                "| Citation ID | Section ID | Segment ID | Claim ID | Title | Identifier | Candidate Source | Metadata Status | Support Status | Zotero Status | Scite / Reader Evidence | Verified By | Verified On | Export Status | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| CIT-001 | SEC-INTRO-001 | SEG-001 | CLM-001 | Strong Paper | 10.0000/example | Zotero | metadata_verified | supports | in_zotero | reader | user | 2026-01-01 | bibtex | ready |\n"
                "| CIT-002 | SEC-INTRO-001 | SEG-002 | CLM-001 | Weak Paper | 10.0000/weak | Zotero | candidate | unchecked | not_added | TBD | user | TBD | bibtex | not ready |\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(EXPORT_ZOTERO_BIBLIOGRAPHY), "--allow-stub", "--out", "references.bib"],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            bib = (project / "references.bib").read_text(encoding="utf-8")
            self.assertIn("wrote bibliography stub", result.stdout)
            self.assertIn("@misc{CIT_001", bib)
            self.assertIn("Strong Paper", bib)
            self.assertNotIn("Weak Paper", bib)

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
            self.assertIn("metadata issues: 1", result.stdout)
            self.assertIn("broken references: 1", result.stdout)
            self.assertIn("missing scripts: 1", result.stdout)
            self.assertTrue((project / "docs" / "thesis" / "skill-audit-report.md").exists())

    def test_audit_skills_warns_on_unsupported_metadata_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            skill = project / "skills" / "demo-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: demo-skill\n"
                "description: Use when testing skill metadata policy.\n"
                "triggers: [demo]\n"
                "model: gpt-test\n"
                "---\n\n"
                "# Demo Skill\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(AUDIT_SKILLS), "--root", str(project)],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("metadata issues: 0", result.stdout)
            self.assertIn("metadata warnings: 2", result.stdout)
            self.assertIn("not part of the current default Codex skill metadata policy", result.stdout)

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
                "console-file-index.md",
                "daily-workflow-entry.md",
                "weekly-review.md",
                "project-scope-control.md",
                "evidence-promotion-policy.md",
                "id-lifecycle-policy.md",
                "material-passport.md",
                "section-citation-map.md",
                "citation-provenance.md",
                "zotero-screening-loop.md",
                "academic-search-policy.md",
                "benchmark-report-schema.md",
                "figure-plan.md",
                "figure-style-qa.md",
                "nature-style-writing-checklist.md",
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
            ):
                (thesis / name).write_text("# placeholder\n", encoding="utf-8")
            (thesis / "academic-search-policy.md").write_text(
                "# Academic Search Policy\n\n| Search ID | Section ID | Segment ID | Query | Source | Keywords / MeSH | Filters | Candidate Count | Useful Count | Next Action |\n"
                "|---|---|---|---|---|---|---|---:|---:|---|\n"
                "| SEARCH-001 | SEC-INTRO-001 | SEG-001 | accuracy method | Semantic Scholar | accuracy | year | 10 | 2 | complete |\n",
                encoding="utf-8",
            )
            (thesis / "figure-style-qa.md").write_text(
                "# Figure Style QA\n\n| Figure ID | Figure Role | Source Data / Script | Export Formats | Panel Hierarchy | Uncertainty / n | Caption Safety | Accessibility | Source Trace | QA Status | Required Fix |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| FIG-001 | support | DATA-001 | SVG/PDF | ready | visible | safe | pass | traceable | ready | none |\n",
                encoding="utf-8",
            )
            (thesis / "nature-style-writing-checklist.md").write_text(
                "# Nature-Style Writing Checklist\n\n| Section ID | Section | Gap / Reader Question | Evidence Source | Citation Coverage | Overclaim Risk | Writing Status | Required Fix |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| SEC-INTRO-001 | Introduction | clear gap | CLM-001; CIT-001 | covered | low | ready | none |\n",
                encoding="utf-8",
            )
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
            (thesis / "experiment-architecture.md").write_text(
                "# Experiment Architecture\n\n| Area | Decision | Status | Notes |\n|---|---|---|---|\n| Primary execution target | local_mac | planned | test |\n",
                encoding="utf-8",
            )
            (thesis / "project-scope-control.md").write_text(
                "# Project Scope Control\n\n"
                "## Title Review Gates\n\n| Gate | Status | Linked IDs |\n|---|---|---|\n| title-intake | ready | CLM-001 |\n\n"
                "## Causal Availability Contract\n\n| Field | Status | Linked IDs |\n|---|---|---|\n| historical target | ready | DATA-001 |\n\n"
                "## Graph / Structure Definition Gate\n\n| Item | Status | Linked IDs |\n|---|---|---|\n| node | ready | EXP-001 |\n\n"
                "## Downgrade / Rename Policy\n\n| Trigger | Status | Linked IDs |\n|---|---|---|\n| weak graph | ready | CLM-001 |\n\n"
                "## Promotion Rule\n\n| Phrase | Status | Linked IDs |\n|---|---|---|\n| title phrase | ready | CLM-001; EXP-001 |\n",
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
            (thesis / "section-citation-map.md").write_text(
                "| Section ID | Thesis Location | Section Purpose | Required Literature Role | Coverage Status | Notes |\n"
                "|---|---|---|---|---|---|\n"
                "| SEC-INTRO-001 | Ch1 | background | foundational | partial | ready |\n\n"
                "| Segment ID | Section ID | Segment / Claim Draft | Candidate Reference | DOI / arXiv / S2 ID | Support Grade | Source Status | Zotero Status | Scite / Reader Status | Export Format | Next Action |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| SEG-001 | SEC-INTRO-001 | claim | Strong Paper | 10.0000/example | strong | metadata_verified | in_zotero | supports_claim | bibtex | cite |\n",
                encoding="utf-8",
            )
            (thesis / "citation-provenance.md").write_text(
                "| Citation ID | Section ID | Segment ID | Claim ID | Title | Identifier | Candidate Source | Metadata Status | Support Status | Zotero Status | Scite / Reader Evidence | Verified By | Verified On | Export Status | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| CIT-001 | SEC-INTRO-001 | SEG-001 | CLM-001 | Strong Paper | 10.0000/example | Zotero | metadata_verified | supports | in_zotero | reader | user | 2026-01-01 | bibtex | ready |\n",
                encoding="utf-8",
            )
            (thesis / "zotero-literature-hub.md").write_text("# Zotero Literature Hub\n\nStrong Paper\n", encoding="utf-8")
            (thesis / "zotero-collection-coverage.md").write_text(
                "| Section ID | Required Literature Roles | Zotero Collections | A-Core Papers | B-Section Papers | Verified Citation IDs | Gap | Status |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| SEC-INTRO-001 | foundational | ZCOL-001 | Strong Paper | TBD | CIT-001 | none | covered |\n",
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
            self.assertIn(dashboard_json["health"], {"ok", "warning"})
            self.assertEqual([], dashboard_json["issues"]["p0"])
            self.assertEqual(1, dashboard_json["counts"]["claims"])
            self.assertIn("natureQualityGates", dashboard_json)
            self.assertIn("skillHealth", dashboard_json)
            self.assertIn("pluginRecommendations", dashboard_json)
            self.assertIn("pluginGateHealth", dashboard_json)
            self.assertIn("consoleFileLayers", dashboard_json)
            self.assertIn("weeklyReview", dashboard_json)
            self.assertIn("experimentComparisons", dashboard_json)
            segment_coverage = {
                item["segmentId"]: item
                for item in dashboard_json["sectionCitationCoverage"]
                if item.get("segmentId")
            }
            self.assertEqual("verified", segment_coverage["SEG-001"]["status"])
            self.assertEqual("verified", segment_coverage["SEG-001"]["strong"])
            self.assertNotIn("old", dashboard)

    def test_plugin_gate_advisor_recommends_stage_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "workflow-dashboard.md").write_text(
                "# Workflow Dashboard\n\n| Field | Value |\n|---|---|\n| Current stage | 5 Research code implementation |\n",
                encoding="utf-8",
            )
            (thesis / "plugin-gate-policy.md").write_text("# policy\n", encoding="utf-8")
            (thesis / "plugin-review-log.md").write_text(
                "| Review ID | Date | Stage | Plugin | Trigger | Required | Result | Record Path | Notes |\n"
                "|---|---|---|---|---|---|---|---|---|\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(PLUGIN_GATE_ADVISOR),
                    "--stage",
                    "5",
                    "--change-type",
                    "dashboard",
                    "--json",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            by_plugin = {item["plugin"]: item for item in payload["recommendations"]}
            self.assertEqual("pending_required", by_plugin["Codex Security"]["status"])
            self.assertEqual("pending_required", by_plugin["Build Web Apps"]["status"])
            self.assertEqual(2, payload["health"]["pendingRequiredGates"])

            stage7 = subprocess.run(
                [sys.executable, str(PLUGIN_GATE_ADVISOR), "--stage", "7", "--json"],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            stage7_payload = json.loads(stage7.stdout)
            self.assertIn("Data Analytics", {item["plugin"] for item in stage7_payload["recommendations"]})

            stage9 = subprocess.run(
                [sys.executable, str(PLUGIN_GATE_ADVISOR), "--stage", "9", "--json"],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            stage9_payload = json.loads(stage9.stdout)
            self.assertIn("Product Design", {item["plugin"] for item in stage9_payload["recommendations"]})

    def test_doctor_reports_missing_plugin_gate_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "workflow-dashboard.md").write_text(
                "# Workflow Dashboard\n\n| Field | Value |\n|---|---|\n| Current stage | 5 Research code implementation |\n| Active focus | dashboard api |\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(RESEARCH_WORKFLOW_DOCTOR), "--warn-only"],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("missing plugin gate policy", result.stdout)
            self.assertIn("missing plugin review log", result.stdout)

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
            self.assertIn("updated current workspace entry", result.stdout)
            self.assertIn("2 文献发现与综述", daily)
            self.assertIn("citation coverage", dashboard)
            self.assertIn("update current workspace", edit_log)

    def test_update_weekly_review_updates_summary_and_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            thesis = project / "docs" / "thesis"
            thesis.mkdir(parents=True)
            (thesis / "workflow-dashboard.md").write_text(
                "# Workflow Dashboard\n\n"
                "| Field | Value |\n"
                "|---|---|\n"
                "| Current stage | 2 文献发现与综述 |\n"
                "| Active focus | TBD |\n"
                "| Current audit tier | quick |\n"
                "| Main blocker | TBD |\n"
                "| Next concrete action | TBD |\n",
                encoding="utf-8",
            )
            (thesis / "workflow-edit-log.md").write_text(
                "| Timestamp | Action | Target | Generated ID | Summary |\n"
                "|---|---|---|---|---|\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(UPDATE_WEEKLY_REVIEW),
                    "--focus",
                    "citation precision",
                    "--completed",
                    "screened 5 papers",
                    "--evidence-stronger",
                    "SEC-INTRO-001",
                    "--evidence-risk",
                    "missing 4060 result",
                    "--best-experiment",
                    "EXP-001",
                    "--next-actions",
                    "confirm strong citations; generate EXP report",
                    "--files-to-ignore",
                    "final-audit.md",
                ],
                cwd=project,
                text=True,
                capture_output=True,
                check=True,
            )
            weekly = (thesis / "weekly-review.md").read_text(encoding="utf-8")
            dashboard = (thesis / "workflow-dashboard.md").read_text(encoding="utf-8")
            edit_log = (thesis / "workflow-edit-log.md").read_text(encoding="utf-8")
            self.assertIn("updated weekly review", result.stdout)
            self.assertIn("citation precision", weekly)
            self.assertIn("EXP-001", weekly)
            self.assertIn("confirm strong citations", dashboard)
            self.assertIn("update weekly review", edit_log)

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
            self.assertIn("not verified on Windows", result.stdout)

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

    def test_autodl_templates_preserve_autoshutdown_evidence_contract(self):
        run_template = (REPO_ROOT / "scripts" / "remote_run_autodl_autoshutdown.sh.template").read_text(
            encoding="utf-8"
        )
        sync_template = (REPO_ROOT / "scripts" / "remote_sync_to_autodl.sh.template").read_text(encoding="utf-8")
        fetch_template = (REPO_ROOT / "scripts" / "remote_fetch_autodl_results.sh.template").read_text(
            encoding="utf-8"
        )

        for required in (
            "AUTO_SHUTDOWN",
            "/usr/bin/shutdown",
            "exit_code.txt",
            "autodl_run_summary.json",
            "checksums.sha256",
            "cloud_autodl",
            "mkdir -p '${REMOTE_OUTPUT}'",
            "trap shutdown_if_requested EXIT",
            "sha256sum",
        ):
            self.assertIn(required, run_template)

        self.assertIn("autodl-gpu", sync_template)
        self.assertIn("remote_run_autodl_autoshutdown.sh.template", sync_template)
        self.assertIn("autodl-gpu", fetch_template)
        self.assertIn("Storage Backend: cloud_autodl", fetch_template)


if __name__ == "__main__":
    unittest.main()
