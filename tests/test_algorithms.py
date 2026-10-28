from evacuation.algorithms import astar, breadth_first, depth_first, greedy_best_first
from evacuation.risk import bayes_update, combine_sensor_evidence
from evacuation.planning import simulate_unexpected_blockage
from evacuation.multiagent import plan_multiple_agents
from evacuation.scenarios import graph_from_tables, graph_tables
from evacuation.scenarios import apply_scenario, base_campus


def test_all_algorithms_reach_exit() -> None:
    graph = base_campus()
    for algorithm in (breadth_first, depth_first, greedy_best_first, astar):
        result = algorithm(graph, "Library", "South Exit")
        assert result.reached
        assert result.path[0] == "Library"
        assert result.path[-1] == "South Exit"


def test_astar_avoids_severe_library_fire() -> None:
    graph = base_campus()
    apply_scenario(graph, "Library fire")
    result = astar(graph, "North Gate", "East Exit", hazard_weight=8.0)
    assert result.reached
    assert "Library" not in result.path


def test_blocked_edges_are_never_used() -> None:
    graph = base_campus()
    apply_scenario(graph, "Blocked east wing")
    result = astar(graph, "Computer Lab", "East Exit")
    traversed = {frozenset(pair) for pair in zip(result.path, result.path[1:])}
    assert traversed.isdisjoint(graph.blocked_edges)


def test_positive_evidence_increases_probability() -> None:
    assert bayes_update(0.1, 0.9, 0.1) > 0.1
    assert combine_sensor_evidence(0.1, True, True) > combine_sensor_evidence(0.1, True, False)


def test_no_path_is_reported() -> None:
    graph = base_campus()
    graph.blocked_edges = {
        frozenset(("East Exit", "Lecture Hall")),
        frozenset(("East Exit", "Admin Block")),
    }
    result = astar(graph, "Library", "East Exit")
    assert not result.reached
    assert result.path == []


def test_dynamic_replanning_blocks_old_route() -> None:
    graph = base_campus()
    drill = simulate_unexpected_blockage(graph, "Library", "South Exit")
    assert drill.newly_blocked is not None
    assert drill.revised_plan is not None
    assert drill.revised_plan.reached
    revised_edges = {frozenset(pair) for pair in zip(drill.revised_plan.path, drill.revised_plan.path[1:])}
    assert frozenset(drill.newly_blocked) not in revised_edges


def test_multiagent_plan_respects_exit_capacity() -> None:
    graph = base_campus()
    plan = plan_multiple_agents(
        graph,
        ["Library", "Cafeteria", "Science Lab"],
        ["East Exit", "South Exit", "North Gate"],
        max_agents_per_exit=2,
    )
    assert len(plan.plans) == 3
    assert max(plan.exit_loads.values()) <= 2
    assert all(item.result.reached for item in plan.plans)


def test_editable_map_round_trip() -> None:
    original = base_campus()
    nodes, edges = graph_tables(original)
    rebuilt = graph_from_tables(nodes, edges)
    assert rebuilt.positions == original.positions
    assert sum(map(len, rebuilt.adjacency.values())) == sum(map(len, original.adjacency.values()))
