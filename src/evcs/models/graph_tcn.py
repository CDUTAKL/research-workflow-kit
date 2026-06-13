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
    ) -> None:
        if nn is None:
            raise RuntimeError("PyTorch is required for GraphTemporalTCN")
        super().__init__()
        if graph_mode not in {"concat", "gated_residual"}:
            raise ValueError(f"unsupported graph_mode: {graph_mode}")
        self.use_events = use_events
        self.use_graph = use_graph
        self.graph_mode = graph_mode
        self.horizon_steps = horizon_steps
        self.last_gate = None
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
        else:
            input_channels = base_channels * (2 if use_graph else 1)
            self.encoder = _make_encoder(input_channels, hidden_channels, tcn_layers, kernel_size, dropout)
            self.head = nn.Linear(hidden_channels, horizon_steps)

    def forward(self, history_load, history_events, graph_indices, graph_weights):
        if torch is None:
            raise RuntimeError("PyTorch is required for GraphTemporalTCN")
        self.last_gate = None
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
        if self.use_graph:
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
