from __future__ import annotations

"""Small, explicit neural baselines used by EXP-108."""

try:
    import torch
    from torch import nn
except Exception:  # pragma: no cover - dependency is checked by the runner
    torch = None
    nn = None


class GRUForecast(nn.Module if nn is not None else object):
    """Node-wise GRU with shared weights and direct multi-horizon output."""

    def __init__(self, input_channels: int, hidden_channels: int, num_layers: int, dropout: float, horizon: int):
        if nn is None:
            raise RuntimeError("PyTorch is required for GRUForecast")
        super().__init__()
        self.gru = nn.GRU(
            input_channels,
            hidden_channels,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.head = nn.Linear(hidden_channels, horizon)

    def forward(self, values):
        # [B,H,N,F] -> [B,N,H,F] -> shared node-wise sequence model
        values = values.permute(0, 2, 1, 3)
        batch, nodes, history, channels = values.shape
        encoded, _ = self.gru(values.reshape(batch * nodes, history, channels))
        return self.head(encoded[:, -1]).reshape(batch, nodes, -1).permute(0, 2, 1)


class STGCNForecast(nn.Module if nn is not None else object):
    """Compact static-graph temporal baseline with train-only adjacency."""

    def __init__(self, input_channels: int, hidden_channels: int, dropout: float, horizon: int, adjacency):
        if nn is None or torch is None:
            raise RuntimeError("PyTorch is required for STGCNForecast")
        super().__init__()
        self.register_buffer("adjacency", adjacency)
        self.temporal_in = nn.Conv2d(input_channels, hidden_channels, kernel_size=(3, 1), padding=(2, 0))
        self.temporal_out = nn.Conv2d(hidden_channels, hidden_channels, kernel_size=(3, 1), padding=(2, 0))
        self.dropout = nn.Dropout(dropout)
        self.head = nn.Linear(hidden_channels, horizon)

    def forward(self, values):
        # Temporal convolution, graph propagation, temporal convolution.
        state = values.permute(0, 3, 1, 2)
        state = torch.relu(self.temporal_in(state))[:, :, : values.shape[1]]
        state = torch.einsum("bctn,nm->bctm", state, self.adjacency)
        state = self.dropout(torch.relu(self.temporal_out(state)))[:, :, : values.shape[1]]
        return self.head(state[:, :, -1].permute(0, 2, 1)).permute(0, 2, 1)
