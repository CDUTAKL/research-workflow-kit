import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
import warnings
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class EvcsStage5Tests(unittest.TestCase):
    def test_load_experiment_config_reads_minimal_yaml_contract(self):
        from evcs.utils.config import load_experiment_config

        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "EXP-101.yaml"
            config_path.write_text(
                textwrap.dedent(
                    """\
                    experiment_id: EXP-101
                    seed: 42
                    split: chronological_70_15_15
                    metric: field_coverage
                    output: outputs/EXP-101
                    data:
                      source_path: data/raw/acn_sessions.csv
                      timestamp_field: connectionTime
                      node_candidates:
                        - stationID
                        - EVSEID
                    """
                ),
                encoding="utf-8",
            )

            config = load_experiment_config(config_path)

        self.assertEqual(config["experiment_id"], "EXP-101")
        self.assertEqual(config["seed"], 42)
        self.assertEqual(config["data"]["source_path"], "data/raw/acn_sessions.csv")
        self.assertEqual(config["data"]["node_candidates"], ["stationID", "EVSEID"])

    def test_audit_sessions_detects_fields_nodes_splits_and_leakage(self):
        from evcs.data.audit import audit_sessions

        df = pd.DataFrame(
            {
                "connectionTime": pd.to_datetime(
                    [
                        "2026-01-01 08:00",
                        "2026-01-01 09:00",
                        "2026-01-02 08:00",
                        "2026-01-03 08:00",
                        "2026-01-04 08:00",
                    ]
                ),
                "disconnectTime": pd.to_datetime(
                    [
                        "2026-01-01 10:00",
                        "2026-01-01 10:30",
                        "2026-01-02 09:00",
                        "2026-01-03 10:00",
                        "2026-01-04 09:30",
                    ]
                ),
                "doneChargingTime": pd.to_datetime(
                    [
                        "2026-01-01 09:30",
                        "2026-01-01 10:10",
                        "2026-01-02 08:45",
                        "2026-01-03 09:20",
                        "2026-01-04 09:00",
                    ]
                ),
                "kWhDelivered": [8.0, 5.0, 4.5, 6.5, 7.0],
                "stationID": ["A", "A", "B", "B", "B"],
                "sessionID": ["s1", "s2", "s3", "s4", "s5"],
            }
        )

        report = audit_sessions(
            df,
            required_fields=["connectionTime", "disconnectTime", "kWhDelivered", "spaceID"],
            blocked_feature_fields=["disconnectTime", "doneChargingTime", "kWhDelivered"],
            timestamp_field="connectionTime",
            node_candidates=["spaceID", "stationID"],
            split_rule={"train": 0.6, "validation": 0.2, "test": 0.2},
        )

        field_rows = {row["field"]: row for row in report.field_availability}
        self.assertTrue(field_rows["connectionTime"]["present"])
        self.assertFalse(field_rows["spaceID"]["present"])
        self.assertEqual(report.recommended_node_field, "stationID")
        self.assertEqual(report.split_manifest["counts"], {"train": 3, "validation": 1, "test": 1})
        self.assertIn("disconnectTime", report.leakage_flags["blocked_fields_present"])
        self.assertEqual(report.data_manifest["row_count"], 5)

    def test_exp101_cli_writes_machine_readable_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            src = project / "sessions.csv"
            src.write_text(
                textwrap.dedent(
                    """\
                    connectionTime,disconnectTime,doneChargingTime,kWhDelivered,stationID,sessionID
                    2026-01-01 08:00,2026-01-01 10:00,2026-01-01 09:30,8.0,A,s1
                    2026-01-01 09:00,2026-01-01 10:30,2026-01-01 10:10,5.0,A,s2
                    2026-01-02 08:00,2026-01-02 09:00,2026-01-02 08:45,4.5,B,s3
                    2026-01-03 08:00,2026-01-03 10:00,2026-01-03 09:20,6.5,B,s4
                    2026-01-04 08:00,2026-01-04 09:30,2026-01-04 09:00,7.0,B,s5
                    """
                ),
                encoding="utf-8",
            )
            config = project / "EXP-101.yaml"
            out = project / "outputs" / "EXP-101"
            config.write_text(
                textwrap.dedent(
                    f"""\
                    experiment_id: EXP-101
                    seed: 42
                    split: chronological_70_15_15
                    metric: field_coverage
                    output: {out}
                    data:
                      source_path: {src}
                      timestamp_field: connectionTime
                      required_fields:
                        - connectionTime
                        - disconnectTime
                        - doneChargingTime
                        - kWhDelivered
                        - stationID
                      node_candidates:
                        - spaceID
                        - stationID
                      blocked_feature_fields:
                        - disconnectTime
                        - doneChargingTime
                        - kWhDelivered
                      split_rule:
                        train: 0.6
                        validation: 0.2
                        test: 0.2
                    """
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "src" / "data" / "audit_evcs_data.py"),
                    "--config",
                    str(config),
                    "--out",
                    str(out),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("wrote EXP-101 audit outputs", result.stdout)
            for name in (
                "field_availability.csv",
                "node_stability.csv",
                "split_manifest.json",
                "leakage_flags.json",
                "data_manifest.json",
                "config_resolved.json",
                "manifest.json",
                "logs/audit.log",
            ):
                self.assertTrue((out / name).exists(), name)

            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["experiment_id"], "EXP-101")
            self.assertIn("field_availability.csv", manifest["artifacts"])

    def test_normalize_acn_sessions_accepts_api_style_records(self):
        from evcs.data.acn import normalize_acn_sessions

        records = [
            {
                "_id": "5bc90cb9f9af8b0d7fe77cd2",
                "connectionTime": "2019-01-01T08:00:00-08:00",
                "disconnectTime": "2019-01-01T10:00:00-08:00",
                "doneChargingTime": "2019-01-01T09:30:00-08:00",
                "kWhDelivered": 8.0,
                "stationID": "CA-301",
                "EVSEID": "CA-301-1",
                "spaceID": "CA-301",
                "siteID": "caltech",
                "userInputs": [{"WhPerMile": 250}],
            }
        ]

        sessions = normalize_acn_sessions(records, site="caltech")

        self.assertEqual(list(sessions["sessionID"]), ["5bc90cb9f9af8b0d7fe77cd2"])
        self.assertEqual(list(sessions["stationID"]), ["CA-301"])
        self.assertEqual(list(sessions["siteID"]), ["caltech"])
        self.assertEqual(float(sessions.loc[0, "kWhDelivered"]), 8.0)
        self.assertIn("has_time_series", sessions.columns)
        self.assertFalse(bool(sessions.loc[0, "has_time_series"]))

    def test_build_time_slices_reconstructs_load_from_sessions(self):
        from evcs.data.timeslice import build_time_slices

        sessions = pd.DataFrame(
            {
                "sessionID": ["s1", "s2"],
                "connectionTime": ["2026-01-01 08:00", "2026-01-01 08:15"],
                "disconnectTime": ["2026-01-01 08:45", "2026-01-01 08:45"],
                "doneChargingTime": ["2026-01-01 08:30", "2026-01-01 08:40"],
                "kWhDelivered": [3.0, 2.0],
                "stationID": ["A", "A"],
            }
        )

        timeslice, manifest = build_time_slices(sessions, node_field="stationID", freq="15min")

        rows = timeslice.set_index("timestamp").to_dict("index")
        self.assertEqual(manifest["load_reconstruction"], "uniform_session_energy")
        self.assertEqual(manifest["source_has_time_series"], False)
        self.assertAlmostEqual(rows[pd.Timestamp("2026-01-01 08:00:00")]["load"], 1.0)
        self.assertAlmostEqual(rows[pd.Timestamp("2026-01-01 08:15:00")]["load"], 2.0)
        self.assertAlmostEqual(rows[pd.Timestamp("2026-01-01 08:30:00")]["load"], 2.0)
        self.assertEqual(rows[pd.Timestamp("2026-01-01 08:15:00")]["access_count"], 1)
        self.assertEqual(rows[pd.Timestamp("2026-01-01 08:45:00")]["departure_count"], 2)
        self.assertEqual(rows[pd.Timestamp("2026-01-01 08:30:00")]["active_count"], 2)

    def test_prepare_timeslices_cli_writes_processed_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            source = project / "sessions.csv"
            out = project / "evcs_timeslice.csv"
            manifest = project / "evcs_timeslice_manifest.json"
            source.write_text(
                textwrap.dedent(
                    """\
                    sessionID,connectionTime,disconnectTime,doneChargingTime,kWhDelivered,stationID
                    s1,2026-01-01 08:00,2026-01-01 08:45,2026-01-01 08:30,3.0,A
                    s2,2026-01-01 08:15,2026-01-01 08:45,2026-01-01 08:40,2.0,A
                    """
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "src" / "data" / "prepare_evcs_timeslices.py"),
                    "--input",
                    str(source),
                    "--out",
                    str(out),
                    "--manifest",
                    str(manifest),
                    "--node-field",
                    "stationID",
                    "--time-granularity",
                    "15min",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("wrote EVCS time-slice data", result.stdout)
            processed = pd.read_csv(out)
            self.assertEqual(
                list(processed.columns),
                [
                    "timestamp",
                    "node_id",
                    "load",
                    "access_count",
                    "departure_count",
                    "active_count",
                    "occupancy_rate",
                    "demand_intensity",
                    "load_jump_flag",
                ],
            )
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["node_field"], "stationID")
            self.assertEqual(payload["load_unit"], "kWh_per_time_slice")

    def test_forecast_metrics_cover_point_and_interval_contracts(self):
        from evcs.metrics.forecast import mean_absolute_error, picp, pinaw, root_mean_squared_error, wis

        y_true = [10.0, 20.0, 30.0]
        y_pred = [12.0, 18.0, 33.0]
        lower = [8.0, 19.0, 28.0]
        upper = [14.0, 22.0, 29.0]

        self.assertAlmostEqual(mean_absolute_error(y_true, y_pred), 7.0 / 3.0)
        self.assertAlmostEqual(root_mean_squared_error(y_true, y_pred), (17.0 / 3.0) ** 0.5)
        self.assertAlmostEqual(picp(y_true, lower, upper), 2.0 / 3.0)
        self.assertAlmostEqual(pinaw(y_true, lower, upper), (10.0 / 3.0) / 20.0)
        self.assertGreater(wis(y_true, lower, upper, alpha=0.2), 0.0)

    def test_event_adjacency_uses_topk_row_normalized_similarity(self):
        from evcs.graphs.event_graph import build_event_adjacency

        events = pd.DataFrame(
            {
                "node_id": ["A", "B", "C"],
                "access_count": [1.0, 0.9, 0.0],
                "departure_count": [0.0, 0.1, 1.0],
            }
        )

        graph = build_event_adjacency(events, node_field="node_id", feature_fields=["access_count", "departure_count"], top_k=1)

        self.assertEqual(graph.nodes, ["A", "B", "C"])
        self.assertEqual(graph.adjacency.shape, (3, 3))
        self.assertAlmostEqual(float(graph.adjacency[0].sum()), 1.0)
        self.assertEqual(graph.top_edges[0]["source"], "A")
        self.assertEqual(graph.top_edges[0]["target"], "B")

    def test_exp103_graph_ablation_runner_writes_smoke_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            out = project / "outputs" / "EXP-103-smoke"
            config = project / "EXP-103-smoke.yaml"
            config.write_text(
                textwrap.dedent(
                    f"""\
                    experiment_id: EXP-103
                    seed: 42
                    output: {out}
                    data:
                      source_path: tests/fixtures/evcs_timeslice_smoke.csv
                      timestamp_field: timestamp
                      node_field: node_id
                      target_field: load
                    graph:
                      event_feature_fields:
                        - access_count
                        - departure_count
                        - active_count
                        - occupancy_rate
                        - demand_intensity
                        - load_jump_flag
                      top_k: 1
                    baselines:
                      - dtw_demand_graph
                      - random_event_graph
                      - shuffled_event_graph
                    """
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "src" / "training" / "run_graph_ablation.py"),
                    "--config",
                    str(config),
                    "--out",
                    str(out),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("wrote EXP-103 graph ablation smoke outputs", result.stdout)
            table = pd.read_csv(out / "graph_ablation_table.csv")
            self.assertEqual(
                set(table["baseline_id"]),
                {"event_graph", "dtw_demand_graph", "random_event_graph", "shuffled_event_graph"},
            )
            manifest = json.loads((out / "graph_manifest.json").read_text(encoding="utf-8"))
            self.assertIn("dtw_demand_graph", manifest["graphs"])
            self.assertTrue((out / "manifest.json").exists())

    def test_exp103_tensor_cache_builds_origin_splits_without_overlap(self):
        from evcs.data.tensor_cache import build_tensor_cache, save_tensor_cache

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            source = project / "timeslice.csv"
            _write_training_timeslice_fixture(source, periods=10, nodes=("A", "B", "C"))
            frame = pd.read_csv(source)

            cache = build_tensor_cache(
                frame,
                timestamp_field="timestamp",
                node_field="node_id",
                target_field="load",
                event_feature_fields=["access_count", "departure_count", "active_count", "occupancy_rate"],
                history_steps=3,
                horizon_steps=2,
                split_rule={"train": 0.5, "validation": 0.25, "test": 0.25},
            )
            npz_path = project / "evcs_tensor_cache.npz"
            split_path = project / "splits" / "chronological_70_15_15.json"
            manifest_path = project / "evcs_tensor_cache_manifest.json"
            save_tensor_cache(cache, npz_path, split_path, manifest_path)

            saved = json.loads(split_path.read_text(encoding="utf-8"))
            all_origins = saved["train"] + saved["validation"] + saved["test"]
            self.assertEqual(cache.load.shape, (10, 3))
            self.assertEqual(cache.event_features.shape, (10, 3, 4))
            self.assertEqual(min(all_origins), 2)
            self.assertEqual(max(all_origins), 7)
            self.assertEqual(len(all_origins), len(set(all_origins)))
            self.assertTrue(npz_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["normalization"], "train_only")
            self.assertEqual(manifest["history_steps"], 3)
            self.assertEqual(manifest["horizon_steps"], 2)

    def test_exp103_tensor_cache_adds_time_context_and_enhanced_event_features(self):
        from evcs.data.tensor_cache import build_tensor_cache

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "timeslice.csv"
            _write_training_timeslice_fixture(source, periods=18, nodes=("A", "B", "C"))

            cache = build_tensor_cache(
                pd.read_csv(source),
                timestamp_field="timestamp",
                node_field="node_id",
                target_field="load",
                event_feature_fields=[
                    "access_count",
                    "departure_count",
                    "active_count",
                    "occupancy_rate",
                    "demand_intensity",
                    "load_jump_flag",
                ],
                history_steps=4,
                horizon_steps=2,
                split_rule={"train": 0.5, "validation": 0.25, "test": 0.25},
                include_time_context=True,
                include_enhanced_events=True,
            )

        feature_names = set(cache.event_feature_names)
        self.assertIn("hour_sin", feature_names)
        self.assertIn("dow_cos", feature_names)
        self.assertIn("weekend_flag", feature_names)
        self.assertIn("access_count_roll_1h", feature_names)
        self.assertIn("active_count_diff", feature_names)
        self.assertIn("near_capacity_history_rate_24h", feature_names)
        self.assertEqual(cache.event_features.shape[-1], len(cache.event_feature_names))
        self.assertTrue(cache.manifest["feature_engineering"]["include_time_context"])
        self.assertTrue(cache.manifest["feature_engineering"]["include_enhanced_events"])
        self.assertEqual(cache.manifest["feature_engineering"]["near_capacity_threshold_source"], "train_only")

    def test_exp103_graph_cache_keeps_train_only_static_graphs_and_dynamic_origin_graphs(self):
        from evcs.data.tensor_cache import build_tensor_cache
        from evcs.graphs.cache import build_exp103_graph_cache

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "timeslice.csv"
            _write_training_timeslice_fixture(source, periods=9, nodes=("A", "B", "C"))
            cache = build_tensor_cache(
                pd.read_csv(source),
                timestamp_field="timestamp",
                node_field="node_id",
                target_field="load",
                event_feature_fields=["access_count", "departure_count", "active_count", "occupancy_rate"],
                history_steps=3,
                horizon_steps=1,
                split_rule={"train": 0.5, "validation": 0.25, "test": 0.25},
            )

            graphs = build_exp103_graph_cache(
                cache,
                baseline_ids=["event_graph_dynamic", "dtw_demand_graph", "historical_correlation_graph", "deleted_event_graph"],
                top_k=1,
                seed=42,
            )

            train_end = max(cache.split_indices["train"])
            self.assertEqual(graphs["event_graph_dynamic"].indices.shape, (len(cache.origin_indices), 3, 1))
            self.assertEqual(graphs["event_graph_dynamic"].weights.shape, (len(cache.origin_indices), 3, 1))
            self.assertEqual(graphs["dtw_demand_graph"].train_origin_end, train_end)
            self.assertEqual(graphs["historical_correlation_graph"].train_origin_end, train_end)
            self.assertTrue((graphs["deleted_event_graph"].weights == 0.0).all())

    def test_exp103_graph_cache_supports_rho_smoothing_and_event_dtw_fusion(self):
        from evcs.data.tensor_cache import build_tensor_cache
        from evcs.graphs.cache import build_exp103_graph_cache

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "timeslice.csv"
            _write_training_timeslice_fixture(source, periods=12, nodes=("A", "B", "C"))
            cache = build_tensor_cache(
                pd.read_csv(source),
                timestamp_field="timestamp",
                node_field="node_id",
                target_field="load",
                event_feature_fields=["access_count", "departure_count", "active_count", "occupancy_rate"],
                history_steps=3,
                horizon_steps=1,
                split_rule={"train": 0.5, "validation": 0.25, "test": 0.25},
            )

            raw_graphs = build_exp103_graph_cache(
                cache,
                baseline_ids=["event_graph_dynamic", "event_graph_dynamic_rho", "dtw_demand_graph", "event_dtw_fusion_graph"],
                top_k=1,
                seed=42,
                rho=0.0,
                lambda_event=1.0,
            )
            dtw_only_graphs = build_exp103_graph_cache(
                cache,
                baseline_ids=["dtw_demand_graph", "event_dtw_fusion_graph"],
                top_k=1,
                seed=42,
                rho=0.7,
                lambda_event=0.0,
            )

        self.assertTrue((raw_graphs["event_graph_dynamic"].indices == raw_graphs["event_graph_dynamic_rho"].indices).all())
        self.assertTrue((raw_graphs["event_graph_dynamic"].weights == raw_graphs["event_graph_dynamic_rho"].weights).all())
        self.assertTrue((raw_graphs["event_graph_dynamic_rho"].indices == raw_graphs["event_dtw_fusion_graph"].indices).all())
        self.assertTrue((raw_graphs["event_graph_dynamic_rho"].weights == raw_graphs["event_dtw_fusion_graph"].weights).all())
        self.assertTrue((dtw_only_graphs["dtw_demand_graph"].indices == dtw_only_graphs["event_dtw_fusion_graph"].indices).all())
        self.assertTrue((dtw_only_graphs["dtw_demand_graph"].weights == dtw_only_graphs["event_dtw_fusion_graph"].weights).all())
        self.assertAlmostEqual(float(raw_graphs["event_dtw_fusion_graph"].weights.sum(axis=-1).mean()), 1.0)

    def test_exp103_historical_correlation_graph_handles_constant_nodes_without_warning(self):
        from evcs.data.tensor_cache import build_tensor_cache
        from evcs.graphs.cache import build_exp103_graph_cache

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "timeslice.csv"
            _write_training_timeslice_fixture(source, periods=9, nodes=("A", "B", "C"))
            frame = pd.read_csv(source)
            frame["load"] = 1.0
            cache = build_tensor_cache(
                frame,
                timestamp_field="timestamp",
                node_field="node_id",
                target_field="load",
                event_feature_fields=["access_count", "departure_count", "active_count", "occupancy_rate"],
                history_steps=3,
                horizon_steps=1,
                split_rule={"train": 0.5, "validation": 0.25, "test": 0.25},
            )

            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always")
                graphs = build_exp103_graph_cache(
                    cache,
                    baseline_ids=["historical_correlation_graph"],
                    top_k=1,
                    seed=42,
                )

            self.assertEqual(captured, [])
            self.assertFalse(pd.isna(graphs["historical_correlation_graph"].weights).any())

    def test_exp103_primary_metric_summary_ranks_baselines_and_deltas(self):
        from training.train_exp103 import build_primary_metric_summary

        baseline_rows = [
            {"baseline_id": "behavior_concat", "MAE": 0.23, "RMSE": 0.4, "epochs_ran": 8},
            {"baseline_id": "event_graph_dynamic", "MAE": 0.21, "RMSE": 0.39, "epochs_ran": 6},
            {"baseline_id": "dtw_demand_graph", "MAE": 0.20, "RMSE": 0.38, "epochs_ran": 7},
        ]

        summary = build_primary_metric_summary(baseline_rows)

        self.assertEqual(list(summary["baseline_id"]), ["dtw_demand_graph", "event_graph_dynamic", "behavior_concat"])
        event_row = summary.set_index("baseline_id").loc["event_graph_dynamic"]
        self.assertAlmostEqual(float(event_row["delta_vs_behavior_concat"]), -0.02)
        self.assertAlmostEqual(float(event_row["delta_vs_dtw_graph"]), 0.01)
        self.assertEqual(bool(event_row["is_best_mae"]), False)

    def test_exp103_progress_helpers_render_terminal_line_and_dashboard(self):
        from training.train_exp103 import _format_epoch_progress, _write_training_dashboard

        curve_rows = [
            {
                "baseline_id": "event_graph_dynamic",
                "epoch": 1,
                "train_loss": 0.5,
                "validation_loss": 0.4,
                "best_validation_loss": 0.4,
                "improved": True,
                "epoch_seconds": 1.2,
                "lr": 0.001,
            },
            {
                "baseline_id": "event_graph_dynamic",
                "epoch": 2,
                "train_loss": 0.4,
                "validation_loss": 0.35,
                "best_validation_loss": 0.35,
                "improved": True,
                "epoch_seconds": 1.1,
                "lr": 0.001,
            },
        ]

        line = _format_epoch_progress(
            "event_graph_dynamic",
            2,
            10,
            0.4,
            0.35,
            0.35,
            0.001,
            1.1,
            curve_rows,
            improved=True,
        )
        self.assertIn("[####", line)
        self.assertIn("val:", line)
        with tempfile.TemporaryDirectory() as tmp:
            dashboard = Path(tmp) / "training_dashboard.html"
            _write_training_dashboard(
                dashboard,
                curve_rows,
                [{"baseline_id": "event_graph_dynamic", "MAE": 0.02, "RMSE": 0.03, "best_epoch": 2}],
                ["event_graph_dynamic", "dtw_demand_graph"],
                active_baseline="event_graph_dynamic",
                refresh_seconds=5,
            )
            html = dashboard.read_text(encoding="utf-8")

        self.assertIn("EXP-103 Training Dashboard", html)
        self.assertIn("event_graph_dynamic", html)
        self.assertIn("polyline", html)

    def test_exp103_graph_temporal_tcn_forward_contract_when_torch_available(self):
        torch = _maybe_import_torch()
        if torch is None:
            self.skipTest("PyTorch is not installed in the local smoke environment")
        from evcs.models.graph_tcn import GraphTemporalTCN

        model = GraphTemporalTCN(
            load_channels=1,
            event_channels=3,
            hidden_channels=8,
            tcn_layers=2,
            kernel_size=3,
            dropout=0.0,
            horizon_steps=2,
            use_events=True,
            use_graph=True,
        )
        history_load = torch.ones(4, 5, 3)
        history_events = torch.ones(4, 5, 3, 3)
        graph_indices = torch.tensor([[[1], [2], [0]]] * 4)
        graph_weights = torch.ones(4, 3, 1)

        prediction = model(history_load, history_events, graph_indices, graph_weights)

        self.assertEqual(tuple(prediction.shape), (4, 2, 3))

    def test_exp103_graph_temporal_tcn_gated_residual_forward_contract_when_torch_available(self):
        torch = _maybe_import_torch()
        if torch is None:
            self.skipTest("PyTorch is not installed in the local smoke environment")
        from evcs.models.graph_tcn import GraphTemporalTCN

        model = GraphTemporalTCN(
            load_channels=1,
            event_channels=3,
            hidden_channels=8,
            tcn_layers=2,
            kernel_size=3,
            dropout=0.0,
            horizon_steps=2,
            use_events=True,
            use_graph=True,
            graph_mode="gated_residual",
        )
        history_load = torch.ones(4, 5, 3)
        history_events = torch.ones(4, 5, 3, 3)
        graph_indices = torch.tensor([[[1], [2], [0]]] * 4)
        graph_weights = torch.ones(4, 3, 1)

        prediction = model(history_load, history_events, graph_indices, graph_weights)

        self.assertEqual(tuple(prediction.shape), (4, 2, 3))
        self.assertIsNotNone(model.last_gate)
        self.assertGreaterEqual(float(model.last_gate.min()), 0.0)
        self.assertLessEqual(float(model.last_gate.max()), 1.0)

    def test_exp103_train_runner_writes_smoke_artifacts_when_torch_available(self):
        if _maybe_import_torch() is None:
            self.skipTest("PyTorch is not installed in the local smoke environment")

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            source = project / "timeslice.csv"
            out = project / "outputs" / "EXP-103-train-smoke"
            cache_dir = project / "cache"
            _write_training_timeslice_fixture(source, periods=12, nodes=("A", "B", "C"))
            config = project / "EXP-103-train-smoke.yaml"
            config.write_text(
                textwrap.dedent(
                    f"""\
                    experiment_id: EXP-103
                    seed: 42
                    output: {out}
                    data:
                      source_path: {source}
                      timestamp_field: timestamp
                      node_field: node_id
                      target_field: load
                    cache:
                      tensor_cache_path: {cache_dir / "evcs_tensor_cache.npz"}
                      split_path: {cache_dir / "chronological_70_15_15.json"}
                      manifest_path: {cache_dir / "evcs_tensor_cache_manifest.json"}
                      history_steps: 3
                      horizon_steps: 1
                      split_rule: {{'train': 0.5, 'validation': 0.25, 'test': 0.25}}
                      auto_build: true
                    graph:
                      event_feature_fields:
                        - access_count
                        - departure_count
                        - active_count
                        - occupancy_rate
                      top_k: 1
                    training:
                      epochs: 1
                      batch_size: 2
                      hidden_channels: 8
                      tcn_layers: 1
                      kernel_size: 3
                      dropout: 0.0
                      lr: 0.001
                      num_workers: 0
                      amp: false
                      max_train_batches: 2
                      max_eval_batches: 2
                    baselines:
                      - no_graph
                      - behavior_concat
                      - event_graph_dynamic
                    """
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "src" / "training" / "train_exp103.py"),
                    "--config",
                    str(config),
                    "--out",
                    str(out),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("wrote EXP-103 training outputs", result.stdout)
            self.assertIn("[no_graph] epoch 1/1", result.stdout)
            for name in (
                "metrics.json",
                "baseline_metrics.csv",
                "graph_ablation_table.csv",
                "event_window_metrics.csv",
                "training_curves.csv",
                "predictions_sample.csv",
                "graph_manifest.json",
                "manifest.json",
                "logs/train.log",
            ):
                self.assertTrue((out / name).exists(), name)
            log_text = (out / "logs" / "train.log").read_text(encoding="utf-8")
            self.assertIn("[event_graph_dynamic] epoch 1/1", log_text)

    def test_exp102_baseline_runner_writes_metrics_predictions_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            series = project / "series.csv"
            series.write_text(
                textwrap.dedent(
                    """\
                    timestamp,node_id,load,access_count
                    2026-01-01 08:00,A,10.0,1
                    2026-01-01 09:00,A,12.0,1
                    2026-01-01 10:00,A,11.0,0
                    2026-01-01 08:00,B,20.0,0
                    2026-01-01 09:00,B,18.0,1
                    2026-01-01 10:00,B,21.0,0
                    """
                ),
                encoding="utf-8",
            )
            out = project / "outputs" / "EXP-102"
            config = project / "EXP-102.yaml"
            config.write_text(
                textwrap.dedent(
                    f"""\
                    experiment_id: EXP-102
                    seed: 42
                    split: chronological_70_15_15
                    metric: MAE
                    output: {out}
                    data:
                      source_path: {series}
                      timestamp_field: timestamp
                      node_field: node_id
                      target_field: load
                    model:
                      baseline_id: persistence
                    """
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "src" / "training" / "run_evcs_forecast.py"),
                    "--config",
                    str(config),
                    "--out",
                    str(out),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn("wrote EXP-102 forecast outputs", result.stdout)
            for name in ("metrics.json", "predictions.csv", "config_resolved.json", "manifest.json", "logs/run.log"):
                self.assertTrue((out / name).exists(), name)
            metrics = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics["baseline_id"], "persistence")
            self.assertIn("MAE", metrics)


def _maybe_import_torch():
    try:
        import torch  # type: ignore[import-not-found]
    except Exception:
        return None
    return torch


def _write_training_timeslice_fixture(path: Path, periods: int, nodes: tuple[str, ...]) -> None:
    rows = ["timestamp,node_id,load,access_count,departure_count,active_count,occupancy_rate,demand_intensity,load_jump_flag"]
    start = pd.Timestamp("2026-01-01 00:00:00")
    for step in range(periods):
        timestamp = start + pd.Timedelta(minutes=15 * step)
        for node_index, node in enumerate(nodes):
            load = float(10 + node_index * 3 + step)
            access = 1 if step % 4 == node_index % 4 else 0
            departure = 1 if step % 5 == node_index % 5 else 0
            active = 1 + ((step + node_index) % 3)
            occupancy = active / 3.0
            rows.append(
                f"{timestamp},{node},{load},{access},{departure},{active},{occupancy},{load},{1 if step % 3 == 0 else 0}"
            )
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
