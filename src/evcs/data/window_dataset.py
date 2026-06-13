from __future__ import annotations

from evcs.data.tensor_cache import EVCSTensorCache
from evcs.graphs.cache import SparseGraphCache

try:
    import torch
    from torch.utils.data import Dataset
except Exception:  # pragma: no cover - exercised only in environments without torch
    torch = None
    Dataset = object


class EVCSWindowDataset(Dataset):
    def __init__(
        self,
        cache: EVCSTensorCache,
        split: str,
        graph: SparseGraphCache,
        use_events: bool,
        normalize: bool = True,
    ) -> None:
        if torch is None:
            raise RuntimeError("PyTorch is required for EVCSWindowDataset")
        self.cache = cache
        self.origins = list(cache.split_indices[split])
        self.graph = graph
        self.use_events = use_events
        self.normalize = normalize
        self.origin_to_graph_position = {origin: position for position, origin in enumerate(cache.origin_indices)}

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
        if self.normalize:
            history_load = (history_load - self.cache.normalization["load_mean"]) / self.cache.normalization["load_std"]
            history_events = (history_events - self.cache.normalization["event_mean"]) / self.cache.normalization["event_std"]
            target = (target - self.cache.normalization["load_mean"]) / self.cache.normalization["load_std"]
        if not self.use_events:
            history_events = history_events[..., :0]
        graph_position = self.origin_to_graph_position[origin]
        return {
            "history_load": torch.as_tensor(history_load, dtype=torch.float32),
            "history_events": torch.as_tensor(history_events, dtype=torch.float32),
            "target": torch.as_tensor(target, dtype=torch.float32),
            "target_raw": torch.as_tensor(self.cache.load[origin + 1 : target_end], dtype=torch.float32),
            "origin": torch.as_tensor(origin, dtype=torch.long),
            "graph_indices": torch.as_tensor(self.graph.indices[graph_position], dtype=torch.long),
            "graph_weights": torch.as_tensor(self.graph.weights[graph_position], dtype=torch.float32),
        }
