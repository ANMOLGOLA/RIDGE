from typing import Dict, Any, List

def generate_plain_english_explanation(features: Dict[str, float], risk_score: float) -> str:
    """
    Returns the top contributing risk factors in plain English.
    Example: 'Heavy rain forecast (84mm) + steep slope (23°) + landslide-prone zone'
    """
    if risk_score >= 0.95:
        return "Critical blockage detected on segment; traffic completely halted."

    reasons = []

    # Rain
    past_rain = features.get("rain_past_24h_mm", 0)
    fc_rain = features.get("rain_forecast_24h_mm", 0)
    if fc_rain > 60:
        reasons.append(f"Heavy rain forecast ({fc_rain:.0f}mm)")
    elif past_rain > 50:
        reasons.append(f"High 24h precipitation ({past_rain:.0f}mm)")

    # Slope
    slope = features.get("slope_deg", 0)
    if slope >= 18:
        reasons.append(f"Steep incline ({slope:.1f}°)")

    # Landslide Zone
    if features.get("landslide_zone", 0) > 0.5:
        reasons.append("Identified landslide-susceptibility corridor")

    # River proximity
    river_prox = features.get("river_proximity_m", 500)
    if river_prox <= 80:
        reasons.append(f"Close to river ({river_prox:.0f}m)")

    # Live incidents
    live_inc = features.get("live_incidents_nearby", 0)
    if live_inc > 0:
        reasons.append(f"{int(live_inc)} active live advisory nearby")

    if not reasons:
        return "Standard transit conditions with low environmental risk."

    return " + ".join(reasons[:3])
