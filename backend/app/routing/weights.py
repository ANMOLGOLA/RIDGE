from typing import Dict, Any

def calculate_edge_weight(
    edge_data: Dict[str, Any],
    preference: str = "safest",
    alpha: float = 3.5
) -> float:
    """
    Computes dynamic risk-penalized edge cost:
    cost = base_travel_time * (1 + alpha * risk_score) + blocked_penalty
    """
    base_time = edge_data.get("base_time_sec", 120)
    risk_score = edge_data.get("risk_score", 0.1)
    risk_label = edge_data.get("risk_label", "open")

    if risk_label == "blocked" or risk_score >= 0.98:
        # Severe penalty that forces rerouting around blocked roads
        return base_time + 100000.0

    if preference == "fastest":
        eff_alpha = 0.4
    elif preference == "balanced":
        eff_alpha = 2.0
    else:  # safest
        eff_alpha = alpha

    return base_time * (1.0 + eff_alpha * (risk_score ** 1.5))
