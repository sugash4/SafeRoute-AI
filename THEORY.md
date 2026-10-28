# SafeRoute AI — theory and viva guide

## 1. Problem formulation

The campus is an undirected weighted graph `G = (V, E)`. A vertex is a location and an edge is a traversable corridor. A search state is the agent's current vertex. An action moves the agent to an unblocked neighbouring vertex. The goal test checks whether the current vertex equals the chosen exit.

The transition cost is:

```text
C(u,v) = distance(u,v) × [1 + hazard_weight × mean_risk(u,v)
                           + congestion_weight × congestion(u,v)]
```

All terms are non-negative. A route's cost is the sum of its transition costs.

## 2. BFS

Breadth-First Search uses a FIFO queue and expands the shallowest unvisited state first. It is complete on a finite graph. It is optimal for the fewest-edge objective when all actions have equal cost, but not for this weighted safety objective.

Complexity is `O(V + E)` with an adjacency list.

## 3. DFS

Depth-First Search uses a LIFO stack. It follows one branch deeply before backtracking. It often uses less frontier memory than BFS, but its returned route depends on neighbour order and need not be shortest or safest.

Complexity is `O(V + E)` for graph search with a visited set.

## 4. Greedy Best-First Search

Greedy search uses a priority queue ordered only by `h(n)`, the estimated remaining distance. It can reach the goal quickly but ignores both accumulated distance and past danger. Therefore it is neither generally optimal nor reliably safe.

## 5. A*

A* orders the priority queue by:

```text
f(n) = g(n) + h(n)
```

`g(n)` is the best known accumulated weighted cost. `h(n)` is straight-line distance to the exit. Because every edge cost is at least its physical distance, straight-line distance does not overestimate the remaining weighted cost when edge distances are consistent with the map. Under that assumption the heuristic is admissible, so A* returns a minimum-cost route.

## 6. Bayesian sensor update

Bayes' rule is:

```text
P(H|E) = P(E|H)P(H) / [P(E|H)P(H) + P(E|not H)P(not H)]
```

`H` means a real hazard and `E` is sensor evidence. The app applies smoke evidence and heat evidence sequentially, assuming conditional independence for teaching purposes. This is an explicit modelling assumption and a limitation, not a universal fact.

## 7. Agent and environment classification

The route planner is a goal-based, utility-sensitive agent. The simulated campus is sequential, dynamic, partially observable, and nondeterministic: actions affect later choices, conditions can change, sensors are uncertain, and a corridor may become unavailable.

The replanning drill follows an observe–update–plan cycle: execute one action, observe a newly blocked corridor, update the graph, and run A* from the agent's current state. Starting the new search from the original location would be conceptually wrong because that state is no longer current.

## 8. How the code maps to theory

- `CampusGraph.adjacency` is the state-space connectivity model.
- `neighbours()` is the successor function and filters blocked actions.
- `parent` records how each discovered state was reached.
- `_reconstruct()` follows parent links backward to produce the solution.
- `deque` implements the BFS queue.
- Python lists implement the DFS stack.
- `heapq` implements the Greedy and A* priority queues.
- `g_score` stores the cheapest known cost from the initial state.
- `expanded_order` makes algorithm behaviour observable and comparable.

## 9. Likely viva questions

**Why is BFS not safest?** It minimizes depth (number of edges), not the weighted hazard cost.

**Why can Greedy fail?** It considers only estimated remaining distance and ignores the cost accumulated so far.

**Why is the A* heuristic admissible?** Straight-line distance is a lower bound on physical route distance, and hazard/congestion only add non-negative cost.

**Why use probability instead of a Boolean fire value?** Sensors can produce false positives and false negatives; probability preserves uncertainty.

**Is the system machine learning?** No. It is classical AI using search, knowledge representation, probability, and planning. AI is broader than machine learning.

**What is the main limitation?** The campus and sensor likelihoods are simulated. Real deployment would require calibrated sensors, validated maps, accessibility constraints, and safety certification.

## 10. Ethical and safety limitation

This is an educational simulator, not a certified life-safety system. A real evacuation tool must handle accessibility, sensor failure, network outage, privacy, crowd behaviour, and official emergency procedures.

## 11. Multiagent planning

The centralized planner tries every feasible assignment of selected agents to available exits. Its objective adds individual route costs and a penalty for each corridor used by more than one agent:

```text
J = sum(route_cost_i) + conflict_penalty × shared_corridor_uses
```

The exit-capacity constraint prevents all agents from being assigned to a single exit. This method is exact for the small classroom graph but grows exponentially with the number of agents. Larger deployments would need conflict-based search, prioritized planning, or another scalable method.

## 12. Editable map validation

The map editor converts node and corridor tables into a `CampusGraph`. Validation rejects blank or duplicate node names, missing edge endpoints, non-positive distance, and probability values outside zero to one. The editor stores a separate custom map so the preset scenarios remain reproducible.

## 13. Additional viva questions

**Why penalize shared corridors?** Several agents on one corridor model congestion and reduce route diversity during an emergency.

**Is the multiagent method scalable?** No. Enumerating all exit assignments is suitable for a small academic graph. The number of assignments grows as exits raised to the number of agents.

**How does the map editor protect correctness?** It validates the graph before replacing the active custom map.
