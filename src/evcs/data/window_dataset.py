from __future__ import annotations

"""EXP-103 滑动窗口 Dataset。

`EVCSTensorCache` 保存完整时间序列、节点顺序、事件特征和 split 索引；
本 Dataset 只负责把某个 split 的 prediction origins 切成模型可训练的 batch。

核心张量约定：

- `history_load`: `[history, node]`
- `history_events`: `[history, node, event_channel]`
- `target`: `[horizon, node]`
- `graph_indices/graph_weights`: `[node, top_k]`
- `event_context`: `[node, context_channel]`

训练时 `target` 可以被标准化；评估时同时返回 `target_raw`、`target_center`、
`target_scale`，让训练脚本能把预测还原到真实负载尺度后计算 MAE/RMSE。
"""

import math

import numpy as np
import pandas as pd

from evcs.data.event_windows import build_event_loss_weights
from evcs.data.event_windows import event_window_masks
from evcs.data.tensor_cache import EVCSTensorCache
from evcs.graphs.cache import SparseGraphCache

try:
    import torch
    from torch.utils.data import Dataset
except Exception:  # pragma: no cover - exercised only in environments without torch
    torch = None
    Dataset = object


class EVCSWindowDataset(Dataset):
    """把 tensor cache 中的预测起点转换为 GraphTemporalTCN batch。

    这里保持 Dataset 纯粹：不关心论文结论，也不决定 baseline 是否胜出；
    它只根据 `use_events`、`graph` 和配置开关返回模型 forward 所需的字段。
    """

    def __init__(
        self,
        cache: EVCSTensorCache,
        split: str,
        graph: SparseGraphCache,
        use_events: bool,
        normalize: bool = True,
        loss_weight_config: dict[str, object] | None = None,
        context_config: dict[str, object] | None = None,
        normalization_config: dict[str, object] | None = None,
    ) -> None:
        if torch is None:
            raise RuntimeError("PyTorch is required for EVCSWindowDataset")
        self.cache = cache
        self.origins = list(cache.split_indices[split])
        self.graph = graph
        self.use_events = use_events
        self.normalize = normalize
        self.context_config = context_config or {}
        self.normalization_config = normalization_config or {}
        self.normalization_mode = str(self.normalization_config.get("mode", "zscore")).lower()
        self.revin_std_clamp = float(self.normalization_config.get("std_clamp", 1e-4))
        # context_features 是 V5 解释性的关键：gate 不只看隐状态，也可看事件窗口、
        # 事件最近发生时间、日内/周内周期，从而学习“什么时候更该相信事件图”。
        self.enable_time_context = bool(self.context_config.get("time_context", False))
        self.enable_event_recency = bool(self.context_config.get("event_recency", False))
        self.enable_event_window_summary = bool(self.context_config.get("event_window_summary", False))
        self.enable_event_window_masks = bool(self.context_config.get("event_window_masks", self.enable_event_window_summary))
        self.origin_to_graph_position = {origin: position for position, origin in enumerate(cache.origin_indices)}
        self.loss_weights = build_event_loss_weights(cache, self.origins, loss_weight_config or {})
        # event_window_names 的顺序必须与 train_exp103.py 中 _event_window_name_to_index 保持一致。
        self.event_window_names = [
            "access_count",
            "departure_count",
            "load_jump_flag",
            "near_capacity_proxy",
            "active_count_high",
            "occupancy_rate_high",
        ]
        self.recency_feature_names = ["access_count", "departure_count", "load_jump_flag", "near_capacity_proxy"]
        train_origins = self.cache.split_indices.get("train", [])
        train_load = self.cache.load[train_origins] if train_origins else self.cache.load
        self.near_capacity_threshold = (
            np.quantile(train_load, 0.9, axis=0).astype(np.float32)
            if train_load.size
            else np.zeros((len(self.cache.nodes),), dtype=np.float32)
        )
        self.event_window_masks_by_origin = event_window_masks(self.cache, self.origins) if (
            self.enable_event_window_summary or self.enable_event_window_masks
        ) else {}
        self.origin_to_dataset_position = {origin: position for position, origin in enumerate(self.origins)}

    def __len__(self) -> int:
        return len(self.origins)

    def __getitem__(self, index: int) -> dict[str, object]:
        origin = self.origins[index]
        start = origin - self.cache.history_steps + 1
        end = origin + 1
        target_end = origin + 1 + self.cache.horizon_steps
        history_load = self.cache.load[start:end].copy()
        history_events = self.cache.event_features[start:end].copy()
        target = self.cache.load[origin + 1 : target_end].copy()
        target_center = np.zeros((len(self.cache.nodes),), dtype=np.float32)
        target_scale = np.ones((len(self.cache.nodes),), dtype=np.float32)
        if self.normalize and self.normalization_mode == "revin_load_only":
            # RevIN-style 标准化只用当前历史窗口估计 load 的中心和尺度；
            # event 特征仍用训练集统计量，避免每个窗口把稀疏事件特征洗平。
            target_center = history_load.mean(axis=0).astype(np.float32)
            target_scale = np.maximum(history_load.std(axis=0), self.revin_std_clamp).astype(np.float32)
            history_load = (history_load - target_center) / target_scale
            target = (target - target_center) / target_scale
            history_events = (history_events - self.cache.normalization["event_mean"]) / self.cache.normalization["event_std"]
        elif self.normalize and self.normalization_mode == "zscore":
            # 默认 z-score 使用 tensor cache 中的训练集统计量，保证 train/val/test 量纲一致。
            target_center = np.asarray(self.cache.normalization["load_mean"], dtype=np.float32)
            target_scale = np.asarray(self.cache.normalization["load_std"], dtype=np.float32)
            history_load = (history_load - self.cache.normalization["load_mean"]) / self.cache.normalization["load_std"]
            history_events = (history_events - self.cache.normalization["event_mean"]) / self.cache.normalization["event_std"]
            target = (target - self.cache.normalization["load_mean"]) / self.cache.normalization["load_std"]
        elif self.normalize and self.normalization_mode not in {"none", ""}:
            raise ValueError(f"unsupported normalization mode: {self.normalization_mode}")
        if not self.use_events:
            # no_graph baseline 关闭事件输入，但保留空通道形状，避免模型分支需要特殊 case。
            history_events = history_events[..., :0]
        graph_position = self.origin_to_graph_position[origin]
        event_window_masks = self._event_window_masks(origin)
        event_window_summary = event_window_masks if self.enable_event_window_summary else np.zeros(
            (len(self.cache.nodes), len(self.event_window_names)),
            dtype=np.float32,
        )
        event_recency = self._event_recency(origin, start, end)
        time_context = self._time_context(origin)
        event_context = np.concatenate(
            [
                event_window_summary if self.enable_event_window_summary else np.zeros((len(self.cache.nodes), 0), dtype=np.float32),
                event_recency if self.enable_event_recency else np.zeros((len(self.cache.nodes), 0), dtype=np.float32),
                time_context if self.enable_time_context else np.zeros((len(self.cache.nodes), 0), dtype=np.float32),
            ],
            axis=-1,
        ).astype(np.float32)
        # 返回字段保持“训练所需 + 评估还原 + 诊断解释”三类分离：
        # - history/graph/context 给模型 forward；
        # - target_raw/center/scale 给真实尺度指标；
        # - masks/recency/window summary 给事件窗口诊断和加权 loss。
        return {
            "history_load": torch.as_tensor(history_load, dtype=torch.float32),
            "history_events": torch.as_tensor(history_events, dtype=torch.float32),
            "target": torch.as_tensor(target, dtype=torch.float32),
            "target_raw": torch.as_tensor(self.cache.load[origin + 1 : target_end], dtype=torch.float32),
            "target_center": torch.as_tensor(target_center, dtype=torch.float32),
            "target_scale": torch.as_tensor(target_scale, dtype=torch.float32),
            "loss_weight": torch.as_tensor(self.loss_weights[index], dtype=torch.float32),
            "origin": torch.as_tensor(origin, dtype=torch.long),
            "time_context": torch.as_tensor(time_context, dtype=torch.float32),
            "event_recency": torch.as_tensor(event_recency, dtype=torch.float32),
            "event_window_mask_summary": torch.as_tensor(event_window_summary, dtype=torch.float32),
            "event_window_masks": torch.as_tensor(event_window_masks, dtype=torch.float32),
            "event_context": torch.as_tensor(event_context, dtype=torch.float32),
            "graph_indices": torch.as_tensor(self.graph.indices[graph_position], dtype=torch.long),
            "graph_weights": torch.as_tensor(self.graph.weights[graph_position], dtype=torch.float32),
            "historical_graph_indices": torch.as_tensor(self.graph.historical_indices[graph_position], dtype=torch.long)
            if self.graph.historical_indices is not None
            else torch.as_tensor(self.graph.indices[graph_position], dtype=torch.long),
            "historical_graph_weights": torch.as_tensor(self.graph.historical_weights[graph_position], dtype=torch.float32)
            if self.graph.historical_weights is not None
            else torch.as_tensor(self.graph.weights[graph_position], dtype=torch.float32),
            "event_channel_indices": torch.as_tensor(self.graph.channel_indices[graph_position], dtype=torch.long)
            if self.graph.channel_indices is not None
            else torch.zeros((0, *self.graph.indices[graph_position].shape), dtype=torch.long),
            "event_channel_weights": torch.as_tensor(self.graph.channel_weights[graph_position], dtype=torch.float32)
            if self.graph.channel_weights is not None
            else torch.zeros((0, *self.graph.weights[graph_position].shape), dtype=torch.float32),
        }

    def _event_window_summary(self, origin: int) -> np.ndarray:
        """返回事件窗口摘要；保留此方法是为了兼容早期调用路径。"""

        if not self.enable_event_window_summary:
            return np.zeros((len(self.cache.nodes), len(self.event_window_names)), dtype=np.float32)
        return self._event_window_masks(origin)

    def _event_window_masks(self, origin: int) -> np.ndarray:
        """按固定顺序返回每个节点是否处于各类事件窗口。"""

        if not (self.enable_event_window_summary or self.enable_event_window_masks):
            return np.zeros((len(self.cache.nodes), len(self.event_window_names)), dtype=np.float32)
        position = self.origin_to_dataset_position[origin]
        columns = []
        for name in self.event_window_names:
            mask = self.event_window_masks_by_origin.get(name)
            if mask is None:
                columns.append(np.zeros((len(self.cache.nodes),), dtype=np.float32))
            else:
                columns.append(mask[position].astype(np.float32))
        return np.stack(columns, axis=-1).astype(np.float32)

    def _event_recency(self, origin: int, start: int, end: int) -> np.ndarray:
        """计算最近一次事件距当前 origin 的归一化时间。

        值越小表示事件越近；若历史窗口内没有该事件，则填充为 1 附近的最大距离。
        """

        if not self.enable_event_recency:
            return np.zeros((len(self.cache.nodes), len(self.recency_feature_names)), dtype=np.float32)
        feature_names = list(self.cache.event_feature_names)
        history = self.cache.event_features[start:end]
        columns = []
        for name in self.recency_feature_names:
            if name == "near_capacity_proxy":
                active = self.cache.load[start:end] >= self.near_capacity_threshold
            elif name in feature_names:
                active = history[:, :, feature_names.index(name)] > 0
            else:
                active = np.zeros((end - start, len(self.cache.nodes)), dtype=bool)
            recency = np.full((len(self.cache.nodes),), float(self.cache.history_steps), dtype=np.float32)
            for node_index in range(len(self.cache.nodes)):
                hits = np.flatnonzero(active[:, node_index])
                if len(hits):
                    recency[node_index] = float((end - start - 1) - hits[-1])
            columns.append(recency / max(1.0, float(self.cache.history_steps)))
        return np.stack(columns, axis=-1).astype(np.float32)

    def _time_context(self, origin: int) -> np.ndarray:
        """生成日内/周内周期特征，并复制到每个节点。

        这些特征不是图结构，但能帮助 gate 分辨工作日/周末或充电高峰时段。
        """

        if not self.enable_time_context:
            return np.zeros((len(self.cache.nodes), 5), dtype=np.float32)
        timestamp = pd.Timestamp(self.cache.timestamps[origin])
        seconds = timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second
        day_fraction = seconds / 86400.0
        dow_fraction = timestamp.dayofweek / 7.0
        values = np.asarray(
            [
                math.sin(2.0 * math.pi * day_fraction),
                math.cos(2.0 * math.pi * day_fraction),
                math.sin(2.0 * math.pi * dow_fraction),
                math.cos(2.0 * math.pi * dow_fraction),
                1.0 if timestamp.dayofweek >= 5 else 0.0,
            ],
            dtype=np.float32,
        )
        return np.repeat(values[np.newaxis, :], len(self.cache.nodes), axis=0)
