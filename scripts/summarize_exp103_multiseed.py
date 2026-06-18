from __future__ import annotations

"""汇总 EXP-103 多 seed 证据表。

这个脚本只读取每个正式 run 目录中的机器可读 CSV，不重新计算预测结果。
它的职责有三层：

1. 把多个 seed 的同名表拼成 `*_all_seeds.csv`，保留 run_dir 和 seed 来源，方便追溯。
2. 对数值列按 baseline / comparator / event window 等主键聚合出 mean/std/min/max。
3. 额外计算 `seed_count` 和主指标获胜次数，供论文表格判断跨 seed 稳定性。

注意：EXP-103 的 run 目录命名迭代过多次，例如
`EXP-103-v5-42-5090` 和 `EXP-103-v5-final-full-42-5090` 都是合法形式。
因此 seed 解析必须从目录名里找“夹在连字符之间的整数”，而不能只匹配早期短格式。
"""

import argparse
import re
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError


TABLES = [
    "primary_metric_summary.csv",
    "baseline_deltas.csv",
    "event_window_metrics.csv",
    "graph_gate_metrics.csv",
    "residual_diagnostics.csv",
    "event_loss_diagnostics.csv",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize EXP-103 multi-seed evidence tables.")
    parser.add_argument("--runs", nargs="+", required=True, help="Run output directories.")
    parser.add_argument("--out", required=True, help="Output summary directory.")
    args = parser.parse_args()

    run_dirs = [Path(path) for path in args.runs]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    for table_name in TABLES:
        frame = _load_table(run_dirs, table_name)
        stem = table_name.removesuffix(".csv")
        frame.to_csv(out_dir / f"{stem}_all_seeds.csv", index=False)
        summary = _summarize_table(stem, frame)
        summary.to_csv(out_dir / f"{stem}_multiseed.csv", index=False)


def _load_table(run_dirs: list[Path], table_name: str) -> pd.DataFrame:
    frames = []
    for run_dir in run_dirs:
        table_path = run_dir / table_name
        if not table_path.exists():
            continue
        try:
            frame = pd.read_csv(table_path)
        except EmptyDataError:
            # 部分诊断表只在对应模型启用时才会有内容；空文件应被视为“无该诊断数据”。
            continue
        if frame.empty:
            continue
        frame.insert(0, "seed", _seed_from_run_dir(run_dir))
        frame.insert(1, "run_dir", str(run_dir))
        frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _seed_from_run_dir(run_dir: Path) -> int:
    """从 run 目录名中解析 seed。

    旧格式：`EXP-103-v5-42-5090`
    新格式：`EXP-103-v5-final-full-3407-5090`

    GPU 型号、日期片段和版本号也可能是数字，所以这里优先寻找项目固定使用的
    seed 集合；若未来新增 seed，再退化为“倒数第二个数字片段”，因为目录末尾通常是
    GPU 型号（如 5090）。
    """

    numeric_tokens = [int(token) for token in re.findall(r"(?<=-)(\d+)(?=-|$)", run_dir.name)]
    known_seed_tokens = [token for token in numeric_tokens if token in {42, 2026, 3407, 5151, 7777}]
    if known_seed_tokens:
        return known_seed_tokens[-1]
    if len(numeric_tokens) >= 2:
        return numeric_tokens[-2]
    if numeric_tokens:
        return numeric_tokens[-1]
    return -1


def _summarize_table(stem: str, frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    if stem == "primary_metric_summary":
        return _aggregate_numeric(frame, ["baseline_id"], add_win_counts=True)
    if stem == "baseline_deltas":
        summary = _aggregate_numeric(frame, ["baseline_id", "comparator_baseline", "metric"])
        if "delta" in frame.columns:
            wins = (
                frame.assign(win=lambda rows: rows["delta"] < 0)
                .groupby(["baseline_id", "comparator_baseline", "metric"], dropna=False)["win"]
                .sum()
                .reset_index(name="negative_delta_seed_count")
            )
            summary = summary.merge(wins, on=["baseline_id", "comparator_baseline", "metric"], how="left")
        return summary
    if stem == "event_window_metrics":
        return _aggregate_numeric(frame, ["baseline_id", "event_window"])
    if stem == "graph_gate_metrics":
        return _aggregate_numeric(frame, ["baseline_id", "gate_scope"])
    if stem == "residual_diagnostics":
        return _aggregate_numeric(frame, ["baseline_id"])
    if stem == "event_loss_diagnostics":
        return _aggregate_numeric(frame, ["baseline_id", "component"])
    return _aggregate_numeric(frame, ["baseline_id"]) if "baseline_id" in frame.columns else frame


def _aggregate_numeric(frame: pd.DataFrame, group_columns: list[str], add_win_counts: bool = False) -> pd.DataFrame:
    numeric_columns = [
        column
        for column in frame.select_dtypes(include="number").columns
        if column not in {"seed"} and column not in group_columns
    ]
    aggregations = {column: ["mean", "std", "min", "max"] for column in numeric_columns}
    grouped = frame.groupby(group_columns, dropna=False).agg(aggregations)
    grouped.columns = [f"{column}_{stat}" for column, stat in grouped.columns]
    result = grouped.reset_index()
    seed_counts = frame.groupby(group_columns, dropna=False)["seed"].nunique().reset_index(name="seed_count")
    result = result.merge(seed_counts, on=group_columns, how="left")
    if add_win_counts and "MAE" in frame.columns:
        winners = frame.loc[frame.groupby("seed")["MAE"].idxmin(), ["seed", "baseline_id"]].copy()
        wins = winners.groupby("baseline_id").size().reset_index(name="best_mae_seed_count")
        result = result.merge(wins, on="baseline_id", how="left")
        result["best_mae_seed_count"] = result["best_mae_seed_count"].fillna(0).astype(int)
    return result


if __name__ == "__main__":
    main()
