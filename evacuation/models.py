from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot


@dataclass(frozen=True)
class Edge:
    target: str
    distance: float
    congestion: float = 0.0


@dataclass
class CampusGraph:
    """Undirected campus graph with environmental state kept separately."""

    positions: dict[str, tuple[float, float]]
    adjacency: dict[str, list[Edge]] = field(default_factory=dict)
    hazards: dict[str, float] = field(default_factory=dict)
    blocked_edges: set[frozenset[str]] = field(default_factory=set)

    def __post_init__(self) -> None:
        for node in self.positions:
            self.adjacency.setdefault(node, [])
            self.hazards.setdefault(node, 0.0)

    def add_edge(self, source: str, target: str, distance: float, congestion: float = 0.0) -> None:
        if source not in self.positions or target not in self.positions:
            raise ValueError("Both edge endpoints must be campus nodes")
        if distance <= 0:
            raise ValueError("Distance must be positive")
        self.adjacency[source].append(Edge(target, distance, congestion))
        self.adjacency[target].append(Edge(source, distance, congestion))

    def neighbours(self, node: str) -> list[Edge]:
        return [
            edge
            for edge in self.adjacency[node]
            if frozenset((node, edge.target)) not in self.blocked_edges
        ]

    def get_edge(self, source: str, target: str) -> Edge:
        for edge in self.adjacency[source]:
            if edge.target == target:
                return edge
        raise KeyError(f"No edge from {source!r} to {target!r}")

    def heuristic(self, node: str, goal: str) -> float:
        """Straight-line distance; admissible when edge lengths reflect map distance."""
        x1, y1 = self.positions[node]
        x2, y2 = self.positions[goal]
        return hypot(x2 - x1, y2 - y1)

    def edge_cost(
        self,
        source: str,
        edge: Edge,
        hazard_weight: float,
        congestion_weight: float,
    ) -> float:
        mean_risk = (self.hazards[source] + self.hazards[edge.target]) / 2
        return edge.distance * (
            1 + hazard_weight * mean_risk + congestion_weight * edge.congestion
        )


@dataclass(frozen=True)
class SearchResult:
    algorithm: str
    path: list[str]
    reached: bool
    weighted_cost: float
    distance: float
    risk_exposure: float
    congestion_exposure: float
    expanded_order: list[str]
    runtime_ms: float

    @property
    def nodes_expanded(self) -> int:
        return len(self.expanded_order)

