from __future__ import annotations

import pandas as pd
import streamlit as st

from evacuation.algorithms import ALGORITHMS
from evacuation.multiagent import plan_multiple_agents
from evacuation.planning import simulate_unexpected_blockage
from evacuation.scenarios import (
    EXITS,
    SCENARIOS,
    apply_scenario,
    base_campus,
    graph_from_tables,
    graph_tables,
)
from evacuation.visualization import campus_figure, multiagent_figure


st.set_page_config(page_title="SafeRoute AI", page_icon="🧭", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&family=Space+Grotesk:wght@500;600&display=swap');
:root { --ink:#071526; --panel:#0b1728; --line:#29415f; --cyan:#8ae8ff; --mint:#38d9a9; --amber:#ffb703; }
.stApp { background: radial-gradient(circle at 80% 0%, #142e47 0, #071526 34rem); color:#eaf2f8; }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-0.035em; }
[data-testid="stSidebar"] { background:#091321; border-right:1px solid #263b54; }
[data-testid="stMetric"] { background:#0d1d31; border:1px solid #29415f; padding:1rem; border-radius:4px; }
[data-testid="stMetricValue"] { font-family:'IBM Plex Mono',monospace; color:#8ae8ff; }
.eyebrow { font:600 .75rem 'IBM Plex Mono'; color:#8ae8ff; letter-spacing:.16em; text-transform:uppercase; }
.hero { border-left:4px solid #38d9a9; padding:.15rem 0 .15rem 1.2rem; margin:.4rem 0 1.6rem; }
.hero p { color:#9db0c3; max-width:56rem; }
.status { font:600 .8rem 'IBM Plex Mono'; color:#38d9a9; }
.route { font:500 .92rem 'IBM Plex Mono'; color:#d8e3ed; background:#0d1d31; border:1px solid #29415f; padding:.85rem 1rem; border-radius:4px; }
.legend { font:.78rem 'IBM Plex Mono'; color:#91a4b8; }
.stButton button { border-radius:3px; border:1px solid #38d9a9; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="eyebrow">Intelligent evacuation laboratory · CO2 / CO3 / CO5</div>', unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>SafeRoute AI</h1><p>Compare classical search strategies on a campus whose risk changes while people move.</p></div>', unsafe_allow_html=True)

if "custom_nodes" not in st.session_state or "custom_edges" not in st.session_state:
    initial_nodes, initial_edges = graph_tables(base_campus())
    st.session_state["custom_nodes"] = initial_nodes
    st.session_state["custom_edges"] = initial_edges

with st.sidebar:
    st.header("Mission controls")
    use_custom_map = st.toggle("Use edited campus map", value=False)
    scenario = st.selectbox("Emergency scenario", SCENARIOS, disabled=use_custom_map)
    if use_custom_map:
        try:
            graph = graph_from_tables(st.session_state["custom_nodes"], st.session_state["custom_edges"])
        except (ValueError, KeyError, TypeError) as error:
            st.error(f"Map validation failed: {error}")
            graph = base_campus()
    else:
        graph = base_campus()
        apply_scenario(graph, scenario)
    available_exits = [node for node in EXITS if node in graph.positions]
    if not available_exits:
        available_exits = list(graph.positions)[-1:]
    starts = [node for node in graph.positions if node not in available_exits]
    preferred_start = starts.index("Library") if "Library" in starts else 0
    preferred_exit = available_exits.index("South Exit") if "South Exit" in available_exits else 0
    start = st.selectbox("Starting location", starts, index=preferred_start)
    goal = st.selectbox("Safe exit", available_exits, index=preferred_exit)
    algorithm_name = st.selectbox("Search strategy", list(ALGORITHMS), index=3)
    st.divider()
    st.caption("Cost priorities")
    hazard_weight = st.slider("Hazard penalty", 0.0, 10.0, 5.0, 0.5)
    congestion_weight = st.slider("Congestion penalty", 0.0, 6.0, 2.0, 0.5)

algorithm = ALGORITHMS[algorithm_name]
result = algorithm(graph, start, goal, hazard_weight, congestion_weight)

tab_map, tab_compare, tab_replan, tab_agents, tab_editor = st.tabs([
    "Live map",
    "Compare",
    "Replanning",
    "Multi-agent",
    "Map editor",
])

with tab_map:
    if result.reached:
        st.markdown('<div class="status">● ROUTE FOUND</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="route">{" → ".join(result.path)}</div>', unsafe_allow_html=True)
    else:
        st.error("No safe route exists with the current blocked corridors.")

    st.plotly_chart(
        campus_figure(graph, result, hazard_weight, congestion_weight, show_calculations=True),
        width="stretch",
        config={"displayModeBar": False},
    )
    st.markdown('<div class="legend">MINT LINE · selected route &nbsp;&nbsp; COST LABEL · weighted edge cost &nbsp;&nbsp; NODE LABEL · hazard value &nbsp;&nbsp; RED · severe risk / blocked</div>', unsafe_allow_html=True)

    columns = st.columns(4)
    columns[0].metric("Weighted cost", f"{result.weighted_cost:.2f}" if result.reached else "∞")
    columns[1].metric("Route distance", f"{result.distance:.1f}" if result.reached else "—")
    columns[2].metric("Nodes expanded", result.nodes_expanded)
    columns[3].metric("Runtime", f"{result.runtime_ms:.3f} ms")

    if result.reached:
        st.divider()
        st.subheader("Mathematical route-cost proof")
        st.latex(r"\bar{H}(u,v)=\frac{H(u)+H(v)}{2}")
        st.latex(r"C(u,v)=d(u,v)\left[1+w_h\bar{H}(u,v)+w_cQ(u,v)\right]")
        st.caption(
            f"Current weights: hazard penalty $w_h={hazard_weight:.1f}$ and "
            f"congestion penalty $w_c={congestion_weight:.1f}$."
        )

        proof_rows = []
        proof_costs = []
        for source, target in zip(result.path, result.path[1:]):
            edge = graph.get_edge(source, target)
            average_hazard = (graph.hazards[source] + graph.hazards[target]) / 2
            edge_cost = graph.edge_cost(source, edge, hazard_weight, congestion_weight)
            proof_costs.append(edge_cost)
            proof_rows.append({
                "Selected edge": f"{source} → {target}",
                "Distance d": f"{edge.distance:.2f}",
                "Average hazard H̄": f"{average_hazard:.2f}",
                "Congestion Q": f"{edge.congestion:.2f}",
                "Substitution": (
                    f"{edge.distance:.2f} × [1 + {hazard_weight:.1f} × {average_hazard:.2f} "
                    f"+ {congestion_weight:.1f} × {edge.congestion:.2f}]"
                ),
                "Edge cost": f"{edge_cost:.2f}",
            })

        st.dataframe(pd.DataFrame(proof_rows), hide_index=True, width="stretch")
        cost_sum = sum(proof_costs)
        addition = " + ".join(f"{cost:.2f}" for cost in proof_costs)
        st.latex(rf"C_{{route}}={addition}={cost_sum:.2f}")
        st.success(
            f"Verified: the sum of the selected edge costs is {cost_sum:.2f}, "
            f"which equals the route's weighted cost of {result.weighted_cost:.2f}."
        )

with tab_compare:
    results = [fn(graph, start, goal, hazard_weight, congestion_weight) for fn in ALGORITHMS.values()]
    rows = [{
        "Algorithm": item.algorithm,
        "Reached": "Yes" if item.reached else "No",
        "Weighted cost": round(item.weighted_cost, 2) if item.reached else None,
        "Distance": round(item.distance, 2) if item.reached else None,
        "Risk exposure": round(item.risk_exposure, 2) if item.reached else None,
        "Congestion exposure": round(item.congestion_exposure, 2) if item.reached else None,
        "Nodes expanded": item.nodes_expanded,
        "Runtime (ms)": round(item.runtime_ms, 4),
        "Route": " → ".join(item.path) if item.reached else "No route",
    } for item in results]
    frame = pd.DataFrame(rows)
    st.dataframe(frame, hide_index=True, width="stretch")
    chart_data = frame.set_index("Algorithm")[["Weighted cost", "Nodes expanded"]]
    st.bar_chart(chart_data, color=["#38d9a9", "#8ae8ff"])
    best = min((item for item in results if item.reached), key=lambda item: item.weighted_cost, default=None)
    if best:
        st.info(f"Lowest risk-aware cost: **{best.algorithm.replace('*', ' star')}** at **{best.weighted_cost:.2f}**.")

with tab_replan:
    drill = simulate_unexpected_blockage(graph, start, goal, hazard_weight, congestion_weight)
    if drill.newly_blocked and drill.revised_plan:
        blocked_from, blocked_to = drill.newly_blocked
        st.markdown('<div class="eyebrow">Unexpected environment change</div>', unsafe_allow_html=True)
        st.subheader(f"Corridor closes after the agent reaches {drill.current_location}")
        first, second = st.columns(2)
        first.markdown("**Original plan**")
        first.code(" → ".join(drill.initial_plan.path), language=None)
        second.markdown("**New observation**")
        second.error(f"{blocked_from} ↔ {blocked_to} is now blocked")
        if drill.revised_plan.reached:
            st.success("The agent discarded the invalid remainder and searched again from its current state.")
            st.markdown(f'<div class="route">{" → ".join(drill.revised_plan.path)}</div>', unsafe_allow_html=True)
        else:
            st.error("No alternative path remains. The correct plan is to stop and request assistance.")
        st.plotly_chart(campus_figure(drill.revised_graph, drill.revised_plan), width="stretch", config={"displayModeBar": False})
    else:
        st.warning("Choose a start and exit with at least two route segments to run this drill.")

with tab_agents:
    st.subheader("Coordinated evacuation planning")
    agent_candidates = [node for node in graph.positions if node not in available_exits]
    default_agents = [node for node in ("Library", "Cafeteria", "Science Lab") if node in agent_candidates]
    agent_starts = st.multiselect(
        "Agent starting locations",
        agent_candidates,
        default=default_agents or agent_candidates[: min(3, len(agent_candidates))],
        max_selections=5,
    )
    left, right = st.columns(2)
    conflict_penalty = left.slider("Shared corridor penalty", 0.0, 20.0, 8.0, 1.0)
    exit_capacity = right.slider("Maximum agents per exit", 1, 5, 2)
    if agent_starts:
        coordinated = plan_multiple_agents(
            graph,
            agent_starts,
            available_exits,
            hazard_weight,
            congestion_weight,
            conflict_penalty,
            exit_capacity,
        )
        if coordinated.plans:
            st.plotly_chart(multiagent_figure(graph, coordinated), width="stretch", config={"displayModeBar": False})
            agent_rows = [{
                "Agent": item.agent,
                "Start": item.start,
                "Assigned exit": item.exit,
                "Cost": round(item.result.weighted_cost, 2),
                "Route": " → ".join(item.result.path),
            } for item in coordinated.plans]
            st.dataframe(pd.DataFrame(agent_rows), hide_index=True, width="stretch")
            metric_columns = st.columns(3)
            metric_columns[0].metric("Joint objective", f"{coordinated.objective_cost:.2f}")
            metric_columns[1].metric("Shared corridors", coordinated.shared_corridors)
            metric_columns[2].metric("Agents planned", len(coordinated.plans))
        else:
            st.error("No assignment satisfies the current exit capacity and route constraints.")
    else:
        st.info("Select at least one agent starting location.")

with tab_editor:
    st.subheader("Editable campus graph")
    st.write("Edit coordinates, hazard probabilities, distances, congestion, or blocked corridors. Node names used by an edge must exist in the node table.")
    node_frame = pd.DataFrame(st.session_state["custom_nodes"])
    edge_frame = pd.DataFrame(st.session_state["custom_edges"])
    edited_nodes = st.data_editor(node_frame, num_rows="dynamic", width="stretch", key="node_editor")
    edited_edges = st.data_editor(edge_frame, num_rows="dynamic", width="stretch", key="edge_editor")
    apply_column, reset_column, note_column = st.columns([1, 1, 3])
    if apply_column.button("Validate and apply map", type="primary", width="stretch"):
        node_records = edited_nodes.to_dict("records")
        edge_records = edited_edges.to_dict("records")
        try:
            graph_from_tables(node_records, edge_records)
        except (ValueError, KeyError, TypeError) as error:
            st.error(f"Map validation failed: {error}")
        else:
            st.session_state["custom_nodes"] = node_records
            st.session_state["custom_edges"] = edge_records
            st.success("Map saved. Turn on Use edited campus map in Mission controls.")
    if reset_column.button("Reset editor", width="stretch"):
        reset_nodes, reset_edges = graph_tables(base_campus())
        st.session_state["custom_nodes"] = reset_nodes
        st.session_state["custom_edges"] = reset_edges
        st.rerun()
    note_column.caption("The editor keeps its own map so preset scenarios remain reproducible.")
