from evacuation.algorithms import astar
from evacuation.scenarios import apply_scenario, base_campus
from evacuation.visualization import campus_figure


def test_live_map_labels_route_costs_and_node_hazards() -> None:
    graph = base_campus()
    apply_scenario(graph, "Science lab leak")
    result = astar(graph, "Library", "South Exit", hazard_weight=5.0, congestion_weight=2.0)

    figure = campus_figure(
        graph,
        result,
        hazard_weight=5.0,
        congestion_weight=2.0,
        show_calculations=True,
    )

    edge_costs = [float(annotation.text.split()[-1]) for annotation in figure.layout.annotations]
    assert len(edge_costs) == len(result.path) - 1
    assert abs(sum(edge_costs) - result.weighted_cost) < 0.02
    assert any("Science Lab<br><b>hazard 98%</b>" == label for label in figure.data[-1].text)
