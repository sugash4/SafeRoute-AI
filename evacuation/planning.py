from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from .algorithms import astar
from .models import CampusGraph, SearchResult


@dataclass(frozen=True)
class ReplanningResult:
    initial_plan: SearchResult
    current_location: str
    newly_blocked: tuple[str, str] | None
    revised_plan: SearchResult | None
    revised_graph: CampusGraph


def simulate_unexpected_blockage(
    graph: CampusGraph,
    start: str,
    goal: str,
    hazard_weight: float = 4.0,
    congestion_weight: float = 2.0,
) -> ReplanningResult:
    """Move once, block the next planned corridor, then search again."""
    initial = astar(graph, start, goal, hazard_weight, congestion_weight)
    revised_graph = deepcopy(graph)
    if len(initial.path) < 3:
        return ReplanningResult(initial, start, None, None, revised_graph)

    current = initial.path[1]
    blocked = (current, initial.path[2])
    revised_graph.blocked_edges.add(frozenset(blocked))
    revised = astar(revised_graph, current, goal, hazard_weight, congestion_weight)
    return ReplanningResult(initial, current, blocked, revised, revised_graph)

