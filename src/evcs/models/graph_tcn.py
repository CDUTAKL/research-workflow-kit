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
    ) -> None:
        if nn is None:
            raise RuntimeError("PyTorch is required for GraphTemporalTCN")
        super().__init__()
        self.use_events = use_events
        self.use_graph = use_graph
        self.horizon_steps = horizon_steps
        base_channels = load_channels + (event_channels if use_events else 0)
        input_channels = base_channels * (2 if use_graph else 1)
        layers = []
        current = input_channels
        for _ in range(tcn_layers):
            layers.append(_TemporalBlock(current, hidden_channels, kernel_size, dropout))
            current = hidden_channels
        self.encoder = nn.Sequential(*layers)
        self.head = nn.Linear(hidden_channels, horizon_steps)

    def forward(self, history_load, history_events, graph_indices, graph_weights):
        if torch is None:
            raise RuntimeError("PyTorch is required for GraphTemporalTCN")
        features = [history_load.unsqueeze(-1)]
        if self.use_events:
            features.append(history_events)
        node_features = torch.cat(features, dim=-1)
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
