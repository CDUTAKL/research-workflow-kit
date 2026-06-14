from __future__ import annotations

try:
    import torch
    from torch import nn
except Exception:  # pragma: no cover - imported only on training hosts
    torch = None
    nn = None


class GraphTemporalTCN(nn.Module if nn is not None else object):
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
    ) -> None:
        if nn is None:
            raise RuntimeError("PyTorch is required for GraphTemporalTCN")
        super().__init__()
        if graph_mode not in {"concat", "gated_residual", "dual_residual", "multichannel_concat"}:
            raise ValueError(f"unsupported graph_mode: {graph_mode}")
        self.use_events = use_events
        self.use_graph = use_graph
        self.graph_mode = graph_mode
        self.horizon_steps = horizon_steps
        self.last_gate = None
        self.last_channel_weights = None
        self.last_alpha_hist = None
        self.last_alpha_event = None
        base_channels = load_channels + (event_channels if use_events else 0)
        if graph_mode == "gated_residual" and use_graph:
            self.self_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout)
            self.graph_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout)
            self.self_head = nn.Linear(hidden_channels, horizon_steps)
            self.graph_head = nn.Linear(hidden_channels, horizon_steps)
            self.gate_mlp = nn.Sequential(
                nn.Linear(hidden_channels * 2, hidden_channels),
                nn.ReLU(),
                nn.Linear(hidden_channels, 1),
            )
        elif graph_mode == "dual_residual" and use_graph:
            self.self_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout)
            self.historical_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout)
            self.event_encoder = _make_encoder(base_channels, hidden_channels, tcn_layers, kernel_size, dropout)
            self.self_head = nn.Linear(hidden_channels, horizon_steps)
            self.historical_head = nn.Linear(hidden_channels, horizon_steps)
            self.event_head = nn.Linear(hidden_channels, horizon_steps)
            raw_alpha = _inverse_softplus(branch_alpha_init)
            self.raw_alpha_hist = nn.Parameter(torch.tensor(raw_alpha, dtype=torch.float32))
            self.raw_alpha_event = nn.Parameter(torch.tensor(raw_alpha, dtype=torch.float32))
        elif graph_mode == "multichannel_concat" and use_graph:
            self.graph_channel_count = int(graph_channel_count)
            self.channel_logits = nn.Parameter(torch.zeros(max(1, self.graph_channel_count), dtype=torch.float32))
            self.encoder = _make_encoder(base_channels * 2, hidden_channels, tcn_layers, kernel_size, dropout)
            self.head = nn.Linear(hidden_channels, horizon_steps)
        else:
            input_channels = base_channels * (2 if use_graph else 1)
            self.encoder = _make_encoder(input_channels, hidden_channels, tcn_layers, kernel_size, dropout)
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
    ):
        if torch is None:
            raise RuntimeError("PyTorch is required for GraphTemporalTCN")
        self.last_gate = None
        self.last_channel_weights = None
        self.last_alpha_hist = None
        self.last_alpha_event = None
        features = [history_load.unsqueeze(-1)]
        if self.use_events:
            features.append(history_events)
        node_features = torch.cat(features, dim=-1)
        if self.use_graph and self.graph_mode == "gated_residual":
            neighbor_features = _neighbor_aggregate(node_features, graph_indices, graph_weights)
            self_state = _encode_last(self.self_encoder, node_features)
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


class _TemporalBlock(nn.Module if nn is not None else object):
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


def _make_encoder(input_channels: int, hidden_channels: int, tcn_layers: int, kernel_size: int, dropout: float):
    layers = []
    current = input_channels
    for _ in range(tcn_layers):
        layers.append(_TemporalBlock(current, hidden_channels, kernel_size, dropout))
        current = hidden_channels
    return nn.Sequential(*layers)


def _encode_last(encoder, node_features):
    batch, history, node_count, channel_count = node_features.shape
    encoded_input = node_features.permute(0, 2, 3, 1).reshape(batch * node_count, channel_count, history)
    encoded = encoder(encoded_input)
    return encoded[:, :, -1]


def _neighbor_aggregate(node_features, graph_indices, graph_weights):
    batch, history, node_count, channel_count = node_features.shape
    aggregate = torch.zeros_like(node_features)
    neighbor_count = graph_indices.shape[-1]
    for neighbor_index in range(neighbor_count):
        indices = graph_indices[:, :, neighbor_index].view(batch, 1, node_count, 1).expand(batch, history, node_count, channel_count)
        gathered = torch.gather(node_features, dim=2, index=indices)
        weights = graph_weights[:, :, neighbor_index].view(batch, 1, node_count, 1)
        aggregate = aggregate + gathered * weights
    return aggregate


def _neighbor_aggregate_multichannel(node_features, channel_indices, channel_weights, model):
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
