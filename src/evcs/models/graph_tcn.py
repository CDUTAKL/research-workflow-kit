from __future__ import annotations

"""EXP-103 使用的图增强时间卷积网络。

本文件是论文实验里“模型结构”的核心实现。输入张量采用统一约定：

- `history_load`: `[batch, history, node]`，每个站点/节点过去若干步的负载。
- `history_events`: `[batch, history, node, event_channel]`，同一时间窗内的事件特征。
- `graph_indices` / `graph_weights`: `[batch, node, top_k]`，每个预测起点对应的邻居索引和权重。
- 输出: `[batch, horizon, node]`，未来多步负载预测。

`GraphTemporalTCN` 同时承载 baseline 和 proposed variants。这样做的好处是
训练脚本可以固定数据、优化器、早停和输出协议，只通过 `graph_mode` 改变信息融合方式，
从而减少“不同模型实现细节不一致”带来的实验噪声。
"""

try:
    import torch
    from torch import nn
except Exception:  # pragma: no cover - imported only on training hosts
    torch = None
    nn = None


class GraphTemporalTCN(nn.Module if nn is not None else object):
    """图增强 TCN 主模型。

    主要模式说明：

    - `concat`: 传统拼接式图输入，把邻居聚合后的时间序列与自身序列拼接。
    - `gated_residual`: EXP-103 v5 主力结构之一，自身预测 + gate * 图分支预测。
    - `event_conditional_dual`: 历史图和事件图双分支，并让事件上下文控制事件分支权重。
    - `event_residual_correction`: 事件图只学习对历史图预测的残差修正，便于解释事件冲击。
    - `multichannel_*`: 将 access/departure/occupancy/demand 等事件族拆成多通道图。

    `last_*` 字段不是训练必需状态，而是诊断接口：训练脚本会读取 gate、alpha、
    residual 和 channel weights，写入 `graph_gate_metrics.csv`、`residual_diagnostics.csv`
    等证据表，支撑论文里的可解释性和消融分析。
    """

    def __init__(
        self,
        load_channels: int,
        event_channels: int,
        hidden_channels: int,
        tcn_layers: int,
        kernel_size: int,
        dropout: float,
        horizon_steps: int,
        use_events: bool,
        use_graph: bool,
        graph_mode: str = "concat",
        graph_channel_count: int = 0,
        branch_alpha_init: float = 0.2,
        temporal_block: str = "residual",
        dilation_schedule: list[int] | tuple[int, ...] | None = None,
        graph_message_stage: str = "raw_history",
        event_context_channels: int = 0,
        node_count: int = 0,
        node_embedding_dim: int = 0,
        residual_clip: float = 0.0,
        event_gate_init_bias: float | None = None,
    ) -> None:
        if nn is None:
            raise RuntimeError("PyTorch is required for GraphTemporalTCN")
        super().__init__()
        supported_modes = {
            "concat",
            "gated_residual",
            "dual_residual",
            "multichannel_concat",
            "event_conditional_dual",
            "multichannel_event_conditional",
            "event_residual_correction",
        }
        if graph_mode not in supported_modes:
            raise ValueError(f"unsupported graph_mode: {graph_mode}")
        if temporal_block not in {"residual", "gated_dilated"}:
            raise ValueError(f"unsupported temporal_block: {temporal_block}")
        if graph_message_stage not in {"raw_history", "encoded_state"}:
            raise ValueError(f"unsupported graph_message_stage: {graph_message_stage}")
        self.use_events = use_events
        self.use_graph = use_graph
        self.graph_mode = graph_mode
        self.temporal_block = temporal_block
        self.dilation_schedule = _normalize_dilation_schedule(dilation_schedule, tcn_layers)
        self.graph_message_stage = graph_message_stage
        self.event_context_channels = int(event_context_channels)
        self.node_count = int(node_count)
        self.node_embedding_dim = max(0, int(node_embedding_dim))
        self.residual_clip = max(0.0, float(residual_clip))
        self.receptive_field = compute_receptive_field(kernel_size, tcn_layers, self.dilation_schedule)
        self.horizon_steps = horizon_steps
        # 以下缓存只保存最近一次 forward 的中间量，用于评估阶段导出诊断指标；
        # 它们不会参与梯度更新，也不应该被视为模型持久状态。
        self.last_gate = None
        self.last_channel_weights = None
        self.last_alpha_hist = None
        self.last_alpha_event = None
        self.last_event_residual = None
        self.last_hist_prediction = None
        self.last_event_correction = None
        self.last_event_residual_clip_rate = None
        self.node_embedding = (
            nn.Embedding(self.node_count, self.node_embedding_dim)
            if self.node_count > 0 and self.node_embedding_dim > 0
            else None
        )
        base_channels = load_channels + (event_channels if use_events else 0)
        if graph_mode == "gated_residual" and use_graph:
            # 主模型 event_graph_dynamic_v5 使用此路径：自身分支保证基础预测能力，
            # 图分支只以残差形式加入，gate 负责在事件图噪声较大时降低图影响。
            self.self_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
            self.graph_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
            self.self_head = nn.Linear(hidden_channels, horizon_steps)
            self.graph_head = nn.Linear(hidden_channels, horizon_steps)
            self.gate_mlp = nn.Sequential(
                nn.Linear(hidden_channels * 2, hidden_channels),
                nn.ReLU(),
                nn.Linear(hidden_channels, 1),
            )
        elif graph_mode == "dual_residual" and use_graph:
            # 早期双图结构：历史相关图与事件图分别预测残差，用全局 alpha 控制幅度。
            # 它能做对照，但不如 event_conditional_dual 细粒度，因为 alpha 不随样本/节点变化。
            self.self_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
            self.historical_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
            self.event_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
            self.self_head = nn.Linear(hidden_channels, horizon_steps)
            self.historical_head = nn.Linear(hidden_channels, horizon_steps)
            self.event_head = nn.Linear(hidden_channels, horizon_steps)
            raw_alpha = _inverse_softplus(branch_alpha_init)
            self.raw_alpha_hist = nn.Parameter(torch.tensor(raw_alpha, dtype=torch.float32))
            self.raw_alpha_event = nn.Parameter(torch.tensor(raw_alpha, dtype=torch.float32))
        elif graph_mode == "event_conditional_dual" and use_graph:
            # V5 的重要候选：同时保留历史相关图和事件图，并把事件上下文接入 gate。
            # 论文上可解释为“历史共变关系提供稳态结构，事件图在事件窗口中动态补充”。
            self.self_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
            if graph_message_stage == "raw_history":
                self.historical_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
                self.event_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
            else:
                self.historical_projection = nn.Sequential(nn.Linear(hidden_channels, hidden_channels), nn.ReLU())
                self.event_projection = nn.Sequential(nn.Linear(hidden_channels, hidden_channels), nn.ReLU())
            self.self_head = nn.Linear(hidden_channels, horizon_steps)
            self.historical_head = nn.Linear(hidden_channels, horizon_steps)
            self.event_head = nn.Linear(hidden_channels, horizon_steps)
            gate_input_channels = hidden_channels * 2 + self.event_context_channels
            self.event_gate_mlp = nn.Sequential(
                nn.Linear(gate_input_channels, hidden_channels),
                nn.ReLU(),
                nn.Linear(hidden_channels, 1),
            )
            raw_alpha = _inverse_softplus(branch_alpha_init)
            self.raw_alpha_hist = nn.Parameter(torch.tensor(raw_alpha, dtype=torch.float32))
            self.raw_alpha_event = nn.Parameter(torch.tensor(raw_alpha, dtype=torch.float32))
        elif graph_mode == "event_residual_correction" and use_graph:
            # 残差修正分支把历史图预测作为主干，只让事件图学习 correction。
            # 这一路适合做机制诊断：事件图到底是在事件窗口里加了多少修正。
            self.self_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
            if graph_message_stage == "raw_history":
                self.historical_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
                self.event_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
            else:
                self.historical_projection = nn.Sequential(nn.Linear(hidden_channels, hidden_channels), nn.ReLU())
                self.event_projection = nn.Sequential(nn.Linear(hidden_channels, hidden_channels), nn.ReLU())
            state_channels = hidden_channels + (self.node_embedding_dim if self.node_embedding is not None else 0)
            self.historical_head = nn.Linear(state_channels, horizon_steps)
            self.event_residual_head = nn.Linear(state_channels, horizon_steps)
            gate_input_channels = hidden_channels * 2 + self.event_context_channels + (
                self.node_embedding_dim if self.node_embedding is not None else 0
            )
            self.event_gate_mlp = nn.Sequential(
                nn.Linear(gate_input_channels, hidden_channels),
                nn.ReLU(),
                nn.Linear(hidden_channels, 1),
            )
            if event_gate_init_bias is not None:
                final_layer = self.event_gate_mlp[-1]
                if getattr(final_layer, "bias", None) is not None:
                    nn.init.constant_(final_layer.bias, float(event_gate_init_bias))
        elif graph_mode == "multichannel_concat" and use_graph:
            # 多通道拼接让不同事件族拥有独立邻接矩阵，再通过可学习 channel logits 融合。
            self.graph_channel_count = int(graph_channel_count)
            self.channel_logits = nn.Parameter(torch.zeros(max(1, self.graph_channel_count), dtype=torch.float32))
            self.encoder = _make_encoder(base_channels * 2, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
            self.head = nn.Linear(hidden_channels, horizon_steps)
        elif graph_mode == "multichannel_event_conditional" and use_graph:
            # 多通道条件门控在节点/样本维度上选择事件通道，代价更高，主要用于探索性消融。
            self.graph_channel_count = int(graph_channel_count)
            self.self_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
            self.self_head = nn.Linear(hidden_channels, horizon_steps)
            self.event_head = nn.Linear(hidden_channels, horizon_steps)
            gate_input_channels = hidden_channels * 2 + self.event_context_channels
            self.channel_gate_mlp = nn.Sequential(
                nn.Linear(gate_input_channels, hidden_channels),
                nn.ReLU(),
                nn.Linear(hidden_channels, 1),
            )
        else:
            input_channels = base_channels * (2 if use_graph else 1)
            self.encoder = _make_encoder(input_channels, hidden_channels, tcn_layers, kernel_size, dropout, temporal_block, self.dilation_schedule)
            self.head = nn.Linear(hidden_channels, horizon_steps)

    @property
    def alpha_hist(self):
        if not hasattr(self, "raw_alpha_hist"):
            return None
        return torch.nn.functional.softplus(self.raw_alpha_hist)

    @property
    def alpha_event(self):
        if not hasattr(self, "raw_alpha_event"):
            return None
        return torch.nn.functional.softplus(self.raw_alpha_event)

    def forward(
        self,
        history_load,
        history_events,
        graph_indices,
        graph_weights,
        historical_graph_indices=None,
        historical_graph_weights=None,
        event_channel_indices=None,
        event_channel_weights=None,
        event_context=None,
    ):
        """执行一次多步预测。

        所有分支最终都返回 `[batch, horizon, node]`。内部会临时转成
        `[batch, node, horizon]`，因为每个节点共享 TCN encoder 和线性预测头。
        """

        if torch is None:
            raise RuntimeError("PyTorch is required for GraphTemporalTCN")
        self.last_gate = None
        self.last_channel_weights = None
        self.last_alpha_hist = None
        self.last_alpha_event = None
        self.last_event_residual = None
        self.last_hist_prediction = None
        self.last_event_correction = None
        self.last_event_residual_clip_rate = None
        features = [history_load.unsqueeze(-1)]
        if self.use_events:
            features.append(history_events)
        node_features = torch.cat(features, dim=-1)
        if self.use_graph and self.graph_mode == "gated_residual":
            self_state = _encode_last(self.self_encoder, node_features)
            if self.graph_message_stage == "encoded_state":
                graph_state = _neighbor_aggregate_state(self_state, graph_indices, graph_weights)
            else:
                neighbor_features = _neighbor_aggregate(node_features, graph_indices, graph_weights)
                graph_state = _encode_last(self.graph_encoder, neighbor_features)
            batch, _, node_count, _ = node_features.shape
            # 门控残差分支让模型自己判断图信息该加多少；当事件图噪声大时，gate 可以自动压低图分支权重。
            gate = torch.sigmoid(self.gate_mlp(torch.cat([self_state, graph_state], dim=-1))).reshape(batch, node_count, 1)
            self_prediction = self.self_head(self_state).reshape(batch, node_count, self.horizon_steps)
            graph_prediction = self.graph_head(graph_state).reshape(batch, node_count, self.horizon_steps)
            self.last_gate = gate.detach()
            prediction = self_prediction + gate * graph_prediction
            return prediction.permute(0, 2, 1).contiguous()
        if self.use_graph and self.graph_mode == "dual_residual":
            historical_indices = historical_graph_indices if historical_graph_indices is not None else graph_indices
            historical_weights = historical_graph_weights if historical_graph_weights is not None else graph_weights
            event_features = _neighbor_aggregate(node_features, graph_indices, graph_weights)
            historical_features = _neighbor_aggregate(node_features, historical_indices, historical_weights)
            self_state = _encode_last(self.self_encoder, node_features)
            historical_state = _encode_last(self.historical_encoder, historical_features)
            event_state = _encode_last(self.event_encoder, event_features)
            batch, _, node_count, _ = node_features.shape
            alpha_hist = self.alpha_hist
            alpha_event = self.alpha_event
            self_prediction = self.self_head(self_state).reshape(batch, node_count, self.horizon_steps)
            historical_prediction = self.historical_head(historical_state).reshape(batch, node_count, self.horizon_steps)
            event_prediction = self.event_head(event_state).reshape(batch, node_count, self.horizon_steps)
            self.last_alpha_hist = alpha_hist.detach()
            self.last_alpha_event = alpha_event.detach()
            prediction = self_prediction + alpha_hist * historical_prediction + alpha_event * event_prediction
            return prediction.permute(0, 2, 1).contiguous()
        if self.use_graph and self.graph_mode == "event_conditional_dual":
            historical_indices = historical_graph_indices if historical_graph_indices is not None else graph_indices
            historical_weights = historical_graph_weights if historical_graph_weights is not None else graph_weights
            self_state = _encode_last(self.self_encoder, node_features)
            if self.graph_message_stage == "encoded_state":
                event_state = self.event_projection(_neighbor_aggregate_state(self_state, graph_indices, graph_weights))
                historical_state = self.historical_projection(_neighbor_aggregate_state(self_state, historical_indices, historical_weights))
            else:
                event_features = _neighbor_aggregate(node_features, graph_indices, graph_weights)
                historical_features = _neighbor_aggregate(node_features, historical_indices, historical_weights)
                event_state = _encode_last(self.event_encoder, event_features)
                historical_state = _encode_last(self.historical_encoder, historical_features)
            batch, node_count, _ = self_state.shape
            event_context = _event_context_or_zeros(
                event_context,
                batch=batch,
                node_count=node_count,
                channel_count=self.event_context_channels,
                device=self_state.device,
                dtype=self_state.dtype,
            )
            gate = torch.sigmoid(self.event_gate_mlp(torch.cat([self_state, event_state, event_context], dim=-1))).reshape(batch, node_count, 1)
            alpha_hist = self.alpha_hist
            alpha_event = self.alpha_event
            self_prediction = self.self_head(self_state).reshape(batch, node_count, self.horizon_steps)
            historical_prediction = self.historical_head(historical_state).reshape(batch, node_count, self.horizon_steps)
            event_prediction = self.event_head(event_state).reshape(batch, node_count, self.horizon_steps)
            # 历史图残差使用全局 alpha；事件图残差再乘以 gate，让事件上下文决定“何时相信事件图”。
            self.last_gate = gate.detach()
            self.last_alpha_hist = alpha_hist.detach()
            self.last_alpha_event = alpha_event.detach()
            prediction = self_prediction + alpha_hist * historical_prediction + gate * alpha_event * event_prediction
            return prediction.permute(0, 2, 1).contiguous()
        if self.use_graph and self.graph_mode == "event_residual_correction":
            historical_indices = historical_graph_indices if historical_graph_indices is not None else graph_indices
            historical_weights = historical_graph_weights if historical_graph_weights is not None else graph_weights
            self_state = _encode_last(self.self_encoder, node_features)
            if self.graph_message_stage == "encoded_state":
                historical_state = self.historical_projection(_neighbor_aggregate_state(self_state, historical_indices, historical_weights))
                event_state = self.event_projection(_neighbor_aggregate_state(self_state, graph_indices, graph_weights))
            else:
                historical_features = _neighbor_aggregate(node_features, historical_indices, historical_weights)
                event_features = _neighbor_aggregate(node_features, graph_indices, graph_weights)
                historical_state = _encode_last(self.historical_encoder, historical_features)
                event_state = _encode_last(self.event_encoder, event_features)
            batch, node_count, _ = self_state.shape
            event_context = _event_context_or_zeros(
                event_context,
                batch=batch,
                node_count=node_count,
                channel_count=self.event_context_channels,
                device=self_state.device,
                dtype=self_state.dtype,
            )
            node_embedding = self._node_embedding(batch, node_count, self_state.device, self_state.dtype)
            historical_head_state = torch.cat([historical_state, node_embedding], dim=-1) if node_embedding.shape[-1] else historical_state
            event_head_state = torch.cat([event_state, node_embedding], dim=-1) if node_embedding.shape[-1] else event_state
            gate_input_parts = [self_state, event_state, event_context]
            if node_embedding.shape[-1]:
                gate_input_parts.append(node_embedding)
            gate = torch.sigmoid(self.event_gate_mlp(torch.cat(gate_input_parts, dim=-1))).reshape(batch, node_count, 1)
            hist_prediction = self.historical_head(historical_head_state).reshape(batch, node_count, self.horizon_steps)
            raw_event_residual = self.event_residual_head(event_head_state).reshape(batch, node_count, self.horizon_steps)
            if self.residual_clip > 0.0:
                # clip 用 tanh 做软截断，避免事件分支在少数异常窗口中产生过大的修正量。
                event_residual = self.residual_clip * torch.tanh(raw_event_residual / self.residual_clip)
                clip_rate = (raw_event_residual.abs() > self.residual_clip).to(dtype=self_state.dtype).mean()
            else:
                event_residual = raw_event_residual
                clip_rate = torch.zeros((), device=self_state.device, dtype=self_state.dtype)
            event_correction = gate * event_residual
            prediction = hist_prediction + event_correction
            self.last_gate = gate.detach()
            self.last_hist_prediction = hist_prediction.detach()
            self.last_event_residual = event_residual.detach()
            self.last_event_correction = event_correction.detach()
            self.last_event_residual_clip_rate = clip_rate.detach()
            return prediction.permute(0, 2, 1).contiguous()
        if self.use_graph and self.graph_mode == "multichannel_event_conditional":
            self_state = _encode_last(self.self_encoder, node_features)
            batch, node_count, _ = self_state.shape
            event_context = _event_context_or_zeros(
                event_context,
                batch=batch,
                node_count=node_count,
                channel_count=self.event_context_channels,
                device=self_state.device,
                dtype=self_state.dtype,
            )
            if event_channel_indices is None or event_channel_indices.shape[1] == 0:
                channel_states = _neighbor_aggregate_state(self_state, graph_indices, graph_weights).unsqueeze(1)
            else:
                states = []
                for channel_index in range(event_channel_indices.shape[1]):
                    states.append(
                        _neighbor_aggregate_state(
                            self_state,
                            event_channel_indices[:, channel_index],
                            event_channel_weights[:, channel_index],
                        )
                    )
                channel_states = torch.stack(states, dim=1)
            channel_count_graph = channel_states.shape[1]
            expanded_self = self_state.unsqueeze(1).expand(batch, channel_count_graph, node_count, self_state.shape[-1])
            expanded_context = event_context.unsqueeze(1).expand(batch, channel_count_graph, node_count, event_context.shape[-1])
            gate_input = torch.cat([expanded_self, channel_states, expanded_context], dim=-1)
            logits = self.channel_gate_mlp(gate_input).squeeze(-1)
            weights = torch.softmax(logits, dim=1)
            event_state = (channel_states * weights.unsqueeze(-1)).sum(dim=1)
            # 记录平均通道权重，用于判断模型更依赖 access、departure、occupancy 还是 demand 图。
            self.last_channel_weights = weights.mean(dim=(0, 2)).detach()
            self_prediction = self.self_head(self_state).reshape(batch, node_count, self.horizon_steps)
            event_prediction = self.event_head(event_state).reshape(batch, node_count, self.horizon_steps)
            prediction = self_prediction + event_prediction
            return prediction.permute(0, 2, 1).contiguous()
        if self.use_graph:
            if self.graph_mode == "multichannel_concat" and event_channel_indices is not None and event_channel_indices.shape[1] > 0:
                neighbor_features = _neighbor_aggregate_multichannel(node_features, event_channel_indices, event_channel_weights, self)
            else:
                neighbor_features = _neighbor_aggregate(node_features, graph_indices, graph_weights)
            node_features = torch.cat([node_features, neighbor_features], dim=-1)
        batch, history, node_count, channel_count = node_features.shape
        encoded_input = node_features.permute(0, 2, 3, 1).reshape(batch * node_count, channel_count, history)
        encoded = self.encoder(encoded_input)
        last_state = encoded[:, :, -1]
        prediction = self.head(last_state).reshape(batch, node_count, self.horizon_steps)
        return prediction.permute(0, 2, 1).contiguous()

    def _node_embedding(self, batch: int, node_count: int, device, dtype):
        """返回节点嵌入，并按 batch 展开。

        节点嵌入用于给残差头提供站点身份信息，避免所有站点共享同一个事件修正偏置。
        """

        if self.node_embedding is None:
            return torch.zeros((batch, node_count, 0), device=device, dtype=dtype)
        if node_count > self.node_count:
            raise ValueError(f"node_count={node_count} exceeds configured node_count={self.node_count}")
        indices = torch.arange(node_count, device=device, dtype=torch.long)
        values = self.node_embedding(indices).to(dtype=dtype)
        return values.unsqueeze(0).expand(batch, node_count, values.shape[-1])


class _TemporalBlock(nn.Module if nn is not None else object):
    """普通残差 TCN block。

    卷积使用左侧历史加右侧裁剪的写法，保证输出长度与输入 history 长度一致。
    """

    def __init__(self, input_channels: int, output_channels: int, kernel_size: int, dropout: float) -> None:
        if nn is None:
            raise RuntimeError("PyTorch is required for _TemporalBlock")
        super().__init__()
        self.conv = nn.Conv1d(input_channels, output_channels, kernel_size, padding=kernel_size - 1)
        self.activation = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.residual = nn.Conv1d(input_channels, output_channels, 1) if input_channels != output_channels else nn.Identity()

    def forward(self, inputs):
        out = self.conv(inputs)
        if out.shape[-1] > inputs.shape[-1]:
            out = out[..., -inputs.shape[-1] :]
        out = self.dropout(self.activation(out))
        return out + self.residual(inputs)


class DilatedGatedTemporalBlock(nn.Module if nn is not None else object):
    """带 dilation 和门控激活的 TCN block。

    `tanh(filter) * sigmoid(gate)` 是 WaveNet/TCN 风格结构，适合扩大感受野，
    用于测试更长历史依赖是否能帮助事件图模型。
    """

    def __init__(self, input_channels: int, output_channels: int, kernel_size: int, dilation: int, dropout: float) -> None:
        if nn is None:
            raise RuntimeError("PyTorch is required for DilatedGatedTemporalBlock")
        super().__init__()
        padding = (kernel_size - 1) * dilation
        self.filter_conv = nn.Conv1d(input_channels, output_channels, kernel_size, padding=padding, dilation=dilation)
        self.gate_conv = nn.Conv1d(input_channels, output_channels, kernel_size, padding=padding, dilation=dilation)
        self.dropout = nn.Dropout(dropout)
        self.residual = nn.Conv1d(input_channels, output_channels, 1) if input_channels != output_channels else nn.Identity()

    def forward(self, inputs):
        filtered = self.filter_conv(inputs)
        gated = self.gate_conv(inputs)
        if filtered.shape[-1] > inputs.shape[-1]:
            filtered = filtered[..., -inputs.shape[-1] :]
            gated = gated[..., -inputs.shape[-1] :]
        out = torch.tanh(filtered) * torch.sigmoid(gated)
        out = self.dropout(out)
        return out + self.residual(inputs)


def compute_receptive_field(kernel_size: int, tcn_layers: int, dilation_schedule: list[int] | tuple[int, ...] | None = None) -> int:
    """计算 TCN 能看到的历史步数，写入 config_resolved 以便复现实验。"""

    dilations = _normalize_dilation_schedule(dilation_schedule, tcn_layers)
    return 1 + int(kernel_size - 1) * int(sum(dilations))


def _make_encoder(
    input_channels: int,
    hidden_channels: int,
    tcn_layers: int,
    kernel_size: int,
    dropout: float,
    temporal_block: str,
    dilation_schedule: list[int],
):
    """按配置构造共享的节点级时间编码器。"""

    layers = []
    current = input_channels
    for layer_index in range(tcn_layers):
        if temporal_block == "gated_dilated":
            layers.append(DilatedGatedTemporalBlock(current, hidden_channels, kernel_size, dilation_schedule[layer_index], dropout))
        else:
            layers.append(_TemporalBlock(current, hidden_channels, kernel_size, dropout))
        current = hidden_channels
    return nn.Sequential(*layers)


def _encode_last(encoder, node_features):
    """把 `[B,H,N,C]` 编码成每个节点的最后时刻状态 `[B,N,D]`。"""

    batch, history, node_count, channel_count = node_features.shape
    encoded_input = node_features.permute(0, 2, 3, 1).reshape(batch * node_count, channel_count, history)
    encoded = encoder(encoded_input)
    return encoded[:, :, -1].reshape(batch, node_count, -1)


def _neighbor_aggregate(node_features, graph_indices, graph_weights):
    """在原始历史序列上做图邻居加权聚合。

    这种聚合保留邻居的完整时间序列，适合 `raw_history` 消息阶段。
    """

    batch, history, node_count, channel_count = node_features.shape
    aggregate = torch.zeros_like(node_features)
    neighbor_count = graph_indices.shape[-1]
    for neighbor_index in range(neighbor_count):
        indices = graph_indices[:, :, neighbor_index].view(batch, 1, node_count, 1).expand(batch, history, node_count, channel_count)
        gathered = torch.gather(node_features, dim=2, index=indices)
        weights = graph_weights[:, :, neighbor_index].view(batch, 1, node_count, 1)
        aggregate = aggregate + gathered * weights
    return aggregate


def _neighbor_aggregate_state(node_state, graph_indices, graph_weights):
    """在编码后的节点状态上做图邻居聚合，适合更省显存的 `encoded_state` 阶段。"""

    batch, node_count, channel_count = node_state.shape
    aggregate = torch.zeros_like(node_state)
    neighbor_count = graph_indices.shape[-1]
    for neighbor_index in range(neighbor_count):
        indices = graph_indices[:, :, neighbor_index].view(batch, node_count, 1).expand(batch, node_count, channel_count)
        gathered = torch.gather(node_state, dim=1, index=indices)
        weights = graph_weights[:, :, neighbor_index].view(batch, node_count, 1)
        aggregate = aggregate + gathered * weights
    return aggregate


def _neighbor_aggregate_multichannel(node_features, channel_indices, channel_weights, model):
    """把多类事件图按可学习通道权重融合成一个邻居聚合结果。"""

    batch, history, node_count, channel_count = node_features.shape
    channel_count_graph = channel_indices.shape[1]
    aggregate = torch.zeros_like(node_features)
    channel_scores = torch.softmax(model.channel_logits[:channel_count_graph], dim=0)
    model.last_channel_weights = channel_scores.detach()
    for channel_index in range(channel_count_graph):
        aggregate = aggregate + channel_scores[channel_index] * _neighbor_aggregate(
            node_features,
            channel_indices[:, channel_index],
            channel_weights[:, channel_index],
        )
    return aggregate


def _inverse_softplus(value: float) -> float:
    return float(torch.log(torch.expm1(torch.tensor(max(value, 1e-6), dtype=torch.float32))))


def _normalize_dilation_schedule(dilation_schedule: list[int] | tuple[int, ...] | None, tcn_layers: int) -> list[int]:
    """把 dilation 配置补齐/截断到 TCN 层数，避免配置长度漂移。"""

    if dilation_schedule is None:
        return [1 for _ in range(int(tcn_layers))]
    values = [max(1, int(value)) for value in dilation_schedule]
    if not values:
        values = [1]
    if len(values) < int(tcn_layers):
        values = values + [values[-1]] * (int(tcn_layers) - len(values))
    return values[: int(tcn_layers)]


def _event_context_or_zeros(event_context, batch: int, node_count: int, channel_count: int, device, dtype):
    """保证事件上下文通道数与模型 gate 输入一致。"""

    if channel_count <= 0:
        return torch.zeros((batch, node_count, 0), device=device, dtype=dtype)
    if event_context is None:
        return torch.zeros((batch, node_count, channel_count), device=device, dtype=dtype)
    if event_context.shape[-1] == channel_count:
        return event_context.to(device=device, dtype=dtype)
    if event_context.shape[-1] > channel_count:
        return event_context[..., :channel_count].to(device=device, dtype=dtype)
    padding = torch.zeros((*event_context.shape[:-1], channel_count - event_context.shape[-1]), device=event_context.device, dtype=event_context.dtype)
    return torch.cat([event_context, padding], dim=-1).to(device=device, dtype=dtype)
