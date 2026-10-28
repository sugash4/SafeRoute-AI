# SafeRoute AI demonstration script

## Opening

My project is SafeRoute AI, an explainable campus evacuation planner. The campus is represented as a weighted graph. Rooms and exits are states, corridors are actions, and the agent chooses routes using distance, hazard probability, and congestion.

## Live route calculation

Open Live map. Every node label shows its hazard probability, and every mint route segment shows its weighted edge cost. Explain that each edge cost combines its distance, the average hazard of its two endpoint nodes, and corridor congestion. The total weighted cost below the map is the sum of the displayed route-segment costs.

## Search comparison

Open the Compare tab with Library as the start and South Exit as the goal. Explain that BFS minimizes the number of edges, DFS follows one branch, Greedy uses only the remaining-distance estimate, and A star combines accumulated cost with a heuristic. Point to weighted cost and nodes expanded rather than claiming that one algorithm wins on every metric.

## Dynamic replanning

Open Replanning. The agent first plans Library to Computer Lab to Science Lab to South Exit. The simulator closes the Computer Lab to Science Lab corridor after the first move. The agent observes the changed environment and searches again from Computer Lab through Admin Block to South Exit.

## Multiagent planning

Open Multi-agent with Library, Cafeteria, and Science Lab selected. Explain that the centralized planner evaluates exit assignments, enforces exit capacity, and penalizes shared corridors. In the default experiment, it plans three agents with no shared corridor.

## Editable campus map

Open Map editor. Show the node and corridor tables. Explain that a user can change coordinates, risk, distance, congestion, and blocked status. The program validates the edited graph before it can become active.

## Closing

The project combines state-space search, risk-aware routing, planning in a changing environment, and multiagent coordination. Its main limitation is that the map and risk values are simulated, so the application is an educational prototype rather than a certified emergency system.

