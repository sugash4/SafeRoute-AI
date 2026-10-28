from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .algorithms import astar
from .models import CampusGraph, SearchResult


@dataclass(frozen=True)
class AgentPlan:
    agent: str
    start: str
    exit: str
    result: SearchResult


@dataclass(frozen=True)
class MultiAgentPlan:
    plans: list[AgentPlan]
    objective_cost: float
    shared_corridors: int
    exit_loads: dict[str, int]


def _path_edges(result: SearchResult) -> set[frozenset[str]]:
    return {frozenset(pair) for pair in zip(result.path, result.path[1:])}


def plan_multiple_agents(
    graph: CampusGraph,
    starts: list[str],
    exits: list[str],
    hazard_weight: float = 4.0,
    congestion_weight: float = 2.0,
    conflict_penalty: float = 8.0,
    max_agents_per_exit: int = 2,
) -> MultiAgentPlan:
    """Search all exit assignments and minimize route cost plus corridor conflicts."""
    if not starts or not exits:
        raise ValueError("At least one agent and one exit are required")
    if len(set(starts)) != len(starts):
        raise ValueError("Agent starting locations must be unique")

    route_cache = {
        (start, exit_name): astar(graph, start, exit_name, hazard_weight, congestion_weight)
        for start in starts
        for exit_name in exits
    }
    best: MultiAgentPlan | None = None
    for assignment in product(exits, repeat=len(starts)):
        loads = {exit_name: assignment.count(exit_name) for exit_name in exits}
        if max(loads.values(), default=0) > max_agents_per_exit:
            continue
        results = [route_cache[(start, exit_name)] for start, exit_name in zip(starts, assignment)]
        if any(not result.reached for result in results):
            continue
        edge_counts: dict[frozenset[str], int] = {}
        for result in results:
            for edge in _path_edges(result):
                edge_counts[edge] = edge_counts.get(edge, 0) + 1
        conflicts = sum(count - 1 for count in edge_counts.values() if count > 1)
        objective = sum(result.weighted_cost for result in results) + conflict_penalty * conflicts
        plans = [
            AgentPlan(f"Agent {index + 1}", start, exit_name, result)
            for index, (start, exit_name, result) in enumerate(zip(starts, assignment, results))
        ]
        candidate = MultiAgentPlan(plans, objective, conflicts, loads)
        if best is None or candidate.objective_cost < best.objective_cost:
            best = candidate
    if best is None:
        return MultiAgentPlan([], float("inf"), 0, {exit_name: 0 for exit_name in exits})
    return best

