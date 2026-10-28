from __future__ import annotations

from collections import deque
from heapq import heappop, heappush
from itertools import count
from time import perf_counter
from typing import Callable

from .models import CampusGraph, SearchResult


def _reconstruct(parent: dict[str, str | None], goal: str) -> list[str]:
    path: list[str] = []
    current: str | None = goal
    while current is not None:
        path.append(current)
        current = parent[current]
    return list(reversed(path))


def _metrics(
    graph: CampusGraph,
    algorithm: str,
    path: list[str],
    expanded: list[str],
    started: float,
    hazard_weight: float,
    congestion_weight: float,
) -> SearchResult:
    distance = risk = congestion = weighted = 0.0
    for source, target in zip(path, path[1:]):
        edge = graph.get_edge(source, target)
        mean_risk = (graph.hazards[source] + graph.hazards[target]) / 2
        distance += edge.distance
        risk += mean_risk * edge.distance
        congestion += edge.congestion * edge.distance
        weighted += graph.edge_cost(source, edge, hazard_weight, congestion_weight)
    return SearchResult(
        algorithm=algorithm,
        path=path,
        reached=bool(path),
        weighted_cost=weighted,
        distance=distance,
        risk_exposure=risk,
        congestion_exposure=congestion,
        expanded_order=expanded,
        runtime_ms=(perf_counter() - started) * 1000,
    )


def _failure(algorithm: str, expanded: list[str], started: float) -> SearchResult:
    return SearchResult(algorithm, [], False, float("inf"), float("inf"), float("inf"), float("inf"), expanded, (perf_counter() - started) * 1000)


def breadth_first(graph: CampusGraph, start: str, goal: str, hazard_weight: float = 4.0, congestion_weight: float = 2.0) -> SearchResult:
    """BFS optimizes number of edges, not weighted evacuation cost."""
    started = perf_counter()
    frontier = deque([start])
    parent: dict[str, str | None] = {start: None}
    expanded: list[str] = []
    while frontier:
        node = frontier.popleft()
        expanded.append(node)
        if node == goal:
            return _metrics(graph, "BFS", _reconstruct(parent, goal), expanded, started, hazard_weight, congestion_weight)
        for edge in sorted(graph.neighbours(node), key=lambda item: item.target):
            if edge.target not in parent:
                parent[edge.target] = node
                frontier.append(edge.target)
    return _failure("BFS", expanded, started)


def depth_first(graph: CampusGraph, start: str, goal: str, hazard_weight: float = 4.0, congestion_weight: float = 2.0) -> SearchResult:
    """Iterative DFS avoids recursion limits and exposes its stack behaviour."""
    started = perf_counter()
    stack = [start]
    parent: dict[str, str | None] = {start: None}
    expanded: list[str] = []
    while stack:
        node = stack.pop()
        expanded.append(node)
        if node == goal:
            return _metrics(graph, "DFS", _reconstruct(parent, goal), expanded, started, hazard_weight, congestion_weight)
        for edge in sorted(graph.neighbours(node), key=lambda item: item.target, reverse=True):
            if edge.target not in parent:
                parent[edge.target] = node
                stack.append(edge.target)
    return _failure("DFS", expanded, started)


def greedy_best_first(graph: CampusGraph, start: str, goal: str, hazard_weight: float = 4.0, congestion_weight: float = 2.0) -> SearchResult:
    """Greedy search prioritizes only estimated distance to the goal."""
    started = perf_counter()
    tie = count()
    frontier: list[tuple[float, int, str]] = [(graph.heuristic(start, goal), next(tie), start)]
    parent: dict[str, str | None] = {start: None}
    expanded: list[str] = []
    closed: set[str] = set()
    while frontier:
        _, _, node = heappop(frontier)
        if node in closed:
            continue
        closed.add(node)
        expanded.append(node)
        if node == goal:
            return _metrics(graph, "Greedy", _reconstruct(parent, goal), expanded, started, hazard_weight, congestion_weight)
        for edge in graph.neighbours(node):
            if edge.target not in closed and edge.target not in parent:
                parent[edge.target] = node
                heappush(frontier, (graph.heuristic(edge.target, goal), next(tie), edge.target))
    return _failure("Greedy", expanded, started)


def astar(graph: CampusGraph, start: str, goal: str, hazard_weight: float = 4.0, congestion_weight: float = 2.0) -> SearchResult:
    """Risk-aware A* using f(n)=g(n)+h(n)."""
    started = perf_counter()
    tie = count()
    frontier: list[tuple[float, int, str]] = [(graph.heuristic(start, goal), next(tie), start)]
    parent: dict[str, str | None] = {start: None}
    g_score = {start: 0.0}
    expanded: list[str] = []
    closed: set[str] = set()
    while frontier:
        _, _, node = heappop(frontier)
        if node in closed:
            continue
        closed.add(node)
        expanded.append(node)
        if node == goal:
            return _metrics(graph, "A*", _reconstruct(parent, goal), expanded, started, hazard_weight, congestion_weight)
        for edge in graph.neighbours(node):
            tentative = g_score[node] + graph.edge_cost(node, edge, hazard_weight, congestion_weight)
            if tentative < g_score.get(edge.target, float("inf")):
                parent[edge.target] = node
                g_score[edge.target] = tentative
                priority = tentative + graph.heuristic(edge.target, goal)
                heappush(frontier, (priority, next(tie), edge.target))
                closed.discard(edge.target)
    return _failure("A*", expanded, started)


ALGORITHMS: dict[str, Callable[..., SearchResult]] = {
    "Breadth-First Search": breadth_first,
    "Depth-First Search": depth_first,
    "Greedy Best-First": greedy_best_first,
    "A* Risk-Aware": astar,
}

