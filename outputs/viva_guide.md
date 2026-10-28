# SafeRoute AI viva guide

## Core definitions

- A state is the agent's current campus location.
- The successor function returns connected locations whose corridors are not blocked.
- The goal test checks whether the agent reached the selected exit.
- The heuristic is straight-line distance from a node to the exit.
- The utility-sensitive cost combines distance, hazard probability, and congestion.

## Search questions

**Why is BFS not always safest?** BFS minimizes the number of edges when each action is treated equally. It does not minimize the weighted risk cost.

**Why is DFS included?** DFS provides an uninformed baseline and demonstrates how neighbour order can produce a poor route.

**What is the difference between Greedy and A star?** Greedy orders nodes using only the remaining estimate. A star adds accumulated route cost to that estimate.

**When is A star optimal?** Graph-search A star is optimal when its heuristic is admissible and the implementation correctly updates improved path costs. Straight-line distance is a lower bound here because hazard and congestion only add non-negative cost.

**What is the time complexity?** BFS and DFS are O of V plus E on a graph with a visited set. Priority-queue search adds logarithmic queue operations, while practical A star performance depends heavily on the heuristic.

## Uncertainty questions

**What does the Bayesian component calculate?** It calculates the probability of a hazard after receiving smoke and heat evidence.

**What assumption does the sensor combination make?** It treats smoke and heat evidence as conditionally independent given the hazard state. This simplifies the classroom model.

**Why not use a Boolean hazard value?** A Boolean value hides false positives and false negatives. Probability allows the route planner to respond proportionally to uncertain evidence.

## Planning questions

**What makes the environment dynamic?** A corridor can become blocked after the agent begins moving.

**Why replan from the current node?** The agent has already executed an action. The original start is no longer its state.

**How does multiagent planning differ from repeated single-agent planning?** The joint objective also considers corridor conflicts and exit capacity.

**What limits the current multiagent approach?** Exhaustive exit assignment grows exponentially as more agents or exits are added.

## Implementation questions

**Why use dataclasses?** They give graph edges, search results, and planning results explicit fields and reduce accidental dictionary-key errors.

**Why use a heap for A star?** A heap retrieves the smallest priority in logarithmic time.

**Why store parent links?** Parent links reconstruct a route without copying the complete path into every frontier entry.

**Did a library calculate the routes?** No. The search algorithms are implemented directly. Plotly renders maps, Pandas displays tables, and Streamlit provides the interface.

**How was the system tested?** Nine automated tests cover reachability, hazard avoidance, blocked routes, failure cases, Bayesian updates, replanning, multiagent capacity, editable-map reconstruction, and the visible route-cost and hazard labels.

## Limitations

- The campus graph and sensor likelihoods are simulated.
- Straight-line coordinates simplify real building geometry.
- The model does not simulate speed, mobility needs, smoke propagation, or human behaviour.
- The multiagent planner supports a small academic graph, not thousands of evacuees.
- A real safety system would require certified data, hardware integration, security review, and emergency-authority approval.
