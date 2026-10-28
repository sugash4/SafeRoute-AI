from __future__ import annotations


def bayes_update(prior: float, likelihood_if_hazard: float, likelihood_if_safe: float) -> float:
    """Return P(hazard | evidence) using Bayes' rule."""
    values = (prior, likelihood_if_hazard, likelihood_if_safe)
    if any(value < 0 or value > 1 for value in values):
        raise ValueError("Probabilities must be between 0 and 1")
    evidence = likelihood_if_hazard * prior + likelihood_if_safe * (1 - prior)
    if evidence == 0:
        return prior
    return likelihood_if_hazard * prior / evidence


def combine_sensor_evidence(prior: float, smoke_alarm: bool, heat_alarm: bool) -> float:
    """Sequential update under the teaching assumption of conditional independence."""
    probability = prior
    smoke_hazard, smoke_safe = (0.92, 0.08) if smoke_alarm else (0.08, 0.92)
    probability = bayes_update(probability, smoke_hazard, smoke_safe)
    heat_hazard, heat_safe = (0.88, 0.12) if heat_alarm else (0.12, 0.88)
    return bayes_update(probability, heat_hazard, heat_safe)

