from __future__ import annotations

from copy import deepcopy

from .models import CampusGraph


POSITIONS = {
    "North Gate": (0, 8),
    "Library": (3, 8),
    "Lecture Hall": (6, 8),
    "East Exit": (10, 8),
    "Cafeteria": (0, 4),
    "Central Atrium": (3, 4),
    "Computer Lab": (6, 4),
    "Admin Block": (10, 4),
    "Sports Hall": (0, 0),
    "South Junction": (3, 0),
    "Science Lab": (6, 0),
    "South Exit": (10, 0),
}

EDGES = [
    ("North Gate", "Library", 3.0, 0.10),
    ("Library", "Lecture Hall", 3.0, 0.35),
    ("Lecture Hall", "East Exit", 4.0, 0.10),
    ("North Gate", "Cafeteria", 4.0, 0.15),
    ("Library", "Central Atrium", 4.0, 0.25),
    ("Lecture Hall", "Computer Lab", 4.0, 0.20),
    ("East Exit", "Admin Block", 4.0, 0.05),
    ("Cafeteria", "Central Atrium", 3.0, 0.55),
    ("Central Atrium", "Computer Lab", 3.0, 0.70),
    ("Computer Lab", "Admin Block", 4.0, 0.30),
    ("Cafeteria", "Sports Hall", 4.0, 0.10),
    ("Central Atrium", "South Junction", 4.0, 0.35),
    ("Computer Lab", "Science Lab", 4.0, 0.15),
    ("Admin Block", "South Exit", 4.0, 0.10),
    ("Sports Hall", "South Junction", 3.0, 0.10),
    ("South Junction", "Science Lab", 3.0, 0.25),
    ("Science Lab", "South Exit", 4.0, 0.10),
    ("Library", "Computer Lab", 5.0, 0.25),
    ("Central Atrium", "Science Lab", 5.0, 0.30),
]


def base_campus() -> CampusGraph:
    graph = CampusGraph(positions=deepcopy(POSITIONS))
    for source, target, distance, congestion in EDGES:
        graph.add_edge(source, target, distance, congestion)
    return graph


def apply_scenario(graph: CampusGraph, name: str) -> None:
    if name == "Library fire":
        graph.hazards.update({"Library": 0.95, "Central Atrium": 0.50, "Lecture Hall": 0.35})
    elif name == "Science lab leak":
        graph.hazards.update({"Science Lab": 0.98, "South Junction": 0.45, "Computer Lab": 0.30})
    elif name == "Atrium congestion":
        graph.hazards.update({"Central Atrium": 0.20})
        for node, edges in graph.adjacency.items():
            graph.adjacency[node] = [
                type(edge)(edge.target, edge.distance, 0.95 if "Central Atrium" in (node, edge.target) else edge.congestion)
                for edge in edges
            ]
    elif name == "Blocked east wing":
        graph.blocked_edges.update({
            frozenset(("Computer Lab", "Admin Block")),
            frozenset(("Lecture Hall", "East Exit")),
        })


SCENARIOS = ["Normal operation", "Library fire", "Science lab leak", "Atrium congestion", "Blocked east wing"]
EXITS = ["East Exit", "South Exit", "North Gate"]


def graph_tables(graph: CampusGraph) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    nodes = [
        {"name": name, "x": position[0], "y": position[1], "hazard": graph.hazards[name]}
        for name, position in graph.positions.items()
    ]
    edges: list[dict[str, object]] = []
    seen: set[frozenset[str]] = set()
    for source, neighbours in graph.adjacency.items():
        for edge in neighbours:
            pair = frozenset((source, edge.target))
            if pair in seen:
                continue
            seen.add(pair)
            edges.append({
                "source": source,
                "target": edge.target,
                "distance": edge.distance,
                "congestion": edge.congestion,
                "blocked": pair in graph.blocked_edges,
            })
    return nodes, edges


def graph_from_tables(nodes: list[dict[str, object]], edges: list[dict[str, object]]) -> CampusGraph:
    positions: dict[str, tuple[float, float]] = {}
    hazards: dict[str, float] = {}
    for row in nodes:
        name = str(row.get("name", "")).strip()
        if not name:
            raise ValueError("Every node needs a name")
        if name in positions:
            raise ValueError(f"Duplicate node name: {name}")
        positions[name] = (float(row["x"]), float(row["y"]))
        hazard = float(row.get("hazard", 0.0))
        if not 0 <= hazard <= 1:
            raise ValueError(f"Hazard for {name} must be between 0 and 1")
        hazards[name] = hazard
    graph = CampusGraph(positions=positions, hazards=hazards)
    for row in edges:
        source, target = str(row.get("source", "")).strip(), str(row.get("target", "")).strip()
        congestion = float(row.get("congestion", 0.0))
        if not 0 <= congestion <= 1:
            raise ValueError("Congestion must be between 0 and 1")
        graph.add_edge(source, target, float(row["distance"]), congestion)
        if bool(row.get("blocked", False)):
            graph.blocked_edges.add(frozenset((source, target)))
    return graph
