from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evacuation.algorithms import ALGORITHMS
from evacuation.multiagent import plan_multiple_agents
from evacuation.scenarios import EXITS, SCENARIOS, apply_scenario, base_campus


OUTPUTS = ROOT / "outputs"
WORK = ROOT / "work"


def main() -> None:
    OUTPUTS.mkdir(exist_ok=True)
    WORK.mkdir(exist_ok=True)
    rows: list[dict[str, object]] = []
    scenario_cases = {
        "Normal operation": ("Library", "South Exit"),
        "Library fire": ("North Gate", "East Exit"),
        "Science lab leak": ("Library", "South Exit"),
        "Atrium congestion": ("Cafeteria", "East Exit"),
        "Blocked east wing": ("Computer Lab", "East Exit"),
    }
    for scenario in SCENARIOS:
        graph = base_campus()
        apply_scenario(graph, scenario)
        start, goal = scenario_cases[scenario]
        for algorithm in ALGORITHMS.values():
            result = algorithm(graph, start, goal, 5.0, 2.0)
            rows.append({
                "scenario": scenario,
                "start": start,
                "goal": goal,
                "algorithm": result.algorithm,
                "reached": result.reached,
                "weighted_cost": round(result.weighted_cost, 3) if result.reached else "",
                "distance": round(result.distance, 3) if result.reached else "",
                "risk_exposure": round(result.risk_exposure, 3) if result.reached else "",
                "congestion_exposure": round(result.congestion_exposure, 3) if result.reached else "",
                "nodes_expanded": result.nodes_expanded,
                "route": " -> ".join(result.path),
            })
    csv_path = OUTPUTS / "experiment_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    graph = base_campus()
    multi = plan_multiple_agents(
        graph,
        ["Library", "Cafeteria", "Science Lab"],
        EXITS,
        hazard_weight=5.0,
        congestion_weight=2.0,
    )
    summary = {
        "experiment_rows": len(rows),
        "multiagent": {
            "objective": round(multi.objective_cost, 3),
            "shared_corridors": multi.shared_corridors,
            "plans": [
                {
                    "agent": plan.agent,
                    "start": plan.start,
                    "exit": plan.exit,
                    "cost": round(plan.result.weighted_cost, 3),
                    "route": plan.result.path,
                }
                for plan in multi.plans
            ],
        },
    }
    (WORK / "experiment_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
