# SafeRoute AI

An explainable campus evacuation planner for an academic Artificial Intelligence course. It compares uninformed and informed search, models changing route risk, and visualizes how the search frontier develops.

## Features

- BFS, DFS, Greedy Best-First, and risk-aware A* implemented from first principles
- Weighted cost combining distance, hazard probability, and congestion
- Five reproducible emergency scenarios
- Mid-route obstacle simulation with automatic replanning
- Joint exit assignment for up to five evacuation agents
- Editable node and corridor tables with validation
- Interactive search replay and algorithm comparison dashboard
- Automated tests for reachability, blocked routes, hazard avoidance, and probability updates

## Run locally

Python 3.10 or newer is recommended.

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` if the browser does not open automatically.

## Run the tests

```bash
pytest -q
```

## Project structure

```text
app.py                       Streamlit user interface
evacuation/models.py         Graph, edge, and result data models
evacuation/algorithms.py     Four search implementations
evacuation/risk.py           Bayesian probability update
evacuation/planning.py       Nondeterministic replanning simulation
evacuation/multiagent.py     Joint exit assignment and conflict penalties
evacuation/scenarios.py      Campus map and emergency scenarios
evacuation/visualization.py  Interactive Plotly campus map
tests/test_algorithms.py     Automated correctness checks
scripts/run_experiments.py   Reproducible experiment table generator
```

## Academic note

NetworkX is intentionally not used to calculate routes. Search is implemented directly so the queue, stack, priority queue, heuristic, parent map, and cost updates can be explained and assessed.

## Generate experiment results

```bash
python scripts/run_experiments.py
```

This writes `outputs/experiment_results.csv` and keeps the computed summary in `work/experiment_summary.json`.
