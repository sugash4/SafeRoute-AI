from __future__ import annotations

import plotly.graph_objects as go

from .models import CampusGraph, SearchResult
from .multiagent import MultiAgentPlan


def campus_figure(
    graph: CampusGraph,
    result: SearchResult,
    hazard_weight: float | None = None,
    congestion_weight: float | None = None,
    show_calculations: bool = False,
) -> go.Figure:
    path_edges = {frozenset(pair) for pair in zip(result.path, result.path[1:])}
    figure = go.Figure()
    cost_annotations: list[dict[str, object]] = []

    seen: set[frozenset[str]] = set()
    for source, edges in graph.adjacency.items():
        for edge in edges:
            pair = frozenset((source, edge.target))
            if pair in seen:
                continue
            seen.add(pair)
            x0, y0 = graph.positions[source]
            x1, y1 = graph.positions[edge.target]
            blocked = pair in graph.blocked_edges
            selected = pair in path_edges
            color = "#ff4d6d" if blocked else "#38d9a9" if selected else "#40546f"
            width = 6 if selected else 3 if blocked else 1.5
            hover_text = (
                f"{source} ↔ {edge.target}<br>{edge.distance:.1f} distance"
                f"<br>{edge.congestion:.0%} congestion"
            )
            if selected and show_calculations and hazard_weight is not None and congestion_weight is not None:
                mean_risk = (graph.hazards[source] + graph.hazards[edge.target]) / 2
                weighted_cost = graph.edge_cost(source, edge, hazard_weight, congestion_weight)
                hover_text += (
                    f"<br>{mean_risk:.0%} average hazard"
                    f"<br><b>Weighted cost: {weighted_cost:.2f}</b>"
                )
                cost_annotations.append({
                    "x": (x0 + x1) / 2,
                    "y": (y0 + y1) / 2,
                    "text": f"cost {weighted_cost:.2f}",
                    "showarrow": False,
                    "font": {"color": "#071526", "family": "IBM Plex Mono, monospace", "size": 12},
                    "bgcolor": "#8ff0d0",
                    "bordercolor": "#071526",
                    "borderwidth": 1,
                    "borderpad": 4,
                    "opacity": 0.96,
                })
            figure.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1], mode="lines",
                line={"color": color, "width": width, "dash": "dot" if blocked else "solid"},
                hoverinfo="text",
                text=hover_text,
                showlegend=False,
            ))

    explored = set(result.expanded_order)
    nodes = list(graph.positions)
    colors = [
        "#ff4d6d" if graph.hazards[node] >= 0.65 else
        "#ffb703" if graph.hazards[node] >= 0.25 else
        "#8ae8ff" if node in explored else "#d8e3ed"
        for node in nodes
    ]
    sizes = [22 + graph.hazards[node] * 18 for node in nodes]
    node_labels = [
        f"{node}<br><b>hazard {graph.hazards[node]:.0%}</b>" if show_calculations else node
        for node in nodes
    ]
    figure.add_trace(go.Scatter(
        x=[graph.positions[node][0] for node in nodes],
        y=[graph.positions[node][1] for node in nodes],
        mode="markers+text",
        text=node_labels,
        textposition="top center",
        textfont={"size": 12},
        marker={"size": sizes, "color": colors, "line": {"color": "#071526", "width": 2}},
        customdata=[
            [graph.hazards[node], "explored" if node in explored else "not explored", node]
            for node in nodes
        ],
        hovertemplate="<b>%{customdata[2]}</b><br>Hazard: %{customdata[0]:.0%}<br>%{customdata[1]}<extra></extra>",
        showlegend=False,
    ))
    figure.update_layout(
        height=560,
        margin={"l": 15, "r": 15, "t": 15, "b": 15},
        paper_bgcolor="#0b1728",
        plot_bgcolor="#0b1728",
        font={"color": "#d8e3ed", "family": "IBM Plex Sans, sans-serif"},
        xaxis={"visible": False, "range": [-1, 11]},
        yaxis={"visible": False, "range": [-1.2, 9.3], "scaleanchor": "x", "scaleratio": 1},
        hoverlabel={"bgcolor": "#132640", "font_color": "#f4f7fb"},
        annotations=cost_annotations,
    )
    return figure


def multiagent_figure(graph: CampusGraph, plan: MultiAgentPlan) -> go.Figure:
    empty = SearchResult("Multi-agent", [], False, 0, 0, 0, 0, [], 0)
    figure = campus_figure(graph, empty)
    palette = ["#38d9a9", "#8ae8ff", "#ffb703", "#ff7b9c", "#b197fc"]
    for index, agent_plan in enumerate(plan.plans):
        color = palette[index % len(palette)]
        x = [graph.positions[node][0] for node in agent_plan.result.path]
        y = [graph.positions[node][1] for node in agent_plan.result.path]
        figure.add_trace(go.Scatter(
            x=x, y=y, mode="lines+markers", name=agent_plan.agent,
            line={"color": color, "width": 6},
            marker={"size": 9, "color": color},
            hovertemplate=f"{agent_plan.agent}: {agent_plan.start} to {agent_plan.exit}<extra></extra>",
        ))
    figure.update_layout(legend={"orientation": "h", "y": 1.02, "x": 0})
    return figure


